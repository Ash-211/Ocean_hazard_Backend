# crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
import models, schemas

def create_hazard_report(db: Session, hazard: schemas.HazardReportCreate):
    point = from_shape(Point(hazard.longitude, hazard.latitude), srid=4326)
    db_hazard = models.HazardReport(
        hazard_type=hazard.hazard_type,
        geom=point,
        severity=hazard.severity,
        description=hazard.description
    )
    db.add(db_hazard)
    db.commit()
    db.refresh(db_hazard)
    return db_hazard

def get_hazard_reports(db: Session, bbox: list[float] | None = None, limit: int = 100, skip: int = 0):
    # bbox expected as [minLon, minLat, maxLon, maxLat]
    if bbox:
        env = func.ST_MakeEnvelope(bbox[0], bbox[1], bbox[2], bbox[3], 4326)
        q = select(models.HazardReport).where(func.ST_Intersects(models.HazardReport.geom, env)).order_by(models.HazardReport.report_time.desc()).offset(skip).limit(limit)
    else:
        q = select(models.HazardReport).order_by(models.HazardReport.report_time.desc()).offset(skip).limit(limit)
    result = db.execute(q).scalars().all()
    return result
