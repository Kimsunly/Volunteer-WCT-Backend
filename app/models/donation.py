
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class DonationCreate(BaseModel):
    donor_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    cause: Optional[str] = "general"
    donation_type: str = "once" # once | monthly
    message: Optional[str] = None

class DonationResponse(DonationCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
