from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import logging
import asyncio
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

active_connections: Dict[str, Set[WebSocket]] = {"telemetry": set()}


class ConnectionManager:
    async def connect(self, websocket: WebSocket, channel: str = "telemetry"):
        await websocket.accept()
        if channel not in active_connections:
            active_connections[channel] = set()
        active_connections[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "telemetry"):
        if channel in active_connections:
            active_connections[channel].discard(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict, channel: str = "telemetry"):
        if channel not in active_connections:
            return
        disconnected = set()
        for connection in active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        for conn in disconnected:
            active_connections[channel].discard(conn)


manager = ConnectionManager()


@router.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await manager.connect(websocket, "telemetry")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, "telemetry")


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket, "alerts")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")