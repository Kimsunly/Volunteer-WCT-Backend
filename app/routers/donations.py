
from fastapi import APIRouter, HTTPException, status
from app.models.donation import DonationCreate, DonationResponse
from app.database import get_supabase
from datetime import datetime

router = APIRouter(prefix="/api/donations", tags=["Donations"])

@router.post("/", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
async def create_donation(donation: DonationCreate):
    """
    Submit a new donation
    """
    supabase = get_supabase()
    try:
        data = donation.model_dump()
        data['created_at'] = datetime.utcnow().isoformat()
        
        result = supabase.table("donations").insert(data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record donation"
            )
            
        return result.data[0]
    except Exception as e:
        print(f"Record donation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record donation: {str(e)}"
        )


# Blood Donation Endpoint
from app.models.blood_donation import BloodDonationCreate, BloodDonationResponse

@router.post("/blood", response_model=BloodDonationResponse, status_code=status.HTTP_201_CREATED)
async def register_blood_donation(donation: BloodDonationCreate):
    """
    Register for blood donation
    """
    supabase = get_supabase()
    try:
        data = donation.model_dump()
        data['created_at'] = datetime.utcnow().isoformat()
        data['status'] = 'pending'
        
        result = supabase.table("blood_donations").insert(data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register blood donation"
            )
            
        return result.data[0]
    except Exception as e:
        print(f"Blood donation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register: {str(e)}"
        )
