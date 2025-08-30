import requests
import json
import sys

BASE_URL = 'http://127.0.0.1:8001'

def test_api():
    try:
        print("Testing /hazards/geojson endpoint...")
        response = requests.get(f'{BASE_URL}/hazards/geojson')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            print('Response:')
            print(json.dumps(response.json(), indent=2))
        else:
            print(f'Error response: {response.text}')
            
    except requests.exceptions.ConnectionError:
        print("Connection error - is the server running?")
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    test_api()
