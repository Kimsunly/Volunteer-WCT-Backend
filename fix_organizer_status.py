from app.database import get_supabase
import asyncio

def fix():
    client = get_supabase()
    
    # 1. Check for 'approved' status
    print("Checking for 'approved' status records...")
    res = client.table('organizer_applications').select('*').eq('status', 'approved').execute()
    
    count = len(res.data)
    print(f"Found {count} records with status='approved'.")
    
    if count > 0:
        print("Updating to 'verified'...")
        update = client.table('organizer_applications').update({'status': 'verified'}).eq('status', 'approved').execute()
        print(f"Updated: {len(update.data)} records.")
    else:
        print("No records to fix.")

if __name__ == "__main__":
    fix()
