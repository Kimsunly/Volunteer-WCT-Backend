"""
Admin routes - UPDATED for new organizer registration flow
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import datetime

from app.models.organizer import ApplicationAction
from app.utils.security import get_current_user, extract_user_id
from app.database import get_supabase

router = APIRouter(prefix="/api/admin", tags=["Admin"])


async def require_admin(current_user = Depends(get_current_user)):
    """Check if user is admin"""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)
    
    try:
        user_profile = supabase.table("user_profiles")\
            .select("role")\
            .match({"user_id": user_id})\
            .single()\
            .execute()
        
        if not user_profile.data or user_profile.data['role'] != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def log_admin_action(admin_id: str, action: str, target_id: int, details: str = None):
    """Log admin actions"""
    supabase = get_supabase()
    try:
        log_data = {
            "admin_id": admin_id,
            "action": action,
            "target_id": target_id,
            "details": details
        }
        supabase.table("admin_activity_log").insert(log_data).execute()
    except Exception as e:
        print(f"Failed to log: {e}")


@router.get("/applications")
async def get_all_applications(
    status_filter: Optional[str] = None,
    current_user = Depends(require_admin)
):
    """Get all organizer applications"""
    supabase = get_supabase()
    
    try:
        query = supabase.table("organizer_applications")\
            .select("*")\
            .order("submitted_at", desc=True)
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        response = query.execute()
        return response.data or []
        
    except Exception as e:
        print(f"Get applications error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get applications: {str(e)}"
        )


@router.get("/applications/pending")
async def get_pending_applications(
    current_user = Depends(require_admin)
):
    """Get only pending applications"""
    return await get_all_applications("pending", current_user)


@router.get("/applications/{application_id}")
async def get_application_detail(
    application_id: int,
    current_user = Depends(require_admin)
):
    """Get application details"""
    supabase = get_supabase()
    
    try:
        # Get application
        app_response = supabase.table("organizer_applications")\
            .select("*")\
            .match({"id": application_id})\
            .single()\
            .execute()
        
        if not app_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        application = app_response.data
        
        # Get user info
        user_response = supabase.table("user_profiles")\
            .select("email, first_name, last_name, created_at, role, status")\
            .match({"user_id": application['user_id']})\
            .single()\
            .execute()
        
        return {
            "application": application,
            "user_info": user_response.data if user_response.data else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get detail error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get application: {str(e)}"
        )


@router.post("/applications/{application_id}/approve")
async def approve_application(
    application_id: int,
    current_user = Depends(require_admin)
):
    """
    Approve organizer application
    UPDATED: Now properly changes status from 'pending' to 'active'
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Get application
        app_response = supabase.table("organizer_applications")\
            .select("*")\
            .match({"id": application_id})\
            .single()\
            .execute()
        
        if not app_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        application = app_response.data
        
        if application['status'] != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve {application['status']} application"
            )
        
        # Update application status to 'approved'
        supabase.table("organizer_applications")\
            .update({
                "status": "approved",
                "reviewed_at": datetime.utcnow().isoformat(),
                "reviewed_by": admin_id
            })\
            .match({"id": application_id})\
            .execute()
        
        # Update user profile: role stays 'organizer', but status changes to 'active'
        supabase.table("user_profiles")\
            .update({
                "role": "organizer",
                "status": "active"  # IMPORTANT: Change from 'pending' to 'active'
            })\
            .match({"user_id": application['user_id']})\
            .execute()
        
        # Create or update organizer profile
        # Check if profile already exists
        existing_profile = supabase.table("organizer_profiles")\
            .select("id")\
            .eq("user_id", application['user_id'])\
            .execute()
        
        organizer_profile_data = {
            "user_id": application['user_id'],
            "organization_name": application['organization_name'],
            "organizer_type": application['organizer_type'],
            "phone": application['phone'],
            "card_image_url": application.get('card_image_url'),
            "verified_at": datetime.utcnow().isoformat()
        }
        
        if existing_profile.data:
            # Update existing profile
            supabase.table("organizer_profiles")\
                .update(organizer_profile_data)\
                .eq("user_id", application['user_id'])\
                .execute()
        else:
            # Insert new profile
            supabase.table("organizer_profiles")\
                .insert(organizer_profile_data)\
                .execute()
        
        # Log action
        log_admin_action(
            admin_id, 
            "approve_organizer", 
            application_id,
            f"Approved: {application['organization_name']}"
        )
        
        return {
            "message": f"✅ {application['organization_name']} approved! They can now login.",
            "application_id": application_id,
            "organization_name": application['organization_name']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Approve error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to approve: {str(e)}"
        )


@router.post("/applications/{application_id}/reject")
async def reject_application(
    application_id: int,
    action: ApplicationAction,
    current_user = Depends(require_admin)
):
    """
    Reject organizer application
    UPDATED: Now properly handles rejection
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Get application
        app_response = supabase.table("organizer_applications")\
            .select("*")\
            .match({"id": application_id})\
            .single()\
            .execute()
        
        if not app_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        application = app_response.data
        
        if application['status'] != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject {application['status']} application"
            )
        
        # Update application status to 'rejected'
        supabase.table("organizer_applications")\
            .update({
                "status": "rejected",
                "reviewed_at": datetime.utcnow().isoformat(),
                "reviewed_by": admin_id,
                "rejection_reason": action.reason
            })\
            .match({"id": application_id})\
            .execute()
        
        # Update user profile: status stays 'pending' (they're still blocked)
        # OR you can change role back to 'user' if you want them to use app as regular user
        supabase.table("user_profiles")\
            .update({
                "status": "rejected"  # Keep them blocked
                # OR: "role": "user", "status": "active"  # Let them be regular user
            })\
            .match({"user_id": application['user_id']})\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "reject_organizer",
            application_id,
            f"Rejected: {application['organization_name']} - {action.reason}"
        )
        
        return {
            "message": "Application rejected",
            "application_id": application_id,
            "reason": action.reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reject error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to reject: {str(e)}"
        )


@router.get("/stats")
async def get_admin_stats(current_user = Depends(require_admin)):
    """Get dashboard statistics"""
    supabase = get_supabase()
    
    try:
        # Pending applications
        pending = supabase.table("organizer_applications")\
            .select("id", count="exact")\
            .eq("status", "pending")\
            .execute()
        
        # Total users
        users = supabase.table("user_profiles")\
            .select("id", count="exact")\
            .eq("role", "user")\
            .execute()
        
        # Organizers
        organizers = supabase.table("user_profiles")\
            .select("id", count="exact")\
            .eq("role", "organizer")\
            .execute()
        
        # Admins
        admins = supabase.table("user_profiles")\
            .select("id", count="exact")\
            .eq("role", "admin")\
            .execute()
        
        return {
            "pending_applications": pending.count or 0,
            "total_users": users.count or 0,
            "total_organizers": organizers.count or 0,
            "total_admins": admins.count or 0
        }
        
    except Exception as e:
        print(f"Stats error: {e}")
        return {
            "pending_applications": 0,
            "total_users": 0,
            "total_organizers": 0,
            "total_admins": 0
        }


@router.get("/logs")
async def get_activity_logs(
    limit: int = 20,
    current_user = Depends(require_admin)
):
    """Get admin activity logs"""
    supabase = get_supabase()
    
    try:
        response = supabase.table("admin_activity_log")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data or []
        
    except Exception as e:
        print(f"Logs error: {e}")
        return []