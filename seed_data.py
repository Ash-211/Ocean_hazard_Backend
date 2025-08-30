# seed_data.py
from database import SessionLocal
from models import HazardReport
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

dummy_reports = [
    {"hazard_type": "Flooding", "description": "Severe flooding reported", "latitude": 19.076, "longitude": 72.877, "severity": 4},
    {"hazard_type": "High Tide", "description": "Unusually high tide levels", "latitude": 15.299, "longitude": 74.124, "severity": 2},
    {"hazard_type": "Erosion", "description": "Coastal erosion noticed", "latitude": 9.931, "longitude": 76.267, "severity": 3}
]

def seed():
    db = SessionLocal()
    for r in dummy_reports:
        h = HazardReport(
            hazard_type=r["hazard_type"],
            geom=from_shape(Point(r["longitude"], r["latitude"]), srid=4326),
            severity=r["severity"],
            description=r["description"]
        )
        db.add(h)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
