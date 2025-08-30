from database import engine
import sqlalchemy as sa
from auth.utils import verify_password

# Test password verification for a specific user
user_email = "testuser@example.com"  # Change this to test different users
test_password = "Abcd1234@"  # Change this to test different passwords

with engine.connect() as conn:
    # Get user data including hashed password
    result = conn.execute(
        sa.text('SELECT email, hashed_password, is_active, is_verified FROM users WHERE email = :email'),
        {'email': user_email}
    )
    user = result.first()
    
    if user:
        print(f"User found: {user[0]}")
        print(f"Stored hash: {user[1]}")
        print(f"Is active: {user[2]}")
        print(f"Is verified: {user[3]}")
        
        # Test password verification
        is_valid = verify_password(test_password, user[1])
        print(f"Password '{test_password}' is valid: {is_valid}")
    else:
        print(f"User {user_email} not found")
