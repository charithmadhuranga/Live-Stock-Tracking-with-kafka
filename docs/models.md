# Models Documentation

This document describes the database models used in the platform.

## SQLAlchemy Models

Models are defined in `app/models/__init__.py`.

## Base Configuration

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

metadata = MetaData()
Base = declarative_base(metadata=metadata)
```

## Animal Model

Represents a tracked animal with its smart belt.

```python
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
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| id | String | Primary Key | Unique identifier |
| name | String | Not Null | Animal name |
| species | String | Default: cattle | Species type |
| belt_id | String | Unique, Not Null | Associated GPS belt ID |
| current_paddock_id | String | Foreign Key | Current paddock location |
| created_at | TIMESTAMP | Auto | Creation timestamp |
| updated_at | TIMESTAMP | Auto | Last update timestamp |

### Usage Example

```python
# Create animal
animal = Animal(
    id="animal-1",
    name="Cow 001",
    species="cattle",
    belt_id="BELT-001"
)
db.add(animal)
db.commit()

# Query animal
animal = db.query(Animal).filter(Animal.belt_id == "BELT-001").first()

# Get animal's paddock
if animal.current_paddock_id:
    paddock = db.query(Paddock).filter(Paddock.id == animal.current_paddock_id).first()
```

## Paddock Model

Represents a geofenced area where animals can graze.

```python
class Paddock(Base):
    __tablename__ = "paddocks"
    __bind_key__ = None

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    geometry = Column(Geometry("POLYGON", srid=4326), nullable=False)
    area_hectares = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| id | String | Primary Key | Unique identifier |
| name | String | Not Null | Paddock name |
| geometry | Geometry | Not Null | PostGIS polygon (SRID 4326) |
| area_hectares | Float | Optional | Area in hectares |
| created_at | TIMESTAMP | Auto | Creation timestamp |

### Geometry Format

The geometry field stores polygons in EWKB format (Extended Well-Known Binary).

```python
from geoalchemy2 import WKTElement

# Create paddock with WKT geometry
paddock = Paddock(
    id="paddock-1",
    name="North Paddock",
    geometry=WKTElement(
        "POLYGON((144.94 -36.59,144.95 -36.59,144.95 -36.6,144.94 -36.6,144.94 -36.59))",
        srid=4326
    ),
    area_hectares=50.5
)
```

### WKT Format

```
POLYGON((longitude1 latitude1, longitude2 latitude2, ...))
```

Example polygon covering approximately 50 hectares at lat:-36.59 to -36.6, lon:144.94 to 144.95.

## Telemetry Model

Stores time-series sensor data from smart belts.

```python
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
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| id | Integer | Primary Key, Auto | Record ID |
| belt_id | String | Not Null, Indexed | GPS belt ID |
| latitude | Float | Not Null | GPS latitude |
| longitude | Float | Not Null | GPS longitude |
| temperature | Float | Optional | Body temperature (°C) |
| activity_level | Float | Optional | Movement index |
| timestamp | TIMESTAMP | Not Null, Indexed | Reading time |
| created_at | TIMESTAMP | Auto | Database insert time |

### TimescaleDB

This model is bound to TimescaleDB for time-series optimization.

```python
__bind_key__ = "timescale"  # Connects to TimescaleDB
```

TimescaleDB automatically creates a hypertable for efficient time-series queries.

### Usage Example

```python
from datetime import datetime

# Store telemetry
telemetry = Telemetry(
    belt_id="BELT-001",
    latitude=-36.595,
    longitude=144.945,
    temperature=38.5,
    activity_level=5.0,
    timestamp=datetime.utcnow()
)
db.add(telemetry)
db.commit()

# Query latest for belt
latest = db.query(Telemetry).filter(
    Telemetry.belt_id == "BELT-001"
).order_by(Telemetry.timestamp.desc()).first()

# Query time range
from datetime import timedelta
since = datetime.utcnow() - timedelta(hours=24)
readings = db.query(Telemetry).filter(
    Telemetry.belt_id == "BELT-001",
    Telemetry.timestamp >= since
).all()
```

## Database Bindings

The platform uses two database engines:

```python
# app/core/database.py

engine = create_engine(settings.database_url)      # PostgreSQL
timescale_engine = create_engine(settings.timescale_url)  # TimescaleDB

SessionLocal = sessionmaker(bind=engine)
TimescaleSessionLocal = sessionmaker(bind=timescale_engine)
```

### Bind Keys

| Model | Bind Key | Database |
|-------|----------|----------|
| Animal | None | PostgreSQL |
| Paddock | None | PostgreSQL |
| Telemetry | timescale | TimescaleDB |

## Relationships

### Animal to Paddock

```python
# Foreign key defined in Animal model
current_paddock_id = Column(String, ForeignKey("paddocks.id"))
```

## Creating Tables

Tables are created during application startup:

```python
# app/main.py - lifespan event
Base.metadata.create_all(bind=engine, tables=[Paddock.__table__, Animal.__table__])
Base.metadata.create_all(bind=timescale_engine, tables=[Telemetry.__table__])
```

## Indexes

### Spatial Index

```sql
CREATE INDEX idx_paddocks_geometry ON paddocks USING GIST(geometry);
```

### Telemetry Indexes

```sql
CREATE INDEX idx_telemetry_belt_id ON telemetry(belt_id);
CREATE INDEX idx_telemetry_timestamp ON telemetry(timestamp DESC);
```

## Type Mappers

GeoAlchemy2 types are automatically converted:

- `Geometry("POLYGON", srid=4326)` → PostGIS GEOMETRY
- `TIMESTAMP(timezone=True)` → TIMESTAMP WITH TIME ZONE