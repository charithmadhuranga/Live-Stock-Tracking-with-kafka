from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db, get_timescale_db
from app.models import Telemetry, Animal, Paddock
from app.schemas import (
    TelemetryCreate,
    TelemetryResponse,
    AnimalCreate,
    AnimalResponse,
    PaddockCreate,
    PaddockResponse,
)

router = APIRouter(prefix="/api", tags=["telemetry"])


@router.post("/telemetry", response_model=TelemetryResponse)
async def create_telemetry(
    data: TelemetryCreate,
    db: Session = Depends(get_timescale_db),
):
    telemetry_record = Telemetry(
        belt_id=data.belt_id,
        latitude=data.latitude,
        longitude=data.longitude,
        temperature=data.temperature,
        activity_level=data.activity_level,
        timestamp=datetime.fromtimestamp(data.timestamp),
    )
    db.add(telemetry_record)
    db.commit()
    db.refresh(telemetry_record)
    return telemetry_record


@router.get("/telemetry/latest")
async def get_latest_telemetry(
    db: Session = Depends(get_timescale_db),
):
    from sqlalchemy import text
    
    result = db.execute(
        text("""
            SELECT telemetry.id, telemetry.belt_id, telemetry.latitude, telemetry.longitude,
                   telemetry.temperature, telemetry.activity_level, telemetry.timestamp,
                   telemetry.created_at
            FROM telemetry
            INNER JOIN (
                SELECT belt_id, MAX(timestamp) as max_ts
                FROM telemetry
                GROUP BY belt_id
            ) sub ON telemetry.belt_id = sub.belt_id AND telemetry.timestamp = sub.max_ts
        """)
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id,
            "belt_id": r.belt_id,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "temperature": r.temperature,
            "activity_level": r.activity_level,
            "timestamp": r.timestamp,
            "created_at": r.created_at,
        }
        for r in rows
    ]


@router.get("/telemetry/{belt_id}", response_model=List[TelemetryResponse])
async def get_telemetry(
    belt_id: str,
    limit: int = Query(100, le=1000),
    hours: int = Query(24, le=168),
    db: Session = Depends(get_timescale_db),
):
    since = datetime.utcnow() - timedelta(hours=hours)
    return (
        db.query(Telemetry)
        .filter(Telemetry.belt_id == belt_id)
        .filter(Telemetry.timestamp >= since)
        .order_by(desc(Telemetry.timestamp))
        .limit(limit)
        .all()
    )


@router.get("/telemetry/latest")
async def get_latest_telemetry(
    db: Session = Depends(get_timescale_db),
):
    from sqlalchemy import text
    
    result = db.execute(
        text("""
            SELECT telemetry.id, telemetry.belt_id, telemetry.latitude, telemetry.longitude,
                   telemetry.temperature, telemetry.activity_level, telemetry.timestamp,
                   telemetry.created_at
            FROM telemetry
            INNER JOIN (
                SELECT belt_id, MAX(timestamp) as max_ts
                FROM telemetry
                GROUP BY belt_id
            ) sub ON telemetry.belt_id = sub.belt_id AND telemetry.timestamp = sub.max_ts
        """)
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id,
            "belt_id": r.belt_id,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "temperature": r.temperature,
            "activity_level": r.activity_level,
            "timestamp": r.timestamp,
            "created_at": r.created_at,
        }
        for r in rows
    ]


@router.post("/animals", response_model=AnimalResponse)
async def create_animal(
    animal: AnimalCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(Animal).filter(Animal.belt_id == animal.belt_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Animal with this belt_id already exists")

    db_animal = Animal(
        id=animal.id,
        name=animal.name,
        species=animal.species,
        belt_id=animal.belt_id,
    )
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal


@router.get("/animals", response_model=List[AnimalResponse])
async def list_animals(
    db: Session = Depends(get_db),
):
    return db.query(Animal).all()


@router.get("/animals/{belt_id}", response_model=AnimalResponse)
async def get_animal(
    belt_id: str,
    db: Session = Depends(get_db),
):
    animal = db.query(Animal).filter(Animal.belt_id == belt_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    return animal


@router.post("/paddocks", response_model=PaddockResponse)
async def create_paddock(
    paddock: PaddockCreate,
    db: Session = Depends(get_db),
):
    from geoalchemy2 import WKTElement

    db_paddock = Paddock(
        id=paddock.id,
        name=paddock.name,
        geometry=WKTElement(paddock.geometry, srid=4326),
        area_hectares=paddock.area_hectares,
    )
    db.add(db_paddock)
    db.commit()
    db.refresh(db_paddock)
    return db_paddock


@router.get("/paddocks", response_model=List[PaddockResponse])
async def list_paddocks(
    db: Session = Depends(get_db),
):
    from sqlalchemy import text
    result = db.execute(
        text("""
            SELECT id, name, ST_AsText(geometry) as geometry, area_hectares, created_at
            FROM paddocks
        """)
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id,
            "name": r.name,
            "geometry": r.geometry,
            "area_hectares": r.area_hectares,
            "created_at": r.created_at,
        }
        for r in rows
    ]


@router.get("/paddocks/{paddock_id}", response_model=PaddockResponse)
async def get_paddock(
    paddock_id: str,
    db: Session = Depends(get_db),
):
    paddock = db.query(Paddock).filter(Paddock.id == paddock_id).first()
    if not paddock:
        raise HTTPException(status_code=404, detail="Paddock not found")
    return paddock
