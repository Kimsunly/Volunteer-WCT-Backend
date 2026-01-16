import asyncio
from app.database import get_supabase
from app.config import settings
from gotrue.errors import AuthApiError

def fix_admin():
    # Helper to get admin api client if possible, or just use the service role client which has admin privileges
    supabase = get_supabase()
    
    email = "admin@volunteer.com"
    password = "password123"
    
    print(f"Fixing admin account {email}...")

    user_id = None

    # 1. Check if user exists using Admin API (list_users)
    # The python client exposes admin methods via supabase.auth.admin
    try:
        # Note: list_users might rely on different methods depending on library version. 
        # Using list_users() generic approach.
        # Alternatively, we can just try to create and catch error.
        pass
    except Exception:
        pass

    # Method A: Try to Create (Admin API)
    # create_user(dict) -> User
    try:
        print("Attempting to create user via Admin API...")
        # options: email, password, email_confirm, user_metadata
        # supabase.auth.admin.create_user is the standard way for server-side
        result = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True
        })
        if result.user:
            user_id = result.user.id
            print(f"Created Admin User: {user_id}")
    except Exception as e:
        if "already registered" in str(e) or "already has been registered" in str(e):
            print("User already exists. Updating password...")
            try:
                # Find the user ID by listing or assume we can't search easily without ID.
                # Actually, Supabase Admin API usually needs ID to update.
                # Let's try to get ID via basic login first (easiest way if we don't want to iterate all users)
                # But if password is wrong, login fails.
                # We can use list_users() to find by email.
                users = supabase.auth.admin.list_users() # This returns a list of users
                # list_users returns an object with 'users' property usually
                
                target_user = None
                for u in users.users:
                    if u.email == email:
                        target_user = u
                        break
                
                if target_user:
                    user_id = target_user.id
                    print(f"Found User ID: {user_id}")
                    # Update password
                    supabase.auth.admin.update_user_by_id(user_id, {"password": password})
                    print("Password updated to 'password123'")
                else:
                    print("Could not find user in list even though create failed?!")
            except Exception as update_e:
                 print(f"Error updating user: {update_e}")
        else:
             print(f"Error creating user: {e}")

    # 2. Ensure Profile
    if user_id:
        print(f"Upserting Admin Profile for {user_id}...")
        try:
            profile_data = {
                "user_id": user_id,
                "email": email,
                "role": "admin",
                "first_name": "System",
                "last_name": "Admin",
                "status": "active"
            }
            res = supabase.table("user_profiles").upsert(profile_data).execute()
            print("Profile ensured.")
        except Exception as e:
            print(f"Error upserting profile: {e}")

if __name__ == "__main__":
    fix_admin()
