import React, { useEffect, useState, useMemo } from 'react'
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet'
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

  console.log('HazardMarkers rendering with reports:', hazardReports.length, 'items')
  if (hazardReports.length > 0) {
    console.log('First hazard coordinates:', hazardReports[0].geometry.coordinates)
  }

  const getSeverityColor = (severity) => {
    if (typeof severity !== 'number') {
      return 'blue'
    }
    switch (severity) {
      case 1:
        return '#ff0000' // critical - bright red
      case 2:
        return '#ff4500' // high - orange red
      case 3:
        return '#ffa500' // medium - orange
      case 4:
        return '#ffff00' // low - yellow
      default:
        return 'blue'
    }
  }

  const getSeverityGlowClass = (severity) => {
    if (typeof severity !== 'number') {
      return 'default-glow'
    }
    switch (severity) {
      case 1:
        return 'critical-glow'
      case 2:
        return 'high-glow'
      case 3:
        return 'medium-glow'
      case 4:
        return 'low-glow'
      default:
        return 'default-glow'
    }
  }

  const getSeverityRadius = (severity) => {
    if (typeof severity !== 'number') {
      return 12
    }
    switch (severity) {
      case 1:
        return 25 // critical
      case 2:
        return 20 // high
      case 3:
        return 15 // medium
      case 4:
        return 10 // low
      default:
        return 12
    }
  }

  const markers = useMemo(() => {
    return hazardReports.map((feature) => {
      const coords = feature.geometry.coordinates
      const props = feature.properties
      const color = getSeverityColor(props.severity)
      const radius = getSeverityRadius(props.severity)
      const glowClass = getSeverityGlowClass(props.severity)
      // Draw a fixed circle around the hazard point
      return (
        <CircleMarker
          key={props.id}
          center={[coords[1], coords[0]]}
          radius={radius}
          color={color}
          fillColor={color}
          fillOpacity={0.6}
          weight={2}
          className={`hazard-circle ${glowClass}`}
        >
          <Popup>
            <strong>{props.hazard_type}</strong><br />
            Severity: {props.severity}<br />
            {props.description}<br />
            Reported: {new Date(props.report_time).toLocaleString()}
          </Popup>
        </CircleMarker>
      )
    })
  }, [hazardReports])

  return <>{markers}</>
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

  const handleMapCreated = (mapInstance) => {
    setMap(mapInstance)
    console.log('Map created with center:', mapInstance.getCenter(), 'zoom:', mapInstance.getZoom())

    // Add event listeners for map changes
    mapInstance.on('moveend', () => {
      const center = mapInstance.getCenter()
      const zoom = mapInstance.getZoom()
      console.log('Map moved to center:', [center.lat, center.lng], 'zoom:', zoom)
    })

    mapInstance.on('zoomend', () => {
      const center = mapInstance.getCenter()
      const zoom = mapInstance.getZoom()
      console.log('Map zoomed to center:', [center.lat, center.lng], 'zoom:', zoom)
    })
  }

  return (
    <div className="map-container">
      <MapContainer
        center={DEFAULT_POSITION}
        zoom={5}
        style={{ height: '100vh', width: '100%' }}
        whenCreated={handleMapCreated}
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
