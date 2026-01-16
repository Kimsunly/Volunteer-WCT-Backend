"""
Test with exact frontend data structure
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Step 1: Login
print("Logging in...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "KhmerChild@gmail.com", "password": "Hi@12345"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()['session']['access_token']
print(f"Logged in successfully")

# Step 2: Try with EXACT frontend data structure
print("\nTesting with frontend data structure...")

# This is exactly what the frontend sends
frontend_data = {
    "title": "Test Post From Frontend",
    "content": "This is the content from frontend",
    "category": "discussion",
    "images": []  # Empty array like frontend
}

print(f"Sending: {json.dumps(frontend_data, indent=2)}")

headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/api/community/",
    headers=headers,
    json=frontend_data
)

print(f"\nStatus: {response.status_code}")

if response.status_code == 422:
    print("VALIDATION ERROR:")
    error_data = response.json()
    print(json.dumps(error_data, indent=2))
elif response.status_code == 201:
    print("SUCCESS!")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"Response: {response.text}")
