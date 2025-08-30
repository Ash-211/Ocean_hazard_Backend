import React, { useState, useEffect } from 'react'
import { useMap } from '../contexts/MapContext'

const SidePanel = ({ isOpen, onClose }) => {
  const { hazardReports, fetchHazardReports, triggerDBSCAN, getDBSCANResults } = useMap()
  const [filters, setFilters] = useState({
    hazardType: '',
    severity: ''
  })
  const [dbscanTaskId, setDbscanTaskId] = useState(null)
  const [dbscanStatus, setDbscanStatus] = useState('idle')

  useEffect(() => {
    if (isOpen) {
      fetchHazardReports()
    }
  }, [isOpen])

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    })
  }

  const handleTriggerDBSCAN = async () => {
    setDbscanStatus('processing')
    try {
      const taskId = await triggerDBSCAN(24, 0.1, 3)
      setDbscanTaskId(taskId)
      
      // Poll for results
      const checkResults = async () => {
        const result = await getDBSCANResults(taskId)
        if (result.status === 'completed') {
          setDbscanStatus('completed')
        } else {
          setTimeout(checkResults, 2000)
        }
      }
      checkResults()
    } catch (error) {
      setDbscanStatus('error')
    }
  }

  const filteredReports = hazardReports.filter(report => {
    const props = report.properties
    if (filters.hazardType && props.hazard_type !== filters.hazardType) return false
    if (filters.severity && props.severity !== parseInt(filters.severity)) return false
    return true
  })

  if (!isOpen) return null

  return (
    <div className="side-panel open">
      <div className="panel-header">
        <h3>Hazard Reports</h3>
        <button className="btn btn-sm" onClick={onClose}>
          <i className="fas fa-times"></i>
        </button>
      </div>
      
      <div className="panel-content">
        <div className="filters">
          <h4>Filters</h4>
          <div className="form-group">
            <label htmlFor="hazard-type">Hazard Type</label>
            <select 
              id="hazard-type" 
              name="hazardType"
              value={filters.hazardType}
              onChange={handleFilterChange}
            >
              <option value="">All Types</option>
              <option value="tsunami">Tsunami</option>
              <option value="storm_surge">Storm Surge</option>
              <option value="high_waves">High Waves</option>
              <option value="coastal_flooding">Coastal Flooding</option>
              <option value="abnormal_currents">Abnormal Currents</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="severity">Severity</label>
            <select 
              id="severity" 
              name="severity"
              value={filters.severity}
              onChange={handleFilterChange}
            >
              <option value="">All Levels</option>
              <option value="1">Low (1)</option>
              <option value="2">Medium (2)</option>
              <option value="3">High (3)</option>
              <option value="4">Critical (4)</option>
              <option value="5">Emergency (5)</option>
            </select>
          </div>
        </div>

        <div className="dbscan-controls">
          <h4>Hotspot Detection</h4>
          <button 
            className="btn btn-warning btn-sm" 
            onClick={handleTriggerDBSCAN}
            disabled={dbscanStatus === 'processing'}
          >
            {dbscanStatus === 'processing' ? 'Processing...' : 'Detect Hotspots'}
          </button>
          {dbscanStatus === 'completed' && (
            <p className="success-message">Hotspots detected successfully!</p>
          )}
          {dbscanStatus === 'error' && (
            <p className="error-message">Failed to detect hotspots</p>
          )}
        </div>

        <div className="reports-list">
          <h4>Reports ({filteredReports.length})</h4>
          {filteredReports.map((report) => {
            const props = report.properties
            const coords = report.geometry.coordinates
            return (
              <div key={props.id} className="report-item">
                <h4>{props.hazard_type}</h4>
                <p><strong>Severity:</strong> {props.severity}/5</p>
                <p><strong>Location:</strong> {coords[1].toFixed(4)}, {coords[0].toFixed(4)}</p>
                {props.description && <p><strong>Description:</strong> {props.description}</p>}
                <p><strong>Reported:</strong> {new Date(props.report_time).toLocaleString()}</p>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default SidePanel
