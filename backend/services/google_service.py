"""Google Custom Search API integration"""
from googleapiclient.discovery import build
from core.config import get_settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class GoogleSearchService:
    """Service for searching courses and articles using Google Custom Search"""
    
    def __init__(self):
        if not settings.GOOGLE_API_KEY or not settings.GOOGLE_CSE_ID:
            logger.warning("Google Search API not fully configured")
            self.service = None
        else:
            self.service = build('customsearch', 'v1', developerKey=settings.GOOGLE_API_KEY)
            self.cse_id = settings.GOOGLE_CSE_ID
    
    async def search_courses(
        self,
        query: str,
        num_results: int = 10
    ) -> List[Dict]:
        """
        Search for online courses
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of course links and information
        """
        if not self.service:
            logger.error("Google Search service not initialized")
            return []
        
        try:
            logger.info(f"Searching courses for: {query}")
            
            # Search for courses on popular platforms
            search_query = f"{query} course site:udemy.com OR site:coursera.org OR site:edx.org OR site:pluralsight.com"
            
            result = self.service.cse().list(
                q=search_query,
                cx=self.cse_id,
                num=min(num_results, 10)
            ).execute()
            
            courses = []
            for item in result.get('items', []):
                courses.append({
                    "title": item.get('title'),
                    "link": item.get('link'),
                    "snippet": item.get('snippet'),
                    "source": self._extract_domain(item.get('link', ''))
                })
            
            logger.info(f"Found {len(courses)} courses")
            return courses
            
        except Exception as e:
            logger.error(f"Google course search failed: {e}")
            return []
    
    async def search_articles(
        self,
        query: str,
        num_results: int = 10
    ) -> List[Dict]:
        """
        Search for educational articles and tutorials
        
        Args:
            query: Search query
            num_results: Number of results
            
        Returns:
            List of article links
        """
        if not self.service:
            return []
        
        try:
            logger.info(f"Searching articles for: {query}")
            
            search_query = f"{query} tutorial guide"
            
            result = self.service.cse().list(
                q=search_query,
                cx=self.cse_id,
                num=min(num_results, 10)
            ).execute()
            
            articles = []
            for item in result.get('items', []):
                articles.append({
                    "title": item.get('title'),
                    "link": item.get('link'),
                    "snippet": item.get('snippet'),
                    "source": self._extract_domain(item.get('link', ''))
                })
            
            logger.info(f"Found {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"Google article search failed: {e}")
            return []
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return "unknown"

def get_google_service() -> GoogleSearchService:
    """Get GoogleSearchService instance"""
    return GoogleSearchService()
