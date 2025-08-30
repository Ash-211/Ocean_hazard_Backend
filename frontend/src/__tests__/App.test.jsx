import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import App from '../App'

describe('App Component', () => {
  test('renders login and register buttons', () => {
    render(<App />)
    expect(screen.getByText(/Login/i)).toBeInTheDocument()
    expect(screen.getByText(/Register/i)).toBeInTheDocument()
  })

  test('opens login modal when login button clicked', () => {
    render(<App />)
    fireEvent.click(screen.getByText(/Login/i))
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText(/Login/i)).toBeInTheDocument()
  })

  test('opens register modal when register button clicked', () => {
    render(<App />)
    fireEvent.click(screen.getByText(/Register/i))
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText(/Register/i)).toBeInTheDocument()
  })
})
