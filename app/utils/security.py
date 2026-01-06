from fastapi import Request, HTTPException, status
from typing import Any, Optional


def extract_user_id(user: Any) -> Optional[str]:
    """Extract a user id from a supabase user object or plain dict/object."""
    if not user:
        return None

    # dict-like
    if isinstance(user, dict):
        return user.get("id") or user.get("user_id") or user.get("sub")

    # object-like
    return getattr(user, "id", None) or getattr(user, "user_id", None) or getattr(user, "sub", None)


class CurrentUser:
    def __init__(self, id: str, email: Optional[str] = None, role: str = "user"):
        self.id = id
        self.email = email
        self.role = role


# Use HTTP Bearer security so FastAPI shows an "Authorize" button in Swagger UI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(_bearer_scheme)
) -> CurrentUser:
    """Dependency that extracts a user from a Bearer Authorization header.

    NOTE: This is a lightweight implementation for local development / tests.
    It treats the Bearer token as a simple payload in the form `id` or `id:email:role`.
    Using `HTTPBearer` here makes OpenAPI include the Bearer security scheme.
    Replace with real token verification against Supabase or your auth provider for production.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing or invalid")

    token = credentials.credentials

    uid = None
    email = None
    role = "user"

    # If it looks like a JWT (three parts), try to read claims without verifying signature
    try:
        if token.count('.') == 2:
            from jose import jwt as jose_jwt
            claims = jose_jwt.get_unverified_claims(token)
            uid = claims.get("sub") or claims.get("user_id") or claims.get("id")
            email = claims.get("email") or (claims.get("user_metadata") or {}).get("email")
            role = claims.get("role") or role

            # If the token was a JWT but didn't yield a user id, reject it explicitly
            if not uid:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT token is missing 'sub' claim or user id")
    except HTTPException:
        # Re-raise HTTP errors we intentionally raised
        raise
    except Exception:
        # If JWT parsing fails and token *looks* like a JWT, reject it explicitly
        if token.count('.') == 2:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT token")
        uid = None

    # Fallback: simple colon-separated token (dev format)
    if not uid:
        parts = token.split(":")
        if not parts or not parts[0]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
        uid = parts[0]
        email = email or (parts[1] if len(parts) > 1 else None)
        role = parts[2] if len(parts) > 2 else role

    # Final sanity check
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not extract user id from token")

    return CurrentUser(uid, email, role)
