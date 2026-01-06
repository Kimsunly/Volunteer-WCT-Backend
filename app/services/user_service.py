from fastapi import HTTPException, status
from app.database import get_supabase

class UserService:
    def __init__(self):
        self.supabase = get_supabase()
    
    async def get_profile(self, user_id: str):
        response = self.supabase.table("user_profiles")\
            .select("*")\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return response.data
    
    async def update_profile(self, user_id: str, profile_data):
        update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
        
        response = self.supabase.table("user_profiles")\
            .update(update_data)\
            .eq("user_id", user_id)\
            .execute()
        
        return {"message": "Profile updated", "data": response.data[0]}
    
    async def get_stats(self, user_id: str):
        # Implementation here
        pass
    
    async def get_activities(self, user_id: str, status_filter: str = None):
        # Implementation here
        pass
    
    async def get_achievements(self, user_id: str):
        # Implementation here
        pass