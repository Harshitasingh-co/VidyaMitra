from fastapi import APIRouter, HTTPException, Query
from app.services.resource_service import ResourceService
from typing import Optional

router = APIRouter()
resource_service = ResourceService()

@router.get("/courses")
async def search_courses(query: str = Query(..., min_length=2)):
    """Search for courses using Google and YouTube APIs"""
    try:
        courses = await resource_service.search_courses(query)
        return {"query": query, "courses": courses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/videos")
async def search_videos(topic: str = Query(..., min_length=2)):
    """Search for educational videos on YouTube"""
    try:
        videos = await resource_service.search_youtube_videos(topic)
        return {"topic": topic, "videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/images")
async def search_images(query: str = Query(..., min_length=2)):
    """Search for educational images using Pexels API"""
    try:
        images = await resource_service.search_images(query)
        return {"query": query, "images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/news")
async def get_industry_news(topic: Optional[str] = "technology"):
    """Get latest industry news"""
    try:
        news = await resource_service.get_news(topic)
        return {"topic": topic, "news": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
