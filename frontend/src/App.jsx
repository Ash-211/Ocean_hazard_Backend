import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import MapComponent from './components/MapComponent'
import AuthModal from './components/AuthModal'
import ReportModal from './components/ReportModal'
import SidePanel from './components/SidePanel'
import { AuthProvider } from './contexts/AuthContext'
import { MapProvider } from './contexts/MapContext'

function App() {
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authModalMode, setAuthModalMode] = useState('login')
  const [showReportModal, setShowReportModal] = useState(false)
  const [showSidePanel, setShowSidePanel] = useState(false)

  const handleShowAuthModal = (mode = 'login') => {
    setAuthModalMode(mode)
    setShowAuthModal(true)
  }

  return (
    <AuthProvider>
      <MapProvider>
        <div className="App">
          <Header 
            onShowAuthModal={handleShowAuthModal}
            onShowReportModal={() => setShowReportModal(true)}
          />
          
          <main className="main">
            <MapComponent 
              onShowReportModal={() => setShowReportModal(true)}
              onShowSidePanel={() => setShowSidePanel(true)}
            />
            
            <SidePanel 
              isOpen={showSidePanel}
              onClose={() => setShowSidePanel(false)}
            />
            
            {showAuthModal && (
              <AuthModal 
                mode={authModalMode}
                onClose={() => setShowAuthModal(false)} 
              />
            )}
            
            {showReportModal && (
              <ReportModal onClose={() => setShowReportModal(false)} />
            )}
          </main>
        </div>
      </MapProvider>
    </AuthProvider>
  )
}

export default App
