# WebSocket Documentation

The platform provides WebSocket endpoints for real-time data streaming.

## WebSocket Endpoints

### Telemetry WebSocket

Stream real-time telemetry data from all connected belts.

**Endpoint:** `ws://localhost:8000/ws/telemetry`

### Alerts WebSocket

Stream geofence breach alerts in real-time.

**Endpoint:** `ws://localhost:8000/ws/alerts`

## Connection

### JavaScript Client

```javascript
// Connect to telemetry stream
const telemetryWs = new WebSocket('ws://localhost:8000/ws/telemetry');

telemetryWs.onopen = () => {
  console.log('Connected to telemetry WebSocket');
};

telemetryWs.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

telemetryWs.onclose = () => {
  console.log('Disconnected');
};

// Connect to alerts stream
const alertsWs = new WebSocket('ws://localhost:8000/ws/alerts');

alertsWs.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  console.log('Alert:', alert);
};
```

## Message Formats

### Telemetry Message

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

### Alert Message

```json
{
  "type": "alert",
  "id": "alert-1",
  "belt_id": "BELT-001",
  "latitude": -36.595,
  "longitude": 144.945,
  "paddock_id": "paddock-1",
  "timestamp": 1713724800,
  "expected_paddock_id": "paddock-1"
}
```

## Broadcasting

The Worker service broadcasts telemetry to connected clients via internal API:

```python
# app/api/broadcast.py
@router.post("/internal/broadcast-telemetry")
async def broadcast_telemetry(data: dict):
    manager = get_manager()
    await manager.broadcast(data, "telemetry")
    return {"status": "ok"}
```

## Connection Manager

The `ConnectionManager` class handles WebSocket connections:

```python
# app/api/websocket.py
class ConnectionManager:
    async def connect(self, websocket: WebSocket, channel: str = "telemetry"):
        await websocket.accept()
        active_connections[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "telemetry"):
        active_connections[channel].discard(websocket)

    async def broadcast(self, message: dict, channel: str = "telemetry"):
        for connection in active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                # Remove disconnected clients
                active_connections[channel].discard(connection)
```

## Handling Disconnections

The frontend handles reconnection:

```typescript
// frontend/src/lib/telemetry.ts
let wsReconnectTimeout: NodeJS.Timeout | null = null;

function scheduleReconnect() {
  if (wsReconnectTimeout) return;
  
  wsReconnectTimeout = setTimeout(() => {
    wsReconnectTimeout = null;
    ws = null;
    connectTelemetryWebSocket();
  }, 3000);
}

ws.onclose = (event) => {
  if (!event.wasClean) {
    scheduleReconnect();
  }
};
```

## Ping/Pong

Clients can send ping messages to keep connections alive:

```javascript
// Send ping
telemetryWs.send(JSON.stringify({ type: "ping" }));

// Receive pong
telemetryWs.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "pong") {
    console.log('Pong received');
  }
};
```

## Error Handling

### Frontend

```typescript
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  useTelemetryStore.getState().setConnected(false);
};
```

### Backend

```python
@router.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await manager.connect(websocket, "telemetry")
    try:
        while True:
            data = await websocket.receive_text()
            # Process data
    except WebSocketDisconnect:
        manager.disconnect(websocket, "telemetry")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "telemetry")
```

## Performance Considerations

1. **Connection Pooling**: Multiple connections are managed in a set
2. **Error Handling**: Disconnected clients are automatically removed
3. **Reconnection**: Frontend implements automatic reconnection
4. **Message Format**: JSON is used for simplicity (protobuf available)

## Security

For production, consider:
- Add authentication to WebSocket connections
- Use WSS (WebSocket Secure) for TLS
- Implement rate limiting
- Add origin validation