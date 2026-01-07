"""
Organizer registration models - SIMPLIFIED VERSION
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class OrganizerType(str, Enum):
    """Types of organizations"""
    NGO = "ngo"
    NONPROFIT = "nonprofit"
    COMMUNITY = "community"
    EDUCATIONAL = "educational"
    RELIGIOUS = "religious"
    GOVERNMENT = "government"
    CORPORATE = "corporate"
    OTHER = "other"


class ApplicationStatus(str, Enum):
    """Status of organizer application"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class OrganizerRegister(BaseModel):
    """Simplified organizer registration - only essential fields"""
    organization_name: str = Field(..., min_length=3, max_length=200)
    email: EmailStr
    phone: str = Field(..., min_length=8, max_length=20)
    password: str = Field(..., min_length=6)
    organizer_type: OrganizerType


class OrganizerProfile(BaseModel):
    """Profile data for approved organizers"""
    organization_name: str = Field(..., min_length=3, max_length=200)
    email: EmailStr
    organizer_type: OrganizerType
    phone: str = Field(..., min_length=8, max_length=20)



class OrganizerApplicationResponse(BaseModel):
    """Organizer application response"""
    id: int
    user_id: str
    organization_name: str
    email: EmailStr
    phone: str
    organizer_type: str
    card_image_url: Optional[str] = None
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    rejection_reason: Optional[str] = None


class ApplicationAction(BaseModel):
    """Admin action on application"""
    reason: Optional[str] = None