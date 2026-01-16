import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = "http://127.0.0.1:8000"
EMAIL = "NexZin@gmail.com"
PASSWORD = "Hi@12345"

def login():
    print(f"Logging in as {EMAIL}...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": EMAIL, "password": PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            if "session" in data and "access_token" in data["session"]:
                return data["session"]["access_token"]
            print("Login response missing session/token")
            return None
        else:
            print(f"Login failed: {response.text}")
            # Try registering if login fails
            return register()
    except Exception as e:
        print(f"Login error: {e}")
        return None

def register():
    print(f"Registering {EMAIL}...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": EMAIL, "password": PASSWORD, "first_name": "Dara", "last_name": "Ly"}
        )
        if response.status_code in (200, 201):
            data = response.json()
            if "session" in data and "access_token" in data["session"]:
                return data["session"]["access_token"]
            return None
        else:
            print(f"Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"Registration error: {e}")
        return None

def update_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Payload similar to frontend
    payload = {
        "first_name": "Dara",
        "last_name": "Ly",
        "phone": "012345678",
        "location": "Phnom Penh",
        "birth_date": "1990-01-01",
        "about_me": "Volunteer enthusiast",
        "skills": "Teaching, Coding",
        "availability": "weekend",
        "time_preference": "morning",
        "emergency_contact_name": "Mom",
        "emergency_contact_phone": "012999999",
        "address_street": "123 St",
        "address_city": "Phnom Penh",
        "address_district": "Daun Penh",
        "address_province": "Phnom Penh"
    }
    
    print("\nSending Update Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/user/profile",
            headers=headers,
            json=payload
        )
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        # Save to file for inspection
        with open("debug_profile_update_response.txt", "w", encoding="utf-8") as f:
            f.write(f"Status: {response.status_code}\n")
            f.write(f"Response:\n{response.text}\n")
        
        if response.status_code == 200:
            print("\n✅ Profile update successful!")
        else:
            print("\n❌ Profile update failed!")
    except Exception as e:
        print(f"Update error: {e}")

if __name__ == "__main__":
    token = login()
    if token:
        update_profile(token)
