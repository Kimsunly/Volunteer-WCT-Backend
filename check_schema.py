
import os
from app.database import get_supabase

def check_schema():
    supabase = get_supabase()
    print("Checking 'opportunities' table columns...")
    try:
        # We can't directly query information_schema via supabase-py client usually, 
        # but we can try to select * limit 1 and look at keys.
        response = supabase.table("opportunities").select("*").limit(1).execute()
        if response.data:
            print("Columns found in a record:")
            print(list(response.data[0].keys()))
        else:
            print("No data in table, cannot infer columns from valid row.")
            # Try inserting a dummy row with just required fields? No, might violate constraints.
            # Try selecting a column we suspect is missing
            try:
                print("Testing 'status' column...")
                supabase.table("opportunities").select("status").limit(1).execute()
                print("✅ 'status' column exists.")
            except Exception as e:
                print(f"❌ 'status' column check failed: {e}")

            try:
                print("Testing 'title_en' column...")
                supabase.table("opportunities").select("title_en").limit(1).execute()
                print("✅ 'title_en' column exists.")
            except Exception as e:
                print(f"❌ 'title_en' column check failed: {e}")

    except Exception as e:
        print(f"Error checking schema: {e}")

if __name__ == "__main__":
    check_schema()
