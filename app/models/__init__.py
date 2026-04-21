from sqlalchemy import Column, String, Float, Integer, DateTime, text, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Paddock(Base):
    __tablename__ = "paddocks"
    __bind_key__ = None

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    geometry = Column(Geometry("POLYGON", srid=4326), nullable=False)
    area_hectares = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Animal(Base):
    __tablename__ = "animals"
    __bind_key__ = None

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    species = Column(String, default="cattle")
    belt_id = Column(String, unique=True, nullable=False)
    current_paddock_id = Column(String, ForeignKey("paddocks.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())


class Telemetry(Base):
    __tablename__ = "telemetry"
    __bind_key__ = "timescale"

    id = Column(Integer, primary_key=True, autoincrement=True)
    belt_id = Column(String, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature = Column(Float, nullable=True)
    activity_level = Column(Float, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())