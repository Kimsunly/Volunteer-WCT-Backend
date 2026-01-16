"""
Test script to verify community post creation endpoint
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_community_post_creation():
    print("=" * 60)
    print("Testing Community Post Creation")
    print("=" * 60)
    
    # Step 1: Login
    print("\n[1/3] Logging in as organizer...")
    login_data = {
        "email": "KhmerChild@gmail.com",
        "password": "Hi@12345"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    print(f"Login response status: {response.status_code}")
    print(f"Login response: {response.text}")
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return False
    
    login_result = response.json()
    print(f"Login result keys: {login_result.keys()}")
    
    # Try different possible token field names
    token = login_result.get("access_token") or login_result.get("token") or login_result.get("accessToken")
    
    if not token:
        print("❌ No access token received")
        return False
    
    print(f"✓ Login successful! Token: {token[:20]}...")
    
    # Step 2: Get organizer profile to verify
    print("\n[2/3] Fetching organizer profile...")
    headers = {"Authorization": f"Bearer {token}"}
    
    profile_response = requests.get(f"{BASE_URL}/api/organizer/profile", headers=headers)
    
    if profile_response.status_code != 200:
        print(f"❌ Failed to get profile: {profile_response.status_code}")
        print(f"Response: {profile_response.text}")
        return False
    
    profile = profile_response.json()
    print(f"✓ Profile retrieved: {profile.get('organization_name', 'N/A')}")
    print(f"  User ID: {profile.get('user_id', 'N/A')}")
    
    # Step 3: Create community post
    print("\n[3/3] Creating community post...")
    
    post_data = {
        "title": "Test Community Post - Verification",
        "content": "This is a test post created by the automated verification script to ensure the community post endpoint works correctly.",
        "category": "General"
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/community/",
        headers=headers,
        json=post_data
    )
    
    print(f"\nResponse Status: {create_response.status_code}")
    print(f"Response Headers: {dict(create_response.headers)}")
    
    if create_response.status_code == 201:
        print("✓ Community post created successfully!")
        result = create_response.json()
        print(f"\nCreated Post Details:")
        print(f"  ID: {result.get('id', 'N/A')}")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  Category: {result.get('category', 'N/A')}")
        print(f"  Organizer ID: {result.get('organizer_id', 'N/A')}")
        print("\n" + "=" * 60)
        print("✓ SUCCESS! Community post creation is working!")
        print("=" * 60)
        return True
    elif create_response.status_code == 422:
        print("❌ Validation error (422)!")
        print("\nValidation Error Details:")
        try:
            error_detail = create_response.json()
            print(json.dumps(error_detail, indent=2))
        except:
            print(create_response.text)
        return False
    else:
        print(f"❌ Failed: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return False

if __name__ == "__main__":
    try:
        success = test_community_post_creation()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
