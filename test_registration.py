import requests
import json

# Test registration endpoint
url = "http://localhost:8000/auth/register"
test_user = {
    "email": "testnew@example.com",
    "full_name": "Test New User",
    "password": "Abcd1234@",
    "role": "citizen"
}

try:
    response = requests.post(url, json=test_user)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("Registration successful!")
        user_data = response.json()
        print(f"User created: {user_data}")
        
        # Now test login
        login_url = "http://localhost:8000/auth/token"
        login_data = {
            "username": "testnew@example.com",
            "password": "Abcd1234@"
        }
        
        login_response = requests.post(login_url, data=login_data)
        print(f"\nLogin Status Code: {login_response.status_code}")
        print(f"Login Response: {login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")
