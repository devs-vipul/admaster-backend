"""
API dependencies - Reusable dependencies for FastAPI endpoints
"""
from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user_id, verify_clerk_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import UserCreate

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get current authenticated user from database
    
    This:
    1. Verifies the Clerk JWT token
    2. Gets the user_id and email from token
    3. Fetches user from MongoDB (or creates if not exists)
    4. Returns User object
    """
    # Verify token and get payload
    payload = await verify_clerk_token(credentials)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    
    # Try to get user from database
    user = await UserService.get_by_clerk_id(user_id)
    
    # If user doesn't exist, create them (auto-sync on first API call)
    if not user:
        # Extract user data from JWT token
        email = payload.get("email") or payload.get("email_addresses", [{}])[0].get("email_address") or f"{user_id}@clerk.user"
        first_name = payload.get("given_name") or payload.get("first_name")
        last_name = payload.get("family_name") or payload.get("last_name")
        
        # Create user in database
        user_data = UserCreate(
            clerk_id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user = await UserService.create_user(user_data)
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure user is active
    (Can add more checks here like subscription status, etc.)
    """
    # For now, just return user
    # Later you can add checks like:
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user

