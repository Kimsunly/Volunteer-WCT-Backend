
from fastapi import APIRouter, HTTPException, status
from app.models.contact import ContactMessageCreate, ContactMessageResponse
from app.database import get_supabase
from datetime import datetime

router = APIRouter(prefix="/api/contact", tags=["Contact"])

@router.post("", response_model=ContactMessageResponse, status_code=status.HTTP_201_CREATED)
def submit_contact_message(message: ContactMessageCreate):
    """
    Submit a contact message
    """
    supabase = get_supabase()
    try:
        data = message.model_dump()
        data['created_at'] = datetime.utcnow().isoformat()
        
        result = supabase.table("contact_messages").insert(data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit message"
            )
            
        return result.data[0]
    except Exception as e:
        print(f"Contact submit error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit message: {str(e)}"
        )
