
import os
import secrets
import string
from app.database import get_supabase

def debug_delete():
    supabase = get_supabase()
    print("DEBUG: Creating dummy opportunity...")
    
    # 1. Create dummy opportunity (we need a valid organizer_id, I'll try to find one or use one from recent opps)
    # Actually, if I can't find one, I'll fail. Let's try to fetch one.
    opp_res = supabase.table("opportunities").select("organizer_id").limit(1).execute()
    if not opp_res.data:
        print("No opportunities found to allow copying organizer_id. Cannot proceed easily.")
        return

    organizer_id = opp_res.data[0]['organizer_id']
    
    data = {
        "organizer_id": organizer_id,
        "title": f"DELETE_ME_{secrets.token_hex(4)}",
        "category_label": "Debug",
        "location_label": "Debug",
        "is_private": False
    }
    
    try:
        res = supabase.table("opportunities").insert(data).execute()
        opp_id = res.data[0]['id']
        print(f"DEBUG: Created opportunity {opp_id}")
    except Exception as e:
        print(f"Failed to create opp: {e}")
        return

    # 2. Create dummy application
    print("DEBUG: Creating dummy application...")
    # Need a user_id. Fetch one.
    user_res = supabase.table("user_profiles").select("user_id").limit(1).execute()
    if not user_res.data:
        print("No users found.")
        return
    user_id = user_res.data[0]['user_id']
    
    app_data = {
        "opportunity_id": opp_id,
        "user_id": user_id,
        "name": "Debug User",
        "status": "pending"
    }
    
    try:
        app_res = supabase.table("applications").insert(app_data).execute()
        app_id = app_res.data[0]['id']
        print(f"DEBUG: Created application {app_id}")
    except Exception as e:
        print(f"Failed to create app: {e}")
        # Clean up opp?
        return

    # 3. Approve application (to potentially trigger 'user_activities' creation if that's the link)
    print("DEBUG: Approving application...")
    try:
        supabase.table("applications").update({"status": "approved"}).eq("id", app_id).execute()
        print("DEBUG: Approved.")
    except Exception as e:
        print(f"Failed to approve app: {e}")

    # 4. Try to delete opportunity (which should cascade fail or we catch it)
    print("DEBUG: Attempting to delete opportunity...")
    try:
        # First naive delete (without manual cleanup) to catch the error
        supabase.table("opportunities").delete().eq("id", opp_id).execute()
        print("SUCCESS: Deleted opportunity without manual cleanup (unexpected based on user report).")
    except Exception as e:
        print(f"\n❌ CAUGHT ERROR DURING DELETION:\n{e}\n")
    
    # Clean up manually if still exists
    # ...

if __name__ == "__main__":
    debug_delete()
