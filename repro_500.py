from app.database import get_supabase
import json

supabase = get_supabase()
category = "wildlife"

print(f"Testing filter with category={category}")
try:
    query = supabase.table("opportunities").select("*")
    query = query.ilike("category_label", f"%{category}%")
    res = query.execute()
    print(f"Success! Data: {res.data}")
except Exception as e:
    print(f"Failed! Error: {e}")
    if hasattr(e, 'response'):
        print(f"Response: {e.response.text}")
