# test_auth.py
import requests
import json

BASE_URL = 'http://127.0.0.1:8001'

def test_auth_flow():
    print("Testing authentication flow...")
    
    # Test registration
    print("\n1. Testing user registration...")
    user_data = {
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/register', json=user_data)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            print(f'Registered user: {response.json()}')
        else:
            print(f'Error: {response.text}')
    except Exception as e:
        print(f'Registration error: {e}')
    
    # Test login
    print("\n2. Testing user login...")
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/token', data=login_data)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            token_data = response.json()
            print(f'Login successful, token: {token_data["access_token"][:50]}...')
            access_token = token_data["access_token"]
            
            # Test protected endpoint
            print("\n3. Testing protected endpoint...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f'{BASE_URL}/auth/me', headers=headers)
            print(f'Status: {response.status_code}')
            if response.status_code == 200:
                print(f'User info: {response.json()}')
            else:
                print(f'Error: {response.text}')
                
        else:
            print(f'Login error: {response.text}')
            
    except Exception as e:
        print(f'Login error: {e}')
    
    # Test logout
    print("\n4. Testing logout...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(f'{BASE_URL}/auth/logout', headers=headers)
        print(f'Status: {response.status_code}')
        print(f'Logout response: {response.json()}')
    except Exception as e:
        print(f'Logout error: {e}')

def test_protected_hazard_endpoint():
    print("\n5. Testing protected hazard endpoint...")
    
    # First login to get token
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/token', data=login_data)
        if response.status_code == 200:
            access_token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test creating a hazard report
            hazard_data = {
                "hazard_type": "Storm",
                "latitude": 18.5204,
                "longitude": 73.8567,
                "severity": 5,
                "description": "Test hazard with authentication"
            }
            
            response = requests.post(f'{BASE_URL}/hazards/', json=hazard_data, headers=headers)
            print(f'Status: {response.status_code}')
            if response.status_code == 200:
                print(f'Created hazard: {response.json()}')
            else:
                print(f'Error: {response.text}')
                
    except Exception as e:
        print(f'Protected endpoint error: {e}')

if __name__ == "__main__":
    test_auth_flow()
    test_protected_hazard_endpoint()
