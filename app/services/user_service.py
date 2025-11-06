"""
User service - Business logic for user operations
"""
from typing import Optional
from datetime import datetime

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service class for user operations"""
    
    @staticmethod
    async def get_by_clerk_id(clerk_id: str) -> Optional[User]:
        """Get user by Clerk ID"""
        return await User.find_one(User.clerk_id == clerk_id)
    
    @staticmethod
    async def get_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        return await User.find_one(User.email == email)
    
    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        """
        Create a new user (called from Clerk webhook)
        """
        user = User(**user_data.model_dump())
        await user.insert()
        return user
    
    @staticmethod
    async def update_user(clerk_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = await UserService.get_by_clerk_id(clerk_id)
        
        if not user:
            return None
        
        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await user.save()
        return user
    
    @staticmethod
    async def delete_user(clerk_id: str) -> bool:
        """Delete user (called from Clerk webhook)"""
        user = await UserService.get_by_clerk_id(clerk_id)
        
        if not user:
            return False
        
        await user.delete()
        return True
    
    @staticmethod
    async def update_last_login(clerk_id: str) -> Optional[User]:
        """Update user's last login timestamp"""
        user = await UserService.get_by_clerk_id(clerk_id)
        
        if not user:
            return None
        
        user.last_login_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        await user.save()
        return user
    
    @staticmethod
    async def get_or_create_user(clerk_id: str, email: str, **kwargs) -> User:
        """
        Get existing user or create new one
        Useful for ensuring user exists on first API call
        """
        user = await UserService.get_by_clerk_id(clerk_id)
        
        if not user:
            user_data = UserCreate(
                clerk_id=clerk_id,
                email=email,
                **kwargs
            )
            user = await UserService.create_user(user_data)
        
        return user

