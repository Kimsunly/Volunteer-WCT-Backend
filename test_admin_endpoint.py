"""Direct test of /admin/users endpoint with real token"""
import requests
import sys

# Read token from file
try:
    with open('token.txt', 'r', encoding='utf-8') as f:
        token = f.read().strip()
    print(f"Using token from token.txt (length: {len(token)})")
except:
    print("Error: token.txt not found!")
    sys.exit(1)

# Test the endpoint
print("\nTesting /admin/users endpoint...")
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(
        "http://127.0.0.1:8000/admin/users",
        headers=headers,
        params={"limit": 5, "offset": 0},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
except requests.exceptions.Timeout:
    print("ERROR: Request timed out - server might be frozen")
except requests.exceptions.ConnectionError as e:
    print(f"ERROR: Connection failed - {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
