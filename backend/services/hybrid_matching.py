from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from geopy.distance import geodesic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

from .image_similarity import image_similarity_engine

logger = logging.getLogger(__name__)

class HybridMatchingEngine:
    def __init__(self):
        # Weights for different components (can be tuned)
        self.IMAGE_WEIGHT = 0.6
        self.METADATA_WEIGHT = 0.25
        self.LOCATION_WEIGHT = 0.15
        
        # Metadata weights
        self.BREED_WEIGHT = 0.4
        self.COLOR_WEIGHT = 0.3
        self.SIZE_WEIGHT = 0.2
        self.AGE_WEIGHT = 0.1
        
        # Initialize text vectorizer for description similarity
        self.text_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
    def calculate_breed_similarity(self, breed1: str, breed2: str) -> float:
        """Calculate breed similarity (exact match or similar breeds)"""
        if not breed1 or not breed2:
            return 0.0
        
        breed1 = breed1.lower().strip()
        breed2 = breed2.lower().strip()
        
        # Exact match
        if breed1 == breed2:
            return 1.0
        
        # Common breed variations and similarities
        breed_mappings = {
            'labrador': ['lab', 'labrador retriever'],
            'german shepherd': ['german shepherd dog', 'gsd'],
            'golden retriever': ['golden', 'retriever'],
            'bulldog': ['english bulldog', 'french bulldog'],
            'pitbull': ['pit bull', 'american pit bull'],
            'husky': ['siberian husky', 'alaskan husky'],
        }
        
        for main_breed, variations in breed_mappings.items():
            if breed1 in variations and breed2 in variations:
                return 0.8
        
        return 0.0
    
    def calculate_color_similarity(self, color1: str, color2: str) -> float:
        """Calculate color similarity"""
        if not color1 or not color2:
            return 0.0
        
        color1 = color1.lower().strip()
        color2 = color2.lower().strip()
        
        # Exact match
        if color1 == color2:
            return 1.0
        
        # Check for overlapping colors
        colors1 = set(color1.replace(',', ' ').split())
        colors2 = set(color2.replace(',', ' ').split())
        
        if colors1 & colors2:  # Intersection
            overlap = len(colors1 & colors2)
            union = len(colors1 | colors2)
            return overlap / union if union > 0 else 0.0
        
        return 0.0
    
    def calculate_size_similarity(self, size1: str, size2: str) -> float:
        """Calculate size similarity"""
        if not size1 or not size2:
            return 0.0
        
        size1 = size1.lower().strip()
        size2 = size2.lower().strip()
        
        if size1 == size2:
            return 1.0
        
        # Adjacent sizes have partial similarity
        size_order = ['small', 'medium', 'large']
        if size1 in size_order and size2 in size_order:
            idx1 = size_order.index(size1)
            idx2 = size_order.index(size2)
            distance = abs(idx1 - idx2)
            return max(0, 1 - distance * 0.5)
        
        return 0.0
    
    def calculate_age_similarity(self, age1: str, age2: str) -> float:
        """Calculate age similarity"""
        if not age1 or not age2:
            return 0.0
        
        age1 = age1.lower().strip()
        age2 = age2.lower().strip()
        
        if age1 == age2:
            return 1.0
        
        # Age categories
        age_categories = ['puppy', 'young', 'adult', 'senior']
        if age1 in age_categories and age2 in age_categories:
            idx1 = age_categories.index(age1)
            idx2 = age_categories.index(age2)
            distance = abs(idx1 - idx2)
            return max(0, 1 - distance * 0.3)
        
        return 0.0
    
    def calculate_description_similarity(self, desc1: str, desc2: str) -> float:
        """Calculate text similarity between descriptions"""
        if not desc1 or not desc2:
            return 0.0
        
        try:
            # Simple text similarity using TF-IDF
            documents = [desc1, desc2]
            tfidf_matrix = self.text_vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def calculate_location_similarity(self, lat1: float, lon1: float, 
                                     lat2: float, lon2: float, 
                                     max_distance_km: float = 50) -> float:
        """Calculate location-based similarity"""
        try:
            distance = geodesic((lat1, lon1), (lat2, lon2)).kilometers
            
            # Convert distance to similarity score
            if distance <= max_distance_km:
                similarity = 1 - (distance / max_distance_km)
                return max(0, similarity)
            else:
                return 0.0
        except:
            return 0.0
    
    def calculate_metadata_similarity(self, pet1: Dict[str, Any], 
                                    pet2: Dict[str, Any]) -> Dict[str, float]:
        """Calculate similarity based on metadata"""
        similarities = {}
        
        # Breed similarity
        similarities['breed'] = self.calculate_breed_similarity(
            pet1.get('breed', ''), pet2.get('breed', '')
        )
        
        # Color similarity
        similarities['color'] = self.calculate_color_similarity(
            pet1.get('color', ''), pet2.get('color', '')
        )
        
        # Size similarity
        similarities['size'] = self.calculate_size_similarity(
            pet1.get('size', ''), pet2.get('size', '')
        )
        
        # Age similarity
        similarities['age'] = self.calculate_age_similarity(
            pet1.get('age', ''), pet2.get('age', '')
        )
        
        # Description similarity
        similarities['description'] = self.calculate_description_similarity(
            pet1.get('description', ''), pet2.get('description', '')
        )
        
        # Weighted metadata score
        metadata_score = (
            similarities['breed'] * self.BREED_WEIGHT +
            similarities['color'] * self.COLOR_WEIGHT +
            similarities['size'] * self.SIZE_WEIGHT +
            similarities['age'] * self.AGE_WEIGHT
        )
        
        similarities['overall'] = metadata_score
        
        return similarities
    
    def calculate_hybrid_score(self, pet1: Dict[str, Any], 
                             pet2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive hybrid similarity score between two pets
        """
        result = {
            'image_similarity': 0.0,
            'metadata_similarity': 0.0,
            'location_similarity': 0.0,
            'hybrid_score': 0.0,
            'details': {}
        }
        
        try:
            # Image similarity
            embedding1 = pet1.get('image_embeddings')
            embedding2 = pet2.get('image_embeddings')
            
            if embedding1 is not None and embedding2 is not None:
                result['image_similarity'] = image_similarity_engine.calculate_similarity(
                    np.array(embedding1), np.array(embedding2)
                )
            
            # Metadata similarity
            metadata_sim = self.calculate_metadata_similarity(pet1, pet2)
            result['metadata_similarity'] = metadata_sim['overall']
            result['details']['metadata'] = metadata_sim
            
            # Location similarity
            lat1, lon1 = pet1.get('latitude'), pet1.get('longitude')
            lat2, lon2 = pet2.get('latitude'), pet2.get('longitude')
            
            if all([lat1, lon1, lat2, lon2]):
                result['location_similarity'] = self.calculate_location_similarity(
                    float(lat1), float(lon1), float(lat2), float(lon2)
                )
            
            # Calculate distance for reference
            if all([lat1, lon1, lat2, lon2]):
                distance = geodesic((float(lat1), float(lon1)), 
                                 (float(lat2), float(lon2))).kilometers
                result['details']['distance_km'] = distance
            
            # Hybrid score (weighted combination)
            result['hybrid_score'] = (
                result['image_similarity'] * self.IMAGE_WEIGHT +
                result['metadata_similarity'] * self.METADATA_WEIGHT +
                result['location_similarity'] * self.LOCATION_WEIGHT
            )
            
            # Add match details
            result['details']['breed_match'] = metadata_sim.get('breed', 0.0) > 0.5
            result['details']['color_match'] = metadata_sim.get('color', 0.0) > 0.5
            result['details']['size_match'] = metadata_sim.get('size', 0.0) > 0.5
            
        except Exception as e:
            logger.error(f"Error calculating hybrid score: {e}")
        
        return result
    
    def find_matches(self, query_pet: Dict[str, Any], 
                    candidate_pets: List[Dict[str, Any]], 
                    top_k: int = 5, 
                    min_threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Find top-k matches for a query pet from candidate pets
        """
        matches = []
        
        for candidate in candidate_pets:
            # Skip if same pet
            if str(candidate.get('_id')) == str(query_pet.get('_id')):
                continue
            
            # Skip if same status (lost-lost or found-found)
            if candidate.get('status') == query_pet.get('status'):
                continue
            
            # Calculate similarity
            similarity_result = self.calculate_hybrid_score(query_pet, candidate)
            
            # Apply threshold
            if similarity_result['hybrid_score'] >= min_threshold:
                match_info = {
                    'pet_id': str(candidate.get('_id')),
                    'pet': candidate,
                    'similarity': similarity_result
                }
                matches.append(match_info)
        
        # Sort by hybrid score (descending)
        matches.sort(key=lambda x: x['similarity']['hybrid_score'], reverse=True)
        
        return matches[:top_k]

# Global instance
hybrid_matching_engine = HybridMatchingEngine()
