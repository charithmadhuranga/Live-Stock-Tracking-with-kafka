# Deployment Guide

This guide covers deploying the Livestock Tracking Platform to production environments.

## Prerequisites

- Docker and Docker Compose
- At least 4GB RAM
- Ports 3000, 8000, 5432, 5433, 1883, 9092, 2181 available

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/livestock-tracking
cd livestock-tracking

# Start all services
make up

# View logs
make logs

# Stop all services
make down
```

## Docker Compose Services

The platform consists of the following services:

| Service | Port | Description |
|---------|------|-------------|
| frontend | 3000 | Next.js web application |
| api | 8000 | FastAPI backend |
| postgres | 5432 | PostgreSQL with PostGIS |
| timescale | 5433 | TimescaleDB for telemetry |
| kafka | 9092 | Kafka message broker |
| zookeeper | 2181 | Zookeeper for Kafka |
| mosquitto | 1883 | MQTT broker |
| bridge | - | MQTT to Kafka bridge |
| worker | - | Kafka consumer |
| simulator | - | Telemetry simulator |

## Make Commands

```bash
# Start all services
make up

# Start specific service
make up API=1

# Stop all services
make down

# View logs
make logs

# View specific logs
make logs SERVICE=worker

# Rebuild services
make rebuild

# Rebuild specific service
make rebuild SERVICE=frontend

# Run tests (if available)
make test

# Clean up volumes
make clean
```

## Environment Configuration

### Development Environment

The default docker-compose.yml is configured for development:

- Debug logging enabled
- Hot reload for frontend (via volume mounts)
- Exposed ports for all services

### Production Environment

For production, consider:

1. **Remove debug mode:**
   ```yaml
   environment:
     DEBUG: "false"
   ```

2. **Use secrets for passwords:**
   ```yaml
   environment:
     POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
   ```

3. **Add health checks:**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

## Production Checklist

### Security

- [ ] Change default passwords
- [ ] Enable SSL/TLS for API
- [ ] Configure CORS for specific origins
- [ ] Add authentication to API
- [ ] Use Docker secrets

### Performance

- [ ] Increase Kafka partition count
- [ ] Configure TimescaleDB data retention
- [ ] Add caching layer (Redis)
- [ ] Configure connection pooling

### Monitoring

- [ ] Add logging aggregation (ELK/EFK)
- [ ] Set up metrics (Prometheus/Grafana)
- [ ] Configure alerts
- [ ] Add health check endpoints

### Backup

- [ ] Configure automated database backups
- [ ] Test backup restoration
- [ ] Set up off-site backup storage

## Scaling

### Horizontal Scaling

To scale services:

```bash
# Scale worker to 3 instances
docker-compose up -d --scale worker=3
```

### Database Scaling

- Use read replicas for PostgreSQL
- Configure TimescaleDB compression
- Use connection poolers (PgBouncer)

### Message Queue Scaling

- Increase Kafka partitions
- Add more consumer groups
- Use Kafka Streams for processing

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs <service>

# Check port conflicts
netstat -tulpn | grep <port>
```

### Database connection issues

```bash
# Check if database is ready
docker-compose exec postgres pg_isready

# Check connection from another service
docker-compose exec api python -c "from app.core.database import engine; engine.connect()"
```

### Kafka issues

```bash
# List topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Check consumer groups
docker-compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list
```

## Maintenance

### Database Maintenance

```bash
# Vacuum PostgreSQL
docker-compose exec postgres psql -U livestock -d livestock_db -c "VACUUM ANALYZE;"

# Check TimescaleDB chunks
docker-compose exec timescale psql -U livestock -d timescale_db -c "SELECT * FROM timescaledb_information.chunks;"
```

### Log Rotation

Configure in docker-compose.yml:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Deployment Examples

### Single Server

```bash
# Deploy on a single server
docker-compose up -d
```

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml livestock
```

### Kubernetes

For Kubernetes deployment, you'll need to create:
- Deployment manifests
- Service definitions
- ConfigMaps
- PersistentVolumeClaims
