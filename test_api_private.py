
import httpx
import json

def test_create_private_opportunity():
    token = open("token.txt", "rb").read().decode("utf-16", errors="ignore").strip()
    
    url = "http://localhost:8000/api/opportunities/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # We use data instead of files for form fields in httpx if we want to simulate Form(...)
    data = {
        "title": "Test Private API",
        "category_label": "Environment",
        "location_label": "Phnom Penh",
        "is_private": "true",
    }
    
    try:
        print(f"Sending request to {url}...")
        response = httpx.post(url, data=data, headers=headers, timeout=30.0)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_create_private_opportunity()
