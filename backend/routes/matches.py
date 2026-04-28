from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.match import Match, MatchCreate, MatchResponse
from models.user import PyObjectId
from services.auth_service import get_current_active_user
from services.hybrid_matching import hybrid_matching_engine
from services.notification_service import notification_service
from config.database import get_matches_collection, get_pets_collection, get_users_collection

router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/", response_model=List[MatchResponse])
async def get_matches(
    status: Optional[str] = Query(None, description="Filter by match status"),
    min_score: Optional[float] = Query(0.0, description="Minimum match score"),
    skip: int = Query(0, ge=0, description="Number of matches to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of matches to return"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get matches for current user's pets"""
    try:
        # Get collections
        matches_collection = await get_matches_collection()
        pets_collection = await get_pets_collection()
        
        # Get user's pets
        user_pets = await pets_collection.find({
            "owner_id": current_user["id"],
            "is_active": True
        }).to_list(length=None)
        
        if not user_pets:
            return []
        
        user_pet_ids = [pet["_id"] for pet in user_pets]
        
        # Build query for matches involving user's pets
        query = {
            "$or": [
                {"lost_pet_id": {"$in": user_pet_ids}},
                {"found_pet_id": {"$in": user_pet_ids}}
            ]
        }
        
        if status:
            query["status"] = status.lower()
        
        if min_score > 0:
            query["match_score"] = {"$gte": min_score}
        
        # Execute query
        cursor = matches_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        matches = await cursor.to_list(length=None)
        
        # Convert to response models
        match_responses = []
        for match in matches:
            match["_id"] = str(match["_id"])
            match["lost_pet_id"] = str(match["lost_pet_id"])
            match["found_pet_id"] = str(match["found_pet_id"])
            match_responses.append(MatchResponse(**match))
        
        return match_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get matches: {str(e)}"
        )

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific match by ID"""
    try:
        # Get collections
        matches_collection = await get_matches_collection()
        pets_collection = await get_pets_collection()
        
        # Find match
        match = await matches_collection.find_one({"_id": PyObjectId(match_id)})
        
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        
        # Check if user owns either pet in the match
        user_pets = await pets_collection.find({
            "owner_id": current_user["id"],
            "is_active": True
        }).to_list(length=None)
        
        user_pet_ids = [pet["_id"] for pet in user_pets]
        
        if (match["lost_pet_id"] not in user_pet_ids and 
            match["found_pet_id"] not in user_pet_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Convert to response model
        match["_id"] = str(match["_id"])
        match["lost_pet_id"] = str(match["lost_pet_id"])
        match["found_pet_id"] = str(match["found_pet_id"])
        
        return MatchResponse(**match)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match: {str(e)}"
        )

@router.post("/{match_id}/review")
async def review_match(
    match_id: str,
    action: str = Query(..., regex="^(accept|reject)$"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Review and accept/reject a match"""
    try:
        # Get collections
        matches_collection = await get_matches_collection()
        pets_collection = await get_pets_collection()
        
        # Find match
        match = await matches_collection.find_one({"_id": PyObjectId(match_id)})
        
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        
        # Check if user owns either pet in the match
        user_pets = await pets_collection.find({
            "owner_id": current_user["id"],
            "is_active": True
        }).to_list(length=None)
        
        user_pet_ids = [pet["_id"] for pet in user_pets]
        
        if (match["lost_pet_id"] not in user_pet_ids and 
            match["found_pet_id"] not in user_pet_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update match status
        new_status = "confirmed" if action == "accept" else "rejected"
        update_data = {
            "status": new_status,
            "reviewed_by": current_user["id"],
            "reviewed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if action == "accept":
            update_data["confirmed_by"] = current_user["id"]
            update_data["confirmed_at"] = datetime.utcnow()
        
        await matches_collection.update_one(
            {"_id": PyObjectId(match_id)},
            {"$set": update_data}
        )
        
        # If accepted, notify the other pet owner
        if action == "accept":
            # Determine which pet belongs to current user
            if match["lost_pet_id"] in user_pet_ids:
                other_pet_id = match["found_pet_id"]
            else:
                other_pet_id = match["lost_pet_id"]
            
            # Get other pet and owner
            other_pet = await pets_collection.find_one({"_id": other_pet_id})
            if other_pet:
                other_owner = await get_users_collection().find_one({"_id": other_pet["owner_id"]})
                if other_owner:
                    await notification_service.create_match_notification(
                        user_data=other_owner,
                        match_data={
                            "match_id": match_id,
                            "pet_id": str(other_pet_id),
                            "pet_status": other_pet["status"],
                            "similarity": {
                                "hybrid_score": match["hybrid_score"],
                                "details": {
                                    "distance_km": match.get("distance_km", 0)
                                }
                            }
                        }
                    )
        
        return {"message": f"Match {new_status} successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to review match: {str(e)}"
        )

@router.get("/feed/lost-and-found")
async def get_lost_and_found_feed(
    pet_type: Optional[str] = Query(None, description="Filter by pet type: lost or found"),
    breed: Optional[str] = Query(None, description="Filter by breed"),
    location: Optional[str] = Query(None, description="Filter by location"),
    radius_km: Optional[float] = Query(None, description="Search radius in kilometers"),
    latitude: Optional[float] = Query(None, description="Center latitude for location search"),
    longitude: Optional[float] = Query(None, description="Center longitude for location search"),
    days_back: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    skip: int = Query(0, ge=0, description="Number of pets to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of pets to return"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get lost and found pets feed with filtering"""
    try:
        # Get collection
        pets_collection = await get_pets_collection()
        
        # Build query
        query = {
            "is_active": True,
            "created_at": {
                "$gte": datetime.utcnow() - datetime.timedelta(days=days_back)
            }
        }
        
        if pet_type:
            query["status"] = pet_type.lower()
        
        if breed:
            query["breed"] = {"$regex": breed, "$options": "i"}
        
        if location:
            query["$or"] = [
                {"location_address": {"$regex": location, "$options": "i"}},
                {"location_city": {"$regex": location, "$options": "i"}},
                {"location_state": {"$regex": location, "$options": "i"}}
            ]
        
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
        
        # Enrich with match information
        enriched_pets = []
        for pet in pets:
            pet["_id"] = str(pet["_id"])
            pet["owner_id"] = str(pet["owner_id"])
            
            # Get match count for this pet
            matches_collection = await get_matches_collection()
            match_count = await matches_collection.count_documents({
                "$or": [
                    {"lost_pet_id": pet["_id"]},
                    {"found_pet_id": pet["_id"]}
                ],
                "status": {"$ne": "rejected"}
            })
            
            pet["match_count"] = match_count
            enriched_pets.append(pet)
        
        return {"pets": enriched_pets, "total": len(enriched_pets)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feed: {str(e)}"
        )

@router.get("/stats/overview")
async def get_match_stats(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get match statistics for current user"""
    try:
        # Get collections
        matches_collection = await get_matches_collection()
        pets_collection = await get_pets_collection()
        
        # Get user's pets
        user_pets = await pets_collection.find({
            "owner_id": current_user["id"],
            "is_active": True
        }).to_list(length=None)
        
        if not user_pets:
            return {
                "total_pets": 0,
                "total_matches": 0,
                "confirmed_matches": 0,
                "pending_matches": 0,
                "rejected_matches": 0
            }
        
        user_pet_ids = [pet["_id"] for pet in user_pets]
        
        # Get match statistics
        total_matches = await matches_collection.count_documents({
            "$or": [
                {"lost_pet_id": {"$in": user_pet_ids}},
                {"found_pet_id": {"$in": user_pet_ids}}
            ]
        })
        
        confirmed_matches = await matches_collection.count_documents({
            "$or": [
                {"lost_pet_id": {"$in": user_pet_ids}},
                {"found_pet_id": {"$in": user_pet_ids}}
            ],
            "status": "confirmed"
        })
        
        pending_matches = await matches_collection.count_documents({
            "$or": [
                {"lost_pet_id": {"$in": user_pet_ids}},
                {"found_pet_id": {"$in": user_pet_ids}}
            ],
            "status": "pending"
        })
        
        rejected_matches = await matches_collection.count_documents({
            "$or": [
                {"lost_pet_id": {"$in": user_pet_ids}},
                {"found_pet_id": {"$in": user_pet_ids}}
            ],
            "status": "rejected"
        })
        
        return {
            "total_pets": len(user_pets),
            "total_matches": total_matches,
            "confirmed_matches": confirmed_matches,
            "pending_matches": pending_matches,
            "rejected_matches": rejected_matches
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )
