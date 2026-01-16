"""
Test the admin users endpoint directly
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Login as admin
print("Logging in as admin...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "pichmony.dev@gmail.com", "password": "Hi@12345"}  # Use known admin account
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()['session']['access_token']
print(f"Logged in successfully as admin")

# Test list users endpoint
print("\nTesting /admin/users endpoint...")
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(
        f"{BASE_URL}/admin/users",
        headers=headers,
        params={"limit": 10, "offset": 0}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        users = response.json()
        print(f"SUCCESS! Found {len(users)} users")
        print(json.dumps(users[:2], indent=2))  # Show first 2 users
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
