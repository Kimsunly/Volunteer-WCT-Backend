"""
Comprehensive Test Suite for 13 Scopes - VERSION 3 (Specific Accounts)
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# User-Provided Credentials
ADMIN_EMAIL = "admin@volunteer.com"
ADMIN_PASS = "password123"
USER_EMAIL = "NexZin@gmail.com"
USER_PASS = "Hi@12345"
ORG_EMAIL = "KhmerChild@gmail.com"
ORG_PASS = "Hi@12345"

class TestSession:
    def __init__(self):
        self.tokens = {}
        self.results = []

    def log(self, scope, test, success, message="", response=None):
        res = "[PASS]" if success else "[FAIL]"
        detail = ""
        if not success and response is not None:
            try:
                detail = f" | Detail: {response.text}"
            except:
                detail = " | Detail: <could not read response>"
        msg = f"Scope {scope} - {test}: {res} {message}{detail}"
        print(msg)
        self.results.append(msg)

    def login(self, email, password):
        try:
            r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                # Handle different response structures if necessary
                if 'session' in data:
                    return data['session']['access_token']
                return data.get('access_token')
        except: pass
        return None

    def ensure_user(self, email, password, role="user"):
        token = self.login(email, password)
        if token:
            return token
        
        print(f"Account {email} not found or login failed. Attempting registration...")
        if role == "user":
            r = requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": email, "password": password,
                "first_name": "Nex", "last_name": "Zin", "phone": "012345678"
            })
        elif role == "organizer":
            r = requests.post(f"{BASE_URL}/api/organizer/register", json={
                "email": email, "password": password,
                "organization_name": "Khmer Child", "phone": "098765432", "organizer_type": "ngo"
            })
            # Admin Approval
            admin_token = self.login(ADMIN_EMAIL, ADMIN_PASS)
            if admin_token:
                time.sleep(1)
                r_list = requests.get(f"{BASE_URL}/admin/organizers?status=pending", headers={"Authorization": f"Bearer {admin_token}"})
                apps = r_list.json().get('data', [])
                target_app = next((a for a in apps if a['email'] == email), None)
                if target_app:
                    requests.post(f"{BASE_URL}/admin/organizers/{target_app['id']}/approve", headers={"Authorization": f"Bearer {admin_token}"})
                    print(f"Approved organizer {email}")
        
        return self.login(email, password)

    def run_tests(self):
        print("\n=== STARTING COMPREHENSIVE TESTS WITH SPECIFIC ACCOUNTS ===\n")
        
        # 1. Admin Login & Dashboard (Scope 12)
        admin_token = self.login(ADMIN_EMAIL, ADMIN_PASS)
        if admin_token:
            self.tokens['admin'] = admin_token
            r = requests.get(f"{BASE_URL}/admin/metrics", headers={"Authorization": f"Bearer {admin_token}"})
            self.log(12, "Admin Dashboard Metrics", r.status_code == 200, f"Status: {r.status_code}", response=r)
        else:
            self.log(12, "Admin Login", False, "Admin login failed. Check credentials.")
            return

        # 2. User Authentication (Scope 2, 1)
        user_token = self.ensure_user(USER_EMAIL, USER_PASS, "user")
        if user_token:
            self.tokens['user'] = user_token
            self.log(2, "User Login/Registration", True)
            r = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {user_token}"})
            self.log(1, "User Role Verification", r.json().get('role') == 'user', response=r)
        else:
            self.log(2, "User Login", False, "User login failed.")

        # 3. Organizer Authentication (Scope 3)
        org_token = self.ensure_user(ORG_EMAIL, ORG_PASS, "organizer")
        if org_token:
            self.tokens['organizer'] = org_token
            self.log(3, "Organizer Login/Registration", True)
            r = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {org_token}"})
            self.log(3, "Verified Organizer Role", r.json().get('role') == 'organizer', response=r)
        else:
            self.log(3, "Organizer Login", False, "Organizer login failed.")

        # 4. Admin Category CRUD (Scope 4)
        if 'admin' in self.tokens:
            cat_name = f"Cat_{int(time.time())}"
            r = requests.post(f"{BASE_URL}/admin/categories", headers={"Authorization": f"Bearer {self.tokens['admin']}"}, 
                             json={"name": cat_name, "description": "Test Category"})
            self.log(4, "Admin Create Category", r.status_code in [200, 201], response=r)

        # 5. Opportunity CRUD (Scope 5)
        if 'organizer' in self.tokens:
            org_token = self.tokens['organizer']
            opp_payload = {
                "title": f"Help Khmer Children {int(time.time())}",
                "category_label": "Education",
                "location_label": "Phnom Penh",
                "description": "Volunteers needed for teaching English and life skills.",
                "is_private": "false"
            }
            r = requests.post(f"{BASE_URL}/api/opportunities/", headers={"Authorization": f"Bearer {org_token}"}, 
                             data=opp_payload)
            opp_id = r.json().get('id') if r.status_code in [200, 201] else None
            self.log(5, "Organizer Create Public Opportunity", r.status_code in [200, 201], response=r)
            
            # Private Opp
            opp_payload["is_private"] = "true"
            opp_payload["title"] = f"Private Support Session {int(time.time())}"
            r = requests.post(f"{BASE_URL}/api/opportunities/", headers={"Authorization": f"Bearer {org_token}"}, 
                             data=opp_payload)
            resp_data = r.json() if r.status_code in [200, 201] else {}
            opp_priv_id = resp_data.get('id')
            opp_priv_key = resp_data.get('access_key')
            self.log(5, "Organizer Create Private Opportunity", r.status_code in [200, 201] and opp_priv_key is not None, response=r)

            # 6. Filters (Scope 6)
            r = requests.get(f"{BASE_URL}/api/opportunities?category=education")
            self.log(6, "Filter by Category", r.status_code == 200, response=r)

            # 8. Community Post (Scope 8)
            r = requests.post(f"{BASE_URL}/api/community", headers={"Authorization": f"Bearer {org_token}"},
                             json={
                                 "title": f"Community Discussion {int(time.time())}", 
                                 "content": "Share your thoughts on recent volunteer events.", 
                                 "category": "discussion"
                             })
            self.log(8, "Organizer Create Community Post", r.status_code in [200, 201], response=r)

            # 9. Private Registration (Scope 9)
            if opp_priv_id and opp_priv_key and 'user' in self.tokens:
                user_token = self.tokens['user']
                r = requests.post(f"{BASE_URL}/api/applications/", headers={"Authorization": f"Bearer {user_token}"},
                                 json={
                                     "opportunity_id": opp_priv_id,
                                     "access_key": opp_priv_key,
                                     "name": "Nex Zin",
                                     "email": USER_EMAIL,
                                     "phone_number": "012345678",
                                     "sex": "male",
                                     "skills": "communication",
                                     "availability": "weekends",
                                     "message": "Interested in the private session."
                                 })
                self.log(9, "Private Opportunity Registration", r.status_code in [200, 201], response=r)

            # 13. Detail & Public Registration (Scope 13)
            if opp_id and 'user' in self.tokens:
                r = requests.get(f"{BASE_URL}/api/opportunities/{opp_id}")
                self.log(13, "Opportunity Detail View", r.status_code == 200, response=r)
                
                r = requests.post(f"{BASE_URL}/api/applications/", headers={"Authorization": f"Bearer {self.tokens['user']}"},
                                 json={
                                     "opportunity_id": opp_id,
                                     "name": "Nex Zin",
                                     "email": USER_EMAIL,
                                     "phone_number": "012345678",
                                     "sex": "male",
                                     "skills": "teaching",
                                     "availability": "weekdays",
                                     "message": "Applying for the public opportunity."
                                 })
                self.log(13, "Public Opportunity Application", r.status_code in [200, 201], response=r)

            # 10. User View Registered (Scope 10)
            if 'user' in self.tokens:
                r = requests.get(f"{BASE_URL}/api/applications/my", headers={"Authorization": f"Bearer {self.tokens['user']}"})
                self.log(10, "User View Registered/Activities", r.status_code == 200, response=r)

            # 11. Organizer Dashboard (Scope 11)
            r = requests.get(f"{BASE_URL}/api/organizer/dashboard", headers={"Authorization": f"Bearer {org_token}"})
            self.log(11, "Organizer Dashboard", r.status_code == 200, response=r)

        # 7. Admin Tips (Scope 7)
        if 'admin' in self.tokens:
            r = requests.post(f"{BASE_URL}/admin/blogs", headers={"Authorization": f"Bearer {self.tokens['admin']}"},
                             json={
                                 "title": f"Tip for Volunteers {int(time.time())}", 
                                 "content": "Verify all details before traveling to the location.", 
                                 "category": "tips", 
                                 "published": True
                             })
            self.log(7, "Admin Create Tip (Blog)", r.status_code in [200, 201], response=r)

        print("\n=== COMPLETED TESTS ===\n")

if __name__ == "__main__":
    session = TestSession()
    session.run_tests()
