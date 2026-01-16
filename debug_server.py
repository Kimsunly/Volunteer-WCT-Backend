
import uvicorn
from fastapi import FastAPI, Depends
from app.main import app as main_app
from app.utils.security import get_current_user
from app.routers.opportunity_with_images import get_organizer_profile

# Mock organizer profile
async def mock_get_organizer_profile():
    return {"id": 2} # Use an existing organizer ID

# Override dependency
main_app.dependency_overrides[get_organizer_profile] = mock_get_organizer_profile

if __name__ == "__main__":
    uvicorn.run(main_app, host="0.0.0.0", port=8002)
