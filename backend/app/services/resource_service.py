import os
import requests
from googleapiclient.discovery import build
from typing import List, Dict

class ResourceService:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")
    
    async def search_courses(self, query: str) -> List[Dict]:
        """Search for courses using Google Custom Search API"""
        try:
            service = build("customsearch", "v1", developerKey=self.google_api_key)
            result = service.cse().list(q=f"{query} online course", cx="your-search-engine-id").execute()
            
            courses = []
            for item in result.get('items', [])[:5]:
                courses.append({
                    "title": item.get('title'),
                    "link": item.get('link'),
                    "snippet": item.get('snippet')
                })
            return courses
        except Exception as e:
            return [{"error": str(e)}]
    
    async def search_youtube_videos(self, topic: str) -> List[Dict]:
        """Search for educational videos on YouTube"""
        try:
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            request = youtube.search().list(
                part="snippet",
                q=f"{topic} tutorial",
                type="video",
                maxResults=5,
                order="relevance"
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                videos.append({
                    "title": item['snippet']['title'],
                    "video_id": item['id']['videoId'],
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    "thumbnail": item['snippet']['thumbnails']['medium']['url'],
                    "description": item['snippet']['description']
                })
            return videos
        except Exception as e:
            return [{"error": str(e)}]
    
    async def search_images(self, query: str) -> List[Dict]:
        """Search for images using Pexels API"""
        try:
            headers = {"Authorization": self.pexels_api_key}
            response = requests.get(
                f"https://api.pexels.com/v1/search?query={query}&per_page=10",
                headers=headers
            )
            data = response.json()
            
            images = []
            for photo in data.get('photos', []):
                images.append({
                    "id": photo['id'],
                    "url": photo['src']['medium'],
                    "photographer": photo['photographer'],
                    "alt": photo.get('alt', query)
                })
            return images
        except Exception as e:
            return [{"error": str(e)}]
    
    async def get_news(self, topic: str) -> List[Dict]:
        """Get latest news using News API"""
        try:
            response = requests.get(
                f"https://newsapi.org/v2/everything?q={topic}&apiKey={self.news_api_key}&pageSize=5"
            )
            data = response.json()
            
            news = []
            for article in data.get('articles', []):
                news.append({
                    "title": article['title'],
                    "description": article['description'],
                    "url": article['url'],
                    "source": article['source']['name'],
                    "published_at": article['publishedAt']
                })
            return news
        except Exception as e:
            return [{"error": str(e)}]
