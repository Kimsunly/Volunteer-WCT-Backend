
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class ContactMessageCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    phone: Optional[str] = None
    message: str = Field(..., min_length=10, max_length=1000)

class ContactMessageResponse(ContactMessageCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
