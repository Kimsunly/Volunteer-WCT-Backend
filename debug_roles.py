"""
Check user roles and organizer status in the database
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def get_token(email, password):
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
    if r.status_code == 200:
        return r.json()['session']['access_token']
    return None

def check_me(token, label):
    r = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    print(f"Me ({label}): {r.status_code}")
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r.text)

admin_token = get_token("admin@volunteer.com", "password123")
organizer_token = get_token("KhmerChild@gmail.com", "Hi@12345")

if admin_token:
    check_me(admin_token, "Admin")
if organizer_token:
    check_me(organizer_token, "Organizer")

print("\nChecking organizer profile specifically...")
if organizer_token:
    # Try an endpoint that requires organizer profile
    r = requests.get(f"{BASE_URL}/api/opportunities/my-opportunities", headers={"Authorization": f"Bearer {organizer_token}"})
    print(f"My Opportunities: {r.status_code}")
    print(r.text)
