"""Opportunity routes - organizers can create, edit, and delete opportunities"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from app.database import get_supabase
from app.models.opportunity import (
    OpportunityCreate, 
    OpportunityUpdate, 
    OpportunityResponse,
    OpportunityListResponse
)
from app.utils.security import get_current_user, extract_user_id

router = APIRouter(prefix="/api/opportunities", tags=["Opportunities"])


async def get_organizer_profile(current_user = Depends(get_current_user)):
    """
    Get the organizer profile for the current user.
    Raises 403 if user is not an organizer.
    """
    supabase = get_supabase()
    user_id = extract_user_id(current_user)

    try:
        # Check organizer_profiles table
        organizer = (
            supabase.table("organizer_profiles")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if not organizer.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only verified organizers can perform this action. Please register as an organizer first."
            )

        organizer_profile = organizer.data[0]
        
        # Check if active
        if not organizer_profile.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your organizer account is not active"
            )
        
        # Check if verified (optional - comment out if not needed)
        if organizer_profile.get("verified_at") is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your organizer account is pending verification"
            )

        return organizer_profile

    except HTTPException:
        raise
    except Exception as e:
        print(f"Organizer check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying organizer status: {str(e)}"
        )


@router.post(
    "/",
    response_model=OpportunityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new opportunity",
    description="Create a new volunteer opportunity. Only verified organizers can create opportunities."
)
async def create_opportunity(
    payload: OpportunityCreate,
    organizer_profile: dict = Depends(get_organizer_profile)
):
    """
    Create a new volunteer opportunity.
    
    **Required:** Must be a verified organizer (exist in organizer_profiles table)
    
    **Required fields:**
    - title: Opportunity title
    - category_slug: Category identifier
    - category_label: Category display name
    - location_slug: Location identifier
    - location_label: Location display name
    
    **Optional fields:**
    - images, description, full_details, organization, date_range,
      time_range, capacity, transport, housing, meals
      
    The opportunity will be automatically linked to your organizer profile.
    """
    supabase = get_supabase()
    organizer_id = organizer_profile["id"]

    try:
        # Build insert data with all your schema fields
        data = {
            "organizer_id": organizer_id,
            "title": payload.title,
            "category_slug": payload.category_slug,
            "category_label": payload.category_label,
            "location_slug": payload.location_slug,
            "location_label": payload.location_label,
            "images": payload.images,
            "description": payload.description,
            "full_details": payload.full_details,
            "organization": payload.organization,
            "date_range": payload.date_range,
            "time_range": payload.time_range,
            "capacity": payload.capacity,
            "transport": payload.transport,
            "housing": payload.housing,
            "meals": payload.meals,
        }

        # Insert into opportunities table.
        # Important: PostgREST can return only what it gets back from the insert.
        # If the API is configured to not return inserted rows, `id` may be missing,
        # which breaks our OpportunityResponse response model.
        insert_result = supabase.table("opportunities").insert(data).execute()

        if not insert_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create opportunity"
            )

        inserted = insert_result.data[0]

        # If `id` is present, we are done.
        if inserted.get("id") is not None:
            return inserted

        # Otherwise fetch the newly inserted row.
        # We can't rely on a unique combination of business fields, so we grab the
        # latest row for this organizer that matches title (and created_at ordering).
        fetched = (
            supabase.table("opportunities")
            .select("*")
            .eq("organizer_id", organizer_id)
            .eq("title", payload.title)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if not fetched.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Opportunity was created but could not be fetched with its id. "
                    "Check your PostgREST/Supabase settings and RLS policies for the opportunities table."
                ),
            )

        return fetched.data[0]

    except HTTPException:
        raise
    except Exception as e:
        print(f"Create opportunity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create opportunity: {str(e)}"
        )


@router.get(
    "/",
    response_model=OpportunityListResponse,
    summary="Get all opportunities",
    description="Get a list of opportunities with optional filtering (public endpoint)"
)
async def get_opportunities(
    limit: int = Query(10, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    category_slug: Optional[str] = Query(None, description="Filter by category slug"),
    location_slug: Optional[str] = Query(None, description="Filter by location slug"),
    organization: Optional[str] = Query(None, description="Filter by organization name")
):
    """
    Get list of opportunities with pagination and filtering.
    
    **Query parameters:**
    - limit: Maximum results (1-100, default 10)
    - offset: Skip N results (default 0)
    - category_slug: Filter by category
    - location_slug: Filter by location
    - organization: Search by organization name
    """
    supabase = get_supabase()

    try:
        # Build query
        query = supabase.table("opportunities").select("*", count="exact")

        # Apply filters
        if category_slug:
            query = query.eq("category_slug", category_slug)

        if location_slug:
            query = query.eq("location_slug", location_slug)

        if organization:
            query = query.ilike("organization", f"%{organization}%")

        # Apply pagination
        response = query.range(offset, offset + limit - 1).execute()

        total_count = response.count if hasattr(response, 'count') else len(response.data)

        return OpportunityListResponse(
            data=response.data,
            total=total_count,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        print(f"Get opportunities error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch opportunities: {str(e)}"
        )


@router.get(
    "/my-opportunities",
    response_model=OpportunityListResponse,
    summary="Get my opportunities",
    description="Get opportunities created by the current organizer"
)
async def get_my_opportunities(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    organizer_profile: dict = Depends(get_organizer_profile)
):
    """
    Get opportunities created by the current organizer.
    
    **Required:** Must be a verified organizer
    """
    supabase = get_supabase()
    organizer_id = organizer_profile["id"]

    try:
        query = supabase.table("opportunities").select("*", count="exact")
        query = query.eq("organizer_id", organizer_id)
        response = query.range(offset, offset + limit - 1).execute()

        total_count = response.count if hasattr(response, 'count') else len(response.data)

        return OpportunityListResponse(
            data=response.data,
            total=total_count,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        print(f"Get my opportunities error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch your opportunities: {str(e)}"
        )


@router.get(
    "/search",
    response_model=list[OpportunityResponse],
    summary="Search opportunities",
    description="Search opportunities by title or description"
)
async def search_opportunities(
    q: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Search opportunities by title or description.
    
    **Query parameters:**
    - q: Search term (minimum 2 characters)
    - limit: Maximum results (1-50, default 10)
    """
    supabase = get_supabase()

    try:
        response = supabase.table("opportunities").select("*").or_(
            f"title.ilike.%{q}%,description.ilike.%{q}%"
        ).limit(limit).execute()

        return response.data

    except Exception as e:
        print(f"Search opportunities error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get(
    "/{opportunity_id}",
    response_model=OpportunityResponse,
    summary="Get opportunity by ID",
    description="Get detailed information about a specific opportunity"
)
async def get_opportunity(opportunity_id: str):
    """
    Get a single opportunity by ID.
    
    **Path parameters:**
    - opportunity_id: UUID of the opportunity
    """
    supabase = get_supabase()

    try:
        response = supabase.table("opportunities").select("*").eq("id", opportunity_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get opportunity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch opportunity: {str(e)}"
        )


@router.patch(
    "/{opportunity_id}",
    response_model=OpportunityResponse,
    summary="Update opportunity",
    description="Update an existing opportunity. Only the organizer who created it can update it."
)
async def update_opportunity(
    opportunity_id: str,
    payload: OpportunityUpdate,
    organizer_profile: dict = Depends(get_organizer_profile)
):
    """
    Update an existing opportunity.
    
    **Required:** Must be the organizer who created the opportunity
    
    **Path parameters:**
    - opportunity_id: UUID of the opportunity
    
    **Body:** Any fields to update (all optional)
    """
    supabase = get_supabase()
    organizer_id = organizer_profile["id"]

    try:
        # First, verify the opportunity exists and belongs to this organizer
        existing = supabase.table("opportunities").select("*").eq("id", opportunity_id).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        # Check ownership
        if existing.data[0]["organizer_id"] != organizer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update opportunities you created"
            )

        # Build update data (exclude None values)
        update_data = payload.model_dump(exclude_none=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Update the opportunity
        result = supabase.table("opportunities").update(update_data).eq("id", opportunity_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update opportunity"
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        print(f"Update opportunity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update opportunity: {str(e)}"
        )


@router.delete(
    "/{opportunity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete opportunity",
    description="Delete an opportunity. Only the organizer who created it can delete it."
)
async def delete_opportunity(
    opportunity_id: str,
    organizer_profile: dict = Depends(get_organizer_profile)
):
    """
    Delete an opportunity.
    
    **Required:** Must be the organizer who created the opportunity
    
    **Path parameters:**
    - opportunity_id: UUID of the opportunity
    """
    supabase = get_supabase()
    organizer_id = organizer_profile["id"]

    try:
        # First, verify the opportunity exists and belongs to this organizer
        existing = supabase.table("opportunities").select("*").eq("id", opportunity_id).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        # Check ownership
        if existing.data[0]["organizer_id"] != organizer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete opportunities you created"
            )

        # Delete the opportunity
        supabase.table("opportunities").delete().eq("id", opportunity_id).execute()

        return None

    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete opportunity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete opportunity: {str(e)}"
        )