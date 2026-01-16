
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hyidxiytjwxknerdrpua.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5aWR4aXl0and4a25lcmRycHVhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzUzNzg3MCwiZXhwIjoyMDgzMTEzODcwfQ.Fm1yVH9ZOJ-sGbegEbik8hZYYFnl9HJOBXpZo5GFuDk")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_insert():
    print(f"Testing insert into 'applications' table...")
    try:
        # Try to select first to see if it works
        res = supabase.table("applications").select("*").limit(1).execute()
        print(f"Select success: {res.data}")
        
        # Try to insert a dummy (it might fail due to FKs but let's see the error)
        # We need a valid opportunity_id and user_id if they are mandatory
        # Let's just try to insert an empty dict or something that will definitely fail schema validation
        # but check IF the error is 'permission denied' or 'null value violates not-null constraint'
        dummy_data = {"opportunity_id": 999999, "user_id": "00000000-0000-0000-0000-000000000000"}
        res = supabase.table("applications").insert(dummy_data).execute()
        print(f"Insert result: {res}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_insert()
