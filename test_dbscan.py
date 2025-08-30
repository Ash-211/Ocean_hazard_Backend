# test_dbscan.py
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def test_dbscan_basic():
    """Test basic DBSCAN functionality"""
    print("Testing DBSCAN clustering...")
    
    # Sample hazard data with coordinates
    hazard_data = [
        {"latitude": 18.5204, "longitude": 73.8567, "hazard_type": "Tsunami", "severity": 8},
        {"latitude": 18.5205, "longitude": 73.8568, "hazard_type": "Tsunami", "severity": 7},
        {"latitude": 18.5206, "longitude": 73.8569, "hazard_type": "Storm", "severity": 5},
        {"latitude": 19.0760, "longitude": 72.8777, "hazard_type": "Flood", "severity": 6},
        {"latitude": 19.0761, "longitude": 72.8778, "hazard_type": "Flood", "severity": 4},
        {"latitude": 13.0827, "longitude": 80.2707, "hazard_type": "Earthquake", "severity": 9},
    ]
    
    # Extract coordinates
    coordinates = []
    for hazard in hazard_data:
        if 'latitude' in hazard and 'longitude' in hazard:
            lat = hazard['latitude']
            lon = hazard['longitude']
            if lat is not None and lon is not None:
                coordinates.append([lat, lon])
    
    print(f"Coordinates: {coordinates}")
    
    if len(coordinates) < 3:
        print("Not enough data points for clustering")
        return
    
    # Convert to numpy array and scale
    X = np.array(coordinates)
    X_scaled = StandardScaler().fit_transform(X)
    
    # Apply DBSCAN
    dbscan = DBSCAN(eps=0.5, min_samples=2)
    labels = dbscan.fit_predict(X_scaled)
    
    print(f"DBSCAN labels: {labels}")
    
    # Count clusters
    unique_labels = set(labels)
    n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
    n_noise = list(labels).count(-1)
    
    print(f"Number of clusters: {n_clusters}")
    print(f"Number of noise points: {n_noise}")
    
    # Show clusters
    for label in unique_labels:
        if label == -1:
            print("Noise points:")
            noise_indices = [i for i, l in enumerate(labels) if l == -1]
            for idx in noise_indices:
                print(f"  - {hazard_data[idx]}")
        else:
            print(f"Cluster {label}:")
            cluster_indices = [i for i, l in enumerate(labels) if l == label]
            for idx in cluster_indices:
                print(f"  - {hazard_data[idx]}")

if __name__ == "__main__":
    test_dbscan_basic()
