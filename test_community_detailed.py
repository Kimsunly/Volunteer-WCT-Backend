"""
Test script to reproduce the exact 422 error for community post creation
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Step 1: Login as organizer
print("Logging in as organizer...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "KhmerChild@gmail.com", "password": "Hi@12345"}
)

print(f"Login status: {login_response.status_code}")

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

# Extract token from session
login_data = login_response.json()
print(f"Login response keys: {list(login_data.keys())}")

# The token might be in session.access_token
if 'session' in login_data:
    token = login_data['session'].get('access_token')
elif 'access_token' in login_data:
    token = login_data['access_token']
else:
    print(f"Cannot find token in response: {json.dumps(login_data, indent=2)}")
    exit(1)

print(f"Token: {token[:50]}...")

# Step 2: Try to create a community post (reproduce the exact frontend request)
print("\nAttempting to create community post...")

post_data = {
    "title": "Test Community Post",
    "content": "This is test content for debugging",
    "category": "discussion",
    "images": [],
}

print(f"Sending data: {json.dumps(post_data, indent=2)}")

headers = {"Authorization": f"Bearer {token}"}
create_response = requests.post(
    f"{BASE_URL}/api/community/",
    headers=headers,
    json=post_data
)

print(f"\nResponse Status: {create_response.status_code}")
print(f"Response Headers: {dict(create_response.headers)}")
print(f"\nResponse Body:")
try:
    print(json.dumps(create_response.json(), indent=2))
except:
    print(create_response.text)

if create_response.status_code == 422:
    print("\n" + "=" * 60)
    print("422 VALIDATION ERROR DETAILS:")
    print("=" * 60)
    error_data = create_response.json()
    if 'detail' in error_data:
        for error in error_data['detail']:
            print(f"\nField: {error.get('loc', 'Unknown')}")
            print(f"Error: {error.get('msg', 'Unknown')}")
            print(f"Type: {error.get('type', 'Unknown')}")
