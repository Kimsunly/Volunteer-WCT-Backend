
from app.database import get_supabase

def list_tables():
    supabase = get_supabase()
    print("Listing all tables...")
    try:
        # We can't query information_schema.tables directly with postgrest-py easily without setup.
        # But we can try to access a known table and maybe we can't 'list tables' via API directly.
        # However, we can use the 'users.py' logic which queries 'user_activities'.
        # Let's try to query 'user_activities' directly.
        try:
            resp = supabase.table("user_activities").select("*").limit(1).execute()
            print("✅ 'user_activities' table exists.")
            if resp.data:
                print("Columns:", list(resp.data[0].keys()))
            else:
                print("Table empty, checking columns via error or assumption.")
                # Try to insert dummy to see constraints? No.
        except Exception as e:
            print(f"❌ 'user_activities' query error: {e}")

        # Also check 'notifications'
        try:
            resp = supabase.table("notifications").select("*").limit(1).execute()
            print("✅ 'notifications' table exists.")
        except Exception as e:
            print(f"❌ 'notifications' query error: {e}")

    except Exception as e:
        print(f"General error: {e}")

if __name__ == "__main__":
    list_tables()
