"""Pydantic models for comments system"""
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, UUID4


class CommentCreate(BaseModel):
    """Create a new comment on an opportunity, blog, or community post"""
    entity_type: Literal['opportunity', 'community_post', 'blog'] = Field(
        ..., 
        description="Type of entity being commented on"
    )
    entity_id: str = Field(..., description="ID of the entity (int for opportunities, UUID for blogs/posts)")
    content: str = Field(..., min_length=1, max_length=2000, description="Comment content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity_type": "opportunity",
                "entity_id": "1",
                "content": "This looks like an amazing opportunity! I'd love to participate."
            }
        }


class CommentUpdate(BaseModel):
    """Update an existing comment (only by the author)"""
    content: str = Field(..., min_length=1, max_length=2000, description="Updated comment content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Updated: This looks like an amazing opportunity! Count me in!"
            }
        }


class CommentResponse(BaseModel):
    """Comment response with user information"""
    id: str
    user_id: str
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    entity_type: str
    entity_id: str
    content: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # User can edit/delete only their own comments
    can_edit: bool = False
    can_delete: bool = False
    
    class Config:
        from_attributes = True


class CommentsListResponse(BaseModel):
    """Paginated list of comments"""
    comments: list[CommentResponse]
    total: int
    limit: int
    offset: int
    has_more: bool
