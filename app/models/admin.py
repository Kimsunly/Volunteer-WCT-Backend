"""
Admin models for all admin-facing operations
Follows specification for admin dashboard, organizers, categories, opportunities, blogs, community, users
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

from app.models.community import (
    VisibilityEnum,
    CommunityStatusEnum,
    CommunityCategoryEnum,
    CommunityPostBase
)


# ============================================
# ENUMS
# ============================================

class OrganizerStatusEnum(str, Enum):
    """Organizer application/account status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class OpportunityStatusEnum(str, Enum):
    """Opportunity status"""
    ACTIVE = "active"
    PENDING = "pending"
    CLOSED = "closed"


class CommentStatusEnum(str, Enum):
    """Comment moderation status"""
    VISIBLE = "visible"
    HIDDEN = "hidden"
    FLAGGED = "flagged"


class UserRoleEnum(str, Enum):
    """User roles"""
    USER = "user"
    ORGANIZER = "organizer"
    ADMIN = "admin"


class UserStatusEnum(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


# ============================================
# DASHBOARD METRICS
# ============================================

class DashboardMetrics(BaseModel):
    """Admin dashboard aggregates"""
    donations_total: float = 0.0
    opportunities_count: dict = Field(default_factory=dict)  # {status: count}
    organizers_count: dict = Field(default_factory=dict)  # {status: count}
    users_count: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "donations_total": 15000.50,
                "opportunities_count": {
                    "active": 25,
                    "pending": 5,
                    "closed": 10
                },
                "organizers_count": {
                    "pending": 3,
                    "verified": 15,
                    "rejected": 2,
                    "suspended": 1
                },
                "users_count": 1250
            }
        }


# ============================================
# ORGANIZERS
# ============================================

class OrganizerListItem(BaseModel):
    """Organizer list item for admin"""
    id: str
    org_name: str = Field(alias="organization_name")
    contact_person: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    registration_number: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    requested_at: Optional[datetime] = Field(alias="submitted_at")
    status: OrganizerStatusEnum
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    reject_reason: Optional[str] = Field(None, alias="rejection_reason")
    
    class Config:
        populate_by_name = True


class OrganizerApproveRequest(BaseModel):
    """Request to approve organizer"""
    pass  # No body needed, just POST to approve


class OrganizerRejectRequest(BaseModel):
    """Request to reject organizer"""
    reason: str = Field(..., min_length=10, max_length=500)


class OrganizerSuspendRequest(BaseModel):
    """Request to suspend organizer"""
    reason: str = Field(..., min_length=10, max_length=500)


# ============================================
# CATEGORIES
# ============================================

class CategoryBase(BaseModel):
    """Base category fields"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = None  # Icon name or URL
    color: Optional[str] = None  # Hex color code
    active: bool = True


class CategoryCreate(CategoryBase):
    """Create category request"""
    pass


class CategoryUpdate(BaseModel):
    """Update category request - all fields optional"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = None
    color: Optional[str] = None
    active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Category response"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================
# OPPORTUNITIES
# ============================================

class OpportunityListItem(BaseModel):
    """Opportunity list item for admin"""
    id: str
    title: str
    organizer: str  # Organizer name
    organizer_id: int
    category: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    visibility: VisibilityEnum = VisibilityEnum.PUBLIC
    status: OpportunityStatusEnum = OpportunityStatusEnum.PENDING
    registered: int = 0  # Count of registrations
    posted_at: Optional[datetime] = Field(alias="created_at")
    
    class Config:
        populate_by_name = True


class OpportunityCreate(BaseModel):
    """Create opportunity (admin creates directly, no organizer needed)"""
    title: str = Field(..., min_length=5, max_length=200)
    category: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    visibility: VisibilityEnum = VisibilityEnum.PUBLIC
    status: OpportunityStatusEnum = OpportunityStatusEnum.ACTIVE


class OpportunityUpdate(BaseModel):
    """Update opportunity - all fields optional"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    category: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    visibility: Optional[VisibilityEnum] = None
    status: Optional[OpportunityStatusEnum] = None


# ============================================
# BLOGS/TIPS
# ============================================

class BlogBase(BaseModel):
    """Base blog fields"""
    title: str = Field(..., min_length=5, max_length=200)
    category: Optional[str] = None
    image: Optional[str] = None  # Image URL
    content: str = Field(..., min_length=10)
    author: Optional[str] = None
    published: bool = False


class BlogCreate(BlogBase):
    """Create blog request"""
    pass


class BlogUpdate(BaseModel):
    """Update blog - all fields optional"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    category: Optional[str] = None
    image: Optional[str] = None
    content: Optional[str] = Field(None, min_length=10)
    author: Optional[str] = None
    published: Optional[bool] = None


class BlogResponse(BlogBase):
    """Blog response"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================
# COMMUNITY POSTS
# ============================================

class CommunityPostListItem(BaseModel):
    """Community post for moderation"""
    id: str
    organizer_id: str
    organizer_name: Optional[str] = None
    title: str
    title_kh: Optional[str] = None
    content: str
    content_kh: Optional[str] = None
    category: CommunityCategoryEnum
    images: List[str] = Field(default_factory=list)
    visibility: VisibilityEnum = VisibilityEnum.PUBLIC
    likes: int = 0
    comments: int = 0  # Renamed from comments_count
    created_at: datetime
    status: CommunityStatusEnum = CommunityStatusEnum.PENDING
    tags: List[str] = Field(default_factory=list)
    reject_reason: Optional[str] = Field(None, alias="rejection_reason")
    
    class Config:
        populate_by_name = True


class CommunityPostCreate(CommunityPostBase):
    """Create community post (admin can create directly)"""
    status: CommunityStatusEnum = CommunityStatusEnum.APPROVED  # Admin posts auto-approved


class CommunityApproveRequest(BaseModel):
    """Approve community post"""
    pass


class CommunityRejectRequest(BaseModel):
    """Reject community post"""
    reason: str = Field(..., min_length=10, max_length=500)


# ============================================
# USERS
# ============================================

class UserListItem(BaseModel):
    """User list item for admin"""
    id: str
    name: Optional[str] = None
    email: EmailStr
    role: UserRoleEnum = UserRoleEnum.USER
    status: UserStatusEnum = UserStatusEnum.ACTIVE
    avatar: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserRoleChangeRequest(BaseModel):
    """Change user role"""
    role: UserRoleEnum


class UserDeactivateRequest(BaseModel):
    """Deactivate user"""
    reason: Optional[str] = None


# ============================================
# COMMENTS
# ============================================

class CommentListItem(BaseModel):
    """Comment for moderation"""
    id: str
    user_id: str
    user_name: Optional[str] = None
    opportunity_id: Optional[str] = None  # or community_post_id
    community_post_id: Optional[str] = None
    content: str
    created_at: datetime
    status: CommentStatusEnum = CommentStatusEnum.VISIBLE
    
    class Config:
        from_attributes = True


class CommentHideRequest(BaseModel):
    """Hide comment"""
    pass


class CommentApproveRequest(BaseModel):
    """Approve comment"""
    pass


# ============================================
# DONATIONS
# ============================================

class DonationListItem(BaseModel):
    """Donation record"""
    id: str
    donor_name: Optional[str] = None
    amount: float
    currency: str = "USD"
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# PAGINATION & FILTERING
# ============================================

class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
    search: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    visibility: Optional[str] = None
    role: Optional[str] = None
    order: str = Field("desc", pattern="^(asc|desc)$")
    sort: str = Field("created_at", pattern="^(created_at|title|name|email)$")


class PaginatedResponse(BaseModel):
    """Standard paginated response wrapper"""
    data: List[dict]
    total: int
    limit: int
    offset: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "total": 100,
                "limit": 50,
                "offset": 0
            }
        }
