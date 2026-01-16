
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class BloodDonationCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    dob: str  # YYYY-MM-DD
    blood_type: str = Field(..., pattern="^(A|B|AB|O)[+-]$")
    agree: bool = True

class BloodDonationResponse(BloodDonationCreate):
    id: str
    created_at: datetime
    status: str = "pending"

    class Config:
        from_attributes = True
