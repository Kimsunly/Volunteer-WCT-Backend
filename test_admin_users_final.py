"""Test /admin/users endpoint with correct admin credentials"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Login as admin
print("Logging in as admin...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "admin@volunteer.com", "password": "password123"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()['session']['access_token']
print(f"✓ Logged in successfully as admin")

# Test list users endpoint
print("\n=== Testing /admin/users endpoint ===")
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(
        f"{BASE_URL}/admin/users",
        headers=headers,
        params={"limit": 10, "offset": 0},
        timeout=15
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        users = response.json()
        print(f"✓ SUCCESS! Found {len(users)} users")
        if users:
            print("\nFirst user:")
            print(json.dumps(users[0], indent=2))
    else:
        print(f"✗ ERROR Response:")
        print(response.text[:1000])
        
except requests.exceptions.Timeout:
    print("✗ ERROR: Request timed out after 15s - server is frozen/crashed")
except requests.exceptions.ConnectionError as e:
    print(f"✗ ERROR: Connection failed - server not responding")
    print(f"Details: {e}")
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")
