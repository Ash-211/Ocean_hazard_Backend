import React from 'react'
import { useAuth } from '../contexts/AuthContext'

const Header = ({ onShowAuthModal, onShowReportModal }) => {
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <header className="header">
      <div className="container">
        <div className="logo">
          <i className="fas fa-water"></i>
          <h1>Ocean Hazard Reporting</h1>
        </div>
        
        <nav className="nav">
          {!isAuthenticated ? (
            <div className="auth-buttons">
              <button 
                className="btn btn-outline" 
                onClick={() => onShowAuthModal('login')}
              >
                Login
              </button>
              <button 
                className="btn btn-primary" 
                onClick={() => onShowAuthModal('register')}
              >
                Register
              </button>
            </div>
          ) : (
            <div className="user-menu">
              <span className="user-email">{user?.email}</span>
              {user?.role === 'citizen' && (
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={onShowReportModal}
                >
                  <i className="fas fa-plus"></i> Report Hazard
                </button>
              )}
              <button 
                className="btn btn-outline btn-sm" 
                onClick={logout}
              >
                Logout
              </button>
            </div>
          )}
        </nav>
      </div>
    </header>
  )
}

export default Header
