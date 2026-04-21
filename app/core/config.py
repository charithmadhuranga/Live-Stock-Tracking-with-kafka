from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://livestock:livestock123@localhost:5432/livestock_db"
    timescale_url: str = "postgresql://livestock:livestock123@timescale:5432/timescale_db"

    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_consumer_group: str = "livestock-consumer-group"
    kafka_telemetry_topic: str = "telemetry_raw"
    kafka_alerts_topic: str = "alerts"

    # MQTT
    mqtt_broker_host: str = "mosquitto"
    mqtt_broker_port: int = 1883
    mqtt_topic: str = "livestock/telemetry/#"

    # App
    app_name: str = "Livestock Tracking Platform"
    debug: bool = True

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
