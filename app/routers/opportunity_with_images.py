"""Minimal opportunity routes with image upload support"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import Optional, List
from datetime import date, time

from app.database import get_supabase
from app.models.opportunity import OpportunityUpdate, OpportunityResponse, OpportunityListResponse
from app.utils.security import get_current_user, extract_user_id
from app.utils.image_upload import (
    upload_multiple_opportunity_images,
    delete_opportunity_image,
    get_image_urls_from_string,
    image_urls_to_string
)

router = APIRouter(prefix="/api/opportunities", tags=["Opportunities"])


def parse_date_field(value: Optional[str]) -> Optional[date]:
    """Parse ISO date string to date object"""
    if value is None or value == "":
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )


def parse_time_field(value: Optional[str]) -> Optional[time]:
    """Parse ISO time string to time object"""
    if value is None or value == "":
        return None
    try:
        return time.fromisoformat(value)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time format. Use HH:MM or HH:MM:SS"
        )


async def get_organizer_profile(current_user = Depends(get_current_user)):
    """Get the organizer profile for the current user."""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)

    try:
        organizer = (
            supabase.table("organizer_profiles")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if not organizer.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only verified organizers can perform this action."
            )

        organizer_profile = organizer.data[0]
        
        if not organizer_profile.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your organizer account is not active"
            )
        
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
    summary="Create opportunity (with images)",
    description="Create an opportunity and upload images in one request"
)
async def create_opportunity(
    title: str = Form(...),
    category_label: str = Form(...),
    location_label: str = Form(...),
    description: Optional[str] = Form(None),
    organization: Optional[str] = Form(None),
    date_range: Optional[str] = Form(None),
    time_range: Optional[str] = Form(None),
    capacity: Optional[int] = Form(None),
    transport: Optional[str] = Form(None),
    housing: Optional[str] = Form(None),
    meals: Optional[str] = Form(None),
    images: List[UploadFile] = File(default=[]),
    organizer_profile: dict = Depends(get_organizer_profile)
):
    """Create a new opportunity with optional images."""
    supabase = get_supabase()
    organizer_id = organizer_profile["id"]

    try:
        parsed_date = parse_date_field(date_range)
        parsed_time = parse_time_field(time_range)

        image_urls = []
        if images and images[0].filename:
            image_urls = await upload_multiple_opportunity_images(images, organizer_id, max_files=5)

        data = {
            "organizer_id": organizer_id,
            "title": title,
            "category_label": category_label,
            "location_label": location_label,
            "images": image_urls_to_string(image_urls) if image_urls else None,
            "description": description,
            "organization": organization,
            # Supabase client sends JSON; native date/time objects aren't JSON serializable.
            # Store as ISO strings (compatible with Postgres date/time columns too).
            "date_range": parsed_date.isoformat() if parsed_date else None,
            "time_range": parsed_time.isoformat() if parsed_time else None,
            "capacity": capacity,
            "transport": transport,
            "housing": housing,
            "meals": meals,
        }

        # The Supabase python client sometimes returns only a subset of columns on insert
        # (depending on PostgREST configuration / return representation). Our
        # OpportunityResponse requires `id`, so we fetch the inserted row explicitly.
        insert_result = supabase.table("opportunities").insert(data).execute()

        if not insert_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create opportunity"
            )

        inserted = insert_result.data[0]
        inserted_id = inserted.get("id")
        if not inserted_id:
            # Fall back to selecting the most recent row for this organizer/title.
            # (Not perfect, but better than a response validation crash.)
            latest = (
                supabase.table("opportunities")
                .select("*")
                .eq("organizer_id", organizer_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if latest.data:
                return latest.data[0]

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Opportunity created but could not retrieve record id"
            )

        full_row = supabase.table("opportunities").select("*").eq("id", inserted_id).single().execute()
        if full_row.data:
            return full_row.data

        # As a last resort return what we have
        return inserted

    except HTTPException:
        raise
    except Exception as e:
        print(f"Create opportunity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create opportunity: {str(e)}"
        )




@router.get(
    "/my-opportunities",
    response_model=OpportunityListResponse,
    summary="Get my opportunities"
)
async def get_my_opportunities(
    limit: int = 50,
    offset: int = 0,
    organizer_profile: dict = Depends(get_organizer_profile)
):
    """Get opportunities created by the current organizer."""
    supabase = get_supabase()
    organizer_id = organizer_profile["id"]

    try:
        response = (
            supabase
            .table("opportunities")
            .select("*", count="exact")
            .eq("organizer_id", organizer_id)
            .range(offset, offset + limit - 1)
            .execute()
        )

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
    "/{opportunity_id}",
    response_model=OpportunityResponse,
    summary="Get opportunity by ID"
)
async def get_opportunity(opportunity_id: str):
    """Get a single opportunity by ID."""
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
    summary="Update opportunity"
)
async def update_opportunity(
    opportunity_id: str,
    payload: OpportunityUpdate,
    organizer_profile: dict = Depends(get_organizer_profile)
):
    """Update an existing opportunity."""
    supabase = get_supabase()
    organizer_id = organizer_profile["id"]

    try:
        existing = supabase.table("opportunities").select("*").eq("id", opportunity_id).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        if existing.data[0]["organizer_id"] != organizer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update opportunities you created"
            )

        update_data = payload.model_dump(exclude_none=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

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
    summary="Delete opportunity"
)
async def delete_opportunity(
    opportunity_id: str,
    organizer_profile: dict = Depends(get_organizer_profile)
):
    """Delete an opportunity and its images."""
    supabase = get_supabase()
    organizer_id = organizer_profile["id"]

    try:
        existing = supabase.table("opportunities").select("*").eq("id", opportunity_id).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        if existing.data[0]["organizer_id"] != organizer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete opportunities you created"
            )

        # Delete images from storage
        image_urls = get_image_urls_from_string(existing.data[0].get("images"))
        for url in image_urls:
            await delete_opportunity_image(url)

        # Delete opportunity
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