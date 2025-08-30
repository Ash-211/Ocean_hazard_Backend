import React, { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet'
import L from 'leaflet'
import { useMap as useMapContext } from '../contexts/MapContext'

const DEFAULT_POSITION = [20.5937, 78.9629] // Center of India

const LocationMarker = () => {
  const { userLocation } = useMapContext()
  const map = useMap()

  useEffect(() => {
    if (userLocation) {
      map.setView([userLocation.latitude, userLocation.longitude], 10)
    }
  }, [userLocation, map])

  if (!userLocation) return null

  return (
    <Marker position={[userLocation.latitude, userLocation.longitude]}>
      <Popup>Your Location</Popup>
    </Marker>
  )
}

const HazardMarkers = () => {
  const { hazardReports } = useMapContext()

  return (
    <>
      {hazardReports.map((feature) => {
        const coords = feature.geometry.coordinates
        const props = feature.properties
        return (
          <Marker 
            key={props.id} 
            position={[coords[1], coords[0]]} 
            icon={L.icon({
              iconUrl: '/marker-icon.png',
              iconSize: [25, 41],
              iconAnchor: [12, 41],
              popupAnchor: [1, -34],
              shadowUrl: '/marker-shadow.png',
              shadowSize: [41, 41]
            })}
          >
            <Popup>
              <strong>{props.hazard_type}</strong><br />
              Severity: {props.severity}<br />
              {props.description}<br />
              Reported: {new Date(props.report_time).toLocaleString()}
            </Popup>
          </Marker>
        )
      })}
    </>
  )
}

const HotspotCircles = () => {
  const { hotspots } = useMapContext()

  return (
    <>
      {hotspots.map((hotspot, idx) => {
        const [lon, lat] = hotspot.coordinates
        return (
          <CircleMarker
            key={idx}
            center={[lat, lon]}
            radius={10}
            color="red"
            fillOpacity={0.5}
          >
            <Popup>Hotspot</Popup>
          </CircleMarker>
        )
      })}
    </>
  )
}

const MapComponent = ({ onShowReportModal, onShowSidePanel }) => {
  const { getUserLocation, fetchHazardReports, userLocation } = useMapContext()
  const [map, setMap] = useState(null)

  useEffect(() => {
    fetchHazardReports()
    getUserLocation()
  }, [])

  const handleRefresh = () => {
    fetchHazardReports()
  }

  const handleLocateMe = () => {
    getUserLocation()
    if (userLocation && map) {
      map.setView([userLocation.latitude, userLocation.longitude], 12)
    }
  }

  return (
    <div className="map-container">
      <MapContainer 
        center={DEFAULT_POSITION} 
        zoom={5} 
        style={{ height: '100vh', width: '100%' }}
        whenCreated={setMap}
      >
        <TileLayer
          attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <LocationMarker />
        <HazardMarkers />
        <HotspotCircles />
      </MapContainer>

      <div className="map-controls">
        <div className="control-group">
          <button className="btn btn-sm" onClick={handleRefresh}>
            <i className="fas fa-sync"></i> Refresh
          </button>
          <button className="btn btn-sm" onClick={handleLocateMe}>
            <i className="fas fa-location-arrow"></i> Locate Me
          </button>
        </div>

        <div className="control-group">
          <button className="btn btn-primary btn-sm" onClick={onShowReportModal}>
            <i className="fas fa-plus"></i> Report Hazard
          </button>
        </div>

        <div className="control-group">
          <button className="btn btn-warning btn-sm" onClick={onShowSidePanel}>
            <i className="fas fa-fire"></i> Show Hotspots
          </button>
        </div>
      </div>
    </div>
  )
}

export default MapComponent
