# API Reference

Complete API endpoint reference for the Livestock Tracking Platform.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required. For production, add authentication middleware.

## Endpoints

---

## Health Check

### GET /health

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Paddocks

### GET /api/paddocks

List all paddocks.

**Response:**
```json
[
  {
    "id": "paddock-1",
    "name": "North Paddock",
    "area_hectares": 50.5,
    "geometry": "POLYGON((144.94 -36.59,144.95 -36.59,144.95 -36.6,144.94 -36.6,144.94 -36.59))",
    "created_at": "2026-04-21T18:27:20.951114Z"
  }
]
```

### GET /api/paddocks/{paddock_id}

Get a specific paddock.

**Parameters:**
- `paddock_id` (path) - Paddock ID

**Response:**
```json
{
  "id": "paddock-1",
  "name": "North Paddock",
  "area_hectares": 50.5,
  "geometry": "POLYGON((144.94 -36.59,...))",
  "created_at": "2026-04-21T18:27:20.951114Z"
}
```

### POST /api/paddocks

Create a new paddock.

**Request Body:**
```json
{
  "id": "paddock-4",
  "name": "West Paddock",
  "geometry": "POLYGON((144.94 -36.59,144.95 -36.59,144.95 -36.6,144.94 -36.6,144.94 -36.59))",
  "area_hectares": 45.0
}
```

**Response:**
```json
{
  "id": "paddock-4",
  "name": "West Paddock",
  "area_hectares": 45.0,
  "geometry": "POLYGON((144.94 -36.59,...))",
  "created_at": "2026-04-21T18:27:20.951114Z"
}
```

---

## Animals

### GET /api/animals

List all animals.

**Response:**
```json
[
  {
    "id": "animal-1",
    "name": "Cow 001",
    "species": "cattle",
    "belt_id": "BELT-001",
    "current_paddock_id": "paddock-1",
    "created_at": "2026-04-21T18:27:20.951114Z",
    "updated_at": "2026-04-21T18:27:20.951114Z"
  }
]
```

### GET /api/animals/{belt_id}

Get a specific animal.

**Parameters:**
- `belt_id` (path) - Belt ID

**Response:**
```json
{
  "id": "animal-1",
  "name": "Cow 001",
  "species": "cattle",
  "belt_id": "BELT-001",
  "current_paddock_id": "paddock-1",
  "created_at": "2026-04-21T18:27:20.951114Z",
  "updated_at": "2026-04-21T18:27:20.951114Z"
}
```

### POST /api/animals

Create a new animal.

**Request Body:**
```json
{
  "id": "animal-6",
  "name": "Cow 006",
  "species": "cattle",
  "belt_id": "BELT-006"
}
```

**Response:**
```json
{
  "id": "animal-6",
  "name": "Cow 006",
  "species": "cattle",
  "belt_id": "BELT-006",
  "current_paddock_id": null,
  "created_at": "2026-04-21T18:27:20.951114Z",
  "updated_at": "2026-04-21T18:27:20.951114Z"
}
```

---

## Telemetry

### GET /api/telemetry/latest

Get latest telemetry for all belts.

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

### GET /api/telemetry/{belt_id}

Get telemetry history for a specific belt.

**Parameters:**
- `belt_id` (path) - Belt ID
- `hours` (query) - Hours to look back (default: 24, max: 168)
- `limit` (query) - Max records (default: 100, max: 1000)

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

### POST /api/telemetry

Create a new telemetry reading.

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

**Response:**
```json
{
  "id": 150,
  "belt_id": "BELT-001",
  "latitude": -36.595,
  "longitude": 144.945,
  "temperature": 38.5,
  "activity_level": 5.0,
  "timestamp": "2026-04-22T00:00:00+00:00",
  "created_at": "2026-04-21T18:45:00.123456Z"
}
```

---

## Alerts

### GET /api/alerts

Get all geofence breach alerts.

**Response:**
```json
[
  {
    "id": "alert-1",
    "belt_id": "BELT-001",
    "latitude": -36.595,
    "longitude": 144.945,
    "paddock_id": "paddock-2",
    "timestamp": 1713724800,
    "type": "geofence_breach",
    "expected_paddock_id": "paddock-1"
  }
]
```

---

## WebSocket

### WS /ws/telemetry

Real-time telemetry stream.

**Protocol:** WebSocket

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

### WS /ws/alerts

Real-time alerts stream.

**Protocol:** WebSocket

**Message Format:**
```json
{
  "type": "alert",
  "id": "alert-1",
  "belt_id": "BELT-001",
  "latitude": -36.595,
  "longitude": 144.945,
  "paddock_id": "paddock-2",
  "timestamp": 1713724800,
  "expected_paddock_id": "paddock-1"
}
```

---

## Internal Endpoints

These endpoints are used by worker services.

### POST /internal/broadcast-telemetry

Broadcast telemetry to WebSocket clients.

**Request Body:**
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

**Response:**
```json
{
  "status": "ok"
}
```

### POST /internal/broadcast-alert

Broadcast alert to WebSocket clients.

**Request Body:**
```json
{
  "type": "alert",
  "belt_id": "BELT-001",
  "latitude": -36.595,
  "longitude": 144.945,
  "paddock_id": "paddock-2",
  "timestamp": 1713724800
}
```

**Response:**
```json
{
  "status": "ok"
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Error message"
}
```

### 404 Not Found

```json
{
  "detail": "Animal not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```
