"""
Brand service - Business logic for brand operations
"""
from typing import Optional
from datetime import datetime

from app.models.brand import Brand
from app.models.business import Business
from app.schemas.brand import BrandCreate, BrandUpdate


class BrandService:
    """Service class for brand operations"""
    
    @staticmethod
    async def get_or_create_brand(business_id: str) -> Brand:
        """
        Get existing brand for a business, or create a new one
        """
        brand = await Brand.find_one(Brand.business_id == business_id)
        if not brand:
            brand = Brand(
                business_id=business_id,
            )
            await brand.insert()
        return brand
    
    @staticmethod
    async def get_brand_by_business_id(business_id: str) -> Optional[Brand]:
        """Get brand by business ID"""
        return await Brand.find_one(Brand.business_id == business_id)
    
    @staticmethod
    async def create_or_update_brand(
        business_id: str,
        brand_data: BrandUpdate,
    ) -> Brand:
        """
        Create or update brand information for a business
        """
        brand = await BrandService.get_or_create_brand(business_id)
        
        # Update brand with provided data
        update_data = brand_data.model_dump(exclude_unset=True)
        await brand.update_brand_info(**update_data)
        
        return brand
    
    @staticmethod
    async def mark_brand_complete(business_id: str) -> Optional[Brand]:
        """Mark brand as complete (user has reviewed)"""
        brand = await BrandService.get_brand_by_business_id(business_id)
        if brand:
            await brand.update_brand_info(is_complete=True)
        return brand

