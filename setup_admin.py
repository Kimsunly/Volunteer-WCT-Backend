import asyncio
from app.database import get_supabase
from gotrue.errors import AuthApiError

def setup_admin():
    supabase = get_supabase()
    email = "admin@volunteer.com"
    password = "password123"
    
    print(f"Setting up admin user {email}...")

    user_id = None

    # 1. Try to Register (if not exists)
    try:
        print("Attempting to create user in Auth...")
        res = supabase.auth.sign_up({
            "email": email, 
            "password": password
        })
        if res.user:
            user_id = res.user.id
            print(f"Created new Auth user: {user_id}")
        else:
            # If confusing response (e.g. confirm email needed), assume exists
            print("User creation response had no user object. Maybe confirmation pending?")
            
    except AuthApiError as e:
        if "User already registered" in str(e):
            print("User already registered in Auth.")
            # Login to get ID
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                user_id = res.user.id
                print(f"Logged in to get ID: {user_id}")
            except Exception as login_e:
                print(f"Login failed: {login_e}")
                # Try to fetch from user_profiles if we can't login (maybe password changed?)
                # We can't search auth.users directly.
                # But we can search user_profiles by email.
                pass
        else:
            print(f"Auth error: {e}")

    # 2. Upsert Profile with Admin Role
    # If we don't have user_id from auth, try to find it in profiles
    if not user_id:
        try:
            res = supabase.table("user_profiles").select("user_id").eq("email", email).execute()
            if res.data:
                user_id = res.data[0]['user_id']
                print(f"Found ID from user_profiles: {user_id}")
        except Exception as e:
            print(f"Error searching profile: {e}")

    if user_id:
        profile_data = {
            "user_id": user_id,
            "email": email,
            "role": "admin",
            "first_name": "System",
            "last_name": "Admin",
            "status": "active"
        }
        try:
            # Upsert
            res = supabase.table("user_profiles").upsert(profile_data).execute()
            print(f"Upserted Admin Profile: {res.data}")
        except Exception as e:
            print(f"Error upserting profile: {e}")
    else:
        print("FAILED: Could not determine user_id for admin.")

if __name__ == "__main__":
    setup_admin()
