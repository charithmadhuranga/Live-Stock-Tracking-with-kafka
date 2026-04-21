import json
import logging
import signal
import sys
from typing import Optional

import paho.mqtt.client as mqtt
from confluent_kafka import Producer
from google.protobuf.json_format import Parse

from app.core.config import settings
from schema_pb2 import Telemetry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MqttToKafkaBridge:
    def __init__(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_topic: str,
        kafka_bootstrap_servers: str,
        kafka_topic: str,
    ):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.kafka_topic = kafka_topic

        self.mqtt_client = mqtt.Client(client_id="mqtt_to_kafka_bridge")
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.on_disconnect = self._on_mqtt_disconnect

        self.kafka_producer = Producer(
            {
                "bootstrap.servers": kafka_bootstrap_servers,
                "client.id": "mqtt_to_kafka_producer",
            }
        )

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.mqtt_host}:{self.mqtt_port}")
            client.subscribe(self.mqtt_topic)
            logger.info(f"Subscribed to MQTT topic: {self.mqtt_topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")

    def _on_mqtt_disconnect(self, client, userdata, rc):
        logger.warning(f"Disconnected from MQTT broker with return code: {rc}")

    def _on_mqtt_message(self, client, userdata, msg):
        try:
            import json
            logger.info(f"Received MQTT message on topic: {msg.topic}")
            payload = json.loads(msg.payload.decode())
            logger.info(f"Payload: {payload}")
            
            telemetry = Telemetry(
                belt_id=payload.get("belt_id", ""),
                latitude=payload.get("latitude", 0),
                longitude=payload.get("longitude", 0),
                temperature=payload.get("temperature", 0),
                activity_level=payload.get("activity_level", 0),
                timestamp=payload.get("timestamp", 0),
            )

            self.kafka_producer.produce(
                self.kafka_topic,
                key=telemetry.belt_id.encode("utf-8"),
                value=telemetry.SerializeToString(),
            )
            self.kafka_producer.flush()

            logger.info(
                f"Forwarded telemetry from belt {telemetry.belt_id} to Kafka topic {self.kafka_topic}"
            )
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def start(self):
        logger.info("Starting MQTT to Kafka bridge...")
        self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
        self.mqtt_client.loop_start()

    def stop(self):
        logger.info("Stopping MQTT to Kafka bridge...")
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        self.kafka_producer.flush()


def main():
    bridge = MqttToKafkaBridge(
        mqtt_host=settings.mqtt_broker_host,
        mqtt_port=settings.mqtt_broker_port,
        mqtt_topic=settings.mqtt_topic,
        kafka_bootstrap_servers=settings.kafka_bootstrap_servers,
        kafka_topic=settings.kafka_telemetry_topic,
    )

    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        bridge.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    bridge.start()

    logger.info("MQTT to Kafka bridge is running. Press Ctrl+C to stop.")
    signal.pause()


if __name__ == "__main__":
    main()
