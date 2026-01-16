import requests
import json

url = "http://localhost:8003/api/opportunities"
params = {
    "limit": 9,
    "offset": 0,
    "sort": "newest",
    "category": "environment"
}

try:
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
