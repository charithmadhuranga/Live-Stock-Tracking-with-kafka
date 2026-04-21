from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models import Telemetry
from app.schemas import GeofenceBreachResponse

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=List[GeofenceBreachResponse])
async def get_alerts(
    limit: int = Query(50, le=100),
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db),
):
    return []