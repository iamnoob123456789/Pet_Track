from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.notification import Notification, NotificationCreate, NotificationResponse
from models.user import PyObjectId
from services.auth_service import get_current_active_user
from services.notification_service import notification_service
from config.database import get_notifications_collection

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = Query(False, description="Get only unread notifications"),
    type: Optional[str] = Query(None, description="Filter by notification type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0, description="Number of notifications to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of notifications to return"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get notifications for current user"""
    try:
        # Get collection
        notifications_collection = await get_notifications_collection()
        
        # Build query
        query = {"user_id": current_user["id"]}
        
        if unread_only:
            query["in_app_read"] = False
        
        if type:
            query["type"] = type.lower()
        
        if priority:
            query["priority"] = priority.lower()
        
        # Execute query
        cursor = notifications_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        notifications = await cursor.to_list(length=None)
        
        # Convert to response models
        notification_responses = []
        for notification in notifications:
            notification["_id"] = str(notification["_id"])
            notification["user_id"] = str(notification["user_id"])
            
            if notification.get("pet_id"):
                notification["pet_id"] = str(notification["pet_id"])
            
            if notification.get("match_id"):
                notification["match_id"] = str(notification["match_id"])
            
            notification_responses.append(NotificationResponse(**notification))
        
        return notification_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )

@router.get("/unread-count")
async def get_unread_count(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get count of unread notifications"""
    try:
        # Get collection
        notifications_collection = await get_notifications_collection()
        
        # Count unread notifications
        count = await notifications_collection.count_documents({
            "user_id": current_user["id"],
            "in_app_read": False
        })
        
        return {"unread_count": count}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )

@router.post("/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Mark a notification as read"""
    try:
        # Get collection
        notifications_collection = await get_notifications_collection()
        
        # Find and update notification
        result = await notifications_collection.update_one(
            {
                "_id": PyObjectId(notification_id),
                "user_id": current_user["id"]
            },
            {
                "$set": {
                    "in_app_read": True,
                    "in_app_read_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Mark all notifications as read for current user"""
    try:
        # Get collection
        notifications_collection = await get_notifications_collection()
        
        # Update all unread notifications
        result = await notifications_collection.update_many(
            {
                "user_id": current_user["id"],
                "in_app_read": False
            },
            {
                "$set": {
                    "in_app_read": True,
                    "in_app_read_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": f"Marked {result.modified_count} notifications as read"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete a notification"""
    try:
        # Get collection
        notifications_collection = await get_notifications_collection()
        
        # Find and delete notification
        result = await notifications_collection.delete_one({
            "_id": PyObjectId(notification_id),
            "user_id": current_user["id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"message": "Notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )

@router.post("/test")
async def test_notification(
    notification_data: NotificationCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a test notification (for development/testing)"""
    try:
        # Get collection
        notifications_collection = await get_notifications_collection()
        
        # Create notification document
        notification_dict = notification_data.dict()
        notification_dict["user_id"] = current_user["id"]
        
        # Insert notification
        result = await notifications_collection.insert_one(notification_dict)
        
        # Get created notification
        created_notification = await notifications_collection.find_one({"_id": result.inserted_id})
        
        # Convert to response model
        created_notification["_id"] = str(created_notification["_id"])
        created_notification["user_id"] = str(created_notification["user_id"])
        
        if created_notification.get("pet_id"):
            created_notification["pet_id"] = str(created_notification["pet_id"])
        
        if created_notification.get("match_id"):
            created_notification["match_id"] = str(created_notification["match_id"])
        
        return NotificationResponse(**created_notification)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test notification: {str(e)}"
        )

@router.get("/preferences")
async def get_notification_preferences(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get user notification preferences"""
    try:
        # Get user collection
        users_collection = await get_users_collection()
        
        # Find user
        user = await users_collection.find_one({"_id": current_user["id"]})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "notification_preferences": user.get("notification_preferences", {
                "email_notifications": True,
                "in_app_notifications": True,
                "match_alerts": True
            })
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification preferences: {str(e)}"
        )

@router.put("/preferences")
async def update_notification_preferences(
    preferences: Dict[str, bool],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update user notification preferences"""
    try:
        # Get user collection
        users_collection = await get_users_collection()
        
        # Validate preferences
        allowed_keys = {"email_notifications", "in_app_notifications", "match_alerts"}
        update_data = {k: v for k, v in preferences.items() if k in allowed_keys}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid preference keys provided"
            )
        
        # Update user preferences
        await users_collection.update_one(
            {"_id": current_user["id"]},
            {"$set": {"notification_preferences": update_data}}
        )
        
        return {"message": "Notification preferences updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification preferences: {str(e)}"
        )
