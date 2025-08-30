# main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi.responses import JSONResponse
import json

import models, schemas, crud, database
from database import get_db
from auth import routes as auth_routes

# Create tables (simple approach for MVP)
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Ocean Hazard API")

# CORS (dev). Restrict origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_routes.router)

@app.get("/")
def root():
    return {"message": "Ocean Hazard API is running!"}

@app.post("/hazards/", response_model=schemas.HazardReport)
def create_hazard(hazard: schemas.HazardReportCreate, db: Session = Depends(get_db)):
    return crud.create_hazard_report(db, hazard)

@app.get("/hazards/geojson")
def read_hazards_geojson(
    bbox: str | None = Query(None, description="bbox=minLon,minLat,maxLon,maxLat"),
    limit: int = Query(100),
    skip: int = Query(0),
    db: Session = Depends(get_db)
):
    if bbox:
        try:
            bbox_list = list(map(float, bbox.split(",")))
            if len(bbox_list) != 4:
                raise ValueError()
        except Exception:
            raise HTTPException(status_code=400, detail="bbox must be 4 comma-separated floats: minLon,minLat,maxLon,maxLat")
    else:
        bbox_list = None

    hazards = crud.get_hazard_reports(db, bbox=bbox_list, limit=limit, skip=skip)
    features = []
    for h in hazards:
        # Use DB-side ST_AsGeoJSON for exact geometry representation
        stmt = select(func.ST_AsGeoJSON(models.HazardReport.geom)).where(models.HazardReport.id == h.id)
        geojson_str = db.execute(stmt).scalar_one()
        geometry = json.loads(geojson_str)
        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": str(h.id),
                "hazard_type": h.hazard_type,
                "severity": h.severity,
                "description": h.description,
                "report_time": h.report_time.isoformat() if h.report_time else None
            }
        })
    return JSONResponse({
        "type": "FeatureCollection",
        "features": features
    })

# DBSCAN Clustering Endpoints
@app.post("/tasks/dbscan-hotspots")
async def trigger_dbscan_hotspots(
    time_window: int = 24,
    eps: float = 0.1,
    min_samples: int = 3
):
    """
    Trigger DBSCAN clustering for hazard hotspots
    """
    from tasks.ml_clustering import generate_dbscan_hotspots
    task = generate_dbscan_hotspots.delay(time_window)
    return {"task_id": task.id, "status": "started"}

@app.get("/tasks/dbscan-hotspots/{task_id}")
async def get_dbscan_result(task_id: str):
    """
    Get DBSCAN clustering results
    """
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    
    if result.ready():
        return {
            "status": "completed",
            "result": result.result
        }
    else:
        return {"status": "processing"}
