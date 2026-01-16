"""
Security and authentication utilities
"""
from fastapi import Depends, HTTPException, status
from typing import Optional
import asyncio
import hashlib
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from gotrue.errors import AuthApiError
from app.database import get_supabase

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Verify JWT token and get current user
    FIXED: Properly extracts user_id as clean string
    """
    token = credentials.credentials
    supabase = get_supabase()
    
    try:
        # Get user from token
        # Using synchronous call because FastAPI runs 'def' dependencies in a thread pool
        response = supabase.auth.get_user(token)
        
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # IMPORTANT: Extract user object with clean UUID string
        user = response.user
        
        return user
        
    except AuthApiError as e:
        print(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except Exception as e:
        print(f"Unexpected auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )



def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Get current user if authenticated, else return None
    """
    if not credentials:
        return None
        
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None


def extract_user_id(user) -> str:
    """
    Extract user_id as clean UUID string
    This fixes the Supabase filter parsing issue
    """
    # Get the raw ID
    if hasattr(user, 'id'):
        user_id = user.id
    else:
        user_id = user.get('id', '')
    
    # Convert to string and clean it
    user_id_str = str(user_id).strip().lower()
    
    # Debug output
    print(f"DEBUG extract_user_id: Input type={type(user_id)}, Input value={user_id}")
    print(f"DEBUG extract_user_id: Output={user_id_str}, Length={len(user_id_str)}")
    
    # Validate UUID format (should be 36 characters with dashes)
    if len(user_id_str) != 36 or user_id_str.count('-') != 4:
        print(f"ERROR: Invalid UUID format: {user_id_str}")
        raise ValueError(f"Invalid user_id format: {user_id_str} (length: {len(user_id_str)})")
    
    
    return user_id_str


def hash_secret(secret: str) -> str:
    """Hash a secret string using SHA256"""
    if not secret:
        return ""
    return hashlib.sha256(str(secret).encode()).hexdigest()
