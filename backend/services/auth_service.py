from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # Move to environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get current user from JWT token"""
        token = credentials.credentials
        payload = self.verify_token(token)
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # This would fetch user from database
        # from ..config.database import get_users_collection
        # users_collection = await get_users_collection()
        # user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        # For now, return basic user info from payload
        user = {
            "id": user_id,
            "email": payload.get("email"),
            "username": payload.get("username"),
            "full_name": payload.get("full_name")
        }
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    async def get_current_active_user(self, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        """Get current active user"""
        # This would check user's active status in database
        # if not current_user.get("is_active", True):
        #     raise HTTPException(status_code=400, detail="Inactive user")
        
        return current_user
    
    def create_user_token(self, user_data: Dict[str, Any]) -> str:
        """Create access token for user"""
        token_data = {
            "sub": str(user_data.get("_id")),
            "email": user_data.get("email"),
            "username": user_data.get("username"),
            "full_name": user_data.get("full_name")
        }
        
        return self.create_access_token(data=token_data)
    
    def authenticate_user(self, user_data: Dict[str, Any], password: str) -> bool:
        """Authenticate user with password"""
        return self.verify_password(password, user_data.get("password_hash", ""))

# Global instance
auth_service = AuthService()

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current user"""
    return await auth_service.get_current_user(credentials)

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency to get current active user"""
    return await auth_service.get_current_active_user(current_user)
