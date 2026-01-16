"""
Applications router - Users apply to opportunities, organizers manage applications
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from typing import Optional

from app.database import get_supabase
from app.models.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationListResponse,
    ApplicationStatus,
)
from app.utils.security import get_current_user, extract_user_id
from app.utils.image_upload import upload_user_cv
from app.utils.security import hash_secret
from typing import Optional
from app.utils.security import hash_secret

router = APIRouter(prefix="/api/applications", tags=["Applications"])


# ==============================================================================
# USER ENDPOINTS - Apply, view own applications, withdraw
# ==============================================================================

@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Apply to an opportunity",
    description="Submit an application to a volunteer opportunity."
)
def create_application(
    payload: ApplicationCreate,
    current_user=Depends(get_current_user)
):
    """
    Apply to a volunteer opportunity.
    
    - User must be authenticated
    - Cannot apply twice to the same opportunity
    - Application starts with status 'pending'
    """
    supabase = get_supabase()
    user_id = extract_user_id(current_user)
    
    # DEBUG: Diagnostic logging for RLS issues
    try:
        auth_header = getattr(supabase.postgrest, "_headers", {}).get("Authorization", "MISSING")
        print(f"DEBUG: create_application for user_id={user_id}")
        print(f"DEBUG: Supabase Client Auth Header: {auth_header[:20]}...{auth_header[-10:] if auth_header != 'MISSING' else ''}")
    except Exception as e:
        print(f"DEBUG: Error getting auth header: {e}")

    try:
        # Check if opportunity exists
        opp_check = supabase.table("opportunities") \
            .select("id, title") \
            .eq("id", payload.opportunity_id) \
            .execute()

        if not opp_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        # If the opportunity is private, require and validate access key
        opp_row = opp_check.data[0]
        if opp_row.get("is_private"):
            # Expect access_key on the application payload
            if not getattr(payload, "access_key", None):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This opportunity is private. An access key is required to apply."
                )

            provided_hash = hash_secret(payload.access_key)
            stored_hash = opp_row.get("access_key_hash")
            if not stored_hash or provided_hash != stored_hash:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid access key for this private opportunity"
                )

        # Check if user already applied
        existing = supabase.table("applications") \
            .select("id") \
            .eq("opportunity_id", payload.opportunity_id) \
            .eq("user_id", user_id) \
            .execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already applied to this opportunity"
            )

        # Create application
        data = {
            "opportunity_id": payload.opportunity_id,
            "user_id": user_id,
            "name": payload.name,
            "skills": payload.skills,
            "availability": payload.availability,
            "email": payload.email,
            "phone_number": payload.phone_number,
            "sex": payload.sex.value,
            "message": payload.message,
            "cv_url": getattr(payload, "cv_url", None),
            "status": "pending",
        }

        result = supabase.table("applications").insert(data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create application"
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        print(f"Create application error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}"
        )


def _create_application_core(supabase, payload: dict, user_id: str):
    """Core logic to validate and insert an application record.

    Accepts a payload dict with keys matching the applications table columns.
    Returns the inserted row (dict) on success or raises HTTPException on errors.
    """
    # DEBUG: Diagnostic logging for RLS issues
    try:
        auth_header = getattr(supabase.postgrest, "_headers", {}).get("Authorization", "MISSING")
        print(f"DEBUG: _create_application_core for user_id={user_id}")
        print(f"DEBUG: Supabase Client Auth Header: {auth_header[:20]}...{auth_header[-10:] if auth_header != 'MISSING' else ''}")
    except Exception as e:
        print(f"DEBUG: Error getting auth header: {e}")

    # Check if opportunity exists
    opp_check = supabase.table("opportunities") \
        .select("id, title, is_private, access_key_hash") \
        .eq("id", payload.get("opportunity_id")) \
        .execute()

    if not opp_check.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    opp_row = opp_check.data[0]

    # If the opportunity is private, require and validate access key
    if opp_row.get("is_private"):
        if not payload.get("access_key"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This opportunity is private. An access key is required to apply."
            )

        provided_hash = hash_secret(payload.get("access_key"))
        stored_hash = opp_row.get("access_key_hash")
        if not stored_hash or provided_hash != stored_hash:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid access key for this private opportunity"
            )

    # Check if user already applied
    existing = supabase.table("applications") \
        .select("id") \
        .eq("opportunity_id", payload.get("opportunity_id")) \
        .eq("user_id", user_id) \
        .execute()

    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this opportunity"
        )

    # Build insertion data (only allowed fields)
    insert_data = {
        "opportunity_id": payload.get("opportunity_id"),
        "user_id": user_id,
        "name": payload.get("name"),
        "skills": payload.get("skills"),
        "availability": payload.get("availability"),
        "email": payload.get("email"),
        "phone_number": payload.get("phone_number"),
        "sex": payload.get("sex"),
        "message": payload.get("message"),
        "status": "pending",
    }

    # Optional fields if present
    if payload.get("cv_url"):
        insert_data["cv_url"] = payload.get("cv_url")

    result = supabase.table("applications").insert(insert_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application"
        )

    return result.data[0]



@router.post(
    "/multipart",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Apply to an opportunity (multipart/form-data)",
    description="Submit an application to a volunteer opportunity with optional CV upload in one request."
)
def create_application_multipart(
    opportunity_id: int = Form(...),
    name: str = Form(...),
    skills: str = Form(...),
    availability: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    sex: str = Form(...),
    message: Optional[str] = Form(None),
    access_key: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user=Depends(get_current_user)
):
    """Apply using multipart form-data. If `file` is provided it will be uploaded and its URL used as `cv_url`."""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)

    try:
        cv_url = None
        if file and file.filename:
            cv_url = upload_user_cv(file, user_id)

        payload = {
            "opportunity_id": opportunity_id,
            "name": name,
            "skills": skills,
            "availability": availability,
            "email": email,
            "phone_number": phone_number,
            "sex": sex,
            "message": message,
            "access_key": access_key,
            "cv_url": cv_url,
        }

        created = _create_application_core(supabase, payload, user_id)
        return created

    except HTTPException:
        raise
    except Exception as e:
        print(f"Create multipart application error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}"
        )



@router.post(
    "/upload-cv",
    summary="Upload CV",
    description="Upload a CV (PDF/DOCX/TXT) and receive a public URL to include in application",
)
def upload_cv(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Upload applicant CV and return public URL."""
    supabase = get_supabase()
    user = current_user
    try:
        user_id = extract_user_id(user)
        url = upload_user_cv(file, user_id)
        return {"cv_url": url}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload CV error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload CV: {str(e)}"
        )


@router.get(
    "/my",
    response_model=ApplicationListResponse,
    summary="Get my applications",
    description="Get all applications submitted by the current user."
)
def get_my_applications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[ApplicationStatus] = Query(None, alias="status"),
    current_user=Depends(get_current_user)
):
    """Get all applications for the current user with optional status filter."""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)

    try:

        query = supabase.table("applications") \
            .select("*, opportunities(title)", count="exact") \
            .eq("user_id", user_id)

        if status_filter:
            query = query.eq("status", status_filter.value)

        query = query.order("created_at", desc=True) \
            .range(offset, offset + limit - 1)

        result = query.execute()

        # Transform data to match ApplicationWithDetails (flatten opportunity title)
        transformed_data = []
        for row in (result.data or []):
            opp = row.get("opportunities")
            if opp and isinstance(opp, dict):
                row["opportunity_title"] = opp.get("title")
            transformed_data.append(row)

        return {
            "data": transformed_data,
            "total": result.count or 0,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        print(f"Get my applications error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applications: {str(e)}"
        )


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
    summary="Get application by ID",
    description="Get a specific application. User can only view their own applications."
)
def get_application(
    application_id: int,
    current_user=Depends(get_current_user)
):
    """Get a specific application by ID."""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)

    try:
        result = supabase.table("applications") \
            .select("*") \
            .eq("id", application_id) \
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )

        application = result.data[0]

        # Check ownership (user can view own, organizer can view for their opportunities)
        if application["user_id"] != user_id:
            # Check if user is the organizer of this opportunity
            opp_check = supabase.table("opportunities") \
                .select("organizer_id") \
                .eq("id", application["opportunity_id"]) \
                .execute()

            if opp_check.data:
                organizer_id = opp_check.data[0]["organizer_id"]
                # Check if current user owns this organizer profile
                org_check = supabase.table("organizer_profiles") \
                    .select("id") \
                    .eq("id", organizer_id) \
                    .eq("user_id", user_id) \
                    .execute()

                if not org_check.data:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can only view your own applications"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view your own applications"
                )

        return application

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get application error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch application: {str(e)}"
        )


@router.delete(
    "/{application_id}",
    status_code=status.HTTP_200_OK,
    summary="Withdraw application",
    description="Withdraw a pending application. Only the applicant can withdraw."
)
async def withdraw_application(
    application_id: int,
    current_user=Depends(get_current_user)
):
    """Withdraw a pending application."""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)

    try:
        # Check application exists and belongs to user
        existing = supabase.table("applications") \
            .select("id, user_id, status") \
            .eq("id", application_id) \
            .execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )

        application = existing.data[0]

        if application["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only withdraw your own applications"
            )

        if application["status"] not in ["pending", "approved"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot withdraw application with status '{application['status']}'. Only pending or approved applications can be withdrawn."
            )

        # Update status to withdrawn
        result = supabase.table("applications") \
            .update({"status": "withdrawn"}) \
            .eq("id", application_id) \
            .execute()

        return {"message": "Application withdrawn successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Withdraw application error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to withdraw application: {str(e)}"
        )


# ==============================================================================
# ORGANIZER ENDPOINTS - View and manage applications for their opportunities
# ==============================================================================

@router.get(
    "/opportunity/{opportunity_id}",
    response_model=ApplicationListResponse,
    summary="Get applications for opportunity (Organizer)",
    description="Get all applications for a specific opportunity. Only the organizer who created the opportunity can view."
)
async def get_applications_for_opportunity(
    opportunity_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[ApplicationStatus] = Query(None, alias="status"),
    current_user=Depends(get_current_user)
):
    """Get all applications for an opportunity (organizer only)."""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)

    try:
        # Verify user is the organizer of this opportunity
        opp_check = supabase.table("opportunities") \
            .select("id, organizer_id") \
            .eq("id", opportunity_id) \
            .execute()

        if not opp_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        organizer_id = opp_check.data[0]["organizer_id"]

        # Verify current user owns this organizer profile
        org_check = supabase.table("organizer_profiles") \
            .select("id") \
            .eq("id", organizer_id) \
            .eq("user_id", user_id) \
            .execute()

        if not org_check.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view applications for your own opportunities"
            )

        # Fetch applications
        query = supabase.table("applications") \
            .select("*", count="exact") \
            .eq("opportunity_id", opportunity_id)

        if status_filter:
            query = query.eq("status", status_filter.value)

        query = query.order("created_at", desc=True) \
            .range(offset, offset + limit - 1)

        result = query.execute()

        return {
            "data": result.data or [],
            "total": result.count or 0,
            "limit": limit,
            "offset": offset
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get applications for opportunity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applications: {str(e)}"
        )


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse,
    summary="Update application status (Organizer)",
    description="Approve or reject an application. Only the organizer of the opportunity can update."
)
async def update_application_status(
    application_id: int,
    payload: ApplicationUpdate,
    current_user=Depends(get_current_user)
):
    """Update application status (organizer only)."""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)

    try:
        # Get application and verify organizer ownership
        app_check = supabase.table("applications") \
            .select("id, opportunity_id, status") \
            .eq("id", application_id) \
            .execute()

        if not app_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )

        application = app_check.data[0]
        opportunity_id = application["opportunity_id"]

        # Get opportunity and verify organizer
        opp_check = supabase.table("opportunities") \
            .select("organizer_id") \
            .eq("id", opportunity_id) \
            .execute()

        if not opp_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        organizer_id = opp_check.data[0]["organizer_id"]

        # Verify current user owns this organizer profile
        org_check = supabase.table("organizer_profiles") \
            .select("id") \
            .eq("id", organizer_id) \
            .eq("user_id", user_id) \
            .execute()

        if not org_check.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage applications for your own opportunities"
            )

        # Build update data
        update_data = {}
        if payload.status is not None:
            # Organizer can only approve or reject (not withdraw - that's user only)
            if payload.status == ApplicationStatus.WITHDRAWN:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organizers cannot set status to 'withdrawn'. Only applicants can withdraw."
                )
            update_data["status"] = payload.status.value

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Update
        result = supabase.table("applications") \
            .update(update_data) \
            .eq("id", application_id) \
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update application"
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        print(f"Update application status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application: {str(e)}"
        )


# ==============================================================================
# STATS ENDPOINT - Get application statistics for an opportunity
# ==============================================================================

@router.get(
    "/opportunity/{opportunity_id}/stats",
    summary="Get application stats (Organizer)",
    description="Get application statistics for an opportunity."
)
async def get_application_stats(
    opportunity_id: int,
    current_user=Depends(get_current_user)
):
    """Get application statistics for an opportunity (organizer only)."""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)

    try:
        # Verify organizer ownership
        opp_check = supabase.table("opportunities") \
            .select("organizer_id") \
            .eq("id", opportunity_id) \
            .execute()

        if not opp_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        organizer_id = opp_check.data[0]["organizer_id"]

        org_check = supabase.table("organizer_profiles") \
            .select("id") \
            .eq("id", organizer_id) \
            .eq("user_id", user_id) \
            .execute()

        if not org_check.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view stats for your own opportunities"
            )

        # Get stats from the view (or calculate manually)
        # Try to use the view first
        try:
            stats = supabase.table("application_stats") \
                .select("*") \
                .eq("opportunity_id", opportunity_id) \
                .execute()

            if stats.data:
                return stats.data[0]
        except Exception:
            pass  # View might not exist, calculate manually

        # Manual calculation fallback
        all_apps = supabase.table("applications") \
            .select("status") \
            .eq("opportunity_id", opportunity_id) \
            .execute()

        apps = all_apps.data or []
        return {
            "opportunity_id": opportunity_id,
            "total_applications": len(apps),
            "pending_count": sum(1 for a in apps if a["status"] == "pending"),
            "approved_count": sum(1 for a in apps if a["status"] == "approved"),
            "rejected_count": sum(1 for a in apps if a["status"] == "rejected"),
            "withdrawn_count": sum(1 for a in apps if a["status"] == "withdrawn"),
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get application stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stats: {str(e)}"
        )

@router.get(
    "/organizer/my",
    response_model=ApplicationListResponse,
    summary="Get all applications for my opportunities (Organizer)",
    description="Get all applications across all opportunities owned by the current organizer."
)
async def get_my_organizer_applications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[ApplicationStatus] = Query(None, alias="status"),
    current_user=Depends(get_current_user)
):
    """Get all applications across all opportunities owned by the current organizer."""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)

    try:
        # 1. Find the organizer profile for this user
        org_profile = supabase.table("organizer_profiles") \
            .select("id") \
            .eq("user_id", user_id) \
            .execute()

        if not org_profile.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizer profile not found for this user"
            )

        organizer_id = org_profile.data[0]["id"]

        # 2. Get all opportunity IDs for this organizer
        opps = supabase.table("opportunities") \
            .select("id") \
            .eq("organizer_id", organizer_id) \
            .execute()

        if not opps.data:
            return {
                "data": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }

        opp_ids = [o["id"] for o in opps.data]

        # 3. Fetch applications for these opportunities
        query = supabase.table("applications") \
            .select("*, opportunities(title)", count="exact") \
            .in_("opportunity_id", opp_ids)

        if status_filter:
            query = query.eq("status", status_filter.value)

        query = query.order("created_at", desc=True) \
            .range(offset, offset + limit - 1)

        result = query.execute()

        # Transform data to match ApplicationWithDetails (flatten opportunity title)
        transformed_data = []
        
        # 4. Manually fetch user profiles for these applications to avoid complex join issues
        app_list = result.data or []
        user_ids = list(set([item["user_id"] for item in app_list if item.get("user_id")]))
        
        profiles_map = {}
        if user_ids:
            try:
                # Use in_ filter for batch fetching
                # Note: user_profiles uses 'user_id' string
                profiles_res = supabase.table("user_profiles") \
                    .select("*") \
                    .in_("user_id", user_ids) \
                    .execute()
                
                for prof in (profiles_res.data or []):
                    profiles_map[prof["user_id"]] = prof
            except Exception as e:
                print(f"Warning: Failed to fetch user profiles batch: {e}")

        # 5. Merge data
        for row in app_list:
            opp = row.get("opportunities")
            if opp and isinstance(opp, dict):
                row["opportunity_title"] = opp.get("title")
            
            # Enrich with profile data
            uid = row.get("user_id")
            if uid and uid in profiles_map:
                profile = profiles_map[uid]
                
                # Basic contact info (prefer profile over application if needed, or use as fallback)
                # Application usually has specific contact info, but we want extra profile details
                
                # Map fields
                row["user_email"] = profile.get("email") 
                row["user_phone"] = profile.get("phone")
                row["user_bio"] = profile.get("about_me")
                row["user_avatar"] = profile.get("avatar_url")
                row["user_first_name"] = profile.get("first_name")
                row["user_last_name"] = profile.get("last_name")
                
                # Construct address
                addr_parts = [
                    profile.get("address_street"),
                    profile.get("address_district"),
                    profile.get("address_city"),
                    profile.get("address_province")
                ]
                row["user_address"] = ", ".join([p for p in addr_parts if p])
                
                # Other fields
                # Education/Experience/Interests are NOT in the current user_profiles schema
                # We will leave them empty or null to avoid errors on frontend
                row["user_education"] = None 
                row["user_experience"] = None
                row["user_skills"] = profile.get("skills") # General skills
                row["user_interests"] = None # Not in schema yet

            transformed_data.append(row)

        return {
            "data": transformed_data,
            "total": result.count or 0,
            "limit": limit,
            "offset": offset
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get organizer applications error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organizer applications: {str(e)}"
        )
