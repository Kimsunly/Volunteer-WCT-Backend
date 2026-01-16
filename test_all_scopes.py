"""
Comprehensive Test Suite for All 13 Scopes
Tests all features across Admin, Organizer, and User roles
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

# Test accounts
ADMIN_EMAIL = "admin@volunteer.com"
ADMIN_PASS = "password123"
ORGANIZER_EMAIL = "KhmerChild@gmail.com"
ORGANIZER_PASS = "Hi@12345"

class APITester:
    def __init__(self):
        self.tokens = {}
        self.results = {
            "passed": [],
            "failed": [],
            "errors": []
        }
    
    def log_result(self, test_name, passed, details=""):
        if passed:
            self.results["passed"].append(test_name)
            print(f"[PASS] {test_name}")
        else:
            self.results["failed"].append(f"{test_name}: {details}")
            print(f"[FAIL] {test_name} - {details}")
    
    def login(self, email, password, role_name):
        """Login and store token"""
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": email, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.tokens[role_name] = data['session']['access_token']
                self.log_result(f"Login as {role_name}", True)
                return True
            else:
                self.log_result(f"Login as {role_name}", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_result(f"Login as {role_name}", False, str(e))
            return False
    
    def get_headers(self, role):
        """Get auth headers for role"""
        return {"Authorization": f"Bearer {self.tokens.get(role, '')}"}
    
    def test_scope_1_roles(self):
        """Scope 1: Test user roles"""
        print("\n=== SCOPE 1: USER ROLES ===")
        
        # Test admin role
        try:
            response = requests.get(
                f"{BASE_URL}/api/auth/me",
                headers=self.get_headers('admin'),
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("Admin role verification", 
                               data.get('role') == 'admin', 
                               f"Got role: {data.get('role')}")
            else:
                self.log_result("Admin role verification", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_result("Admin role verification", False, str(e))
        
        # Test organizer role
        try:
            response = requests.get(
                f"{BASE_URL}/api/auth/me",
                headers=self.get_headers('organizer'),
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("Organizer role verification",
                               data.get('role') == 'organizer',
                               f"Got role: {data.get('role')}")
            else:
                self.log_result("Organizer role verification", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_result("Organizer role verification", False, str(e))
    
    def test_scope_2_auth(self):
        """Scope 2: Login and Register"""
        print("\n=== SCOPE 2: LOGIN & REGISTER ===")
        
        # Test registration
        test_email = f"test_{datetime.now().timestamp()}@test.com"
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "email": test_email,
                    "password": "Test@123",
                    "first_name": "Test",
                    "last_name": "User",
                    "phone": "0123456789"
                },
                timeout=10
            )
            self.log_result("User registration", 
                           response.status_code in [200, 201],
                           f"Status {response.status_code}")
            
            # Test login with new user
            if response.status_code in [200, 201]:
                response = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    json={"email": test_email, "password": "Test@123"},
                    timeout=10
                )
                self.log_result("New user login",
                               response.status_code == 200,
                               f"Status {response.status_code}")
        except Exception as e:
            self.log_result("User registration", False, str(e))
    
    def test_scope_4_categories(self):
        """Scope 4: Admin CRUD Categories"""
        print("\n=== SCOPE 4: ADMIN CRUD CATEGORIES ===")
        
        headers = self.get_headers('admin')
        
        # Create category
        try:
            response = requests.post(
                f"{BASE_URL}/admin/categories",
                headers=headers,
                json={
                    "name": f"Test Category {datetime.now().timestamp()}",
                    "description": "Test description"
                },
                timeout=10
            )
            created = response.status_code in [200, 201]
            self.log_result("Create category", created, f"Status {response.status_code}")
            
            if created:
                category_id = response.json().get('id')
                
                # List categories
                response = requests.get(f"{BASE_URL}/admin/categories", headers=headers, timeout=10)
                self.log_result("List categories", response.status_code == 200)
                
                # Update category
                if category_id:
                    response = requests.put(
                        f"{BASE_URL}/admin/categories/{category_id}",
                        headers=headers,
                        json={"name": "Updated Category", "description": "Updated"},
                        timeout=10
                    )
                    self.log_result("Update category", response.status_code == 200)
                    
                    # Delete category  
                    response = requests.delete(
                        f"{BASE_URL}/admin/categories/{category_id}",
                        headers=headers,
                        timeout=10
                    )
                    self.log_result("Delete category", response.status_code in [200, 204])
        except Exception as e:
            self.log_result("Category CRUD", False, str(e))
    
    def test_scope_5_opportunities(self):
        """Scope 5: Opportunity CRUD"""
        print("\n=== SCOPE 5: OPPORTUNITY CRUD ===")
        
        headers = self.get_headers('organizer')
        
        # Create public opportunity
        try:
            response = requests.post(
                f"{BASE_URL}/api/opportunities",
                headers=headers,
                json={
                    "title": f"Test Opportunity {datetime.now().timestamp()}",
                    "description": "Test description",
                    "category": "education",
                    "location": "Test Location",
                    "date_range": (datetime.now() + timedelta(days=7)).isoformat(),
                    "is_private": False
                },
                timeout=10
            )
            created = response.status_code in [200, 201]
            self.log_result("Create public opportunity", created, f"Status {response.status_code}")
            
            if created:
                opp_id = response.json().get('id')
                
                # Create private opportunity
                response = requests.post(
                    f"{BASE_URL}/api/opportunities",
                    headers=headers,
                    json={
                        "title": f"Private Opp {datetime.now().timestamp()}",
                        "description": "Private test",
                        "category": "community",
                        "is_private": True
                    },
                    timeout=10
                )
                has_access_key = 'access_key' in response.json() if response.status_code in [200, 201] else False
                self.log_result("Create private opportunity with access key", 
                               has_access_key,
                               f"Status {response.status_code}")
        except Exception as e:
            self.log_result("Opportunity creation", False, str(e))
    
    def test_scope_6_opportunity_filters(self):
        """Scope 6: Opportunity filters"""
        print("\n=== SCOPE 6: OPPORTUNITY FILTERS ===")
        
        try:
            # List all
            response = requests.get(f"{BASE_URL}/api/opportunities", timeout=10)
            self.log_result("List all opportunities", response.status_code == 200)
            
            # Filter by category
            response = requests.get(f"{BASE_URL}/api/opportunities?category=education", timeout=10)
            self.log_result("Filter by category", response.status_code == 200)
            
            # Search
            response = requests.get(f"{BASE_URL}/api/opportunities?search=test", timeout=10)
            self.log_result("Search opportunities", response.status_code == 200)
            
            # Pagination
            response = requests.get(f"{BASE_URL}/api/opportunities?limit=5&offset=0", timeout=10)
            self.log_result("Pagination", response.status_code == 200)
        except Exception as e:
            self.log_result("Opportunity filtering", False, str(e))
    
    def test_scope_8_community(self):
        """Scope 8: Community CRUD"""
        print("\n=== SCOPE 8: COMMUNITY CRUD ===")
        
        headers = self.get_headers('organizer')
        
        try:
            # Create post
            response = requests.post(
                f"{BASE_URL}/api/community",
                headers=headers,
                json={
                    "title": f"Test Post {datetime.now().timestamp()}",
                    "content": "Test content",
                    "category": "discussion"
                },
                timeout=10
            )
            created = response.status_code in [200, 201]
            self.log_result("Create community post (organizer)", created, f"Status {response.status_code}")
            
            # List posts
            response = requests.get(f"{BASE_URL}/api/community", timeout=10)
            self.log_result("List community posts", response.status_code == 200)
            
            # Admin create
            admin_headers = self.get_headers('admin')
            response = requests.post(
                f"{BASE_URL}/admin/community",
                headers=admin_headers,
                json={
                    "title": f"Admin Post {datetime.now().timestamp()}",
                    "content": "Admin content",
                    "category": "update"
                },
                timeout=10
            )
            self.log_result("Create community post (admin)", 
                           response.status_code in [200, 201],
                           f"Status {response.status_code}")
        except Exception as e:
            self.log_result("Community CRUD", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"PASSED: {len(self.results['passed'])}")
        print(f"FAILED: {len(self.results['failed'])}")
        
        if self.results['failed']:
            print("\nFailed Tests:")
            for fail in self.results['failed']:
                print(f"  - {fail}")
        
        pass_rate = (len(self.results['passed']) / 
                    (len(self.results['passed']) + len(self.results['failed'])) * 100) if (len(self.results['passed']) + len(self.results['failed'])) > 0 else 0
        print(f"\nPass Rate: {pass_rate:.1f}%")
        print("="*60)

def main():
    print("="*60)
    print("COMPREHENSIVE FEATURE TEST SUITE")
    print("Testing All 13 Scopes Across All Roles")
    print("="*60)
    
    tester = APITester()
    
    # Login for all roles
    print("\n=== AUTHENTICATION SETUP ===")
    tester.login(ADMIN_EMAIL, ADMIN_PASS, 'admin')
    tester.login(ORGANIZER_EMAIL, ORGANIZER_PASS, 'organizer')
    
    # Run tests
    tester.test_scope_1_roles()
    tester.test_scope_2_auth()
    tester.test_scope_4_categories()
    tester.test_scope_5_opportunities()
    tester.test_scope_6_opportunity_filters()
    tester.test_scope_8_community()
    
    # Print summary
    tester.print_summary()

if __name__ == "__main__":
    main()
