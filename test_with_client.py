from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_application_creation():
    print("=== Testing Application Creation with Diagnostics ===")
    
    # 1. Login to get token
    print("\n1. Logging in...")
    login_res = client.post("/api/auth/login", json={"email": "NexZin@gmail.com", "password": "Hi@12345"})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.status_code} {login_res.text}")
        return
    
    data = login_res.json()
    token = data.get('access_token') or data.get('session', {}).get('access_token')
    print("Login successful.")

    # 2. Find an opportunity
    print("\n2. Fetching an opportunity...")
    opp_res = client.get("/api/opportunities?limit=1")
    opps = opp_res.json().get('data', [])
    if not opps:
        print("No opportunities found.")
        return
    opp_id = opps[0]['id']
    print(f"Using Opportunity ID: {opp_id}")

    # 3. Create application
    print("\n3. Creating application...")
    payload = {
        "opportunity_id": opp_id,
        "name": "Diagnostic Test",
        "email": "NexZin@gmail.com",
        "phone_number": "012345678",
        "sex": "male",
        "skills": "debugging",
        "availability": "immediately",
        "message": "Testing with TestClient diagnostics"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    app_res = client.post("/api/applications/", json=payload, headers=headers)
    
    print(f"Status Code: {app_res.status_code}")
    print(f"Response: {app_res.text}")
    
    if app_res.status_code == 500 and "permission denied" in app_res.text.lower():
        print("\nFAILURE REPRODUCED: Permission Denied (42501) detected!")
    elif app_res.status_code == 201:
        print("\nSUCCESS: Application created.")
    elif app_res.status_code == 400 and "already applied" in app_res.text.lower():
        print("\nINFO: Already applied, but that means it passed RLS check (or it's cached).")
    else:
        print(f"\nRESULT: {app_res.status_code}")

if __name__ == "__main__":
    test_application_creation()
