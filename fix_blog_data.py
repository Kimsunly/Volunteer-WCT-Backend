from app.database import get_supabase
import asyncio

def fix_blog_data():
    supabase = get_supabase()
    print("Fixing blog data...")
    
    try:
        # Fetch all blogs
        response = supabase.table("blogs").select("*").execute()
        blogs = response.data
        
        count = 0
        for blog in blogs:
            updates = {}
            
            # Check for bad image
            if blog.get("image") == "string" or not blog.get("image"):
                updates["image"] = "/images/opportunities/Education/card-8/img-2.png"
                
            # Check for bad category
            if blog.get("category") == "string" or not blog.get("category"):
                updates["category"] = "General"
                
            if updates:
                print(f"Updating blog {blog['id']}: {updates}")
                supabase.table("blogs").update(updates).eq("id", blog['id']).execute()
                count += 1
                
        print(f"Fixed {count} blogs.")
        
    except Exception as e:
        print(f"Error fixing blogs: {e}")

if __name__ == "__main__":
    fix_blog_data()
