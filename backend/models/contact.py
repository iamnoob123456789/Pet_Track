from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId

class Contact(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    match_id: PyObjectId
    initiator_id: PyObjectId  # User who initiated contact
    recipient_id: PyObjectId  # User who receives contact
    
    # Contact information (masked for privacy)
    masked_email: Optional[str] = None
    masked_phone: Optional[str] = None
    contact_method: str  # email, phone, in_app_chat
    
    # Message content
    initial_message: str
    response_message: Optional[str] = None
    
    # Status tracking
    status: str = "pending"  # pending, accepted, rejected, completed
    responded_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Privacy settings
    share_phone: bool = False
    share_email: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContactCreate(BaseModel):
    match_id: str
    initiator_id: str
    recipient_id: str
    contact_method: str
    initial_message: str
    share_phone: bool = False
    share_email: bool = True

class ContactResponse(BaseModel):
    id: str
    match_id: str
    initiator_id: str
    recipient_id: str
    masked_email: Optional[str] = None
    masked_phone: Optional[str] = None
    contact_method: str
    initial_message: str
    response_message: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
