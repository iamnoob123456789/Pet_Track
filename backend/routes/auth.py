from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from typing import Dict, Any

from models.user import User, UserCreate, UserLogin, UserResponse
from services.auth_service import auth_service, get_current_active_user
from config.database import get_users_collection

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Get users collection
        users_collection = await get_users_collection()
        
        # Check if user already exists
        existing_user = await users_collection.find_one({
            "$or": [
                {"email": user_data.email},
                {"username": user_data.username}
            ]
        })
        
        if existing_user:
            if existing_user.get("email") == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Hash password
        password_hash = auth_service.get_password_hash(user_data.password)
        
        # Create user document
        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "password_hash": password_hash,
            "full_name": user_data.full_name,
            "phone": user_data.phone,
            "is_active": True,
            "created_at": user_data.created_at if hasattr(user_data, 'created_at') else None,
            "notification_preferences": {
                "email_notifications": True,
                "in_app_notifications": True,
                "match_alerts": True
            }
        }
        
        # Insert user
        result = await users_collection.insert_one(user_dict)
        
        # Get created user
        created_user = await users_collection.find_one({"_id": result.inserted_id})
        
        # Convert to response model
        created_user["_id"] = str(created_user["_id"])
        return UserResponse(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login")
async def login(login_data: UserLogin):
    """Login user and return access token"""
    try:
        # Get users collection
        users_collection = await get_users_collection()
        
        # Find user by email
        user = await users_collection.find_one({"email": login_data.email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not auth_service.authenticate_user(user, login_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )
        
        # Create access token
        access_token = auth_service.create_user_token(user)
        
        # Update last login
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": user.get("created_at")}}  # Using created_at as fallback
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "full_name": user.get("full_name")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Get current user information"""
    try:
        # Get users collection
        users_collection = await get_users_collection()
        
        # Find user
        user = await users_collection.find_one({"_id": current_user["id"]})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Convert to response model
        user["_id"] = str(user["_id"])
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update current user information"""
    try:
        # Get users collection
        users_collection = await get_users_collection()
        
        # Allowed fields to update
        allowed_fields = {"full_name", "phone", "notification_preferences"}
        update_data = {k: v for k, v in user_update.items() if k in allowed_fields}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        # Update user
        result = await users_collection.update_one(
            {"_id": current_user["id"]},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user
        updated_user = await users_collection.find_one({"_id": current_user["id"]})
        updated_user["_id"] = str(updated_user["_id"])
        
        return UserResponse(**updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Logout user (client-side token removal)"""
    # In a stateless JWT setup, logout is typically handled client-side
    # by removing the token. This endpoint can be used for logging or cleanup.
    
    return {"message": "Successfully logged out"}
