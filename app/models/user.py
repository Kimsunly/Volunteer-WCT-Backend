"""
User Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ORGANIZER = "organizer"
    ADMIN = "admin"


class AvailabilityType(str, Enum):
    WEEKEND = "weekend"
    WEEKDAYS = "weekdays"
    FLEXIBLE = "flexible"


class TimePreference(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    """User profile update request"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[date] = None
    about_me: Optional[str] = Field(None, max_length=400)
    skills: Optional[str] = None
    availability: Optional[AvailabilityType] = None
    time_preference: Optional[TimePreference] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_district: Optional[str] = None
    address_province: Optional[str] = None


class UserProfileResponse(BaseModel):
    """User profile response"""
    id: int
    user_id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    role: UserRole
    volunteer_level: str
    rating: float
    points: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User statistics for dashboard"""
    total_hours: float
    completed_projects: int
    upcoming_events: int
    points: int


class ProfileCompleteness(BaseModel):
    """Profile completion status"""
    percentage: int
    filled_fields: int
    total_fields: int
    missing_fields: list[str]
    is_complete: bool