# test_comprehensive.py
import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8001'

def test_comprehensive_flow():
    print("=== COMPREHENSIVE OCEAN HAZARD API TEST ===\n")
    
    # Test 1: User Registration
    print("1. Testing user registration...")
    user_data = {
        "email": "testuser2@example.com",
        "full_name": "Test User 2",
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
    
    # Test 2: User Login
    print("\n2. Testing user login...")
    login_data = {
        "username": "testuser2@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/token', data=login_data)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            token_data = response.json()
            print(f'Login successful, token received')
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            print(f'Login error: {response.text}')
            return
    except Exception as e:
        print(f'Login error: {e}')
        return
    
    # Test 3: Protected User Info
    print("\n3. Testing protected user endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/auth/me', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            print(f'User info: {response.json()}')
        else:
            print(f'Error: {response.text}')
    except Exception as e:
        print(f'User info error: {e}')
    
    # Test 4: Create Hazard Report
    print("\n4. Testing hazard report creation...")
    hazard_data = {
        "hazard_type": "Tsunami",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "severity": 8,
        "description": "Large tsunami warning detected"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/hazards/', json=hazard_data, headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            hazard = response.json()
            print(f'Created hazard: {hazard}')
            hazard_id = hazard["id"]
        else:
            print(f'Error: {response.text}')
    except Exception as e:
        print(f'Hazard creation error: {e}')
    
    # Test 5: Get GeoJSON Hazards
    print("\n5. Testing GeoJSON endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/hazards/geojson')
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            geojson = response.json()
            print(f'GeoJSON response: {len(geojson["features"])} features found')
            print(f'Feature collection type: {geojson["type"]}')
        else:
            print(f'Error: {response.text}')
    except Exception as e:
        print(f'GeoJSON error: {e}')
    
    # Test 6: Get GeoJSON with Bounding Box
    print("\n6. Testing GeoJSON with bounding box...")
    try:
        response = requests.get(f'{BASE_URL}/hazards/geojson?bbox=73,18,74,19')
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            geojson = response.json()
            print(f'Bounded GeoJSON: {len(geojson["features"])} features in bbox')
        else:
            print(f'Error: {response.text}')
    except Exception as e:
        print(f'Bounded GeoJSON error: {e}')
    
    # Test 7: Logout
    print("\n7. Testing logout...")
    try:
        response = requests.post(f'{BASE_URL}/auth/logout', headers=headers)
        print(f'Status: {response.status_code}')
        print(f'Logout response: {response.json()}')
    except Exception as e:
        print(f'Logout error: {e}')
    
    # Test 8: Test Authentication Required
    print("\n8. Testing authentication requirement...")
    try:
        response = requests.post(f'{BASE_URL}/hazards/', json=hazard_data)
        print(f'Status: {response.status_code}')
        if response.status_code == 401:
            print('✓ Authentication required - correct behavior')
        else:
            print(f'Unexpected response: {response.text}')
    except Exception as e:
        print(f'Auth test error: {e}')
    
    print("\n=== COMPREHENSIVE TEST COMPLETED ===")

def test_celery_tasks():
    print("\n=== TESTING CELERY TASKS (if available) ===")
    
    # Test NLP analysis
    print("\nTesting NLP analysis...")
    test_text = "Major tsunami warning issued for coastal areas. Immediate evacuation required!"
    
    try:
        response = requests.post(f'{BASE_URL}/tasks/analyze-text', json={"text": test_text})
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            analysis = response.json()
            print(f'NLP Analysis: {analysis.get("urgency_score", "N/A")} urgency score')
            print(f'Hazard keywords: {analysis.get("hazard_keywords", [])}')
        else:
            print(f'Error: {response.text}')
    except Exception as e:
        print(f'NLP test error: {e}')

if __name__ == "__main__":
    test_comprehensive_flow()
    test_celery_tasks()
