
from app.database import get_supabase

def check_structure():
    supabase = get_supabase()
    print("Checking 'user_activities' columns...")
    try:
        response = supabase.table("user_activities").select("*").limit(1).execute()
        if response.data:
            print("Row data:", response.data[0])
        else:
            print("Table found but empty.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_structure()
