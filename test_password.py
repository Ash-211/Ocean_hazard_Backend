from database import SessionLocal
from auth.models import User
from auth.utils import verify_password

db = SessionLocal()

# Test password verification for a specific user
user_email = "testuser@example.com"  # Change this to test different users
test_password = "Abcd1234@"  # Change this to test different passwords

user = db.query(User).filter(User.email == user_email).first()
if user:
    print(f"User found: {user.email}")
    print(f"Stored hash: {user.hashed_password}")
    print(f"Is active: {user.is_active}")
    print(f"Is verified: {user.is_verified}")
    
    # Test password verification
    is_valid = verify_password(test_password, user.hashed_password)
    print(f"Password '{test_password}' is valid: {is_valid}")
else:
    print(f"User {user_email} not found")

db.close()
