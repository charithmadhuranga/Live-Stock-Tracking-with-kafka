from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator


class TelemetryBase(BaseModel):
    belt_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    temperature: Optional[float] = None
    activity_level: Optional[float] = None


class TelemetryCreate(TelemetryBase):
    timestamp: int


class TelemetryResponse(TelemetryBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AnimalBase(BaseModel):
    id: str
    name: str
    species: str = "cattle"
    belt_id: str


class AnimalCreate(AnimalBase):
    pass


class AnimalResponse(AnimalBase):
    current_paddock_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaddockBase(BaseModel):
    id: str
    name: str
    area_hectares: Optional[float] = None


class PaddockCreate(PaddockBase):
    geometry: str


class PaddockResponse(PaddockBase):
    geometry: Optional[str] = None
    created_at: datetime

    @field_validator("geometry", mode="before")
    @classmethod
    def geometry_to_wkt(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, str):
            if v.startswith("POLYGON") or v.startswith("POINT"):
                return v
            from geoalchemy2 import elements
            if isinstance(v, elements.WKBElement):
                return v.desc
            return v
        if hasattr(v, "desc"):
            return v.desc
        return str(v)

    class Config:
        from_attributes = True


class GeofenceBreachResponse(BaseModel):
    belt_id: str
    latitude: float
    longitude: float
    paddock_id: str
    timestamp: int
