
import os
import sys
sys.path.append(os.getcwd())

from app.database import get_supabase
from dotenv import load_dotenv

load_dotenv()

def test_real_insert():
    print("Testing real insert into 'applications'...")
    supabase = get_supabase()
    
    # 1. Get real user and opportunity
    user_res = supabase.table("user_profiles").select("user_id").limit(1).execute()
    opp_res = supabase.table("opportunities").select("id").limit(1).execute()
    
    if not user_res.data or not opp_res.data:
        print("No user or opportunity found. Cannot test.")
        return
        
    user_id = user_res.data[0]['user_id']
    opp_id = opp_res.data[0]['id']
    
    print(f"Using user_id={user_id}, opp_id={opp_id}")
    
    # 2. Try insert with minimal columns (what we saw in inspect_schema)
    d = {
        'opportunity_id': opp_id, 
        'user_id': user_id, 
        'name': 'Repro Real',
        'status': 'pending'
    }
    
    try:
        res = supabase.table('applications').insert(d).execute()
        print("SUCCESS! Minimal insert worked.")
        # Cleanup
        if res.data:
            app_id = res.data[0]['id']
            supabase.table('applications').delete().eq('id', app_id).execute()
            print("Cleanup successful.")
    except Exception as e:
        print(f"Error with minimal insert: {e}")

    # 3. Try insert with ALL columns (including missing ones)
    d_all = d.copy()
    d_all.update({
        'skills': 'test',
        'availability': 'test',
        'message': 'test'
    })
    
    print("\nTesting insert with extra columns (skills, availability, message)...")
    try:
        res = supabase.table('applications').insert(d_all).execute()
        print("SUCCESS! Extra columns insert worked (Wait, what?)")
    except Exception as e:
        print(f"Error with extra columns: {e}")

if __name__ == "__main__":
    test_real_insert()
