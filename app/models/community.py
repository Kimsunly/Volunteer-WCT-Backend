from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ============================================
# ENUMS
# ============================================

class VisibilityEnum(str, Enum):
    """Visibility status for content"""
    PUBLIC = "public"
    PRIVATE = "private"

class CommunityStatusEnum(str, Enum):
    """Community post status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class CommunityCategoryEnum(str, Enum):
    """Community post categories"""
    UPDATE = "update"
    EVENT = "event"
    DISCUSSION = "discussion"
    STORY = "story"

# ============================================
# MODELS
# ============================================

class CommunityPostBase(BaseModel):
    """Base community post fields"""
    title: str = Field(..., min_length=5, max_length=200)
    title_kh: Optional[str] = Field(None, max_length=200)
    content: str = Field(..., min_length=10)
    content_kh: Optional[str] = None
    category: CommunityCategoryEnum
    images: List[str] = Field(default_factory=list)
    visibility: VisibilityEnum = VisibilityEnum.PUBLIC
    tags: List[str] = Field(default_factory=list)

class CommunityPostCreate(CommunityPostBase):
    """Create community post request"""
    # Organizers: status defaults to approved (handled in logic) or pending
    # Admin: status defaults to approved
    pass

class CommunityPostUpdate(BaseModel):
    """Update community post - all fields optional"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    title_kh: Optional[str] = None
    content: Optional[str] = Field(None, min_length=10)
    content_kh: Optional[str] = None
    category: Optional[CommunityCategoryEnum] = None
    images: Optional[List[str]] = None
    visibility: Optional[VisibilityEnum] = None
    tags: Optional[List[str]] = None

class CommunityPostResponse(CommunityPostBase):
    """Community post response (Public/Organizer view)"""
    id: str
    organizer_id: str
    organizer_name: Optional[str] = None  # Fetched via join
    likes: int = 0
    comments: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: CommunityStatusEnum
    
    class Config:
        from_attributes = True
        populate_by_name = True
