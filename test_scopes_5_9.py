import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
USER_EMAIL = "NexZin@gmail.com"
USER_PASS = "Hi@12345"
ORG_EMAIL = "KhmerChild@gmail.com"
ORG_PASS = "Hi@12345"

def run_test():
    print("=== TESTING SCOPES 5 & 9 ===")
    
    # Login Organizer
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": ORG_EMAIL, "password": ORG_PASS})
    if r.status_code != 200:
        print(f"Org Login Fail: {r.text}")
        return
    org_token = r.json()['session']['access_token']
    
    # Login User
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": USER_EMAIL, "password": USER_PASS})
    if r.status_code != 200:
        print(f"User Login Fail: {r.text}")
        return
    user_token = r.json()['session']['access_token']


    # Scope 5: Organizer Create Public Opportunity
    print("Test Scope 5: Create Public Opp...")
    opp_data = {
        "title": f"Scope 5 Public Opp {int(time.time())}",
        "category_label": "Education",
        "location_label": "Test Loc",
        "description": "Public Desc",
        "is_private": "false"
    }
    r = requests.post(f"{BASE_URL}/api/opportunities/", headers={"Authorization": f"Bearer {org_token}"}, data=opp_data)
    if r.status_code not in [200, 201]:
        print(f"Scope 5 FAIL: {r.status_code} {r.text}")
    else:
        print(f"Scope 5 PASS: {r.json()['id']}")

    # Scope 9: Private Opportunity Registration
    print("Test Scope 9: Private Opp + Apply...")
    # 1. Create Private Opp
    priv_key = "secret123"
    opp_priv_data = {
        "title": f"Scope 9 Private Opp {int(time.time())}",
        "category_label": "Health",
        "location_label": "Test Priv",
        "description": "Private Desc",
        "is_private": "true",
        "access_key": priv_key
    }
    r = requests.post(f"{BASE_URL}/api/opportunities/", headers={"Authorization": f"Bearer {org_token}"}, data=opp_priv_data)
    if r.status_code not in [200, 201]:
        print(f"Create Private Opp FAIL: {r.status_code} {r.text}")
        return
    priv_id = r.json()['id']
    print(f"Private Opp Created: {priv_id}")

    # 2. Apply with key
    app_data = {
        "opportunity_id": priv_id,
        "access_key": priv_key,
        "name": "Nex Zin",
        "email": USER_EMAIL,
        "phone_number": "012345678",
        "sex": "male",
        "skills": "Secret skills",
        "availability": "Anytime",
        "message": "Let me in secret!"
    }
    r = requests.post(f"{BASE_URL}/api/applications/", headers={"Authorization": f"Bearer {user_token}"}, json=app_data)
    if r.status_code in [200, 201]:
        print(f"Scope 9 PASS: Application {r.json()['id']}")
    else:
        print(f"Scope 9 FAIL: {r.status_code} {r.text}")

if __name__ == "__main__":
    run_test()
