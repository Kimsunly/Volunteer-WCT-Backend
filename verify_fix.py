import requests
import json

# Testing on default port 8000
url = "http://localhost:8000/api/opportunities"
params = {
    "limit": 9,
    "offset": 0,
    "sort": "newest",
    "category": "environment"
}

try:
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data.get('total')}")
        print(f"Items: {len(data.get('data', []))}")
    else:
        print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
