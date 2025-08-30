# Authentication Fixes TODO

## Issues Fixed:
1. [x] Both login and register buttons open login screen
2. [x] Registration fails due to missing role field
3. [x] No password strength validation

## Steps Completed:
1. [x] Fix Header.jsx to pass mode parameter to AuthModal
2. [x] Fix AuthModal.jsx to accept initial mode parameter
3. [x] Fix App.jsx to handle mode parameter passing
4. [x] Fix auth/crud.py to include role in user creation
5. [x] Add password validation to auth/schemas.py
6. [x] Add client-side password validation to AuthModal.jsx
7. [ ] Test the fixes

## Password Validation Requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one number
- At least one special character

## Next Steps:
- Test the registration and login flows
- Verify password validation works on both frontend and backend
- Check that both buttons now open the correct modal view
- Test with various password strengths to ensure validation works
