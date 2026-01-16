import requests
import json
import sys

# API Base URL
BASE_URL = "http://127.0.0.1:8000"

# Test Credentials
EMAIL = "NexZin@gmail.com"
PASSWORD = "Hi@12345"

def login():
    print(f"Logging in as {EMAIL}...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        
        if response.status_code == 200:
            print("Login successful!")
            data = response.json()
            return data["session"]["access_token"]
        else:
            print(f"Login failed: {response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Login error: {e}")
        sys.exit(1)

def get_me(token):
    print("\nFetching current user info...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            data = response.json()
            if "avatar_url" in data:
                print("\n✅ SUCCESS: avatar_url is present!")
            else:
                print("\n❌ FAILURE: avatar_url is MISSING!")
        
    except Exception as e:
        print(f"Error fetching user info: {e}")

if __name__ == "__main__":
    token = login()
    get_me(token)
