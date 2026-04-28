from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.pet import Pet, PetCreate, PetUpdate, PetResponse
from models.user import PyObjectId
from services.auth_service import get_current_active_user
from services.image_similarity import image_similarity_engine
from services.hybrid_matching import hybrid_matching_engine
from services.notification_service import notification_service
from config.database import get_pets_collection, get_users_collection

router = APIRouter(prefix="/pets", tags=["pets"])

@router.post("/", response_model=PetResponse)
async def create_pet(
    pet_data: PetCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new pet listing"""
    try:
        # Get collections
        pets_collection = await get_pets_collection()
        
        # Check for duplicates using image similarity
        existing_pets = await pets_collection.find({
            "owner_id": {"$ne": current_user["id"]},
            "status": pet_data.status,
            "image_embeddings": {"$exists": True}
        }).to_list(length=None)
        
        # Generate embedding for new pet
        new_embedding = image_similarity_engine.get_average_embedding(pet_data.image_urls)
        
        if new_embedding is not None:
            # Check for duplicates
            for existing_pet in existing_pets:
                if existing_pet.get("image_embeddings"):
                    existing_embedding = existing_pet["image_embeddings"]
                    is_duplicate, _ = image_similarity_engine.detect_duplicate(
                        new_embedding, [existing_embedding], threshold=0.95
                    )
                    
                    if is_duplicate:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This pet appears to be a duplicate of an existing listing"
                        )
        
        # Create pet document
        pet_dict = pet_data.dict()
        pet_dict["owner_id"] = current_user["id"]
        pet_dict["image_embeddings"] = new_embedding.tolist() if new_embedding is not None else None
        
        # Calculate image quality scores
        quality_scores = []
        for url in pet_data.image_urls:
            is_valid, score, reason = image_similarity_engine.check_image_quality(url)
            if is_valid:
                quality_scores.append(score)
        
        if quality_scores:
            pet_dict["image_quality_score"] = sum(quality_scores) / len(quality_scores)
        
        # Insert pet
        result = await pets_collection.insert_one(pet_dict)
        
        # Get created pet
        created_pet = await pets_collection.find_one({"_id": result.inserted_id})
        
        # Run matching if it's a found pet
        if pet_data.status == "found":
            await _run_matching_for_pet(created_pet)
        
        # Convert to response model
        created_pet["_id"] = str(created_pet["_id"])
        created_pet["owner_id"] = str(created_pet["owner_id"])
        
        return PetResponse(**created_pet)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pet: {str(e)}"
        )

@router.get("/", response_model=List[PetResponse])
async def get_pets(
    status: Optional[str] = Query(None, description="Filter by status: lost or found"),
    breed: Optional[str] = Query(None, description="Filter by breed"),
    color: Optional[str] = Query(None, description="Filter by color"),
    location: Optional[str] = Query(None, description="Filter by location"),
    radius_km: Optional[float] = Query(None, description="Search radius in kilometers"),
    latitude: Optional[float] = Query(None, description="Center latitude for location search"),
    longitude: Optional[float] = Query(None, description="Center longitude for location search"),
    skip: int = Query(0, ge=0, description="Number of pets to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of pets to return"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get pets with optional filtering"""
    try:
        # Get collection
        pets_collection = await get_pets_collection()
        
        # Build query
        query = {"is_active": True}
        
        if status:
            query["status"] = status.lower()
        
        if breed:
            query["breed"] = {"$regex": breed, "$options": "i"}
        
        if color:
            query["color"] = {"$regex": color, "$options": "i"}
        
        # Location-based filtering
        if latitude and longitude and radius_km:
            query["location"] = {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": radius_km * 1000  # Convert to meters
                }
            }
        
        # Execute query
        cursor = pets_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        pets = await cursor.to_list(length=None)
        
        # Convert to response models
        pet_responses = []
        for pet in pets:
            pet["_id"] = str(pet["_id"])
            pet["owner_id"] = str(pet["owner_id"])
            pet_responses.append(PetResponse(**pet))
        
        return pet_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pets: {str(e)}"
        )

@router.get("/{pet_id}", response_model=PetResponse)
async def get_pet(
    pet_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific pet by ID"""
    try:
        # Get collection
        pets_collection = await get_pets_collection()
        
        # Find pet
        pet = await pets_collection.find_one({"_id": PyObjectId(pet_id), "is_active": True})
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pet not found"
            )
        
        # Convert to response model
        pet["_id"] = str(pet["_id"])
        pet["owner_id"] = str(pet["owner_id"])
        
        return PetResponse(**pet)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pet: {str(e)}"
        )

@router.put("/{pet_id}", response_model=PetResponse)
async def update_pet(
    pet_id: str,
    pet_update: PetUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update a pet listing"""
    try:
        # Get collection
        pets_collection = await get_pets_collection()
        
        # Find pet and check ownership
        pet = await pets_collection.find_one({
            "_id": PyObjectId(pet_id),
            "owner_id": current_user["id"]
        })
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pet not found or access denied"
            )
        
        # Prepare update data
        update_data = pet_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # Update pet
        await pets_collection.update_one(
            {"_id": PyObjectId(pet_id)},
            {"$set": update_data}
        )
        
        # Get updated pet
        updated_pet = await pets_collection.find_one({"_id": PyObjectId(pet_id)})
        
        # Convert to response model
        updated_pet["_id"] = str(updated_pet["_id"])
        updated_pet["owner_id"] = str(updated_pet["owner_id"])
        
        return PetResponse(**updated_pet)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update pet: {str(e)}"
        )

@router.delete("/{pet_id}")
async def delete_pet(
    pet_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete a pet listing (soft delete)"""
    try:
        # Get collection
        pets_collection = await get_pets_collection()
        
        # Find pet and check ownership
        pet = await pets_collection.find_one({
            "_id": PyObjectId(pet_id),
            "owner_id": current_user["id"]
        })
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pet not found or access denied"
            )
        
        # Soft delete
        await pets_collection.update_one(
            {"_id": PyObjectId(pet_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        return {"message": "Pet deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete pet: {str(e)}"
        )

@router.post("/{pet_id}/matches")
async def find_matches(
    pet_id: str,
    top_k: int = Query(5, ge=1, le=20, description="Number of top matches to return"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Find matches for a specific pet"""
    try:
        # Get collection
        pets_collection = await get_pets_collection()
        
        # Find pet
        pet = await pets_collection.find_one({
            "_id": PyObjectId(pet_id),
            "is_active": True
        })
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pet not found"
            )
        
        # Check ownership
        if str(pet["owner_id"]) != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Find candidate pets (opposite status)
        candidate_pets = await pets_collection.find({
            "_id": {"$ne": pet["_id"]},
            "status": {"$ne": pet["status"]},
            "is_active": True,
            "image_embeddings": {"$exists": True}
        }).to_list(length=None)
        
        # Find matches using hybrid matching
        matches = hybrid_matching_engine.find_matches(
            query_pet=pet,
            candidate_pets=candidate_pets,
            top_k=top_k,
            min_threshold=0.6
        )
        
        return {"matches": matches}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find matches: {str(e)}"
        )

async def _run_matching_for_pet(new_pet: Dict[str, Any]):
    """Run matching process for a newly created pet"""
    try:
        pets_collection = await get_pets_collection()
        
        # Find candidate pets (opposite status)
        candidate_pets = await pets_collection.find({
            "_id": {"$ne": new_pet["_id"]},
            "status": {"$ne": new_pet["status"]},
            "is_active": True,
            "image_embeddings": {"$exists": True}
        }).to_list(length=None)
        
        # Find matches
        matches = hybrid_matching_engine.find_matches(
            query_pet=new_pet,
            candidate_pets=candidate_pets,
            top_k=5,
            min_threshold=0.7
        )
        
        # Send notifications for high-confidence matches
        for match in matches:
            if match["similarity"]["hybrid_score"] >= 0.8:
                # Get owner of the matched pet
                matched_pet_owner_id = match["pet"]["owner_id"]
                users_collection = await get_users_collection()
                owner = await users_collection.find_one({"_id": matched_pet_owner_id})
                
                if owner:
                    await notification_service.create_match_notification(
                        user_data=owner,
                        match_data={
                            "match_id": match["pet_id"],
                            "pet_id": match["pet_id"],
                            "pet_status": match["pet"]["status"],
                            "similarity": match["similarity"]
                        }
                    )
        
    except Exception as e:
        print(f"Error in matching process: {e}")
