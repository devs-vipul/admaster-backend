"""
Business service - Business logic for business operations
"""
from typing import List, Optional
from datetime import datetime

from app.models.business import Business, BusinessStatus
from app.models.user import User
from app.schemas.business import BusinessCreate, BusinessUpdate
from app.services.user_service import UserService


class BusinessService:
    """Service class for business operations"""
    
    @staticmethod
    async def create_business(user_id: str, business_data: BusinessCreate) -> Business:
        """
        Create a new business and link it to the user
        """
        # Create business
        business = Business(
            user_id=user_id,
            **business_data.model_dump()
        )
        await business.insert()
        
        # Add business to user's businesses list
        user = await UserService.get_by_clerk_id(user_id)
        if user:
            await user.add_business(str(business.id))
        
        return business
    
    @staticmethod
    async def get_business_by_id(business_id: str, user_id: str) -> Optional[Business]:
        """Get business by ID (only if it belongs to the user)"""
        business = await Business.get(business_id)
        
        if business and business.user_id == user_id:
            return business
        
        return None
    
    @staticmethod
    async def get_user_businesses(
        user_id: str,
        status: Optional[BusinessStatus] = None
    ) -> List[Business]:
        """Get all businesses belonging to a user"""
        query = Business.find(Business.user_id == user_id)
        
        # Filter by status if provided
        if status:
            query = query.find(Business.status == status)
        
        # Sort by created_at descending
        query = query.sort(-Business.created_at)
        
        return await query.to_list()
    
    @staticmethod
    async def update_business(
        business_id: str,
        user_id: str,
        business_data: BusinessUpdate
    ) -> Optional[Business]:
        """Update business information"""
        business = await BusinessService.get_business_by_id(business_id, user_id)
        
        if not business:
            return None
        
        # Update only provided fields
        update_data = business_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(business, field, value)
        
        await business.save()
        return business
    
    @staticmethod
    async def delete_business(business_id: str, user_id: str) -> bool:
        """Delete business (only if it belongs to the user)"""
        business = await BusinessService.get_business_by_id(business_id, user_id)
        
        if not business:
            return False
        
        # Remove from user's businesses list
        user = await UserService.get_by_clerk_id(user_id)
        if user:
            await user.remove_business(str(business.id))
        
        # Delete business
        await business.delete()
        return True
    
    @staticmethod
    async def has_any_business(user_id: str) -> bool:
        """Check if user has any business"""
        count = await Business.find(Business.user_id == user_id).count()
        return count > 0

