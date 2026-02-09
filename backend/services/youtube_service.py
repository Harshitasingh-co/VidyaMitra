"""YouTube Data API integration"""
from googleapiclient.discovery import build
from core.config import get_settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class YouTubeService:
    """Service for fetching YouTube learning resources"""
    
    def __init__(self):
        if not settings.YOUTUBE_API_KEY:
            logger.warning("YouTube API key not configured")
            self.youtube = None
        else:
            self.youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 10,
        order: str = "relevance"
    ) -> List[Dict]:
        """
        Search for educational videos
        
        Args:
            query: Search query
            max_results: Maximum number of results
            order: Sort order (relevance/viewCount/rating)
            
        Returns:
            List of video information
        """
        if not self.youtube:
            logger.error("YouTube service not initialized")
            return []
        
        try:
            logger.info(f"Searching YouTube for: {query}")
            
            request = self.youtube.search().list(
                part="snippet",
                q=f"{query} tutorial",
                type="video",
                maxResults=max_results,
                order=order,
                videoCategoryId="27",  # Education category
                relevanceLanguage="en"
            )
            
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                videos.append({
                    "video_id": video_id,
                    "title": snippet['title'],
                    "description": snippet['description'],
                    "channel": snippet['channelTitle'],
                    "published_at": snippet['publishedAt'],
                    "thumbnail": snippet['thumbnails']['medium']['url'],
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })
            
            logger.info(f"Found {len(videos)} videos")
            return videos
            
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return []
    
    async def get_playlists(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for educational playlists
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of playlist information
        """
        if not self.youtube:
            return []
        
        try:
            logger.info(f"Searching YouTube playlists for: {query}")
            
            request = self.youtube.search().list(
                part="snippet",
                q=f"{query} course playlist",
                type="playlist",
                maxResults=max_results,
                order="relevance"
            )
            
            response = request.execute()
            
            playlists = []
            for item in response.get('items', []):
                playlist_id = item['id']['playlistId']
                snippet = item['snippet']
                
                playlists.append({
                    "playlist_id": playlist_id,
                    "title": snippet['title'],
                    "description": snippet['description'],
                    "channel": snippet['channelTitle'],
                    "thumbnail": snippet['thumbnails']['medium']['url'],
                    "url": f"https://www.youtube.com/playlist?list={playlist_id}"
                })
            
            logger.info(f"Found {len(playlists)} playlists")
            return playlists
            
        except Exception as e:
            logger.error(f"YouTube playlist search failed: {e}")
            return []

def get_youtube_service() -> YouTubeService:
    """Get YouTubeService instance"""
    return YouTubeService()
