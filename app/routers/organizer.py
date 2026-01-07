"""
Organizer registration routes - FIXED & SIMPLIFIED
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import Optional
from datetime import datetime

from app.models.organizer import OrganizerRegister
from app.utils.security import get_current_user, extract_user_id
from app.database import get_supabase

router = APIRouter(prefix="/api/organizer", tags=["Organizer"])


@router.post("/apply", status_code=status.HTTP_201_CREATED)
async def apply_as_organizer(
    application: OrganizerRegister,
    current_user = Depends(get_current_user)
):
    """
    Apply to become an organizer
    Simplified - only essential fields
    """
    supabase = get_supabase()
    
    # FIXED: Proper UUID extraction
    try:
        user_id = extract_user_id(current_user)
        print(f"DEBUG: Applying with user_id: {user_id} (type: {type(user_id)})")
    except Exception as e:
        print(f"ERROR extracting user_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID: {str(e)}"
        )
    
    try:
        # Check if user already has an application
        print(f"DEBUG: Checking existing applications for: {user_id}")
        
        # FIXED: Use match() instead of eq() for UUID filtering
        existing = supabase.table("organizer_applications")\
            .select("id, status")\
            .match({"user_id": user_id})\
            .execute()
        
        print(f"DEBUG: Existing check response: {existing}")
        
        if existing.data:
            app = existing.data[0]
            if app['status'] == 'pending':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You already have a pending application"
                )
            elif app['status'] == 'approved':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You are already an organizer"
                )
            else:
                # Delete rejected application to allow reapply
                print(f"DEBUG: Deleting old rejected application: {app['id']}")
                supabase.table("organizer_applications")\
                    .delete()\
                    .eq("user_id", user_id) \
                    .execute()
        
        # Create new application
        application_data = {
            "user_id": user_id,  # This should be a clean UUID string
            "organization_name": application.organization_name,
            "email": application.email,
            "phone": application.phone,
            "organizer_type": application.organizer_type.value,
            "status": "pending"
        }
        
        print(f"DEBUG: Inserting application: {application_data}")
        
        response = supabase.table("organizer_applications")\
            .insert(application_data)\
            .execute()
        
        print(f"DEBUG: Insert response: {response}")
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to submit application"
            )
        
        return {
            "message": "Application submitted successfully! Please wait for admin approval.",
            "application_id": response.data[0]['id'],
            "status": "pending"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Apply organizer error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to submit application: {str(e)}"
        )


@router.post("/application/{application_id}/upload-card")
async def upload_organization_card(
    application_id: int,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Upload organization ID card"""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)
    
    try:
        # Verify application exists and belongs to user
        app_check = supabase.table("organizer_applications")\
            .select("id")\
            .match({"id": application_id, "user_id": user_id})\
            .execute()
        
        if not app_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Validate file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Read and validate size
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be less than 5MB"
            )
        
        # Upload to storage
        file_ext = file.filename.split(".")[-1] if file.filename else "jpg"
        file_name = f"{user_id}/org_card.{file_ext}"
        
        # Try to upload
        try:
            supabase.storage.from_("organization-cards").upload(
                file_name,
                file_content,
                {"content-type": file.content_type, "upsert": "true"}
            )
        except Exception as storage_error:
            print(f"Storage error: {storage_error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to upload. Ensure 'organization-cards' bucket exists."
            )
        
        # Get public URL
        card_url = supabase.storage.from_("organization-cards").get_public_url(file_name)
        
        # Update application
        supabase.table("organizer_applications")\
            .update({"card_image_url": card_url})\
            .eq("id", application_id)\
            .execute()
        
        return {
            "message": "Card uploaded successfully",
            "card_url": card_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/application/my")
async def get_my_application(current_user = Depends(get_current_user)):
    """Get current user's application status"""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)
    
    try:
        response = supabase.table("organizer_applications")\
            .select("*")\
            .match({"user_id": user_id})\
            .execute()
        
        if not response.data or len(response.data) == 0:
            return {
                "has_application": False,
                "message": "No application found"
            }
        
        return {
            "has_application": True,
            "application": response.data[0]
        }
        
    except Exception as e:
        print(f"Get application error: {e}")
        return {
            "has_application": False,
            "message": "Error loading application"
        }


@router.get("/profile")
async def get_organizer_profile(current_user = Depends(get_current_user)):
    """Get organizer profile (only for approved organizers)"""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)
    
    try:
        # Check role
        user_profile = supabase.table("user_profiles")\
            .select("role")\
            .match({"user_id": user_id})\
            .single()\
            .execute()
        
        if not user_profile.data or user_profile.data['role'] != 'organizer':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not an organizer"
            )
        
        # Get organizer profile
        response = supabase.table("organizer_profiles")\
            .select("*")\
            .match({"user_id": user_id})\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organizer profile not found"
            )
        
        return response.data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get profile: {str(e)}"
        )