"""
User profile routes - FIXED VERSION
Properly handles UUID in Supabase queries
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import Optional
from datetime import datetime

from app.models.user import (
    UserProfileUpdate, 
    UserProfileResponse, 
    UserStats,
    ProfileCompleteness
)
from app.utils.security import get_current_user, extract_user_id
from app.database import get_supabase
from app.config import settings

router = APIRouter(prefix="/api/user", tags=["User Profile"])


@router.get("/profile")
async def get_profile(current_user = Depends(get_current_user)):
    """Get current user profile - PROPERLY FIXED"""
    supabase = get_supabase()
    
    try:
        # Extract clean user_id
        user_id = extract_user_id(current_user)
        print(f"DEBUG: Getting profile for user_id: {user_id}")
        
        # Ensure user_id is a clean string and not a JWT/token
        user_id = str(user_id).strip()
        if not user_id or "\n" in user_id or "\r" in user_id or "." in user_id or " " in user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")

        # Query with proper string format using explicit filter
        try:
            response = supabase.table("user_profiles")\
                .select("*")\
                .filter("user_id", "eq", user_id)\
                .execute()
        except ValueError as e:
            print(f"ValueError while querying profile: {e!r}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid response from database: {str(e)}")
        except Exception as e:
            print(f"Error querying profile: {e!r}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to query profile: {str(e)}")
        
        print(f"DEBUG: Query response: {response}")
        
        if not response.data or len(response.data) == 0:
            # Profile doesn't exist, create it
            print(f"DEBUG: Profile not found, creating new profile")
            profile_data = {
                "user_id": user_id,
                "email": current_user.email,
                "first_name": "",
                "last_name": "",
                "role": "user",
                "status": "active",
                "volunteer_level": "bronze",
                "rating": 0.0,
                "points": 0
            }
            
            create_response = supabase.table("user_profiles")\
                .insert(profile_data)\
                .execute()
            
            if create_response.data:
                return create_response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found and could not be created"
                )
        
        return response.data[0]
        
    except ValueError as e:
        print(f"ValueError: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to load profile: {str(e)}"
        )


@router.put("/profile")
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user = Depends(get_current_user)
):
    """Update user profile - PROPERLY FIXED"""
    supabase = get_supabase()
    
    try:
        # Extract clean user_id
        user_id = extract_user_id(current_user)
        print(f"DEBUG: Updating profile for user_id: {user_id}")
        
        # Prepare update data
        update_data = {}
        
        if profile_data.first_name is not None:
            update_data["first_name"] = profile_data.first_name.strip()
        if profile_data.last_name is not None:
            update_data["last_name"] = profile_data.last_name.strip()
        if profile_data.phone is not None:
            update_data["phone"] = profile_data.phone.strip()
        if profile_data.location is not None:
            update_data["location"] = profile_data.location.strip()
        if profile_data.birth_date is not None:
            update_data["birth_date"] = profile_data.birth_date.isoformat()
        if profile_data.about_me is not None:
            update_data["about_me"] = profile_data.about_me.strip()[:400]
        if profile_data.skills is not None:
            update_data["skills"] = profile_data.skills.strip()
        if profile_data.availability is not None:
            update_data["availability"] = profile_data.availability.value
        if profile_data.time_preference is not None:
            update_data["time_preference"] = profile_data.time_preference.value
        if profile_data.emergency_contact_name is not None:
            update_data["emergency_contact_name"] = profile_data.emergency_contact_name.strip()
        if profile_data.emergency_contact_phone is not None:
            update_data["emergency_contact_phone"] = profile_data.emergency_contact_phone.strip()
        if profile_data.address_street is not None:
            update_data["address_street"] = profile_data.address_street.strip()
        if profile_data.address_city is not None:
            update_data["address_city"] = profile_data.address_city.strip()
        if profile_data.address_district is not None:
            update_data["address_district"] = profile_data.address_district.strip()
        if profile_data.address_province is not None:
            update_data["address_province"] = profile_data.address_province.strip()
        
        if not update_data:
            return {"message": "No data to update", "success": False}
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        print(f"DEBUG: Update data: {update_data}")
        
        # Ensure user_id is a clean string and not a JWT/token
        user_id = str(user_id).strip()
        if not user_id or "\n" in user_id or "\r" in user_id or "." in user_id or " " in user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")

        # Perform the update and then fetch the updated row (some clients don't support select() on Update)
        try:
            update_resp = supabase.table("user_profiles")\
                .update(update_data)\
                .filter("user_id", "eq", user_id)\
                .execute()
        except ValueError as e:
            print(f"ValueError while updating profile: {e!r}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid response from database: {str(e)}")
        except Exception as e:
            print(f"Update profile error (db): {e!r}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update profile: {str(e)}")

        # Fetch the updated row
        try:
            response = supabase.table("user_profiles")\
                .select("*")\
                .filter("user_id", "eq", user_id)\
                .single()\
                .execute()
        except Exception as e:
            print(f"Error fetching updated profile: {e!r}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to fetch updated profile: {str(e)}")

        # Verify we got a row back
        if not response or not getattr(response, "data", None):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found or no data returned from update")
        
        print(f"DEBUG: Update response: {response}")
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return {
            "message": "Profile updated successfully! ✅",
            "success": True,
            "data": response.data[0]
        }
        
    except ValueError as e:
        print(f"ValueError: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Upload user avatar"""
    supabase = get_supabase()
    
    try:
        user_id = extract_user_id(current_user)
        # Ensure user_id is clean
        user_id = str(user_id).strip()
        if not user_id or "\n" in user_id or "\r" in user_id or "." in user_id or " " in user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 5MB"
            )
        
        # Generate filename
        file_ext = file.filename.split(".")[-1] if file.filename else "jpg"
        file_name = f"{user_id}/avatar.{file_ext}"
        
        # Upload to storage (call storage() then from_(bucket))
        bucket = getattr(settings, 'STORAGE_AVATAR_BUCKET', 'avatars')
        # Upload file and capture response for debugging
        try:
            upload_resp = supabase.storage().from_(bucket).upload(
                file_name,
                file_content,
                {"content-type": file.content_type, "upsert": "true"}
            )
            print(f"DEBUG: storage.upload response: {getattr(upload_resp, '__dict__', str(upload_resp))}")
        except Exception as e:
            print(f"Avatar upload error (storage): {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to upload avatar: {e}")
        
        # Get public URL (handle different return shapes)
        try:
            pub = supabase.storage().from_(bucket).get_public_url(file_name)
        except Exception as e:
            print(f"Get public url error: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to get public URL: {e}")
        avatar_url = None
        if isinstance(pub, dict):
            avatar_url = pub.get('publicUrl') or pub.get('public_url') or pub.get('publicURL') or pub.get('url')
            if not avatar_url:
                # fall back to first value
                vals = list(pub.values())
                avatar_url = vals[0] if vals else None
        else:
            avatar_url = pub
        
        # Update profile (use explicit filter and handle DB errors)
        try:
            supabase.table("user_profiles")\
                .update({"avatar_url": avatar_url})\
                .filter("user_id", "eq", user_id)\
                .execute()
        except Exception as e:
            print(f"Avatar update error (db): {e!r}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update profile: {e}")
        
        return {
            "message": "Avatar uploaded successfully",
            "avatar_url": avatar_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Avatar upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to upload avatar: {str(e)}"
        )


@router.delete("/avatar")
async def delete_avatar(current_user = Depends(get_current_user)):
    """Delete user avatar"""
    supabase = get_supabase()
    
    try:
        user_id = extract_user_id(current_user)
        # Ensure user_id is clean
        user_id = str(user_id).strip()
        if not user_id or "\n" in user_id or "\r" in user_id or "." in user_id or " " in user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")
        
        # Remove from storage (ignore errors if file doesn't exist)
        try:
            bucket = getattr(settings, 'STORAGE_AVATAR_BUCKET', 'avatars')
            # Try common extensions in case the uploaded file used a different one
            tried = []
            for ext in ('jpg', 'jpeg', 'png', 'webp', 'gif'):
                file_path = f"{user_id}/avatar.{ext}"
                try:
                    supabase.storage().from_(bucket).remove([file_path])
                    tried.append(file_path)
                except Exception:
                    # Ignore missing files for now
                    pass
            print(f"DEBUG: attempted to remove files: {tried}")
        except Exception as exc:
            print(f"Warning: failed to remove avatar from storage: {exc}")
            pass
        
        # Update profile
        try:
            supabase.table("user_profiles")\
                .update({"avatar_url": None})\
                .filter("user_id", "eq", user_id)\
                .execute()
        except Exception as e:
            print(f"Avatar delete update error (db): {e!r}")
            # Don't fail the whole operation because storage removal might have worked
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update profile: {e}")
        
        return {
            "message": "Avatar deleted successfully",
            "success": True
        }
        
    except Exception as e:
        print(f"Delete avatar error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete avatar: {str(e)}"
        )


@router.get("/stats", response_model=UserStats)
async def get_user_stats(current_user = Depends(get_current_user)):
    """Get user statistics"""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)
    
    try:
        # Get completed activities
        hours_response = supabase.table("user_activities")\
            .select("hours")\
            .eq("user_id", user_id)\
            .eq("status", "completed")\
            .execute()
        
        total_hours = sum(a.get("hours", 0) for a in (hours_response.data or []))
        completed_count = len(hours_response.data or [])
        
        # Get upcoming activities
        upcoming_response = supabase.table("user_activities")\
            .select("id")\
            .eq("user_id", user_id)\
            .eq("status", "upcoming")\
            .execute()
        
        upcoming_count = len(upcoming_response.data or [])
        
        # Get points
        profile_response = supabase.table("user_profiles")\
            .select("points")\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        points = profile_response.data.get("points", 0) if profile_response.data else 0
        
        return UserStats(
            total_hours=float(total_hours),
            completed_projects=completed_count,
            upcoming_events=upcoming_count,
            points=points
        )
        
    except Exception as e:
        print(f"Get stats error: {e}")
        return UserStats(
            total_hours=0.0,
            completed_projects=0,
            upcoming_events=0,
            points=0
        )


@router.get("/profile/complete", response_model=ProfileCompleteness)
async def get_profile_completeness(current_user = Depends(get_current_user)):
    """Get profile completion percentage"""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)
    
    try:
        response = supabase.table("user_profiles")\
            .select("*")\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        if not response.data:
            return ProfileCompleteness(
                percentage=0,
                filled_fields=0,
                total_fields=12,
                missing_fields=[],
                is_complete=False
            )
        
        profile = response.data
        
        fields_to_check = [
            'first_name', 'last_name', 'phone', 'location', 
            'birth_date', 'about_me', 'skills', 'availability',
            'emergency_contact_name', 'emergency_contact_phone',
            'address_city', 'avatar_url'
        ]
        
        filled_fields = sum(1 for field in fields_to_check if profile.get(field))
        total_fields = len(fields_to_check)
        percentage = int((filled_fields / total_fields) * 100)
        missing_fields = [field for field in fields_to_check if not profile.get(field)]
        
        return ProfileCompleteness(
            percentage=percentage,
            filled_fields=filled_fields,
            total_fields=total_fields,
            missing_fields=missing_fields,
            is_complete=percentage == 100
        )
        
    except Exception as e:
        print(f"Profile completeness error: {e}")
        return ProfileCompleteness(
            percentage=0,
            filled_fields=0,
            total_fields=12,
            missing_fields=[],
            is_complete=False
        )