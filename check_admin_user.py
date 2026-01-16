import asyncio
from app.database import get_supabase

def check_admin():
    supabase = get_supabase()
    email = "admin@volunteer.com"
    
    # 1. Check Auth (approximated by checking public.users if synced, or just profiles)
    # Supabase Auth 'users' table is in 'auth' schema, not accessible via client usually.
    # We check 'public.user_profiles' or 'public.users' depending on schema.
    
    print(f"Checking for {email}...")
    
    # Try to find in user_profiles by email if that column exists, or query all and filter?
    # Better: Try to login? No, I want to check DB state.
    
    # Let's check 'users' table (custom table) or 'user_profiles'
    try:
        # Assuming 'users' table or similar maps to auth
        res = supabase.table("users").select("*").eq("email", email).execute()
        print("Users table result:", res.data)
        
        if not res.data:
            print("User not found in 'public.users'.")
        else:
            user = res.data[0]
            print(f"User found: ID={user.get('id')}, Role={user.get('role')}")
            
    except Exception as e:
        print(f"Error checking users table: {e}")

if __name__ == "__main__":
    check_admin()
