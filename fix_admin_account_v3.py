import asyncio
from app.database import get_supabase
from app.config import settings

def fix_admin_v3():
    supabase = get_supabase()
    email = "admin@volunteer.com"
    password = "password123"
    
    print(f"Fixing admin account {email} (v3)...")

    user_id = None
    
    # 1. Find User via List Users
    try:
        print("Listing users...")
        response = supabase.auth.admin.list_users()
        # FIX: The response might be the list itself or an object. 
        # based on error "list object has no attribute users", response IS the list.
        users = response 
        
        target_user = None
        for u in users:
            if hasattr(u, 'email') and u.email == email:
                target_user = u
                break
        
        if target_user:
            user_id = target_user.id
            print(f"Found Admin User ID: {user_id}")
            
            # 2. Update Password
            print("Updating password...")
            try:
                supabase.auth.admin.update_user_by_id(user_id, {"password": password})
                print("Password successfully updated.")
            except Exception as e:
                print(f"Failed to update password: {e}")
        else:
            print("Admin user NOT found in list. Attempting creation...")
            try:
                res = supabase.auth.admin.create_user({
                    "email": email,
                    "password": password,
                    "email_confirm": True
                })
                user_id = res.user.id
                print(f"Created Admin User: {user_id}")
            except Exception as create_e:
                print(f"Creation failed: {create_e}")

    except Exception as e:
        print(f"Error listing users: {e}")
        import traceback
        traceback.print_exc()

    # 3. Upsert Profile
    if user_id:
        print(f"Ensuring 'admin' in user_profiles for {user_id}...")
        try:
            profile_data = {
                "user_id": user_id,
                "email": email,
                "role": "admin",
                "first_name": "System",
                "last_name": "Admin",
                "status": "active"
            }
            supabase.table("user_profiles").upsert(profile_data).execute()
            print("Profile ensured.")
        except Exception as e:
            print(f"Error upserting profile: {e}")

if __name__ == "__main__":
    fix_admin_v3()
