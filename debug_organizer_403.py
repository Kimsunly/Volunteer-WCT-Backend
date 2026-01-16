"""
Debug Organizer 403 for specific account
"""
import requests

BASE_URL = "http://127.0.0.1:8000"
EMAIL = "KhmerChild@gmail.com"
PASS = "Password123"

def debug():
    print(f"Checking account: {EMAIL}")
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": EMAIL, "password": PASS})
    if r.status_code != 200:
        print(f"Login failed: {r.text}")
        return
    
    token = r.json()['session']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check /me
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"/api/auth/me: {r.status_code} - {r.text}")
    
    # Check if they can create opportunity
    r = requests.post(f"{BASE_URL}/api/opportunities/", headers=headers, data={
        "title": "Debug Opp",
        "category_label": "Education",
        "location_label": "Phnom Penh",
        "description": "Debug",
        "is_private": "false"
    })
    print(f"Create Opportunity: {r.status_code} - {r.text}")

if __name__ == "__main__":
    debug()
