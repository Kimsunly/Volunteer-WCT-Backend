
import os
import sys
# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app.database import get_supabase
from dotenv import load_dotenv

load_dotenv()

def test_poisoning_fix():
    print("1. Testing insert with get_supabase()...")
    # This should get a fresh client with service_role privileges
    supabase = get_supabase()
    d = {'opportunity_id': 6, 'user_id': 'b2d1d230-6712-4f3b-8f0a-7e04f878f44d', 'name': 'Repro Clean'}
    try:
        # Should fail with FK violation but NOT permission denied
        res = supabase.table('applications').insert(d).execute()
        print("Success (unexpected):", res.data)
    except Exception as e:
        error_str = str(e).lower()
        if "permission denied" in error_str or "violates row-level security policy" in error_str:
            print("ERROR: Permission denied even when clean!")
            return
        elif "is not present in table \"users\"" in error_str:
            print("CONFIRMED: Client has service_role privileges (bypasses RLS).")
        else:
            print("Unexpected error:", e)
            return

    print("\n2. Simulating Login (trying to poison the singleton)...")
    try:
        user_email = "NexZin@gmail.com"
        user_pass = "Hi@12345"
        # Since get_supabase() returns a NEW client every time now, 
        # this login will ONLY affect the 'supabase_session' instance created here.
        supabase_session = get_supabase()
        auth_res = supabase_session.auth.sign_in_with_password({"email": user_email, "password": user_pass})
        print(f"Logged in as {user_email} on a specific client instance.")
    except Exception as e:
        print("Login failed:", e)
        return

    print("\n3. Testing subsequent get_supabase() call (should be clean)...")
    try:
        supabase_fresh = get_supabase()
        # This should STILL have service_role privileges because it's a fresh client
        # and doesn't share state with 'supabase_session'
        res = supabase_fresh.table('applications').insert(d).execute()
        print("Success (unexpected):", res.data)
    except Exception as e:
        error_str = str(e).lower()
        if "permission denied" in error_str or "violates row-level security policy" in error_str:
            print("FAILURE: Client is STILL poisoned! The singleton behavior persists.")
        elif "is not present in table \"users\"" in error_str:
            print("VICTORY: Fresh client is CLEAN and has service_role privileges.")
        else:
            print("Step 3 gave unexpected error:", e)

if __name__ == "__main__":
    test_poisoning_fix()
