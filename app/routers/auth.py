"""
Authentication routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from gotrue.errors import AuthApiError
from datetime import datetime

from app.models.user import UserRegister, UserLogin
from app.database import get_supabase
from app.utils.security import get_current_user, extract_user_id

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register new user"""
    supabase = get_supabase()
    
    try:
        # Create auth user
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. User may already exist."
            )
        
        # Extract clean user_id
        user_id = extract_user_id(auth_response.user)
        
        # Create user profile
        profile_data = {
            "user_id": user_id,
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "phone": user_data.phone,
            "role": "user",
            "status": "active",
            "volunteer_level": "bronze",
            "rating": 0.0,
            "points": 0
        }
        
        try:
            supabase.table("user_profiles").insert(profile_data).execute()
        except Exception as db_error:
            print(f"Database error creating profile: {db_error}")
        
        return {
            "message": "Registration successful!",
            "user": {
                "id": user_id,
                "email": auth_response.user.email
            },
            "session": {
                "access_token": auth_response.session.access_token if auth_response.session else None,
                "refresh_token": auth_response.session.refresh_token if auth_response.session else None
            }
        }
        
    except AuthApiError as e:
        print(f"Supabase Auth Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error in register: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration error: {str(e)}"
        )


@router.post("/login")
async def login(credentials: UserLogin):
    """Login user"""
    supabase = get_supabase()
    print(f"DEBUG /api/auth/login called with email={credentials.email}")
    print(f"DEBUG password received: {'*' * len(credentials.password) if credentials.password else 'None'}")

    try:
        # Sign in
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        print(f"DEBUG sign_in_with_password returned: {getattr(auth_response, '__dict__', str(auth_response))}")

        if not auth_response.user or not auth_response.session:
            print("DEBUG: Auth response missing user or session")
            print(f"DEBUG: user={auth_response.user}, session={auth_response.session}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Extract clean user_id
        user_id = extract_user_id(auth_response.user)

        # Check/create profile
        try:
            profile_check = supabase.table("user_profiles")\
                .select("id")\
                .eq("user_id", user_id)\
                .execute()

            if not profile_check.data:
                # Create profile if missing
                profile_data = {
                    "user_id": user_id,
                    "email": credentials.email,
                    "first_name": "",
                    "last_name": "",
                    "role": "user",
                    "status": "active",
                    "volunteer_level": "bronze",
                    "rating": 0.0,
                    "points": 0
                }
                supabase.table("user_profiles").insert(profile_data).execute()
        except Exception as profile_error:
            print(f"Profile check/create error: {profile_error}")

        print(f"DEBUG: login success for user_id={user_id}")
        return {
            "message": "Login successful",
            "user": {
                "id": user_id,
                "email": auth_response.user.email
            },
            "session": {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token
            }
        }

    except AuthApiError as e:
        # Extract more detailed error information
        error_message = str(e)
        error_detail = getattr(e, 'message', error_message)
        error_status = getattr(e, 'status_code', None)
        
        print(f"Login error (AuthApiError): {error_message}")
        print(f"Login error detail: {error_detail}")
        print(f"Login error status: {error_status}")
        print(f"Login error type: {type(e)}")
        print(f"Login error attributes: {dir(e)}")
        
        # Check for specific error types
        if "Invalid login credentials" in error_message or "Invalid credentials" in error_message:
            detail_msg = "Invalid email or password. Please check your credentials and try again."
        elif "Email not confirmed" in error_message or "not confirmed" in error_message.lower():
            detail_msg = "Please confirm your email address before logging in."
        else:
            detail_msg = f"Authentication failed: {error_detail}"
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail_msg
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected login error: {e}")
        print(f"Unexpected login error type: {type(e)}")
        import traceback
        print(f"Unexpected login error traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """Logout user"""
    supabase = get_supabase()
    
    try:
        supabase.auth.sign_out()
        return {"message": "Logout successful"}
    except Exception as e:
        print(f"Logout error: {e}")
        return {"message": "Logout completed"}


@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role if hasattr(current_user, 'role') else 'user'
    }


# --- Development helper endpoints (local only) ---
@router.get("/debug/ping")
async def debug_ping():
    """Simple ping to verify server is up and responding"""
    print("DEBUG /api/auth/debug/ping received")
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.post("/debug/echo")
async def debug_echo(payload: dict):
    """Echo posted JSON back to the client (useful for debugging request bodies)"""
    print(f"DEBUG /api/auth/debug/echo payload: {payload}")
    return {"received": payload}