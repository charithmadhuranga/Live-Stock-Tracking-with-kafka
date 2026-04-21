import logging
from typing import Optional, Tuple

from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import Paddock, Telemetry, Animal
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class GeofenceService:
    def __init__(self, db: Session):
        self.db = db

    def check_geofence(
        self, belt_id: str, latitude: float, longitude: float
    ) -> Tuple[bool, Optional[str]]:
        animal = self.db.query(Animal).filter(Animal.belt_id == belt_id).first()
        if not animal or not animal.current_paddock_id:
            logger.warning(f"Animal {belt_id} not assigned to any paddock")
            return True, None

        paddock = self.db.query(Paddock).filter(Paddock.id == animal.current_paddock_id).first()
        if not paddock:
            logger.warning(f"Paddock {animal.current_paddock_id} not found")
            return True, None

        point = f"POINT({longitude} {latitude})"
        point_wkt = WKTElement(point, srid=4326)

        query = text(
            """
            SELECT ST_Contains(
                ST_GeomFromEWKT(:paddock_geom),
                ST_GeomFromEWKT(:point_geom)
            ) AS is_within
            """
        )
        result = self.db.execute(
            query,
            {
                "paddock_geom": text(f"ST_GeomFromEWKT('{paddock.geometry.desc}')"),
                "point_geom": point_wkt.desc,
            },
        ).fetchone()

        is_within = result[0] if result else False

        if not is_within:
            logger.warning(
                f"Geofence Breach: Belt {belt_id} at ({latitude}, {longitude}) "
                f"is outside paddock {paddock.id}"
            )

        return is_within, paddock.id if not is_within else None

    def create_breach_alert(
        self, belt_id: str, latitude: float, longitude: float, paddock_id: str
    ):
        logger.info(
            f"Creating geofence breach alert - Belt: {belt_id}, "
            f"Position: ({latitude}, {longitude}), "
            f"Expected Paddock: {paddock_id}"
        )
        return {
            "belt_id": belt_id,
            "latitude": latitude,
            "longitude": longitude,
            "paddock_id": paddock_id,
        }