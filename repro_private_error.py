
import os
import json
from app.database import get_supabase
from app.utils.security import hash_secret

def reproduce():
    supabase = get_supabase()
    
    # Mock data for a private opportunity
    data = {
        "organizer_id": 2, # Use a valid organizer ID
        "title": "Reproduction Test Private",
        "category_label": "Education",
        "location_label": "Phnom Penh",
        "description": "Test reproduction",
        "is_private": True,
        "access_key_hash": hash_secret("TESTKEY123")
    }
    
    try:
        print(f"Attempting to insert: {data}")
        res = supabase.table("opportunities").insert(data).execute()
        print(f"Success! Inserted row: {res.data[0]}")
    except Exception as e:
        print(f"FAILED with error: {e}")

if __name__ == "__main__":
    reproduce()
