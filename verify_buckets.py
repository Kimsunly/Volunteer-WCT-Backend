from app.database import get_supabase
from app.config import settings

def verify_buckets():
    supabase = get_supabase()
    
    print("Checking storage buckets...")
    try:
        # Try as property first
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        print(f"Existing buckets: {bucket_names}")
        
        target_bucket = settings.STORAGE_AVATAR_BUCKET
        
        if target_bucket not in bucket_names:
            print(f"Bucket '{target_bucket}' not found. Attempting to create...")
            try:
                # Create public bucket
                supabase.storage().create_bucket(target_bucket, options={"public": True})
                print(f"Successfully created bucket '{target_bucket}'")
            except Exception as e:
                print(f"Failed to create bucket: {e}")
        else:
            print(f"Bucket '{target_bucket}' exists.")
            
            # Check if public
            try:
                # There isn't a direct "get_bucket" in some python client versions, 
                # but we can try to update it to ensure public or just assume it is.
                # listing buckets gives info
                for b in buckets:
                    if b.name == target_bucket:
                        print(f"Bucket info: Public={b.public}")
            except Exception as e:
                print(f"Could not inspect bucket details: {e}")

    except Exception as e:
        print(f"Error listing buckets: {e}")

if __name__ == "__main__":
    verify_buckets()
