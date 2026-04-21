import logging
import signal
import sys
import asyncio
import aiohttp
from datetime import datetime

from confluent_kafka import Consumer, KafkaError, KafkaException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import TimescaleSessionLocal, SessionLocal
from app.models import Telemetry
from app.worker.geofence_service import GeofenceService
from schema_pb2 import Telemetry as TelemetryProto, GeofenceBreach

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class TelemetryWorker:
    def __init__(
        self,
        kafka_bootstrap_servers: str,
        kafka_topic: str,
        kafka_group: str,
        alerts_topic: str,
    ):
        self.kafka_topic = kafka_topic
        self.alerts_topic = alerts_topic

        self.consumer = Consumer(
            {
                "bootstrap.servers": kafka_bootstrap_servers,
                "group.id": kafka_group,
                "auto.offset.reset": "earliest",
                "enable.auto.commit": True,
            }
        )

        self.alerts_producer = Consumer(
            {
                "bootstrap.servers": kafka_bootstrap_servers,
                "group.id": f"{kafka_group}_alerts",
            }
        )

    def process_message(self, msg):
        try:
            import json
            logger.info(f"Processing message from {msg.topic()} [{msg.partition()}]")
            
            try:
                telemetry = TelemetryProto()
                telemetry.ParseFromString(msg.value())
                logger.info(f"Parsed protobuf: belt_id={telemetry.belt_id}")
            except Exception as parse_err:
                logger.info(f"JSON parse fallback: {parse_err}")
                payload = json.loads(msg.value())
                telemetry = TelemetryProto()
                telemetry.belt_id = payload.get("belt_id", "")
                telemetry.latitude = payload.get("latitude", 0)
                telemetry.longitude = payload.get("longitude", 0)
                telemetry.temperature = payload.get("temperature", 0)
                telemetry.activity_level = payload.get("activity_level", 0)
                telemetry.timestamp = payload.get("timestamp", 0)
                logger.info(f"Parsed JSON: belt_id={telemetry.belt_id}")

            logger.info(
                f"Processing telemetry - Belt: {telemetry.belt_id}, "
                f"Position: ({telemetry.latitude}, {telemetry.longitude}), "
                f"Temp: {telemetry.temperature}, "
                f"Activity: {telemetry.activity_level}"
            )

            timescale_db: Session = TimescaleSessionLocal()
            main_db: Session = SessionLocal()
            try:
                db_telemetry = Telemetry(
                    belt_id=telemetry.belt_id,
                    latitude=telemetry.latitude,
                    longitude=telemetry.longitude,
                    temperature=telemetry.temperature,
                    activity_level=telemetry.activity_level,
                    timestamp=datetime.fromtimestamp(telemetry.timestamp),
                )
                timescale_db.add(db_telemetry)
                timescale_db.commit()

                asyncio.run(self._broadcast_telemetry(
                    telemetry.belt_id,
                    telemetry.latitude,
                    telemetry.longitude,
                    telemetry.temperature,
                    telemetry.activity_level,
                    telemetry.timestamp,
                ))

                geofence_service = GeofenceService(main_db)
                is_within, breached_paddock_id = geofence_service.check_geofence(
                    telemetry.belt_id,
                    telemetry.latitude,
                    telemetry.longitude,
                )

                if not is_within and breached_paddock_id:
                    alert = geofence_service.create_breach_alert(
                        telemetry.belt_id,
                        telemetry.latitude,
                        telemetry.longitude,
                        breached_paddock_id,
                    )
                    self._send_alert(alert)

            finally:
                timescale_db.close()
                main_db.close()

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _send_alert(self, alert: dict):
        logger.info(f"Sending alert to Kafka topic {self.alerts_topic}: {alert}")

    async def _broadcast_telemetry(self, belt_id: str, latitude: float, longitude: float, temperature: float, activity_level: float, timestamp: int):
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "type": "telemetry",
                    "belt_id": belt_id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "temperature": temperature,
                    "activity_level": activity_level,
                    "timestamp": timestamp,
                }
                async with session.post(
                    f"http://api:8000/internal/broadcast-telemetry",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        logger.info(f"Broadcasted telemetry for {belt_id} to WebSocket clients")
                    else:
                        logger.warning(f"Broadcast returned status {resp.status}")
        except Exception as e:
            logger.error(f"Failed to broadcast telemetry: {e}")

    def start(self):
        logger.info(f"Starting telemetry worker, subscribing to {self.kafka_topic}")
        self.consumer.subscribe([self.kafka_topic])

        run = True

        def signal_handler(sig, frame):
            logger.info("Received shutdown signal")
            run = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        while run:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())

            self.process_message(msg)

        self.consumer.close()

    def stop(self):
        self.consumer.close()


def main():
    worker = TelemetryWorker(
        kafka_bootstrap_servers=settings.kafka_bootstrap_servers,
        kafka_topic=settings.kafka_telemetry_topic,
        kafka_group=settings.kafka_consumer_group,
        alerts_topic=settings.kafka_alerts_topic,
    )

    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Shutting down worker...")
        worker.stop()


if __name__ == "__main__":
    main()
