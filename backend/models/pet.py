from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId

class Pet(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: Optional[str] = None
    breed: str
    color: str
    size: Optional[str] = None  # small, medium, large
    age: Optional[str] = None  # puppy, young, adult, senior
    gender: Optional[str] = None  # male, female, unknown
    description: Optional[str] = None
    image_urls: List[str] = []
    image_embeddings: Optional[List[float]] = None
    thumbnail_url: Optional[str] = None
    
    # Location information
    latitude: float
    longitude: float
    location_address: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: Optional[str] = None
    
    # Status and metadata
    status: str  # "lost" or "found"
    date_lost_or_found: datetime = Field(default_factory=datetime.utcnow)
    contact_info: Dict[str, Any] = {}
    owner_id: PyObjectId
    
    # Quality and duplicate detection
    image_quality_score: Optional[float] = None
    is_duplicate: bool = False
    duplicate_of: Optional[PyObjectId] = None
    
    # Matching information
    match_count: int = 0
    last_matched: Optional[datetime] = None
    
    # Additional metadata
    distinctive_features: Optional[str] = None
    medical_info: Optional[str] = None
    behavior_traits: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    @validator('status')
    def validate_status(cls, v):
        if v.lower() not in ['lost', 'found']:
            raise ValueError('Status must be either "lost" or "found"')
        return v.lower()

    @validator('image_urls')
    def validate_images(cls, v):
        if not v:
            raise ValueError('At least one image URL is required')
        return v

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PetCreate(BaseModel):
    name: Optional[str] = None
    breed: str
    color: str
    size: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    image_urls: List[str]
    latitude: float
    longitude: float
    location_address: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: Optional[str] = None
    status: str
    date_lost_or_found: Optional[datetime] = None
    contact_info: Dict[str, Any] = {}
    distinctive_features: Optional[str] = None
    medical_info: Optional[str] = None
    behavior_traits: Optional[str] = None

class PetUpdate(BaseModel):
    name: Optional[str] = None
    breed: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    image_urls: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_address: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: Optional[str] = None
    status: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    distinctive_features: Optional[str] = None
    medical_info: Optional[str] = None
    behavior_traits: Optional[str] = None
    is_active: Optional[bool] = None

class PetResponse(BaseModel):
    id: str
    name: Optional[str] = None
    breed: str
    color: str
    size: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    image_urls: List[str]
    thumbnail_url: Optional[str] = None
    latitude: float
    longitude: float
    location_address: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: Optional[str] = None
    status: str
    date_lost_or_found: datetime
    contact_info: Dict[str, Any]
    distinctive_features: Optional[str] = None
    medical_info: Optional[str] = None
    behavior_traits: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
