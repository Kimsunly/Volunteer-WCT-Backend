"""Pydantic models for volunteer applications to opportunities"""
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ApplicationStatus(str, Enum):
    """Application status values"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class GenderEnum(str, Enum):
    """Gender options"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ApplicationCreate(BaseModel):
    """Payload for creating a new application (user applies to opportunity)"""
    opportunity_id: int = Field(..., description="ID of the opportunity to apply to")
    name: str = Field(..., min_length=1, max_length=100, description="Applicant's full name")
    skills: str = Field(..., min_length=1, max_length=500, description="Skills or qualifications")
    availability: str = Field(..., min_length=1, max_length=200, description="Availability (e.g., 'Weekends', 'Mon-Fri 9am-5pm')")
    email: str = Field(..., description="Contact email")
    phone_number: str = Field(..., min_length=1, max_length=20, description="Phone number")
    sex: GenderEnum = Field(..., description="Gender (male, female, other)")
    message: Optional[str] = Field(None, max_length=2000, description="Optional message to organizer")
    # For private opportunities, the applicant may supply the access key
    access_key: Optional[str] = Field(None, description="Access key for private opportunities (plain text)")
    # Optional CV URL (applicant can upload a CV and include its public URL here)
    cv_url: Optional[str] = Field(None, description="Public URL to applicant CV (PDF/DOCX)")

    class Config:
        json_schema_extra = {
            "example": {
                "opportunity_id": 1,
                "name": "John Doe",
                "skills": "First Aid, Event Management, Communication",
                "availability": "Weekends and holidays",
                "email": "john.doe@example.com",
                "phone_number": "+855 12 345 678",
                "sex": "male",
                "message": "I am excited to volunteer for this opportunity!",
                "access_key": None,
                "cv_url": None
            }
        }


class ApplicationUpdate(BaseModel):
    """Payload for updating an application (organizer approves/rejects, or user withdraws)"""
    status: Optional[ApplicationStatus] = Field(None, description="New status")
    # admin_notes is optional and only used if your table has this column
    # admin_notes: Optional[str] = Field(None, max_length=1000, description="Notes from organizer")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "approved"
            }
        }


class ApplicationResponse(BaseModel):
    """Response model for an application"""
    id: int
    opportunity_id: int
    user_id: str  # UUID from auth.users
    name: Optional[str] = None
    skills: Optional[str] = None
    availability: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    sex: Optional[str] = None
    message: Optional[str] = None
    status: ApplicationStatus
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApplicationWithDetails(ApplicationResponse):
    """Application with opportunity and user details (for listing)"""
    opportunity_title: Optional[str] = None
    applicant_email: Optional[str] = None
    applicant_name: Optional[str] = None



class ApplicationListResponse(BaseModel):
    """Response for listing applications"""
    data: list[ApplicationWithDetails]
    total: int
    limit: int
    offset: int
