from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.contact import Contact, ContactCreate, ContactResponse
from models.user import PyObjectId
from services.auth_service import get_current_active_user
from services.notification_service import notification_service
from config.database import get_contacts_collection, get_matches_collection, get_users_collection

router = APIRouter(prefix="/contacts", tags=["contacts"])

def _mask_email(email: str) -> str:
    """Mask email for privacy"""
    if "@" not in email:
        return email
    
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"

def _mask_phone(phone: str) -> str:
    """Mask phone number for privacy"""
    # Remove non-digit characters
    digits = "".join(filter(str.isdigit, phone))
    
    if len(digits) <= 4:
        return "*" * len(phone)
    
    # Show last 4 digits
    return "*" * (len(phone) - 4) + phone[-4:]

@router.post("/", response_model=ContactResponse)
async def initiate_contact(
    contact_data: ContactCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Initiate contact with another user about a match"""
    try:
        # Get collections
        contacts_collection = await get_contacts_collection()
        matches_collection = await get_matches_collection()
        users_collection = await get_users_collection()
        
        # Verify match exists and user has access
        match = await matches_collection.find_one({"_id": PyObjectId(contact_data.match_id)})
        
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        
        # Get pets involved in the match
        pets_collection = await get_pets_collection() if 'get_pets_collection' in globals() else None
        
        # Verify user is involved in this match
        user_pets = []  # This would need to be implemented based on your pet collection
        user_pet_ids = [pet["_id"] for pet in user_pets]
        
        if (match["lost_pet_id"] not in user_pet_ids and 
            match["found_pet_id"] not in user_pet_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied - you are not involved in this match"
            )
        
        # Check if contact already exists
        existing_contact = await contacts_collection.find_one({
            "match_id": PyObjectId(contact_data.match_id),
            "initiator_id": current_user["id"]
        })
        
        if existing_contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact already initiated for this match"
            )
        
        # Get recipient user info
        recipient_user = await users_collection.find_one({"_id": PyObjectId(contact_data.recipient_id)})
        
        if not recipient_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient not found"
            )
        
        # Create masked contact information
        masked_email = None
        masked_phone = None
        
        if contact_data.share_email and recipient_user.get("email"):
            masked_email = _mask_email(recipient_user["email"])
        
        if contact_data.share_phone and recipient_user.get("phone"):
            masked_phone = _mask_phone(recipient_user["phone"])
        
        # Create contact document
        contact_dict = contact_data.dict()
        contact_dict["initiator_id"] = current_user["id"]
        contact_dict["masked_email"] = masked_email
        contact_dict["masked_phone"] = masked_phone
        
        # Insert contact
        result = await contacts_collection.insert_one(contact_dict)
        
        # Get created contact
        created_contact = await contacts_collection.find_one({"_id": result.inserted_id})
        
        # Send notification to recipient
        await notification_service.create_contact_notification(
            user_data=recipient_user,
            contact_data={
                "contact_id": str(result.inserted_id),
                "match_id": contact_data.match_id,
                "initiator_name": current_user.get("full_name", current_user.get("username", "Anonymous")),
                "initial_message": contact_data.initial_message
            }
        )
        
        # Convert to response model
        created_contact["_id"] = str(created_contact["_id"])
        created_contact["match_id"] = str(created_contact["match_id"])
        created_contact["initiator_id"] = str(created_contact["initiator_id"])
        created_contact["recipient_id"] = str(created_contact["recipient_id"])
        
        return ContactResponse(**created_contact)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate contact: {str(e)}"
        )

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get contacts for current user"""
    try:
        # Get collection
        contacts_collection = await get_contacts_collection()
        
        # Build query
        query = {
            "$or": [
                {"initiator_id": current_user["id"]},
                {"recipient_id": current_user["id"]}
            ]
        }
        
        if status:
            query["status"] = status.lower()
        
        # Execute query
        cursor = contacts_collection.find(query).sort("created_at", -1)
        contacts = await cursor.to_list(length=None)
        
        # Convert to response models
        contact_responses = []
        for contact in contacts:
            contact["_id"] = str(contact["_id"])
            contact["match_id"] = str(contact["match_id"])
            contact["initiator_id"] = str(contact["initiator_id"])
            contact["recipient_id"] = str(contact["recipient_id"])
            contact_responses.append(ContactResponse(**contact))
        
        return contact_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contacts: {str(e)}"
        )

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific contact by ID"""
    try:
        # Get collection
        contacts_collection = await get_contacts_collection()
        
        # Find contact
        contact = await contacts_collection.find_one({"_id": PyObjectId(contact_id)})
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Check if user is involved in this contact
        if (contact["initiator_id"] != current_user["id"] and 
            contact["recipient_id"] != current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Convert to response model
        contact["_id"] = str(contact["_id"])
        contact["match_id"] = str(contact["match_id"])
        contact["initiator_id"] = str(contact["initiator_id"])
        contact["recipient_id"] = str(contact["recipient_id"])
        
        return ContactResponse(**contact)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contact: {str(e)}"
        )

@router.post("/{contact_id}/respond")
async def respond_to_contact(
    contact_id: str,
    response_message: str,
    action: str = "accept",  # accept or reject
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Respond to a contact request"""
    try:
        # Get collection
        contacts_collection = await get_contacts_collection()
        
        # Find contact
        contact = await contacts_collection.find_one({"_id": PyObjectId(contact_id)})
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Check if user is the recipient
        if contact["recipient_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied - only recipients can respond"
            )
        
        # Check if contact is still pending
        if contact["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contact already {contact['status']}"
            )
        
        # Update contact
        new_status = "accepted" if action == "accept" else "rejected"
        update_data = {
            "status": new_status,
            "response_message": response_message,
            "responded_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if action == "accept":
            update_data["completed_at"] = datetime.utcnow()
        
        await contacts_collection.update_one(
            {"_id": PyObjectId(contact_id)},
            {"$set": update_data}
        )
        
        return {"message": f"Contact {new_status} successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to respond to contact: {str(e)}"
        )

@router.post("/{contact_id}/reveal-contact")
async def reveal_contact_info(
    contact_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Reveal full contact information for accepted contacts"""
    try:
        # Get collections
        contacts_collection = await get_contacts_collection()
        users_collection = await get_users_collection()
        
        # Find contact
        contact = await contacts_collection.find_one({"_id": PyObjectId(contact_id)})
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Check if user is involved and contact is accepted
        if (contact["initiator_id"] != current_user["id"] and 
            contact["recipient_id"] != current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        if contact["status"] != "accepted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact information can only be revealed for accepted contacts"
            )
        
        # Get other user's information
        other_user_id = (contact["recipient_id"] if contact["initiator_id"] == current_user["id"] 
                        else contact["initiator_id"])
        
        other_user = await users_collection.find_one({"_id": other_user_id})
        
        if not other_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Other user not found"
            )
        
        # Return full contact information
        return {
            "user_id": str(other_user["_id"]),
            "email": other_user.get("email"),
            "phone": other_user.get("phone"),
            "full_name": other_user.get("full_name"),
            "username": other_user.get("username")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reveal contact info: {str(e)}"
        )
