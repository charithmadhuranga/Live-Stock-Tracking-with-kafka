.PHONY: help install dev-deps lint test proto run-api run-bridge run-worker up down logs clean frontend-install frontend-dev frontend-build frontend-lint feed-data realtime-data build up-docker down-docker logs-docker docs-dev docs-prod docs-serve

help:
	@echo "Livestock Tracking Platform - Make Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install       - Install backend dependencies with uv"
	@echo "  make proto         - Generate Python protobuf classes"
	@echo "  make run-api       - Start FastAPI server"
	@echo "  make run-bridge    - Start MQTT to Kafka bridge"
	@echo "  make run-worker  - Start Kafka consumer worker"
	@echo "  make feed-data   - Feed test data to API"
	@echo "  make realtime-data - Send real-time telemetry via MQTT"
	@echo ""
	@echo "Docker:"
	@echo "  make build       - Build Docker images"
	@echo "  make up-docker   - Start all services with docker-compose"
	@echo "  make down-docker - Stop all services"
	@echo "  make logs-docker - View Docker logs"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend-install - Install frontend dependencies"
	@echo "  make frontend-dev    - Start Next.js dev server"
	@echo "  make frontend-build  - Build Next.js app"
	@echo "  make frontend-lint   - Lint frontend code"
	@echo ""
	@echo "Docker:"
	@echo "  make up            - Start all Docker services"
	@echo "  make down          - Stop all Docker services"
	@echo "  make logs          - View Docker logs"
	@echo "  make clean         - Remove Docker volumes"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs-dev     - Start documentation dev server"
	@echo "  make docs-prod    - Build documentation for production"
	@echo "  make docs-serve   - Serve built documentation"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linting"

install:
	uv venv
	uv pip install -r requirements.txt

dev-deps:
	uv pip install pytest pytest-asyncio black ruff mypy

proto:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. schema.proto

run-api:
	@echo "Starting FastAPI server..."
	python -m app.main

run-bridge:
	@echo "Starting MQTT to Kafka bridge..."
	python -m app.worker.mqtt_to_kafka_bridge

run-worker:
	@echo "Starting Kafka consumer worker..."
	python -m app.worker.kafka_consumer

up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "Services started: Kafka, Zookeeper, Mosquitto, Postgres, Kafka-UI"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf __pycache__ app/__pycache__ app/*/__pycache__
	rm -f schema_pb2.py schema_pb2_grpc.py

test:
	pytest -v

lint:
	ruff check .

typecheck:
	mypy app/

frontend-install:
	cd frontend && npm install

frontend-dev:
	@echo "Starting Next.js dev server..."
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

frontend-lint:
	cd frontend && npm run lint

feed-data:
	@echo "Feeding test data..."
	python scripts/feed_test_data.py

realtime-data:
	@echo "Starting real-time telemetry simulator (MQTT)..."
	python scripts/realtime_simulator.py

build:
	@echo "Building Docker images..."
	docker-compose build

up-docker:
	@echo "Starting all services with docker-compose..."
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Creating Kafka topics..."
	docker exec livestock-kafka kafka-topics --bootstrap-server localhost:9092 --create --topic telemetry_raw --partitions 1 --replication-factor 1 || true
	docker exec livestock-kafka kafka-topics --bootstrap-server localhost:9092 --create --topic alerts --partitions 1 --replication-factor 1 || true
	@echo ""
	@echo "Services started:"
	@echo "  Frontend:    http://localhost:3000"
	@echo "  API:         http://localhost:8000"
	@echo "  API Docs:    http://localhost:8000/docs"

down-docker:
	@echo "Stopping all services..."
	docker-compose down

logs-docker:
	docker-compose logs -f

docs-dev:
	@echo "Starting MkDocs development server..."
	cd docs && pip install -r requirements.txt -q && mkdocs serve

docs-prod:
	@echo "Building documentation for production..."
	cd docs && pip install -r requirements.txt -q && mkdocs build

docs-serve:
	@echo "Serving built documentation..."
	cd docs && python -m http.server 8001
