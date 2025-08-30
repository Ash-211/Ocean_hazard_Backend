import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useMap } from '../contexts/MapContext'

const ReportModal = ({ onClose }) => {
  const { isAuthenticated } = useAuth()
  const { submitHazardReport, getUserLocation, userLocation } = useMap()
  
  const [formData, setFormData] = useState({
    hazard_type: '',
    severity: '2',
    description: '',
    latitude: '',
    longitude: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [locationLoading, setLocationLoading] = useState(false)

  useEffect(() => {
    if (userLocation) {
      setFormData(prev => ({
        ...prev,
        latitude: userLocation.latitude.toString(),
        longitude: userLocation.longitude.toString()
      }))
    }
  }, [userLocation])

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleGetLocation = async () => {
    setLocationLoading(true)
    setError('')
    
    try {
      await getUserLocation()
    } catch (err) {
      setError(err.message)
    } finally {
      setLocationLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!isAuthenticated) {
      setError('Please login to submit a hazard report')
      return
    }

    setLoading(true)
    setError('')

    try {
      const reportData = {
        hazard_type: formData.hazard_type,
        severity: parseInt(formData.severity),
        description: formData.description,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude)
      }

      await submitHazardReport(reportData)
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="modal">
        <div className="modal-content">
          <span className="close" onClick={onClose}>&times;</span>
          <h2>Authentication Required</h2>
          <p>Please login to submit hazard reports.</p>
          <button className="btn btn-primary" onClick={onClose}>
            OK
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="modal">
      <div className="modal-content">
        <span className="close" onClick={onClose}>&times;</span>
        
        <h2>Report Ocean Hazard</h2>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="hazard_type">Hazard Type *</label>
            <select
              id="hazard_type"
              name="hazard_type"
              value={formData.hazard_type}
              onChange={handleInputChange}
              required
            >
              <option value="">Select Hazard Type</option>
              <option value="tsunami">Tsunami</option>
              <option value="storm_surge">Storm Surge</option>
              <option value="high_waves">High Waves</option>
              <option value="coastal_flooding">Coastal Flooding</option>
              <option value="abnormal_currents">Abnormal Currents</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="severity">Severity Level *</label>
            <select
              id="severity"
              name="severity"
              value={formData.severity}
              onChange={handleInputChange}
              required
            >
              <option value="1">Low (1)</option>
              <option value="2">Medium (2)</option>
              <option value="3">High (3)</option>
              <option value="4">Critical (4)</option>
              <option value="5">Emergency (5)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Describe what you observed..."
              rows="3"
            />
          </div>

          <div className="form-group">
            <label>Location Coordinates *</label>
            <div className="location-inputs">
              <input
                type="number"
                step="any"
                placeholder="Latitude"
                name="latitude"
                value={formData.latitude}
                onChange={handleInputChange}
                required
              />
              <input
                type="number"
                step="any"
                placeholder="Longitude"
                name="longitude"
                value={formData.longitude}
                onChange={handleInputChange}
                required
              />
            </div>
            <button 
              type="button" 
              className="btn btn-sm" 
              onClick={handleGetLocation}
              disabled={locationLoading}
            >
              <i className="fas fa-location-arrow"></i>
              {locationLoading ? 'Getting Location...' : 'Use Current Location'}
            </button>
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              className="btn btn-outline" 
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={loading}
            >
              {loading ? 'Submitting...' : 'Submit Report'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ReportModal
