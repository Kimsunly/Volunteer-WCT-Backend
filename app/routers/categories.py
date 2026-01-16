from fastapi import APIRouter, HTTPException, status
from typing import List
from app.database import get_supabase
from app.models.admin import CategoryResponse

router = APIRouter(prefix="/api/categories", tags=["Categories"])

@router.get("/", response_model=List[CategoryResponse])
def list_public_categories():
    """
    GET /api/categories
    List all active categories for public/organizer usage.
    """
    supabase = get_supabase()
    
    try:
        response = supabase.table("categories")\
            .select("*")\
            .eq("active", True)\
            .order("name")\
            .execute()
            
        return response.data or []
        
    except Exception as e:
        print(f"ERROR: List public categories error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list categories: {str(e)}"
        )
