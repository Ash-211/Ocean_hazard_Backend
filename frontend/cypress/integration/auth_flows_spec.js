describe('User Registration and Login Flows', () => {
  beforeEach(() => {
    cy.visit('/')
    // Mock geolocation to prevent errors
    cy.window().then((win) => {
      cy.stub(win.navigator.geolocation, 'getCurrentPosition').callsFake((success) => {
        success({
          coords: {
            latitude: 19.0760,
            longitude: 72.8777,
            accuracy: 50
          }
        })
      })
    })
  })

  it('User can register successfully', () => {
    cy.contains('Register').click()
    cy.get('input#name').type('Cypress User')
    cy.get('input#register-email').type('cypressuser@example.com')
    cy.get('input#register-password').type('cypresspassword')
    cy.get('select#role').select('citizen')
    cy.contains('Register').click()
    cy.contains('Logout', { timeout: 10000 }).should('be.visible')
  })

  it('User can login successfully', () => {
    cy.contains('Logout').click() // Logout if logged in
    cy.contains('Login').click()
    cy.get('input#email').type('cypressuser@example.com')
    cy.get('input#password').type('cypresspassword')
    cy.contains('Login').click()
    cy.contains('Logout', { timeout: 10000 }).should('be.visible')
  })

  it('Role-based UI elements appear correctly', () => {
    cy.contains('Report Hazard').should('be.visible')
    // Add more role-based UI checks as needed
  })
})
