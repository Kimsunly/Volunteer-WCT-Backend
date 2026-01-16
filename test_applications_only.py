import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
USER_EMAIL = "NexZin@gmail.com"
USER_PASS = "Hi@12345"
ORG_EMAIL = "KhmerChild@gmail.com"
ORG_PASS = "Hi@12345"

def run_test():
    print("=== TESTING APPLICATION SUBMISSION (RLS DEBUG) ===")
    
    # 1. Login Organization
    print("Logging in Organizer...")
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": ORG_EMAIL, "password": ORG_PASS})
    if r.status_code != 200:
        print(f"Organizer login failed: {r.text}")
        return
    org_token = r.json()['session']['access_token']
    
    # 2. Create Opportunity
    print("Creating Opportunity...")
    opp_data = {
        "title": f"Test Application RLS {int(time.time())}",
        "category_label": "Education",
        "location_label": "Test Loc",
        "description": "Test Desc",
        "is_private": "false"
    }
    r = requests.post(f"{BASE_URL}/api/opportunities/", headers={"Authorization": f"Bearer {org_token}"}, json=opp_data)
    # The endpoint might expect form data or json, attempting json first based on previous knowledge
    if r.status_code not in [200, 201]:
         # Try form data
         r = requests.post(f"{BASE_URL}/api/opportunities/", headers={"Authorization": f"Bearer {org_token}"}, data=opp_data)
    
    if r.status_code not in [200, 201]:
        print(f"Create Opportunity failed: {r.text}")
        return
        
    opp_id = r.json()['id']
    print(f"Opportunity Created: {opp_id}")

    # 3. Login User
    print("Logging in User...")
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": USER_EMAIL, "password": USER_PASS})
    if r.status_code != 200:
        print(f"User login failed: {r.text}")
        return
    user_token = r.json()['session']['access_token']
    
    # 4. Apply to Opportunity
    print("Applying to Opportunity...")
    app_data = {
        "opportunity_id": opp_id,
        "name": "Nex Zin",
        "email": USER_EMAIL,
        "phone_number": "012345678",
        "message": "Let me in!",
        "skills": "Coding, Testing",
        "availability": "Weekends",
        "sex": "male"
    }
    r = requests.post(f"{BASE_URL}/api/applications/", headers={"Authorization": f"Bearer {user_token}"}, json=app_data)
    
    print(f"Application Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    run_test()
