
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.database import get_supabase
from app.utils.security import get_current_user, extract_user_id
from app.models.community import (
    CommunityPostCreate, 
    CommunityPostUpdate, 
    CommunityPostResponse,
    CommunityStatusEnum
)
from datetime import datetime

router = APIRouter(prefix="/api/community", tags=["Community"])


def get_organizer_profile(current_user = Depends(get_current_user)):
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
                detail="Only verified organizers can perform this action."
            )

        organizer_profile = organizer.data[0]
        
        # Check if active
        if not organizer_profile.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your organizer account is not active"
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


def get_organizer_or_admin_profile(current_user = Depends(get_current_user)):
    """
    Get profile for organizer OR admin.
    Returns organizer profile with is_admin flag.
    """
    supabase = get_supabase()
    user_id = extract_user_id(current_user)

    try:
        # First check if user is an admin
        user_profile = supabase.table("user_profiles").select("role").eq("user_id", user_id).single().execute()
        
        if user_profile.data and user_profile.data.get("role") == "admin":
            # Return a pseudo-profile for admin
            return {
                "user_id": user_id,
                "is_admin": True,
                "is_active": True,
                "organization_name": "Admin"
            }
        
        # Otherwise, check organizer_profiles table
        organizer = supabase.table("organizer_profiles").select("*").eq("user_id", user_id).execute()

        if not organizer.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only verified organizers or admins can perform this action."
            )

        organizer_profile = organizer.data[0]
        organizer_profile["is_admin"] = False
        
        # Check if active
        if not organizer_profile.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your organizer account is not active"
            )
        
        return organizer_profile

    except HTTPException:
        raise
    except Exception as e:
        print(f"Organizer/Admin check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying access: {str(e)}"
        )


@router.get("", response_model=List[CommunityPostResponse])
def list_community_posts(
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List approved community posts
    """
    supabase = get_supabase()
    try:
        # Attempt to join with organizer_profiles to get organization name
        # If this fails (e.g. relationship not defined in Supabase), we fallback to simple select
        try:
            query = supabase.table("community_posts")\
                .select("*, organizer:user_profiles(first_name, last_name)")\
                .eq("status", "approved")\
                .order("created_at", desc=True)
            
            if category and category != "all":
                query = query.eq("category", category)
                
            query = query.range(offset, offset + limit - 1)
            response = query.execute()
            data = response.data or []
        except Exception as join_err:
            print(f"Join query failed, falling back to simple select: {join_err}")
            query = supabase.table("community_posts")\
                .select("*")\
                .eq("status", "approved")\
                .order("created_at", desc=True)
            
            if category and category != "all":
                query = query.eq("category", category)
                
            query = query.range(offset, offset + limit - 1)
            response = query.execute()
            data = response.data or []

        # Process and flatten data
        for item in data:
            # Flatten organizer name
            # Flatten organizer name from user_profiles if that worked
            if item.get("organizer") and isinstance(item["organizer"], dict):
                org = item["organizer"]
                first = org.get('first_name') or ""
                last = org.get('last_name') or ""
                name = f"{first} {last}".strip()
                item["organizer_name"] = name if name else "Verified Volunteer"
            
            # Ensure organizer_name exists even if join failed
            if not item.get("organizer_name"):
                item["organizer_name"] = "Verified Volunteer"
            
            # Map comments_count to comments to match CommunityPostResponse model
            if "comments_count" in item:
                item["comments"] = item["comments_count"]
            elif "comments" not in item:
                item["comments"] = 0
        
        return data
    except Exception as e:
        print(f"List community posts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list posts: {str(e)}"
        )


@router.get("/my", response_model=List[CommunityPostResponse])
def list_my_posts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    organizer_profile: dict = Depends(get_organizer_profile)
):
    """
    Get community posts created by the current organizer
    """
    supabase = get_supabase()
    organizer_id = organizer_profile["user_id"]
    
    try:
        query = supabase.table("community_posts")\
            .select("*")\
            .eq("organizer_id", organizer_id)\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)
            
        response = query.execute()
        data = response.data or []
        
        # Map comments_count to comments
        for item in data:
            if "comments_count" in item:
                item["comments"] = item["comments_count"]
            elif "comments" not in item:
                item["comments"] = 0
            # Also set a default organizer_name for 'my posts' if needed, 
            # though the frontend might use its own state.
            item["organizer_name"] = organizer_profile.get("organization_name", "My Organization")
                
        return data
        
    except Exception as e:
        print(f"List my posts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list your posts: {str(e)}"
        )


@router.post("", response_model=CommunityPostResponse, status_code=status.HTTP_201_CREATED)
def create_community_post(
    post: CommunityPostCreate,
    organizer_profile: dict = Depends(get_organizer_or_admin_profile)
):
    """
    Create a new community post.
    Organizers can create posts which are Auto-Approved by default (as per requirement).
    """
    supabase = get_supabase()
    organizer_id = organizer_profile["user_id"]
    
    try:
        post_data = post.model_dump()
        post_data["organizer_id"] = organizer_id
        # Default to APPROVED since organizers are verified
        post_data["status"] = CommunityStatusEnum.APPROVED.value
        post_data["created_at"] = datetime.utcnow().isoformat()
        post_data["likes"] = 0
        post_data["comments_count"] = 0  # Initialize count
        
        response = supabase.table("community_posts").insert(post_data).execute()
        
        if not response.data:
            raise Exception("Failed to create post")
            
        data = response.data[0]
        # Map for response model
        data["comments"] = data.get("comments_count", 0)
        data["organizer_name"] = organizer_profile.get("organization_name")
            
        return data
        
    except Exception as e:
        print(f"Create post error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {str(e)}"
        )


@router.put("/{post_id}", response_model=CommunityPostResponse)
def update_community_post(
    post_id: str,
    post_update: CommunityPostUpdate,
    organizer_profile: dict = Depends(get_organizer_or_admin_profile)
):
    """
    Update a community post.
    Organizers can update their own posts, admins can update any post.
    """
    supabase = get_supabase()
    organizer_id = organizer_profile["user_id"]
    is_admin = organizer_profile.get("is_admin", False)
    
    try:
        # Verify ownership (unless admin)
        existing = supabase.table("community_posts")\
            .select("organizer_id")\
            .eq("id", post_id)\
            .single()\
            .execute()
            
        if not existing.data:
            raise HTTPException(status_code=404, detail="Post not found")
            
        # Admins can edit any post, organizers can only edit their own
        if not is_admin and str(existing.data["organizer_id"]) != str(organizer_id):
            raise HTTPException(status_code=403, detail="You can only update your own posts")
            
        # Update
        update_data = post_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
            
        response = supabase.table("community_posts")\
            .update(update_data)\
            .eq("id", post_id)\
            .execute()
            
        data = response.data[0]
        data["comments"] = data.get("comments_count", 0)
        data["organizer_name"] = organizer_profile.get("organization_name")

        return data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update post error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update post: {str(e)}"
        )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_community_post(
    post_id: str,
    organizer_profile: dict = Depends(get_organizer_or_admin_profile)
):
    """
    Delete a community post.
    Organizers can delete their own posts, admins can delete any post.
    """
    supabase = get_supabase()
    organizer_id = organizer_profile["user_id"]
    is_admin = organizer_profile.get("is_admin", False)
    
    try:
        # Verify ownership (unless admin)
        existing = supabase.table("community_posts")\
            .select("organizer_id")\
            .eq("id", post_id)\
            .single()\
            .execute()
            
        if not existing.data:
            raise HTTPException(status_code=404, detail="Post not found")
            
        # Admins can delete any post, organizers can only delete their own
        if not is_admin and str(existing.data["organizer_id"]) != str(organizer_id):
            raise HTTPException(status_code=403, detail="You can only delete your own posts")
            
        # Delete
        supabase.table("community_posts").delete().eq("id", post_id).execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete post error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete post: {str(e)}"
        )


@router.post("/{post_id}/like")
def like_post(post_id: str):
    """
    Like a community post
    """
    supabase = get_supabase()
    try:
        # Get current likes
        res = supabase.table("community_posts").select("likes").eq("id", post_id).single().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Post not found")
            
        new_likes = (res.data.get("likes") or 0) + 1
        
        # Update likes
        update_res = supabase.table("community_posts").update({"likes": new_likes}).eq("id", post_id).execute()
        return update_res.data[0]
    except Exception as e:
        print(f"Like post error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
