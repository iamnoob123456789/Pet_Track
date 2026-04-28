from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId

class Notification(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    pet_id: Optional[PyObjectId] = None
    match_id: Optional[PyObjectId] = None
    
    # Notification content
    title: str
    message: str
    type: str  # match_found, pet_updated, contact_request, system
    
    # Delivery status
    email_sent: bool = False
    email_sent_at: Optional[datetime] = None
    in_app_read: bool = False
    in_app_read_at: Optional[datetime] = None
    
    # Metadata
    data: Dict[str, Any] = {}
    priority: str = "medium"  # low, medium, high
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

class NotificationCreate(BaseModel):
    user_id: str
    pet_id: Optional[str] = None
    match_id: Optional[str] = None
    title: str
    message: str
    type: str
    data: Dict[str, Any] = {}
    priority: str = "medium"

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    pet_id: Optional[str] = None
    match_id: Optional[str] = None
    title: str
    message: str
    type: str
    email_sent: bool
    in_app_read: bool
    data: Dict[str, Any]
    priority: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
