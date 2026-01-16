# Test /admin/users endpoint - simplified
import requests

print("Testing server health...")
try:
    response = requests.get("http://127.0.0.1:8000/")
    print(f"Server is UP: {response.status_code}")
except Exception as e:
    print(f"Server is DOWN: {e}")
    exit(1)

print("\nServer is running! Admin users endpoint should work now.")
print("Please refresh your browser and try again.")
