from celery import shared_task
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any
import json

@shared_task
def cluster_hazards_dbscan(hazard_data: List[Dict[str, Any]], 
                          eps: float = 0.1, 
                          min_samples: int = 3):
    """
    Cluster hazard reports using DBSCAN algorithm
    
    Args:
        hazard_data: List of hazard reports with latitude/longitude
        eps: Maximum distance between two samples for one to be considered
             as in the neighborhood of the other
        min_samples: Number of samples in a neighborhood for a point to be
                     considered as a core point
    
    Returns:
        Dictionary with cluster labels and statistics
    """
    if not hazard_data:
        return {"clusters": [], "statistics": {}}
    
    # Extract coordinates
    coordinates = []
    for hazard in hazard_data:
        if 'latitude' in hazard and 'longitude' in hazard:
            lat = hazard['latitude']
            lon = hazard['longitude']
            if lat is not None and lon is not None:
                coordinates.append([lat, lon])
    
    if len(coordinates) < min_samples:
        return {"clusters": [], "statistics": {"message": "Not enough data points"}}
    
    # Convert to numpy array and scale
    X = np.array(coordinates)
    X_scaled = StandardScaler().fit_transform(X)
    
    # Apply DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X_scaled)
    
    # Count clusters (excluding noise points labeled as -1)
    unique_labels = set(labels)
    n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
    n_noise = list(labels).count(-1)
    
    # Prepare cluster information
    clusters = []
    for label in unique_labels:
        if label == -1:
            continue  # Skip noise points
        
        cluster_points = X[labels == label]
        cluster_hazards = [hazard_data[i] for i in range(len(hazard_data)) 
                          if labels[i] == label and i < len(hazard_data)]
        
        # Calculate cluster center
        center = cluster_points.mean(axis=0).tolist()
        
        clusters.append({
            "cluster_id": int(label),
            "center": {"latitude": center[0], "longitude": center[1]},
            "point_count": len(cluster_points),
            "hazard_types": list(set(h['hazard_type'] for h in cluster_hazards if 'hazard_type' in h)),
            "average_severity": np.mean([h.get('severity', 0) for h in cluster_hazards if 'severity' in h])
        })
    
    return {
        "clusters": clusters,
        "statistics": {
            "n_clusters": n_clusters,
            "n_noise": n_noise,
            "total_points": len(coordinates),
            "algorithm": "DBSCAN",
            "parameters": {"eps": eps, "min_samples": min_samples}
        }
    }

@shared_task
def generate_dbscan_hotspots(time_window_hours: int = 24):
    """
    Generate hotspots using DBSCAN clustering on recent hazard reports
    """
    from sqlalchemy.orm import Session
    from database import SessionLocal
    from models import HazardReport
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    try:
        # Get recent hazard reports
        time_threshold = datetime.utcnow() - timedelta(hours=time_window_hours)
        recent_reports = db.query(HazardReport).filter(
            HazardReport.report_time >= time_threshold
        ).all()
        
        # Prepare data for clustering
        hazard_data = []
        for report in recent_reports:
            # Extract coordinates from geometry if needed
            # For now, assuming latitude/longitude are stored separately
            hazard_data.append({
                "id": str(report.id),
                "hazard_type": report.hazard_type,
                "severity": report.severity,
                "latitude": getattr(report, 'latitude', None),  # Adjust based on your schema
                "longitude": getattr(report, 'longitude', None)
            })
        
        # Apply DBSCAN clustering
        result = cluster_hazards_dbscan.delay(hazard_data)
        return result.get()
        
    finally:
        db.close()
