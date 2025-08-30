from sqlalchemy.orm import Session
import database, models
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

def verify_tables():
    db: Session = database.SessionLocal()

    # Create a test hazard report with proper geometry
    point = from_shape(Point(56.78, 12.34), srid=4326)  # longitude, latitude
    new_report = models.HazardReport(
        hazard_type="tsunami",
        geom=point,
        severity=4,
        description="Test hazard report"
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    print(f"Inserted hazard report with ID {new_report.id}")

    reports = db.query(models.HazardReport).all()
    print("Current Hazard Reports in DB:")
    for r in reports:
        # Query the geometry to get coordinates
        from sqlalchemy import select, func
        stmt = select(func.ST_AsText(models.HazardReport.geom)).where(models.HazardReport.id == r.id)
        geom_text = db.execute(stmt).scalar_one()
        print(f" - {r.id}: {r.hazard_type} at {geom_text} severity={r.severity}")

    db.close()

if __name__ == "__main__":
    verify_tables()
