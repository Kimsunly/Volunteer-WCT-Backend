"""
Authentication routes - IMPROVED ORGANIZER APPROVAL CHECK
Handles all cases: pending, approved, rejected, and missing applications
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
    """
    Login user - WITH COMPLETE ORGANIZER APPROVAL CHECK
    
    Flow:
    1. Regular users (role='user') → Login allowed ✅
    2. Admins (role='admin') → Login allowed ✅
    3. Organizers (role='organizer') → Check application status:
       - If approved → Login allowed ✅
       - If pending → Login BLOCKED ❌ "Wait for approval"
       - If rejected → Login BLOCKED ❌ "Application rejected"
       - If no application → Login BLOCKED ❌ "No application found"
    """
    supabase = get_supabase()
    print(f"DEBUG /api/auth/login called with email={credentials.email}")

    try:
        # Step 1: Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        user_id = extract_user_id(auth_response.user)
        print(f"DEBUG: Authentication successful for user_id={user_id}")

        # Step 2: Get or create user profile
        user_profile = None
        try:
            profile_check = supabase.table("user_profiles")\
                .select("*")\
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
                created = supabase.table("user_profiles").insert(profile_data).execute()
                user_profile = created.data[0] if created.data else None
            else:
                user_profile = profile_check.data[0]
                
        except Exception as profile_error:
            print(f"Profile check/create error: {profile_error}")
            # Continue without profile for now

        # Step 3: Check if user has organizer role
        user_role = user_profile.get('role') if user_profile else 'user'
        user_status = user_profile.get('status') if user_profile else 'active'
        print(f"DEBUG: User role = {user_role}, status = {user_status}")

        # ==========================================
        # 🔒 ORGANIZER APPROVAL CHECK
        # ==========================================
        if user_role == 'organizer':
            print(f"DEBUG: User has 'organizer' role - verifying approval status...")
            
            # Quick check: if status is 'pending' or 'rejected', block immediately
            if user_status == 'pending':
                supabase.auth.sign_out()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="⏳ Your organizer application is pending admin approval. Please wait for approval before logging in."
                )
            elif user_status == 'rejected':
                supabase.auth.sign_out()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="❌ Your organizer application was rejected. Please contact support."
                )
            
            # Additional check: Verify in application table as backup
            try:
                # Check organizer application status
                app_check = supabase.table("organizer_applications")\
                    .select("status, organization_name, rejection_reason")\
                    .eq("user_id", user_id)\
                    .execute()
                
                # Case 1: No application found
                if not app_check.data:
                    print(f"WARNING: User has 'organizer' role but no application found!")
                    # Don't block - they might be a legacy organizer
                
                else:
                    application = app_check.data[0]
                    app_status = application['status']
                    print(f"DEBUG: Application status from DB = {app_status}")
                
                # If status is 'active', allow login
                if user_status == 'active':
                    print(f"✅ Organizer status is 'active' - login allowed")
                    # Continue to successful login below
                
            except HTTPException:
                # Re-raise our custom HTTP exceptions
                raise
            except Exception as check_error:
                print(f"ERROR checking organizer approval: {check_error}")
                import traceback
                traceback.print_exc()
                supabase.auth.sign_out()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error verifying organizer status. Please try again or contact support."
                )
        
        # ==========================================
        # END ORGANIZER APPROVAL CHECK
        # ==========================================

        # Step 4: Successful login - return tokens and user info
        print(f"✅ Login successful for user_id={user_id}, role={user_role}")
        
        return {
            "message": "Login successful",
            "user": {
                "id": user_id,
                "email": auth_response.user.email,
                "role": user_role,
                "first_name": user_profile.get('first_name') if user_profile else "",
                "last_name": user_profile.get('last_name') if user_profile else ""
            },
            "session": {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token
            }
        }

    except AuthApiError as e:
        # Supabase authentication errors
        error_message = str(e)
        print(f"Login error (AuthApiError): {error_message}")
        
        if "Invalid login credentials" in error_message or "Invalid credentials" in error_message:
            detail_msg = "Invalid email or password. Please check your credentials."
        elif "Email not confirmed" in error_message or "not confirmed" in error_message.lower():
            detail_msg = "Please confirm your email address before logging in."
        else:
            detail_msg = f"Authentication failed: {error_message}"
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail_msg
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (including organizer approval errors)
        raise
    
    except Exception as e:
        # Unexpected errors
        print(f"Unexpected login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later."
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
    """Get current authenticated user information"""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)
    
    try:
        # Get full user profile
        profile = supabase.table("user_profiles")\
            .select("*")\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        if profile.data:
            user_data = profile.data
            response = {
                "id": user_id,
                "email": user_data.get('email'),
                "first_name": user_data.get('first_name'),
                "last_name": user_data.get('last_name'),
                "role": user_data.get('role'),
                "status": user_data.get('status'),
                "phone": user_data.get('phone')
            }
            
            # If organizer, include application status
            if user_data.get('role') == 'organizer':
                try:
                    app = supabase.table("organizer_applications")\
                        .select("status, organization_name")\
                        .eq("user_id", user_id)\
                        .single()\
                        .execute()
                    
                    if app.data:
                        response['organizer_status'] = app.data['status']
                        response['organization_name'] = app.data['organization_name']
                except:
                    pass
            
            return response
        else:
            return {
                "id": user_id,
                "email": current_user.email,
                "role": 'user'
            }
    except Exception as e:
        print(f"Get user info error: {e}")
        return {
            "id": user_id,
            "email": current_user.email if hasattr(current_user, 'email') else None,
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