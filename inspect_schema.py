
import os
import sys
sys.path.append(os.getcwd())

from app.database import get_supabase
from dotenv import load_dotenv

load_dotenv()

def inspect_applications():
    print("Inspecting 'applications' table...")
    try:
        supabase = get_supabase()
        # Fetch one row to see columns
        res = supabase.table("applications").select("*").limit(1).execute()
        if res.data:
            print("Columns:", res.data[0].keys())
        else:
            print("No data found in 'applications' to inspect columns.")
            # Try to query pg_attribute if possible (unlikely via Postgrest)
            print("Trying to fetch from opportunities to verify connection...")
            opp_res = supabase.table("opportunities").select("*").limit(1).execute()
            if opp_res.data:
                print("Opportunities columns:", opp_res.data[0].keys())
    except Exception as e:
        print("Inspection failed:", e)

if __name__ == "__main__":
    inspect_applications()
