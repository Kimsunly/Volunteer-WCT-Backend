"""
Organizer registration routes - WITH DIRECT ORGANIZER REGISTRATION
Organizers can now register separately from regular users
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import Optional
from datetime import datetime
from enum import Enum
from gotrue.errors import AuthApiError

from app.models.organizer import OrganizerRegister
from app.models.user import UserLogin
from app.utils.security import get_current_user, extract_user_id
from app.database import get_supabase

router = APIRouter(prefix="/api/organizer", tags=["Organizer"])


class OrganizerType(str, Enum):
    NGO = "ngo"
    NONPROFIT = "nonprofit"
    BUSINESS = "business"
    COMMUNITY_GROUP = "community_group"
    OTHER = "other"
    NEW = "new"    # <-- add this if you want to accept "new"


@router.post("/login")
def organizer_login(credentials: UserLogin):
    """Organizer-only login.

    This is a convenience endpoint so Swagger shows a login button under the
    Organizer section. It uses the same Supabase Auth user as normal login, but
    it blocks login unless the user is an approved organizer.

    Rules:
    - Must have an organizer application with status='approved' OR have an active
      organizer profile.
    """
    supabase = get_supabase()

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })

        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        user_id = extract_user_id(auth_response.user)

        # Prefer checking organizer_profiles (source of truth for "verified organizer")
        organizer_profile = supabase.table("organizer_profiles") \
            .select("id, is_active, verified_at") \
            .eq("user_id", user_id) \
            .execute()

        if organizer_profile.data:
            profile = organizer_profile.data[0]
            if not profile.get("is_active", True):
                supabase.auth.sign_out()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your organizer account is not active.",
                )
            if profile.get("verified_at") is None:
                supabase.auth.sign_out()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your organizer account is pending verification.",
                )

            return {
                "message": "Organizer login successful",
                "user": {
                    "id": user_id,
                    "email": auth_response.user.email,
                    "role": "organizer",
                },
                "session": {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                },
            }

        # Fallback: check organizer application status
        app_check = supabase.table("organizer_applications") \
            .select("status") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        if not app_check.data:
            supabase.auth.sign_out()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No organizer application found for this account.",
            )

        status_value = app_check.data[0].get("status")
        if status_value != "approved":
            supabase.auth.sign_out()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Organizer login not allowed. Application status is '{status_value}'.",
            )

        return {
            "message": "Organizer login successful",
            "user": {
                "id": user_id,
                "email": auth_response.user.email,
                "role": "organizer",
            },
            "session": {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
            },
        }

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
        )

    except HTTPException:
        raise

    except Exception as e:
        print(f"Organizer login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Organizer login failed. Please try again later.",
        )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_as_organizer(application: OrganizerRegister):
    """
    NEW: Direct organizer registration
    Organizers register with their own email/password, separate from regular users
    They get 'organizer' role but status is 'pending' until admin approval
    """
    supabase = get_supabase()
    
    try:
        # Step 1: Create auth user in Supabase
        auth_response = supabase.auth.sign_up({
            "email": application.email,
            "password": application.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. Email may already be in use."
            )
        
        user_id = extract_user_id(auth_response.user)
        print(f"DEBUG: Created organizer auth user with ID: {user_id}")
        
        # Step 2: Create user profile as a regular user so they can login immediately
        # Their organizer application will remain 'pending' until admin approval
        profile_data = {
            "user_id": user_id,
            "email": application.email,
            "first_name": "",  # Can be updated later
            "last_name": "",   # Can be updated later
            "phone": application.phone,
            # Keep them as a regular user so they can login and use non-organizer features
            "role": "user",
            "status": "active",
            "volunteer_level": "bronze",
            "rating": 0.0,
            "points": 0
        }

        supabase.table("user_profiles").insert(profile_data).execute()
        print(f"DEBUG: Created user profile with role='user', status='active' (organizer application pending)")
        
        # Step 3: Create organizer application
        application_data = {
            "user_id": user_id,
            "organization_name": application.organization_name,
            "email": application.email,
            "phone": application.phone,
            "organizer_type": application.organizer_type.value,
            "status": "pending"
        }
        
        app_response = supabase.table("organizer_applications")\
            .insert(application_data)\
            .execute()
        
        if not app_response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create application"
            )
        
        print(f"DEBUG: Created organizer application with status='pending'")
        
        return {
            "message": "Organizer registration successful! You can login now. Organizer features will be enabled after admin approval.",
            "user": {
                "id": user_id,
                "email": application.email,
                "organization_name": application.organization_name
            },
            "application": {
                "id": app_response.data[0]['id'],
                "status": "pending"
            },
            "note": "You can use the platform as a regular user. Admin will promote you to organizer when they approve your application."
        }
        
    except AuthApiError as e:
        print(f"Supabase Auth Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/apply", status_code=status.HTTP_201_CREATED)
def apply_as_organizer(
    application: OrganizerRegister,
    current_user = Depends(get_current_user)
):
    """
    OLD: Existing users can apply to become organizers
    This is for users who are already registered and want to upgrade to organizer
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
            "user_id": user_id,
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
def upload_organization_card(
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
def get_my_application(current_user = Depends(get_current_user)):
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
def get_organizer_profile_endpoint(current_user = Depends(get_current_user)):
    """Get organizer profile (only for approved organizers)"""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)
    
    try:
        # Check role
        user_profile = supabase.table("user_profiles")\
            .select("role, status")\
            .match({"user_id": user_id})\
            .single()\
            .execute()
        
        if not user_profile.data or user_profile.data['role'] != 'organizer':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not an organizer"
            )
        
        if user_profile.data['status'] == 'pending':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your organizer application is still pending approval"
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

@router.get("/dashboard")
def get_organizer_dashboard(current_user = Depends(get_current_user)):
    """Get organizer dashboard statistics"""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)
    
    try:
        # Check if organizer
        org_check = supabase.table("organizer_profiles")\
            .select("id")\
            .match({"user_id": user_id})\
            .execute()
            
        if not org_check.data:
            # If not verified organizer, return empty stats or forbidden
            # For dashboard, maybe just return empty / pending msg
            return {
                "opportunities_count": 0,
                "applications_total": 0,
                "applications_pending": 0,
                "applications_approved": 0
            }
        
        organizer_id = org_check.data[0]['id']
        
        # Get opportunities count
        opps = supabase.table("opportunities")\
            .select("id", count="exact")\
            .eq("organizer_id", organizer_id)\
            .execute()
        
        opp_count = opps.count or 0
        opp_ids = [o['id'] for o in (opps.data or [])]
        
        # Get applications stats
        # If no opportunities, no applications
        if not opp_ids:
            return {
                "opportunities_count": 0,
                "applications_total": 0,
                "applications_pending": 0,
                "applications_approved": 0
            }
            
        # We can't easily do IN query for count breakdown in one go with simple Postgrest client 
        # without writing raw SQL or multiple queries. 
        # Using a view would be better, but for now we'll do a simple fetch.
        
        apps = supabase.table("applications")\
            .select("status")\
            .in_("opportunity_id", opp_ids)\
            .execute()
            
        app_list = apps.data or []
        total = len(app_list)
        pending = sum(1 for a in app_list if a['status'] == 'pending')
        approved = sum(1 for a in app_list if a['status'] == 'approved')
        
        return {
            "opportunities_count": opp_count,
            "applications_total": total,
            "applications_pending": pending,
            "applications_approved": approved
        }
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load dashboard: {str(e)}"
        )
