import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
SUPABASE_URL = os.getenv("SUPABASE_URL")
# WE USE THE ANON KEY HERE to simulate a frontend/direct user access
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5aWR4aXl0and4a25lcmRycHVhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc1Mzc4NzAsImV4cCI6MjA4MzExMzg3MH0.o9VPrR9ZOJ-sGbegEbik8hZYYFnl9HJOBXpZo5GFuDk") # Usually in .env

USER_EMAIL = "NexZin@gmail.com"
USER_PASS = "Hi@12345"

def test_rls():
    # 1. Login to get token
    print("Logging in...")
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": USER_EMAIL, "password": USER_PASS})
    token = r.json().get('access_token') or r.json().get('session', {}).get('access_token')
    
    # 2. Try to query applications directly via PostgREST
    print("\nQuerying 'applications' table directly via PostgREST (simulating user)...")
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {token}"
    }
    url = f"{SUPABASE_URL}/rest/v1/applications?select=*"
    r = requests.get(url, headers=headers)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print(f"Found {len(r.json())} applications.")
    else:
        print(f"Error: {r.text}")

    # 3. Try to insert directly
    print("\nInserting into 'applications' table directly via PostgREST...")
    # This should fail if RLS is on and no INSERT policy exists for users
    payload = {
        "opportunity_id": 1,
        "user_id": "b21d1d230-6712-4f3b-8f0a-7e04f878f44d", # Must match current user if RLS is strict
        "name": "Direct User Test"
    }
    r = requests.post(url, headers=headers, json=payload)
    print(f"Status: {r.status_code}")
    if r.status_code >= 400:
        print(f"Direct insert failed (expected if RLS is on): {r.text}")
    else:
        print("Direct insert SUCCEEDED!")

if __name__ == "__main__":
    test_rls()
