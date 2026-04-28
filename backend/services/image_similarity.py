import cv2
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util
from PIL import Image, ImageFilter
import requests
from typing import List, Optional, Tuple
import io
import logging

logger = logging.getLogger(__name__)

class ImageSimilarityEngine:
    def __init__(self):
        # Load CLIP model for image embeddings
        self.model = SentenceTransformer("clip-ViT-B-32")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # Quality thresholds
        self.MIN_RESOLUTION = (224, 224)
        self.BLUR_THRESHOLD = 100.0  # Lower values mean more blurry
        self.BRIGHTNESS_MIN = 30
        self.BRIGHTNESS_MAX = 225
        
    def check_image_quality(self, image_url: str) -> Tuple[bool, float, str]:
        """
        Check image quality and return (is_valid, quality_score, reason)
        """
        try:
            # Download image
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            
            # Check resolution
            width, height = image.size
            if width < self.MIN_RESOLUTION[0] or height < self.MIN_RESOLUTION[1]:
                return False, 0.0, f"Image too small: {width}x{height}"
            
            # Convert to numpy array for OpenCV operations
            img_array = np.array(image)
            
            # Check blur using Laplacian variance
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if blur_score < self.BLUR_THRESHOLD:
                return False, blur_score, f"Image too blurry: {blur_score:.2f}"
            
            # Check brightness
            brightness = np.mean(gray)
            if brightness < self.BRIGHTNESS_MIN or brightness > self.BRIGHTNESS_MAX:
                return False, brightness, f"Poor brightness: {brightness:.2f}"
            
            # Calculate overall quality score (0-1)
            resolution_score = min(width * height / (1920 * 1080), 1.0)
            blur_score_norm = min(blur_score / 500, 1.0)
            brightness_score = 1.0 - abs(brightness - 127) / 127
            
            quality_score = (resolution_score * 0.3 + blur_score_norm * 0.4 + brightness_score * 0.3)
            
            return True, quality_score, "Good quality"
            
        except Exception as e:
            logger.error(f"Error checking image quality: {e}")
            return False, 0.0, f"Error processing image: {str(e)}"
    
    def get_image_embedding(self, image_url: str) -> Optional[np.ndarray]:
        """
        Generate embedding for a single image URL
        """
        try:
            # Check quality first
            is_valid, quality_score, reason = self.check_image_quality(image_url)
            if not is_valid:
                logger.warning(f"Image quality check failed: {reason}")
                return None
            
            # Download and process image
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            
            # Generate embedding
            with torch.no_grad():
                embedding = self.model.encode(image, convert_to_tensor=True)
                return embedding.cpu().numpy()
                
        except Exception as e:
            logger.error(f"Error generating embedding for {image_url}: {e}")
            return None
    
    def get_average_embedding(self, image_urls: List[str]) -> Optional[np.ndarray]:
        """
        Generate average embedding from multiple image URLs
        """
        embeddings = []
        
        for url in image_urls:
            embedding = self.get_image_embedding(url)
            if embedding is not None:
                embeddings.append(embedding)
        
        if not embeddings:
            return None
        
        # Average the embeddings
        avg_embedding = np.mean(embeddings, axis=0)
        return avg_embedding
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        if embedding1 is None or embedding2 is None:
            return 0.0
        
        # Convert to tensors
        tensor1 = torch.from_numpy(embedding1).float()
        tensor2 = torch.from_numpy(embedding2).float()
        
        # Calculate cosine similarity
        similarity = util.cos_sim(tensor1, tensor2)
        return float(similarity.item())
    
    def detect_duplicate(self, embedding: np.ndarray, existing_embeddings: List[np.ndarray], 
                        threshold: float = 0.95) -> Tuple[bool, Optional[int]]:
        """
        Detect if an embedding is duplicate of existing ones
        Returns (is_duplicate, index_of_duplicate)
        """
        if not existing_embeddings:
            return False, None
        
        for i, existing_emb in enumerate(existing_embeddings):
            similarity = self.calculate_similarity(embedding, existing_emb)
            if similarity >= threshold:
                return True, i
        
        return False, None
    
    def find_top_k_similar(self, query_embedding: np.ndarray, 
                          candidate_embeddings: List[np.ndarray], 
                          k: int = 5) -> List[Tuple[int, float]]:
        """
        Find top-k most similar embeddings
        Returns list of (index, similarity_score) tuples
        """
        if not candidate_embeddings:
            return []
        
        similarities = []
        for i, candidate_emb in enumerate(candidate_embeddings):
            if candidate_emb is not None:
                similarity = self.calculate_similarity(query_embedding, candidate_emb)
                similarities.append((i, similarity))
        
        # Sort by similarity (descending) and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

# Global instance
image_similarity_engine = ImageSimilarityEngine()
