"""Pydantic models for volunteer opportunities"""
from typing import Optional
from datetime import date, time
from pydantic import BaseModel, Field


class OpportunityCreate(BaseModel):
    """Payload for creating a new opportunity (organizer only)"""
    
    # Required fields
    title: str = Field(..., min_length=1, max_length=200, description="Opportunity title")
    category_label: str = Field(..., description="Category display name (e.g., 'Environmental')")
    location_label: str = Field(..., description="Location display name (e.g., 'Phnom Penh')")
    
    # Optional fields
    images: Optional[str] = Field(None, description="Image URLs (comma-separated or JSON)")
    description: Optional[str] = Field(None, description="Brief description of the opportunity")
    organization: Optional[str] = Field(None, description="Organization name")
    date_range: Optional[date] = Field(None, description="Date of the opportunity")
    time_range: Optional[str] = Field(None, description="Time range (e.g. 8am - 5pm)")
    capacity: Optional[int] = Field(None, ge=0, description="Maximum number of volunteers")
    transport: Optional[str] = Field(None, description="Transportation information")
    housing: Optional[str] = Field(None, description="Housing information")
    meals: Optional[str] = Field(None, description="Meals information")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Beach Cleanup Volunteer",
                "category_label": "Environmental",
                "location_label": "Phnom Penh",
                "images": "https://example.com/beach.jpg",
                "description": "Join us for a beach cleanup event",
                "organization": "Green Earth Cambodia",
                "date_range": "2024-03-15",
                "time_range": "09:00 AM - 05:00 PM",
                "capacity": 50,
                "transport": "Bus provided from city center",
                "housing": "Not provided",
                "meals": "Lunch and snacks included"
            }
        }


class OpportunityUpdate(BaseModel):
    """Payload for updating an opportunity (organizer only - must own it)"""
    
    # All fields optional for partial updates
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category_label: Optional[str] = None
    location_label: Optional[str] = None
    images: Optional[str] = None
    description: Optional[str] = None
    organization: Optional[str] = None
    date_range: Optional[date] = None
    time_range: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=0)
    transport: Optional[str] = None
    housing: Optional[str] = None
    meals: Optional[str] = None
    # Add missing fields
    skills: Optional[list[str]] = None
    tasks: Optional[list[str]] = None
    impact_description: Optional[str] = None
    is_private: Optional[bool] = None
    access_key: Optional[str] = None
    status: Optional[str] = None # Added status field


class OpportunityResponse(BaseModel):
    """Response model for an opportunity"""
    
    # In this project the opportunities table uses an integer primary key.
    # (If you later migrate to UUIDs, adjust this back to `str`.)
    id: int
    organizer_id: int  # Foreign key to organizer_profiles.id
    title: str
    category_label: str
    location_label: str
    images: Optional[str] = None
    description: Optional[str] = None
    organization: Optional[str] = None
    date_range: Optional[date] = None
    time_range: Optional[str] = None
    capacity: Optional[int] = None
    transport: Optional[str] = None
    housing: Optional[str] = None
    meals: Optional[str] = None
    created_at: str  # Supabase timestamp

    class Config:
        from_attributes = True


class OpportunityListResponse(BaseModel):
    """Response for listing opportunities"""
    
    data: list[OpportunityResponse]
    total: int
    limit: int
    offset: int