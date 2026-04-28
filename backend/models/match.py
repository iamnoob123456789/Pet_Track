from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId

class Match(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    lost_pet_id: PyObjectId
    found_pet_id: PyObjectId
    match_score: float
    image_similarity_score: float
    metadata_similarity_score: float
    location_similarity_score: float
    hybrid_score: float
    
    # Matching details
    breed_match: bool
    color_match: bool
    size_match: bool
    distance_km: float
    
    # Status tracking
    status: str = "pending"  # pending, reviewed, confirmed, rejected
    reviewed_by: Optional[PyObjectId] = None
    reviewed_at: Optional[datetime] = None
    confirmed_by: Optional[PyObjectId] = None
    confirmed_at: Optional[datetime] = None
    
    # Communication
    contact_initiated: bool = False
    contact_initiated_by: Optional[PyObjectId] = None
    contact_initiated_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MatchCreate(BaseModel):
    lost_pet_id: str
    found_pet_id: str
    match_score: float
    image_similarity_score: float
    metadata_similarity_score: float
    location_similarity_score: float
    hybrid_score: float
    breed_match: bool
    color_match: bool
    size_match: bool
    distance_km: float

class MatchResponse(BaseModel):
    id: str
    lost_pet_id: str
    found_pet_id: str
    match_score: float
    image_similarity_score: float
    metadata_similarity_score: float
    location_similarity_score: float
    hybrid_score: float
    breed_match: bool
    color_match: bool
    size_match: bool
    distance_km: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
