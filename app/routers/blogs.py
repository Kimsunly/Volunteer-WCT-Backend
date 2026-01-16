from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.database import get_supabase
from app.models.admin import BlogResponse

router = APIRouter(prefix="/api/blogs", tags=["Blogs"])

@router.get("", response_model=List[BlogResponse])
def list_public_blogs(
    category: Optional[str] = Query(None, description="Filter by category"),
    q: Optional[str] = Query(None, description="Search query")
):
    """
    GET /api/blogs
    List published blogs with optional filtering.
    """
    supabase = get_supabase()
    
    try:
        # Only show published blogs
        query = supabase.table("blogs").select("*").eq("published", True).order("created_at", desc=True)
        
        if category and category.lower() != 'all':
            query = query.ilike("category", f"%{category}%")
            
        if q:
            query = query.or_(f"title.ilike.%{q}%,content.ilike.%{q}%")
            
        response = query.execute()
        return response.data or []
        
    except Exception as e:
        print(f"ERROR: List public blogs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list blogs: {str(e)}"
        )

@router.get("/{blog_id}", response_model=BlogResponse)
def get_public_blog(blog_id: str):
    """
    GET /api/blogs/{blog_id}
    Get a single published blog by ID.
    """
    supabase = get_supabase()
    
    try:
        response = supabase.table("blogs").select("*").eq("id", blog_id).eq("published", True).single().execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found or not published"
            )
            
        return response.data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Get public blog error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch blog: {str(e)}"
        )
