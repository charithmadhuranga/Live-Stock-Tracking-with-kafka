from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.database_url,
    poolclass=NullPool,
    echo=settings.debug,
)

timescale_engine = create_engine(
    settings.timescale_url,
    poolclass=NullPool,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TimescaleSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=timescale_engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_timescale_db() -> Session:
    db = TimescaleSessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.commit()
            logger.info("PostGIS extension created")
        except Exception as e:
            logger.warning(f"PostGIS extension error: {e}")

    with timescale_engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            conn.commit()
            logger.info("TimescaleDB extension created")
        except Exception as e:
            logger.warning(f"TimescaleDB extension error: {e}")
