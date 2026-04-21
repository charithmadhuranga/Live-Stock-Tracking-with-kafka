from fastapi import APIRouter, Request
from typing import Dict, Set
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

active_connections: Dict[str, Set] = {"telemetry": set(), "alerts": set()}


def get_manager():
    from app.api.websocket import manager
    return manager


@router.post("/internal/broadcast-telemetry")
async def broadcast_telemetry(data: dict):
    try:
        manager = get_manager()
        await manager.broadcast(data, "telemetry")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        return {"status": "error", "detail": str(e)}


@router.post("/internal/broadcast-alert")
async def broadcast_alert(data: dict):
    try:
        manager = get_manager()
        await manager.broadcast(data, "alerts")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Alert broadcast error: {e}")
        return {"status": "error", "detail": str(e)}
