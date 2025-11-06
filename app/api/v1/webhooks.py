"""
Clerk webhooks for syncing users to MongoDB
"""
from fastapi import APIRouter, Request, HTTPException, status

from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/clerk", summary="Clerk webhook handler")
async def clerk_webhook(request: Request):
    """
    Handle Clerk webhook events to sync users to MongoDB
    
    Setup:
    1. Go to Clerk Dashboard → Webhooks
    2. Add endpoint: https://yourdomain.com/api/v1/webhooks/clerk
    3. Subscribe to: user.created, user.updated, user.deleted
    4. Copy webhook secret to .env as CLERK_WEBHOOK_SECRET
    
    This keeps MongoDB in sync with Clerk automatically
    """
    # Get webhook payload
    payload = await request.json()
    event_type = payload.get("type")
    data = payload.get("data", {})
    
    try:
        if event_type == "user.created":
            # New user signed up
            user_data = UserCreate(
                clerk_id=data["id"],
                email=data["email_addresses"][0]["email_address"],
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                image_url=data.get("image_url"),
            )
            await UserService.create_user(user_data)
            print(f"✅ User created: {user_data.clerk_id}")
            
        elif event_type == "user.updated":
            # User updated their profile
            user_data = UserUpdate(
                email=data["email_addresses"][0]["email_address"],
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                image_url=data.get("image_url"),
            )
            await UserService.update_user(data["id"], user_data)
            print(f"✅ User updated: {data['id']}")
            
        elif event_type == "user.deleted":
            # User deleted their account
            await UserService.delete_user(data["id"])
            print(f"✅ User deleted: {data['id']}")
            
        else:
            print(f"⚠️  Unhandled event type: {event_type}")
        
        return {"status": "success", "event": event_type}
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}",
        )

