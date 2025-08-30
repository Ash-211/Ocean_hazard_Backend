import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'

describe('User Registration and Login Flows', () => {
  test('User can register successfully', async () => {
    render(<App />)
    userEvent.click(screen.getByText(/Register/i))

    userEvent.type(screen.getByLabelText(/Full Name/i), 'Test User')
    userEvent.type(screen.getByLabelText(/^Email$/i), 'testuser@example.com')
    userEvent.type(screen.getByLabelText(/^Password$/i), 'testpassword')
    userEvent.selectOptions(screen.getByLabelText(/Role/i), 'citizen')

    userEvent.click(screen.getByRole('button', { name: /Register/i }))

    await waitFor(() => {
      expect(screen.queryByText(/Register/i)).not.toBeInTheDocument()
    })
  })

  test('User can login successfully', async () => {
    render(<App />)
    userEvent.click(screen.getByText(/Login/i))

    userEvent.type(screen.getByLabelText(/^Email$/i), 'testuser@example.com')
    userEvent.type(screen.getByLabelText(/^Password$/i), 'testpassword')

    userEvent.click(screen.getByRole('button', { name: /Login/i }))

    await waitFor(() => {
      expect(screen.queryByText(/Login/i)).not.toBeInTheDocument()
      expect(screen.getByText(/Logout/i)).toBeInTheDocument()
    })
  })

  test('Role-based UI elements appear correctly', async () => {
    render(<App />)
    // Assuming user is logged in as citizen from previous test
    await waitFor(() => {
      expect(screen.getByText(/Report Hazard/i)).toBeInTheDocument()
      // Officials and analysts might see additional UI elements, test accordingly
    })
  })
})
