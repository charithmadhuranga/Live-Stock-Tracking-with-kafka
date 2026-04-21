# Backend Documentation

The backend is built with **FastAPI** and provides REST APIs for the frontend and WebSocket support for real-time updates.

## Project Structure

```
app/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── api/
│   ├── __init__.py
│   ├── telemetry.py       # Telemetry, Animals, Paddocks endpoints
│   ├── websocket.py        # WebSocket endpoints
│   ├── alerts.py          # Alerts endpoints
│   └── broadcast.py       # Internal broadcast endpoints
├── core/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   └── database.py        # Database connections
├── models/
│   └── __init__.py        # SQLAlchemy models
└── schemas/
    └── __init__.py        # Pydantic schemas
```

## Running the Backend

### Using Docker

```bash
# Build and run with docker-compose
docker-compose up -d api
```

### Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Health Check

```http
GET /health
```

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy"
}
```

### Paddocks

#### List Paddocks

```http
GET /api/paddocks
```

Returns a list of all paddocks with their geometry.

**Response:**
```json
[
  {
    "id": "paddock-1",
    "name": "North Paddock",
    "area_hectares": 50.5,
    "geometry": "POLYGON((144.94 -36.59,144.95 -36.59,...))",
    "created_at": "2026-04-21T18:27:20.951114Z"
  }
]
```

#### Get Paddock

```http
GET /api/paddocks/{paddock_id}
```

Returns a single paddock by ID.

#### Create Paddock

```http
POST /api/paddocks
```

Creates a new paddock.

**Request Body:**
```json
{
  "id": "paddock-4",
  "name": "West Paddock",
  "geometry": "POLYGON((144.94 -36.59,144.95 -36.59,144.95 -36.6,144.94 -36.6,144.94 -36.59))",
  "area_hectares": 45.0
}
```

### Animals

#### List Animals

```http
GET /api/animals
```

Returns a list of all animals.

**Response:**
```json
[
  {
    "id": "animal-1",
    "name": "Cow 001",
    "species": "cattle",
    "belt_id": "BELT-001",
    "current_paddock_id": "paddock-1",
    "created_at": "2026-04-21T18:27:20.951114Z"
  }
]
```

#### Get Animal

```http
GET /api/animals/{belt_id}
```

Returns a single animal by belt ID.

#### Create Animal

```http
POST /api/animals
```

Creates a new animal.

**Request Body:**
```json
{
  "id": "animal-6",
  "name": "Cow 006",
  "species": "cattle",
  "belt_id": "BELT-006"
}
```

### Telemetry

#### Get Latest Telemetry

```http
GET /api/telemetry/latest
```

Returns the latest telemetry reading for each belt.

**Response:**
```json
[
  {
    "id": 147,
    "belt_id": "BELT-001",
    "latitude": -36.595,
    "longitude": 144.945,
    "temperature": 38.5,
    "activity_level": 5.0,
    "timestamp": "2026-04-22T00:09:45+00:00",
    "created_at": "2026-04-21T18:39:45.055833Z"
  }
]
```

#### Get Telemetry History

```http
GET /api/telemetry/{belt_id}?hours=24&limit=100
```

Returns telemetry history for a specific belt.

**Query Parameters:**
- `hours` - Number of hours to look back (default: 24, max: 168)
- `limit` - Maximum number of records (default: 100, max: 1000)

#### Create Telemetry

```http
POST /api/telemetry
```

Creates a new telemetry reading.

**Request Body:**
```json
{
  "belt_id": "BELT-001",
  "latitude": -36.595,
  "longitude": 144.945,
  "temperature": 38.5,
  "activity_level": 5.0,
  "timestamp": 1713724800
}
```

### Alerts

#### Get Alerts

```http
GET /api/alerts
```

Returns all geofence breach alerts.

**Response:**
```json
[
  {
    "id": "alert-1",
    "belt_id": "BELT-001",
    "latitude": -36.595,
    "longitude": 144.945,
    "paddock_id": "paddock-1",
    "timestamp": 1713724800,
    "type": "geofence_breach",
    "expected_paddock_id": "paddock-1"
  }
]
```

## WebSocket Endpoints

### Telemetry WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/telemetry');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Telemetry:', data);
};
```

**Message Format:**
```json
{
  "type": "telemetry",
  "belt_id": "BELT-001",
  "latitude": -36.595,
  "longitude": 144.945,
  "temperature": 38.5,
  "activity_level": 5.0,
  "timestamp": 1713724800
}
```

### Alerts WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/alerts');
```

## Internal Endpoints

These endpoints are used by worker services for broadcasting:

### Broadcast Telemetry

```http
POST /internal/broadcast-telemetry

{
  "type": "telemetry",
  "belt_id": "BELT-001",
  "latitude": -36.595,
  "longitude": 144.945,
  "temperature": 38.5,
  "activity_level": 5.0,
  "timestamp": 1713724800
}
```

### Broadcast Alert

```http
POST /internal/broadcast-alert

{
  "type": "alert",
  "belt_id": "BELT-001",
  "latitude": -36.595,
  "longitude": 144.945,
  "paddock_id": "paddock-1",
  "timestamp": 1713724800
}
```

## Configuration

Configuration is managed through environment variables in `app/core/config.py`:

```python
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
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

Error responses include a detail message:

```json
{
  "detail": "Animal with this belt_id already exists"
}
```
