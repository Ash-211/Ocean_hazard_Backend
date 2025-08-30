import React, { createContext, useContext, useState, useEffect } from 'react'

const MapContext = createContext()

export const useMap = () => {
  const context = useContext(MapContext)
  if (!context) {
    throw new Error('useMap must be used within a MapProvider')
  }
  return context
}

export const MapProvider = ({ children }) => {
  const [hazardReports, setHazardReports] = useState([])
  const [hotspots, setHotspots] = useState([])
  const [userLocation, setUserLocation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Get user's current location
  const getUserLocation = () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser'))
        return
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          }
          setUserLocation(location)
          resolve(location)
        },
        (error) => {
          const errorMessage = getGeolocationError(error)
          setError(errorMessage)
          reject(new Error(errorMessage))
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000
        }
      )
    })
  }

  const getGeolocationError = (error) => {
    switch (error.code) {
      case error.PERMISSION_DENIED:
        return 'Location access denied. Please enable location services.'
      case error.POSITION_UNAVAILABLE:
        return 'Location information is unavailable.'
      case error.TIMEOUT:
        return 'Location request timed out.'
      default:
        return 'An unknown error occurred while getting location.'
    }
  }

  // Fetch hazard reports from API
  const fetchHazardReports = async (bbox = null) => {
    setLoading(true)
    setError(null)
    
    try {
      // India bounding box: minLon, minLat, maxLon, maxLat
      const indiaBBox = [68.0, 6.5, 97.5, 35.5]
      if (!bbox) {
        bbox = indiaBBox
      }
      
      let url = '/hazards/geojson?limit=100'
      if (bbox) {
        url += `&bbox=${bbox.join(',')}`
      }
      
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error('Failed to fetch hazard reports')
      }
      
      const data = await response.json()
      setHazardReports(data.features || [])
    } catch (err) {
      setError(err.message)
      console.error('Error fetching hazard reports:', err)
    } finally {
      setLoading(false)
    }
  }

  // Trigger DBSCAN clustering
  const triggerDBSCAN = async (timeWindow = 24, eps = 0.1, minSamples = 3) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/tasks/dbscan-hotspots', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ timeWindow, eps, minSamples })
      })
      
      if (!response.ok) {
        throw new Error('Failed to trigger DBSCAN clustering')
      }
      
      const data = await response.json()
      return data.task_id
    } catch (err) {
      setError(err.message)
      console.error('Error triggering DBSCAN:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get DBSCAN results
  const getDBSCANResults = async (taskId) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`/tasks/dbscan-hotspots/${taskId}`)
      if (!response.ok) {
        throw new Error('Failed to fetch DBSCAN results')
      }
      
      const data = await response.json()
      if (data.status === 'completed') {
        setHotspots(data.result || [])
      }
      return data
    } catch (err) {
      setError(err.message)
      console.error('Error fetching DBSCAN results:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Submit new hazard report
  const submitHazardReport = async (reportData) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/hazards/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(reportData)
      })
      
      if (!response.ok) {
        throw new Error('Failed to submit hazard report')
      }
      
      const data = await response.json()
      // Refresh reports after successful submission
      await fetchHazardReports()
      return data
    } catch (err) {
      setError(err.message)
      console.error('Error submitting hazard report:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const value = {
    hazardReports,
    hotspots,
    userLocation,
    loading,
    error,
    getUserLocation,
    fetchHazardReports,
    triggerDBSCAN,
    getDBSCANResults,
    submitHazardReport,
    clearError: () => setError(null)
  }

  return (
    <MapContext.Provider value={value}>
      {children}
    </MapContext.Provider>
  )
}
