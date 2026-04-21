# Data Flow

This document explains how data flows through the Livestock Tracking Platform from the IoT devices to the user interface.

## Overview

The platform follows a **streaming architecture** where data flows continuously from smart belts through various processing stages to the final user interface:

```mermaid
flowchart LR
    subgraph Stage1["1. Data Generation"]
        Belt[Smart Belt]
    end

    subgraph Stage2["2. MQTT Bridge"]
        MQTT[("MQTT Broker")]
    end

    subgraph Stage3["3. Processing"]
        Kafka[("Kafka")]
        Worker[("Worker Service")]
    end

    subgraph Stage4["4. Storage"]
        TimescaleDB[("TimescaleDB")]
        PostgreSQL[("PostgreSQL")]
    end

    subgraph Stage5["5. API & Frontend"]
        API[("FastAPI")]
        WS[("WebSocket")]
        Frontend[("Frontend")]
    end

    Belt -->|Publish| MQTT
    MQTT -->|Subscribe| Kafka
    Kafka -->|Consume| Worker
    Worker -->|Store| TimescaleDB
    Worker -->|Check| PostgreSQL
    Worker -->|Broadcast| API
    API -->|Push| WS
    WS -->|Real-time| Frontend
```

## Step-by-Step Data Flow

### 1. Data Generation (Simulation)

The **Simulator** generates fake telemetry data to simulate smart belts:

**File:** `scripts/realtime_simulator.py`

```python
# Example telemetry payload
{
    "belt_id": "BELT-001",
    "latitude": -36.595,
    "longitude": 144.945,
    "temperature": 38.5,
    "activity_level": 5.0,
    "timestamp": 1713724800
}
```

The simulator publishes this data to the MQTT broker on topics like:
- `livestock/telemetry/BELT-001`
- `livestock/telemetry/BELT-002`
- etc.

### 2. MQTT to Kafka Bridging

The **Bridge Service** subscribes to MQTT topics and forwards messages to Kafka:

**File:** `app/worker/mqtt_to_kafka_bridge.py`

```mermaid
flowchart LR
    MQTT[("MQTT Broker")]
    Bridge[("Bridge Service")]
    Kafka[("Kafka")]

    MQTT -->|livestock/telemetry/+| Bridge
    Bridge -->|Produce| Kafka
```

Key operations:
1. Connects to MQTT broker
2. Subscribes to `livestock/telemetry/#` (all belt topics)
3. Parses JSON payload
4. Converts to Protocol Buffer format
5. Produces to Kafka `telemetry_raw` topic

### 3. Kafka Consumer (Worker)

The **Worker Service** consumes from Kafka and processes the data:

**File:** `app/worker/kafka_consumer.py`

```mermaid
flowchart TB
    subgraph Worker["Worker Service"]
        Consume[Consume Message]
        Parse[Parse Data]
        Store[(Store in TimescaleDB)]
        Geofence[Check Geofence]
        Broadcast[Broadcast to WebSocket]

        Consume --> Parse
        Parse --> Store
        Store --> Geofence
        Geofence --> Broadcast
    end

    Kafka[("Kafka")] --> Consume
    Broadcast --> API[("API")]
```

Processing steps:
1. **Consume** message from Kafka
2. **Parse** protobuf or JSON data
3. **Store** in TimescaleDB (`telemetry` table)
4. **Check** geofence (is animal in expected paddock?)
5. **Broadcast** to WebSocket clients via API
6. **Create alert** if geofence breach detected

### 4. WebSocket Broadcasting

The Worker calls an internal API endpoint to broadcast data to connected WebSocket clients:

**File:** `app/api/broadcast.py`

```mermaid
sequenceDiagram
    participant W as Worker
    participant A as API Server
    participant WS as WebSocket Clients

    W->>A: POST /internal/broadcast-telemetry
    A->>WS: Broadcast to all connections
```

### 5. Frontend Data Reception

The **Frontend** connects to the WebSocket and updates the UI in real-time:

**File:** `frontend/src/lib/telemetry.ts`

```mermaid
flowchart TB
    subgraph Frontend["Frontend"]
        WS[("WebSocket")]
        Store[("Zustand Store")]
        UI[("React Components")]
    end

    WS -->|Parse JSON| Store
    Store -->|Update State| UI
```

## API Data Flow (Polling)

The frontend also supports REST API polling as a fallback:

```mermaid
sequenceDiagram
    participant F as Frontend
    participant A as API
    participant DB as Database

    F->>A: GET /api/telemetry/latest
    A->>DB: SELECT latest per belt_id
    DB-->>A: Results
    A-->>F: JSON Response
```

## Geofence Checking Flow

```mermaid
flowchart TB
    subgraph GeofenceCheck["Geofence Check Process"]
        Step1[Get animal's current_paddock_id]
        Step2[Get paddock geometry]
        Step3[ST_Contains check]
        Step4[Create alert if breach]
    end

    Telemetry[Telemetry Data] --> Step1
    Step1 --> Step2
    Step2 --> Step3
    Step3 -->|Outside| Step4
    Step4 --> Alert[(Alert)]
    Step3 -->|Inside| Done[(OK)]
```

Steps:
1. Get animal's current_paddock_id from database
2. Get paddock geometry
3. Check if point is inside polygon using ST_Contains
4. If NOT within paddock:
   - Create alert
   - Store in alerts table
   - Broadcast via WebSocket

## Error Handling

### MQTT Connection Lost
- Bridge automatically reconnects to MQTT broker
- Logs warning: "Disconnected from MQTT broker"

### Kafka Consumer Error
- Worker logs error and continues processing
- Failed messages are logged but not requeued

### WebSocket Disconnection
- Frontend attempts to reconnect after 3 seconds
- Status indicator shows "Disconnected"

### Database Connection Error
- SQLAlchemy handles connection pooling
- Errors are logged and reported via API

## Performance Considerations

1. **Kafka** provides message buffering during high load
2. **TimescaleDB** optimizes time-series queries
3. **WebSocket** reduces HTTP polling overhead
4. **PostGIS** efficiently handles spatial queries
5. **Connection pooling** via SQLAlchemy NullPool in Docker