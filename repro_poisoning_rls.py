import requests
import time

BASE_URL = "http://127.0.0.1:8000"
USER_EMAIL = "NexZin@gmail.com"
USER_PASS = "Hi@12345"

def test_poisoning():
    print("1. Logging in user...")
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": USER_EMAIL, "password": USER_PASS})
    if r.status_code != 200:
        print("Login failed:", r.text)
        return
    token = r.json().get('access_token') or r.json().get('session', {}).get('access_token')
    
    print("2. Attempting to apply to an opportunity...")
    # We'll use a known opportunity ID or just try a random one and check the error type
    # If it's a permission denied (42501), it's RLS.
    # If it's 404, it might still be RLS (if it can't see the opportunity).
    # But the user reported "permission denied" (42501).
    
    # First, let's find an opportunity
    opp_r = requests.get(f"{BASE_URL}/api/opportunities?limit=1")
    opps = opp_r.json().get('data', [])
    if not opps:
        print("No opportunities found to test with.")
        return
    opp_id = opps[0]['id']
    print(f"Testing with opportunity ID: {opp_id}")

    payload = {
        "opportunity_id": opp_id,
        "name": "Repro Test",
        "email": USER_EMAIL,
        "phone_number": "012345678",
        "sex": "male",
        "skills": "debugging",
        "availability": "now",
        "message": "Testing poisoning"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{BASE_URL}/api/applications/", json=payload, headers=headers)
    
    print(f"Status Code: {r.status_code}")
    print(f"Response Body: {r.text}")
    
    if r.status_code == 500 and "permission denied" in r.text.lower():
        print("\nFAILURE REPRODUCED: Permission Denied (42501) detected!")
    elif r.status_code == 201:
        print("\nSUCCESS: Application created. No poisoning detected.")
    else:
        print(f"\nUNEXPECTED RESULT: {r.status_code}")

if __name__ == "__main__":
    test_poisoning()
