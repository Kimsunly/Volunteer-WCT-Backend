"""
Comments Router - Allow all authenticated users to comment on opportunities, blogs, and community posts
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import get_supabase
from app.models.comment import (
    CommentCreate, 
    CommentUpdate, 
    CommentResponse, 
    CommentsListResponse
)
from app.utils.security import get_current_user, get_current_user_optional, extract_user_id


router = APIRouter(prefix="/comments", tags=["Comments"])


def get_user_info(user_id: str) -> dict:
    """Get user name and avatar from user_profiles"""
    supabase = get_supabase()
    try:
        result = supabase.table("user_profiles").select("first_name, last_name, avatar_url").eq("user_id", user_id).execute()
        if result.data and len(result.data) > 0:
            user_data = result.data[0]
            first_name = user_data.get("first_name", "")
            last_name = user_data.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip() if first_name or last_name else "Anonymous"
            return {
                "user_name": full_name,
                "user_avatar": user_data.get("avatar_url")
            }
        return {"user_name": "Anonymous", "user_avatar": None}
    except Exception as e:
        print(f"Error getting user info: {e}")
        return {"user_name": "Anonymous", "user_avatar": None}


@router.get("/entity/{entity_type}/{entity_id}", response_model=CommentsListResponse)
def get_comments_for_entity(
    entity_type: str,
    entity_id: str,  # Changed from UUID4 to str to support both int and UUID
    limit: int = Query(20, ge=1, le=100, description="Number of comments per page"),
    offset: int = Query(0, ge=0, description="Number of comments to skip"),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get all comments for a specific entity (opportunity, blog, or community post)
    
    - **Public access**: Anyone can view visible comments
    - **entity_type**: 'opportunity', 'blog', or 'community_post'
    - **entity_id**: ID of the entity (int for opportunities, UUID for others)
    - Returns comments with user information
    """
    supabase = get_supabase()
    try:
        # Validate entity_type
        if entity_type not in ['opportunity', 'community_post', 'blog']:
            raise HTTPException(status_code=400, detail="Invalid entity_type. Must be 'opportunity', 'blog', or 'community_post'")
        
        # Build query - only show visible comments to non-admin users
        query = supabase.table("comments").select("*", count="exact")
        # Convert entity_id to string to match database storage format
        query = query.eq("entity_type", entity_type).eq("entity_id", str(entity_id))
        
        # Non-admin users only see visible comments
        user_role = getattr(current_user, 'role', None) if current_user else None
        if not current_user or user_role != "admin":
            query = query.eq("status", "visible")
        
        # Order by newest first
        query = query.order("created_at", desc=True)
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        
        comments = []
        current_user_id = extract_user_id(current_user) if current_user else None
        
        for comment in result.data:
            # Get user info
            user_info = get_user_info(comment["user_id"])
            
            # Check if current user can edit/delete
            can_modify = current_user_id == comment["user_id"]
            
            comments.append(CommentResponse(
                id=comment["id"],
                user_id=comment["user_id"],
                user_name=user_info["user_name"],
                user_avatar=user_info["user_avatar"],
                entity_type=comment["entity_type"],
                entity_id=comment["entity_id"],
                content=comment["content"],
                status=comment["status"],
                created_at=comment["created_at"],
                updated_at=comment.get("updated_at"),
                can_edit=can_modify,
                can_delete=can_modify
            ))
        
        total = result.count if result.count else 0
        
        return CommentsListResponse(
            comments=comments,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR in get_comments_for_entity: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch comments: {str(e)}")


@router.post("/", response_model=CommentResponse, status_code=201)
def create_comment(
    comment: CommentCreate,
    current_user = Depends(get_current_user)
):
    """
    Create a new comment on an opportunity, blog, or community post
    
    - **Authentication required**: Any logged-in user can comment
    - **entity_type**: 'opportunity', 'blog', or 'community_post'
    - **entity_id**: ID of the entity to comment on
    - **content**: Comment text (1-2000 characters)
    """
    supabase = get_supabase()
    try:
        # Verify the entity exists
        entity_table_map = {
            'opportunity': 'opportunities',
            'community_post': 'community_posts',
            'blog': 'blogs'
        }
        
        entity_table = entity_table_map.get(comment.entity_type)
        if not entity_table:
            raise HTTPException(status_code=400, detail="Invalid entity_type")
        
        # Check if entity exists
        entity_check = supabase.table(entity_table).select("id").eq("id", str(comment.entity_id)).execute()
        if not entity_check.data:
            raise HTTPException(status_code=404, detail=f"{comment.entity_type} not found")
        
        # Create comment
        user_id = extract_user_id(current_user)
        new_comment = {
            "user_id": user_id,
            "entity_type": comment.entity_type,
            "entity_id": str(comment.entity_id),
            "content": comment.content,
            "status": "visible",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("comments").insert(new_comment).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create comment")
        
        created_comment = result.data[0]
        
        # Get user info
        user_info = get_user_info(user_id)
        
        return CommentResponse(
            id=created_comment["id"],
            user_id=created_comment["user_id"],
            user_name=user_info["user_name"],
            user_avatar=user_info["user_avatar"],
            entity_type=created_comment["entity_type"],
            entity_id=created_comment["entity_id"],
            content=created_comment["content"],
            status=created_comment["status"],
            created_at=created_comment["created_at"],
            updated_at=created_comment.get("updated_at"),
            can_edit=True,
            can_delete=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    current_user = Depends(get_current_user)
):
    """
    Update your own comment
    
    - **Authentication required**: Only the comment author can update
    - Users can only update their own comments
    - Admins can update any comment
    """
    supabase = get_supabase()
    try:
        # Get the comment
        result = supabase.table("comments").select("*").eq("id", str(comment_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        existing_comment = result.data[0]
        
        # Check if user owns the comment or is admin
        user_id = extract_user_id(current_user)
        user_role = getattr(current_user, 'role', None)
        if existing_comment["user_id"] != user_id and user_role != "admin":
            raise HTTPException(status_code=403, detail="You can only update your own comments")
        
        # Update comment
        update_data = {
            "content": comment_update.content,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        update_result = supabase.table("comments").update(update_data).eq("id", str(comment_id)).execute()
        
        if not update_result.data:
            raise HTTPException(status_code=500, detail="Failed to update comment")
        
        updated_comment = update_result.data[0]
        
        # Get user info
        user_info = get_user_info(updated_comment["user_id"])
        
        return CommentResponse(
            id=updated_comment["id"],
            user_id=updated_comment["user_id"],
            user_name=user_info["user_name"],
            user_avatar=user_info["user_avatar"],
            entity_type=updated_comment["entity_type"],
            entity_id=updated_comment["entity_id"],
            content=updated_comment["content"],
            status=updated_comment["status"],
            created_at=updated_comment["created_at"],
            updated_at=updated_comment.get("updated_at"),
            can_edit=True,
            can_delete=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update comment: {str(e)}")


@router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment_id: str,
    current_user = Depends(get_current_user)
):
    """
    Delete your own comment
    
    - **Authentication required**: Only the comment author can delete
    - Users can only delete their own comments
    - Admins can delete any comment
    """
    supabase = get_supabase()
    try:
        # Get the comment
        result = supabase.table("comments").select("*").eq("id", str(comment_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        existing_comment = result.data[0]
        
        # Check if user owns the comment or is admin
        user_id = extract_user_id(current_user)
        user_role = getattr(current_user, 'role', None)
        if existing_comment["user_id"] != user_id and user_role != "admin":
            raise HTTPException(status_code=403, detail="You can only delete your own comments")
        
        # Delete comment
        delete_result = supabase.table("comments").delete().eq("id", str(comment_id)).execute()
        
        if not delete_result.data:
            raise HTTPException(status_code=500, detail="Failed to delete comment")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")


@router.get("/my-comments", response_model=CommentsListResponse)
def get_my_comments(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """
    Get all comments made by the current user
    
    - **Authentication required**
    - Returns all your comments across all entities
    """
    supabase = get_supabase()
    try:
        # Get user's comments
        user_id = extract_user_id(current_user)
        query = supabase.table("comments").select("*", count="exact")
        query = query.eq("user_id", user_id)
        query = query.order("created_at", desc=True)
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        
        comments = []
        user_info = get_user_info(user_id)
        
        for comment in result.data:
            comments.append(CommentResponse(
                id=comment["id"],
                user_id=comment["user_id"],
                user_name=user_info["user_name"],
                user_avatar=user_info["user_avatar"],
                entity_type=comment["entity_type"],
                entity_id=comment["entity_id"],
                content=comment["content"],
                status=comment["status"],
                created_at=comment["created_at"],
                updated_at=comment.get("updated_at"),
                can_edit=True,
                can_delete=True
            ))
        
        total = result.count if result.count else 0
        
        return CommentsListResponse(
            comments=comments,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch your comments: {str(e)}")
