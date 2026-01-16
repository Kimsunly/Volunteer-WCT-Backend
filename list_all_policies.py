
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

from app.config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def list_policies():
    print(f"Checking policies for 'applications' table...")
    
    # We can try to query information_schema or pg_policies
    # But service_role might not have access to pg_catalog via Postgrest
    # However, we can try to use a raw query if we had an SQL endpoint.
    # Since we don't, we'll try to use the 'check_schema' tricks.
    
    # Let's try to see if there are any RPC functions that can help
    try:
        # This is a shot in the dark, but some projects have an 'exec_sql' rpc for admins
        res = supabase.rpc('exec_sql', {'sql': 'SELECT * FROM pg_policies WHERE tablename = \'applications\''}).execute()
        print("Policies via RPC:", res.data)
    except Exception as e:
        print("RPC 'exec_sql' failed (expected if not exists):", e)

    # Let's try to use the REST API to get schema info if possible
    # Actually, let's just try to do an insert with a user token and see if it fails differently.
    
    # One thing: maybe the table has a TRIGGER that fails? 
    # But the error says "violates row-level security policy". That's very specific to RLS.

    print("\nAttempting to query pg_policies via standard table select (might fail)...")
    try:
        # Sometimes pg_policies is exposed if the user has been naughty with permissions
        res = supabase.table('pg_policies').select('*').eq('tablename', 'applications').execute()
        print("Policies via table select:", res.data)
    except Exception as e:
        print("Table select 'pg_policies' failed:", e)

if __name__ == "__main__":
    list_policies()
