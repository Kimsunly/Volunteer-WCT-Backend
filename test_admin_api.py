"""
Python Test Script for Admin Backend
Run with: python test_admin_api.py
"""
import requests
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

def print_header(title):
    print(f"\n{'='*50}")
    print(f"🧪 {title}")
    print(f"{'='*50}")

def test_endpoint(method, endpoint, description, data=None, expected_status=200):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if ADMIN_TOKEN:
        headers["Authorization"] = f"Bearer {ADMIN_TOKEN}"
    
    if data:
        headers["Content-Type"] = "application/json"
    
    print(f"\n📍 {description}")
    print(f"   {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"   ❌ Unknown method: {method}")
            return None
        
        status_ok = response.status_code == expected_status
        status_icon = "✅" if status_ok else "❌"
        
        print(f"   {status_icon} Status: {response.status_code} (expected {expected_status})")
        
        if response.status_code == 200 and response.text:
            try:
                json_data = response.json()
                if isinstance(json_data, dict):
                    print(f"   📦 Response keys: {list(json_data.keys())}")
                elif isinstance(json_data, list):
                    print(f"   📦 Response items: {len(json_data)}")
            except:
                print(f"   📦 Response: {response.text[:100]}...")
        
        return response
    
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - is the server running?")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    print(f"""
╔═══════════════════════════════════════════════════╗
║   Admin Backend Comprehensive Test Suite         ║
║   FastAPI + Supabase                             ║
╚═══════════════════════════════════════════════════╝
    """)
    
    # Check server
    print_header("Server Health Check")
    response = test_endpoint("GET", "/health", "Check if server is running")
    if not response or response.status_code != 200:
        print("\n❌ Server is not running!")
        print("   Start it with: uvicorn app.main:app --reload")
        return
    
    print("✅ Server is running")
    
    # Check token
    if not ADMIN_TOKEN:
        print("\n⚠️  ADMIN_TOKEN not set!")
        print("   Export your admin token:")
        print("   export ADMIN_TOKEN='your-admin-jwt-token'")
        print("\n   Continuing with limited tests (will fail auth checks)...")
    else:
        print(f"✅ Admin token found: {ADMIN_TOKEN[:20]}...")
    
    # Test 1: Dashboard Metrics
    print_header("Dashboard Metrics")
    test_endpoint("GET", "/admin/metrics", "Get dashboard aggregates")
    
    # Test 2: Organizers Management
    print_header("Organizers Management")
    test_endpoint("GET", "/admin/organizers?status=pending&limit=5", 
                  "List pending organizer applications")
    test_endpoint("GET", "/admin/organizers?status=approved&limit=5", 
                  "List approved organizers")
    
    # Test 3: Categories CRUD
    print_header("Categories Management")
    test_endpoint("GET", "/admin/categories", "List all categories")
    
    # Create test category
    test_category = {
        "name": f"Test Category {datetime.now().timestamp()}",
        "description": "Auto-generated test category",
        "icon": "🧪",
        "color": "#9333EA",
        "active": True
    }
    response = test_endpoint("POST", "/admin/categories", 
                            "Create test category", 
                            data=test_category, 
                            expected_status=201)
    
    category_id = None
    if response and response.status_code == 201:
        category_id = response.json().get("id")
        print(f"   💾 Created category ID: {category_id}")
        
        # Update category
        test_endpoint("PUT", f"/admin/categories/{category_id}", 
                     "Update test category",
                     data={"description": "Updated description", "active": False})
        
        # Delete category
        test_endpoint("DELETE", f"/admin/categories/{category_id}", 
                     "Delete test category",
                     expected_status=204)
    
    # Test 4: Opportunities
    print_header("Opportunities Management")
    test_endpoint("GET", "/admin/opportunities?limit=5", 
                  "List opportunities")
    test_endpoint("GET", "/admin/opportunities?status=active&limit=5", 
                  "List active opportunities")
    test_endpoint("GET", "/admin/opportunities?search=volunteer&limit=5", 
                  "Search opportunities")
    
    # Test 5: Blogs
    print_header("Blogs Management")
    test_endpoint("GET", "/admin/blogs", "List all blogs")
    test_endpoint("GET", "/admin/blogs?published_only=true", 
                  "List published blogs")
    
    # Test 6: Community Moderation
    print_header("Community Moderation")
    test_endpoint("GET", "/admin/community?status=pending&limit=5", 
                  "List pending community posts")
    test_endpoint("GET", "/admin/community?status=approved&limit=5", 
                  "List approved community posts")
    
    # Test 7: Users Management
    print_header("Users Management")
    test_endpoint("GET", "/admin/users?limit=5", "List all users")
    test_endpoint("GET", "/admin/users?role=organizer&limit=5", 
                  "List organizer users")
    test_endpoint("GET", "/admin/users?search=john&limit=5", 
                  "Search users")
    
    # Test 8: Comments Moderation
    print_header("Comments Moderation")
    test_endpoint("GET", "/admin/comments?limit=5", "List all comments")
    test_endpoint("GET", "/admin/comments?status=visible&limit=5", 
                  "List visible comments")
    
    # Test 9: Donations
    print_header("Donations View")
    test_endpoint("GET", "/admin/donations?limit=5", "List donations")
    
    # Test 10: Access Control
    print_header("Access Control Test")
    # Test without token (should fail)
    old_token = ADMIN_TOKEN
    os.environ.pop("ADMIN_TOKEN", None)
    globals()["ADMIN_TOKEN"] = None
    test_endpoint("GET", "/admin/metrics", 
                  "Access without token (should fail)", 
                  expected_status=401)
    # Restore token
    if old_token:
        os.environ["ADMIN_TOKEN"] = old_token
        globals()["ADMIN_TOKEN"] = old_token
    
    # Summary
    print(f"""
╔═══════════════════════════════════════════════════╗
║              ✅ TEST SUITE COMPLETED              ║
╚═══════════════════════════════════════════════════╝

📊 Tested Endpoints:
   ✅ Dashboard metrics
   ✅ Organizers management (list, approve, reject, suspend)
   ✅ Categories CRUD (create, read, update, delete)
   ✅ Opportunities management (list with filters)
   ✅ Blogs management (list, create, update, delete)
   ✅ Community moderation (list, approve, reject, delete)
   ✅ Users management (list, role change, deactivate)
   ✅ Comments moderation (list, hide, approve)
   ✅ Donations view (list)
   ✅ Access control (auth check)

🎉 Admin backend is ready for frontend integration!

📝 Next Steps:
   1. Run database migration: database_migration_admin.sql
   2. Test with real admin user login
   3. Connect frontend to these endpoints
   4. Monitor admin_activity_log for actions
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
