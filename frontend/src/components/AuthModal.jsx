import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

const AuthModal = ({ mode = 'login', onClose }) => {
  const [isLogin, setIsLogin] = useState(mode === 'login')
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'citizen'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [passwordError, setPasswordError] = useState('')
  
  const { login, register } = useAuth()

  useEffect(() => {
    setIsLogin(mode === 'login')
    setError('')
    setPasswordError('')
  }, [mode])

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    
    // Clear password error when user starts typing
    if (e.target.name === 'password') {
      setPasswordError('')
    }
  }

  const validatePassword = (password) => {
    if (password.length < 8) {
      return 'Password must be at least 8 characters long'
    }
    if (!/[A-Z]/.test(password)) {
      return 'Password must contain at least one uppercase letter'
    }
    if (!/[a-z]/.test(password)) {
      return 'Password must contain at least one lowercase letter'
    }
    if (!/[0-9]/.test(password)) {
      return 'Password must contain at least one number'
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      return 'Password must contain at least one special character'
    }
    return ''
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setPasswordError('')

    try {
      // Validate password for registration
      if (!isLogin) {
        const passwordValidation = validatePassword(formData.password)
        if (passwordValidation) {
          setPasswordError(passwordValidation)
          setLoading(false)
          return
        }
      }

      let result
      if (isLogin) {
        result = await login(formData.email, formData.password)
      } else {
        // Rename name to full_name for backend schema
        const registerData = {
          email: formData.email,
          full_name: formData.name,
          password: formData.password,
          role: formData.role
        }
        result = await register(registerData)
      }

      if (result.success) {
        onClose()
      } else {
        setError(result.error)
      }
    } catch (err) {
      setError('An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal">
      <div className="modal-content">
        <span className="close" onClick={onClose}>&times;</span>
        
        {isLogin ? (
          <form onSubmit={handleSubmit} className="auth-form">
            <h2>Login</h2>
            
            {error && <div className="error-message">{error}</div>}
            
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={loading}
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>

            <p>
              Don't have an account?{' '}
              <a 
                href="#" 
                onClick={(e) => {
                  e.preventDefault()
                  setIsLogin(false)
                  setError('')
                  setPasswordError('')
                }}
              >
                Register
              </a>
            </p>
          </form>
        ) : (
          <form onSubmit={handleSubmit} className="auth-form">
            <h2>Register</h2>
            
            {error && <div className="error-message">{error}</div>}
            
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="register-email">Email</label>
              <input
                type="email"
                id="register-email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="register-password">Password</label>
              <input
                type="password"
                id="register-password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
              />
              {passwordError && <div className="error-message">{passwordError}</div>}
              <div className="password-hint">
                Password must contain: 8+ characters, uppercase, lowercase, number, and special character
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="role">Role</label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleInputChange}
                required
              >
                <option value="citizen">Citizen</option>
                <option value="official">Official</option>
                <option value="analyst">Analyst</option>
              </select>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={loading || passwordError}
            >
              {loading ? 'Registering...' : 'Register'}
            </button>

            <p>
              Already have an account?{' '}
              <a 
                href="#" 
                onClick={(e) => {
                  e.preventDefault()
                  setIsLogin(true)
                  setError('')
                  setPasswordError('')
                }}
              >
                Login
              </a>
            </p>
          </form>
        )}
      </div>
    </div>
  )
}

export default AuthModal
