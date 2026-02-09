from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ai.career_ai import get_career_ai
from utils.response_formatter import get_response_formatter
from services.youtube_service import get_youtube_service
from services.google_service import get_google_service
from core.security import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CareerRoadmapRequest(BaseModel):
    current_role: str
    target_role: str
    current_skills: List[str]
    experience_years: int

class SkillGapRequest(BaseModel):
    current_skills: List[str]
    target_role: str

@router.post("/roadmap")
async def generate_career_roadmap(
    request: CareerRoadmapRequest
):
    """
    Generate comprehensive career transition roadmap
    Scenario 3: Career Path Recommendation and Upskilling Planner
    
    Provides:
    - Transferable skills analysis
    - Skills to acquire
    - 3-6 month learning path
    - Certifications
    - Milestones
    """
    try:
        logger.info(f"Requesting roadmap: {request.current_role} -> {request.target_role}")
        
        career_ai = get_career_ai()
        roadmap = await career_ai.generate_career_roadmap(
            current_role=request.current_role,
            target_role=request.target_role,
            current_skills=request.current_skills,
            experience_years=request.experience_years
        )
        
        # Fetch learning resources for top skills (optional)
        skills_to_acquire = roadmap.get('skills_to_acquire', [])
        learning_resources = []
        
        if skills_to_acquire:
            try:
                youtube_service = get_youtube_service()
                google_service = get_google_service()
                
                for skill_obj in skills_to_acquire[:3]:  # Top 3 skills
                    skill_name = skill_obj.get('skill') if isinstance(skill_obj, dict) else skill_obj
                    
                    videos = await youtube_service.search_videos(skill_name, max_results=3)
                    courses = await google_service.search_courses(skill_name, num_results=3)
                    
                    learning_resources.append({
                        "skill": skill_name,
                        "videos": videos,
                        "courses": courses
                    })
            except Exception as resource_error:
                logger.warning(f"Failed to fetch learning resources: {resource_error}")
                # Continue without resources
        
        roadmap['learning_resources'] = learning_resources
        
        formatter = get_response_formatter()
        return formatter.success(roadmap, "Career roadmap generated successfully")
        
    except Exception as e:
        logger.error(f"Career roadmap generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {str(e)}")

@router.post("/skill-gap")
async def analyze_skill_gap(
    request: SkillGapRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze skill gaps for target role
    
    Returns:
    - Matching skills
    - Missing critical skills
    - Learning priorities
    """
    try:
        logger.info(f"User {current_user['email']} analyzing skill gap for {request.target_role}")
        
        career_ai = get_career_ai()
        gap_analysis = await career_ai.analyze_skill_gap(
            current_skills=request.current_skills,
            target_role=request.target_role
        )
        
        formatter = get_response_formatter()
        return formatter.success(gap_analysis, "Skill gap analyzed")
        
    except Exception as e:
        logger.error(f"Skill gap analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/role-requirements/{role}")
async def get_role_requirements(
    role: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed requirements for a specific role"""
    try:
        career_ai = get_career_ai()
        requirements = await career_ai.get_role_requirements(role)
        
        formatter = get_response_formatter()
        return formatter.success(requirements, f"Requirements for {role}")
        
    except Exception as e:
        logger.error(f"Role requirements fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learning-resources")
async def get_learning_resources(
    skills: List[str],
    learning_style: str = "mixed",
    current_user: dict = Depends(get_current_user)
):
    """Get curated learning resources for specific skills"""
    try:
        career_ai = get_career_ai()
        resources = await career_ai.suggest_learning_resources(skills, learning_style)
        
        formatter = get_response_formatter()
        return formatter.success(resources, "Learning resources suggested")
        
    except Exception as e:
        logger.error(f"Learning resource suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
