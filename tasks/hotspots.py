# tasks/hotspots.py
from celery import shared_task
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from database import SessionLocal
from models import HazardReport
from geoalchemy2.functions import ST_AsGeoJSON, ST_Point, ST_Intersects, ST_MakeEnvelope
from datetime import datetime, timedelta
import json
import math

@shared_task
def generate_hotspots(time_window_hours=24, bbox=None, min_reports=3):
    """Generate hazard hotspots based on report density"""
    db = SessionLocal()
    try:
        # Calculate time window
        time_threshold = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Base query
        query = db.query(HazardReport).filter(
            HazardReport.report_time >= time_threshold
        )
        
        # Apply bounding box filter if provided
        if bbox and len(bbox) == 4:
            min_lon, min_lat, max_lon, max_lat = bbox
            envelope = ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
            query = query.filter(ST_Intersects(HazardReport.geom, envelope))
        
        recent_reports = query.all()
        
        if not recent_reports:
            return {"hotspots": [], "total_reports": 0}
        
        # Convert to GeoJSON for clustering
        features = []
        for report in recent_reports:
            # Get coordinates from geometry
            stmt = db.query(ST_AsGeoJSON(HazardReport.geom)).filter(HazardReport.id == report.id)
            geojson_str = db.execute(stmt).scalar_one()
            geometry = json.loads(geojson_str)
            
            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "id": str(report.id),
                    "hazard_type": report.hazard_type,
                    "severity": report.severity,
                    "report_time": report.report_time.isoformat() if report.report_time else None
                }
            })
        
        # Simple grid-based clustering
        hotspots = self.cluster_reports(features, grid_size=0.1, min_reports=min_reports)
        
        return {
            "hotspots": hotspots,
            "total_reports": len(recent_reports),
            "time_window_hours": time_window_hours,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    finally:
        db.close()

def cluster_reports(self, features, grid_size=0.1, min_reports=3):
    """Cluster reports using a simple grid-based approach"""
    grid_cells = {}
    
    for feature in features:
        coords = feature["geometry"]["coordinates"]
        if coords and len(coords) == 2:
            lon, lat = coords
            # Calculate grid cell
            grid_x = math.floor(lon / grid_size) * grid_size
            grid_y = math.floor(lat / grid_size) * grid_size
            grid_key = f"{grid_x}_{grid_y}"
            
            if grid_key not in grid_cells:
                grid_cells[grid_key] = {
                    "count": 0,
                    "total_severity": 0,
                    "hazard_types": set(),
                    "reports": [],
                    "center_lon": grid_x + grid_size / 2,
                    "center_lat": grid_y + grid_size / 2
                }
            
            cell = grid_cells[grid_key]
            cell["count"] += 1
            cell["total_severity"] += feature["properties"].get("severity", 0)
            cell["hazard_types"].add(feature["properties"].get("hazard_type", "unknown"))
            cell["reports"].append(feature["properties"]["id"])
    
    # Filter and format hotspots
    hotspots = []
    for grid_key, cell in grid_cells.items():
        if cell["count"] >= min_reports:
            avg_severity = cell["total_severity"] / cell["count"] if cell["count"] > 0 else 0
            
            hotspot = {
                "id": f"hotspot_{grid_key}",
                "center": [cell["center_lon"], cell["center_lat"]],
                "count": cell["count"],
                "average_severity": round(avg_severity, 2),
                "hazard_types": list(cell["hazard_types"]),
                "report_ids": cell["reports"],
                "radius": min(5.0, cell["count"] * 0.5),  # Dynamic radius based on count
                "intensity": self.calculate_intensity(cell["count"], avg_severity),
                "grid_size": grid_size
            }
            hotspots.append(hotspot)
    
    # Sort by intensity (most critical first)
    hotspots.sort(key=lambda x: x["intensity"], reverse=True)
    
    return hotspots

def calculate_intensity(self, count, avg_severity):
    """Calculate hotspot intensity score"""
    # Weight count more heavily than severity
    intensity = (count * 0.7) + (avg_severity * 0.3)
    return min(intensity, 10.0)  # Cap at 10

@shared_task
def generate_social_media_hotspots(social_media_data, time_window_hours=6):
    """Generate hotspots from social media data"""
    if not social_media_data:
        return {"hotspots": [], "total_posts": 0}
    
    # Extract locations from social media posts
    location_posts = []
    for post in social_media_data:
        locations = post.get("nlp_analysis", {}).get("locations", [])
        urgency = post.get("nlp_analysis", {}).get("urgency_score", 0)
        
        if locations and urgency > 10:  # Only consider posts with some urgency
            for location in locations:
                location_posts.append({
                    "location": location,
                    "urgency": urgency,
                    "post_id": post.get("id", ""),
                    "source": post.get("source", "")
                })
    
    # Simple location-based clustering
    location_counts = {}
    for post in location_posts:
        loc = post["location"].lower()
        if loc not in location_counts:
            location_counts[loc] = {
                "count": 0,
                "total_urgency": 0,
                "post_ids": [],
                "sources": set()
            }
        
        location_counts[loc]["count"] += 1
        location_counts[loc]["total_urgency"] += post["urgency"]
        location_counts[loc]["post_ids"].append(post["post_id"])
        location_counts[loc]["sources"].add(post["source"])
    
    # Format hotspots
    hotspots = []
    for location, data in location_counts.items():
        if data["count"] >= 3:  # Minimum posts for a hotspot
            avg_urgency = data["total_urgency"] / data["count"]
            
            hotspot = {
                "location": location,
                "post_count": data["count"],
                "average_urgency": round(avg_urgency, 2),
                "post_ids": data["post_ids"],
                "sources": list(data["sources"]),
                "intensity": min(10.0, avg_urgency / 10.0),  # Scale to 0-10
                "type": "social_media"
            }
            hotspots.append(hotspot)
    
    hotspots.sort(key=lambda x: x["intensity"], reverse=True)
    
    return {
        "hotspots": hotspots,
        "total_posts": len(social_media_data),
        "time_window_hours": time_window_hours,
        "generated_at": datetime.utcnow().isoformat()
    }

@shared_task
def update_hotspots_continuously():
    """Continuous hotspot generation (to be scheduled)"""
    # Generate hotspots from recent reports
    report_hotspots = generate_hotspots.delay(time_window_hours=24)
    
    # You could also generate social media hotspots if you have that data
    # social_media_hotspots = generate_social_media_hotspots.delay(social_media_data)
    
    return {
        "report_hotspots": report_hotspots.get() if report_hotspots.ready() else [],
        # "social_media_hotspots": social_media_hotspots.get() if social_media_hotspots.ready() else [],
        "updated_at": datetime.utcnow().isoformat()
    }
