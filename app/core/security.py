"""
Authentication and security utilities for Clerk
"""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

from app.core.config import settings


# HTTP Bearer token security
security = HTTPBearer()


async def verify_clerk_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Verify Clerk JWT token and return decoded payload
    
    This decodes the JWT without verification for development.
    In production, you should verify the signature using Clerk's JWKS.
    """
    token = credentials.credentials
    
    try:
        # Decode JWT without verification (for development)
        # In production, use options={"verify_signature": True} and fetch JWKS
        decoded = jwt.decode(
            token,
            key="",  # Empty key for unverified decode
            options={"verify_signature": False},  # Skip signature verification
        )
        
        return decoded
            
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    Get current user's Clerk ID from token
    
    Returns just the user_id for easier use in endpoints
    """
    payload = await verify_clerk_token(credentials)
    
    # Clerk JWT has 'sub' claim which is the user ID
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    
    return user_id


def verify_webhook_signature(payload: bytes, headers: dict) -> bool:
    """
    Verify Clerk webhook signature
    
    This ensures webhooks are actually from Clerk
    """
    try:
        from svix.webhooks import Webhook as SvixWebhook
        
        wh = SvixWebhook(settings.CLERK_WEBHOOK_SECRET)
        wh.verify(payload, headers)
        return True
        
    except Exception as e:
        print(f"Webhook verification failed: {e}")
        return False

