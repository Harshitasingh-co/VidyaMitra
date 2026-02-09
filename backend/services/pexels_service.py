"""Pexels API integration for visual learning resources"""
import httpx
from core.config import get_settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class PexelsService:
    """Service for fetching educational images from Pexels"""
    
    def __init__(self):
        self.api_key = settings.PEXELS_API_KEY
        self.base_url = "https://api.pexels.com/v1"
    
    async def search_images(
        self,
        query: str,
        per_page: int = 15,
        orientation: str = "landscape"
    ) -> List[Dict]:
        """
        Search for educational images
        
        Args:
            query: Search query
            per_page: Number of images per page
            orientation: Image orientation (landscape/portrait/square)
            
        Returns:
            List of image information
        """
        if not self.api_key:
            logger.warning("Pexels API key not configured")
            return []
        
        try:
            logger.info(f"Searching Pexels for: {query}")
            
            headers = {
                "Authorization": self.api_key
            }
            
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": orientation
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    headers=headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
            
            images = []
            for photo in data.get('photos', []):
                images.append({
                    "id": photo['id'],
                    "url": photo['src']['large'],
                    "thumbnail": photo['src']['medium'],
                    "photographer": photo['photographer'],
                    "photographer_url": photo['photographer_url'],
                    "alt": photo.get('alt', query),
                    "width": photo['width'],
                    "height": photo['height']
                })
            
            logger.info(f"Found {len(images)} images")
            return images
            
        except httpx.HTTPError as e:
            logger.error(f"Pexels HTTP error: {e}")
            return []
        except Exception as e:
            logger.error(f"Pexels search failed: {e}")
            return []
    
    async def get_curated_images(self, per_page: int = 15) -> List[Dict]:
        """
        Get curated images
        
        Args:
            per_page: Number of images
            
        Returns:
            List of curated images
        """
        if not self.api_key:
            return []
        
        try:
            headers = {"Authorization": self.api_key}
            params = {"per_page": per_page}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/curated",
                    headers=headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
            
            images = []
            for photo in data.get('photos', []):
                images.append({
                    "id": photo['id'],
                    "url": photo['src']['large'],
                    "thumbnail": photo['src']['medium'],
                    "photographer": photo['photographer'],
                    "alt": photo.get('alt', 'Curated image')
                })
            
            return images
            
        except Exception as e:
            logger.error(f"Pexels curated fetch failed: {e}")
            return []

def get_pexels_service() -> PexelsService:
    """Get PexelsService instance"""
    return PexelsService()
