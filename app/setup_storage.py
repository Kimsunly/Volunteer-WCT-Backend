"""
Setup and test script for Supabase Storage
Run this to verify your storage bucket is configured correctly
"""
import asyncio
from app.database import get_supabase
from app.config import settings

def check_storage_bucket():
    """Check if the opportunity-images bucket exists and is accessible"""
    print("🔍 Checking Supabase Storage configuration...")
    print(f"   Bucket name: {settings.STORAGE_OPPORTUNITY_BUCKET}")
    
    supabase = get_supabase()
    
    try:
        # Try to list buckets
        print("\n📦 Attempting to access storage buckets...")
        buckets = supabase.storage.list_buckets()
        
        print(f"✓ Found {len(buckets)} bucket(s)")
        
        # Check if our bucket exists
        bucket_names = [b.name for b in buckets]
        print(f"   Available buckets: {bucket_names}")
        
        if settings.STORAGE_OPPORTUNITY_BUCKET in bucket_names:
            print(f"\n✓ Bucket '{settings.STORAGE_OPPORTUNITY_BUCKET}' exists!")
            
            # Check bucket details
            for bucket in buckets:
                if bucket.name == settings.STORAGE_OPPORTUNITY_BUCKET:
                    print(f"   - Public: {bucket.public}")
                    print(f"   - ID: {bucket.id}")
            
            # Try to list files in the bucket
            try:
                files = supabase.storage.from_(settings.STORAGE_OPPORTUNITY_BUCKET).list()
                print(f"   - Contains {len(files)} file(s)/folder(s)")
            except Exception as e:
                print(f"   ⚠ Could not list files: {e}")
            
            return True
        else:
            print(f"\n❌ Bucket '{settings.STORAGE_OPPORTUNITY_BUCKET}' NOT found!")
            print("\n📝 To create the bucket:")
            print("   1. Go to your Supabase Dashboard")
            print("   2. Navigate to Storage")
            print("   3. Click 'Create a new bucket'")
            print(f"   4. Name it: {settings.STORAGE_OPPORTUNITY_BUCKET}")
            print("   5. Make it PUBLIC (for image URLs to work)")
            print("   6. Click 'Create bucket'")
            return False
            
    except Exception as e:
        print(f"\n❌ Error accessing storage: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your SUPABASE_URL and SUPABASE_KEY in .env")
        print("   2. Make sure you're using the service_role key (not anon key)")
        print("   3. Verify your Supabase project is active")
        return False


def create_storage_bucket():
    """Attempt to create the storage bucket"""
    print(f"\n🔨 Attempting to create bucket '{settings.STORAGE_OPPORTUNITY_BUCKET}'...")
    
    supabase = get_supabase()
    
    try:
        bucket = supabase.storage.create_bucket(
            settings.STORAGE_OPPORTUNITY_BUCKET,
            options={
                "public": True,  # Make bucket public for image URLs
                "file_size_limit": 5242880,  # 5MB
                "allowed_mime_types": ["image/jpeg", "image/png", "image/gif", "image/webp"]
            }
        )
        print(f"✓ Bucket created successfully!")
        print(f"   Name: {bucket.name}")
        return True
    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            print(f"✓ Bucket already exists!")
            return True
        else:
            print(f"❌ Failed to create bucket: {error_msg}")
            print("\n💡 You may need to create it manually in the Supabase Dashboard")
            return False


def print_summary():
    """Print setup summary"""
    print("\n" + "="*60)
    print("📋 SETUP SUMMARY")
    print("="*60)
    print(f"Supabase URL: {settings.SUPABASE_URL}")
    print(f"Bucket name: {settings.STORAGE_OPPORTUNITY_BUCKET}")
    print("\n✅ What's working:")
    print("   - FastAPI app with image upload endpoints")
    print("   - File validation (type, size)")
    print("   - Unique filename generation")
    print("   - Image URL storage in database")
    print("\n📝 API Endpoints available:")
    print("   POST   /api/opportunities/with-images")
    print("          Create opportunity with images in one request")
    print("\n   POST   /api/opportunities/{id}/upload-images")
    print("          Add images to existing opportunity")
    print("\n   DELETE /api/opportunities/{id}/images")
    print("          Delete specific image from opportunity")
    print("\n💡 Frontend integration tips:")
    print("   - Use FormData for file uploads")
    print("   - Set Content-Type: multipart/form-data")
    print("   - Include authentication token in headers")
    print("   - Max 5 images per upload, 5MB per file")
    print("="*60)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 SUPABASE STORAGE SETUP CHECKER")
    print("="*60)
    
    # Check if bucket exists
    exists = check_storage_bucket()
    
    # If not, try to create it
    if not exists:
        user_input = input("\n❓ Would you like to try creating the bucket automatically? (y/n): ")
        if user_input.lower() == 'y':
            create_storage_bucket()
            print("\n🔄 Checking again...")
            check_storage_bucket()
    
    # Print summary
    print_summary()
    
    print("\n✨ Setup check complete!")
