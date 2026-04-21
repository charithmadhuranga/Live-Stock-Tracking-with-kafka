#!/usr/bin/env python3
import json
import time
import random
import paho.mqtt.client as mqtt
from datetime import datetime

import os

BROKER = os.environ.get("MQTT_BROKER_HOST", "mosquitto")
PORT = int(os.environ.get("MQTT_BROKER_PORT", "1883"))
TOPIC = "livestock/telemetry/+"

BELT_IDS = ["BELT-001", "BELT-002", "BELT-003", "BELT-004", "BELT-005"]

BASE_COORDS = {
    "BELT-001": (-36.595, 144.945),
    "BELT-002": (-36.596, 144.946),
    "BELT-003": (-36.605, 144.945),
    "BELT-004": (-36.606, 144.946),
    "BELT-005": (-36.605, 144.955),
}


def on_connect(client, userdata, flags, rc):
    import sys
    if rc == 0:
        print(f"✓ Connected to MQTT broker at {BROKER}:{PORT}", flush=True)
        for belt_id in BELT_IDS:
            topic = f"livestock/telemetry/{belt_id}"
            client.subscribe(topic)
            print(f"  Subscribed to {topic}", flush=True)
    else:
        print(f"✗ Connection failed with code {rc}", flush=True)


def on_publish(client, userdata, mid):
    pass


def send_telemetry(client, belt_id: str):
    lat, lng = BASE_COORDS[belt_id]
    lat += random.uniform(-0.0005, 0.0005)
    lng += random.uniform(-0.0005, 0.0005)

    payload = {
        "belt_id": belt_id,
        "latitude": round(lat, 6),
        "longitude": round(lng, 6),
        "temperature": round(random.uniform(37.5, 40.0), 1),
        "activity_level": round(random.uniform(0.5, 10.0), 1),
        "battery_level": random.randint(60, 100),
        "timestamp": int(time.time()),
    }

    topic = f"livestock/telemetry/{belt_id}"
    client.publish(topic, json.dumps(payload))
    return payload


def main():
    print("=== Real-time Telemetry Simulator ===")
    print(f"Connecting to MQTT broker {BROKER}:{PORT}...")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"Error connecting to MQTT: {e}")
        print("Make sure MQTT broker is running: docker-compose up")
        return

    print("\nSending telemetry every 2 seconds. Press Ctrl+C to stop.\n")

    try:
        while True:
            for belt_id in BELT_IDS:
                payload = send_telemetry(client, belt_id)
                print(f"  {belt_id}: {payload['temperature']}°C, "
                      f"activity: {payload['activity_level']}, "
                      f"lat: {payload['latitude']:.4f}", flush=True)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\nStopping simulator...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("✓ Disconnected from MQTT broker")


if __name__ == "__main__":
    main()