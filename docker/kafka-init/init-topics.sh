#!/bin/bash
set -e

echo "Waiting for Kafka to be ready..."
until kafka-topics --bootstrap-server kafka:9092 --list &>/dev/null; do
    sleep 2
done

echo "Creating Kafka topics..."
kafka-topics --bootstrap-server kafka:9092 --create --topic telemetry_raw --partitions 1 --replication-factor 1 || echo "Topic telemetry_raw may already exist"
kafka-topics --bootstrap-server kafka:9092 --create --topic alerts --partitions 1 --replication-factor 1 || echo "Topic alerts may already exist"

echo "Listing topics:"
kafka-topics --bootstrap-server kafka:9092 --list

echo "Kafka topics created successfully!"