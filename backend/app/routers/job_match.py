"""
API endpoints for AI Skill-to-Job Matching Engine
Feature 4: Job Matching
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ai.job_match_ai import get_job_match_ai
from ai.resume_ai import get_resume_ai
from utils.response_formatter import get_response_formatter
from core.security import get_current_user
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class JobMatchRequest(BaseModel):
    resume_text: Optional[str] = None
    user_skills: Optional[List[str]] = None
    experience_years: int
    target_domain: Optional[str] = None

class SkillGapAnalysisRequest(BaseModel):
    user_skills: List[str]
    target_role: str
    target_domain: Optional[str] = None

@router.post("/match")
async def match_jobs(
    request: JobMatchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    AI Skill-to-Job Matching Engine
    Feature 4: Determine job fit and identify skill gaps
    
    Analyzes user skills against job roles and provides:
    - Fit score for each role (0-100)
    - Matching skills
    - Missing critical skills
    - Quick wins (easy-to-learn, high-impact skills)
    - Specific recommendations
    """
    try:
        logger.info(f"User {current_user['email']} requesting job match")
        
        # Extract skills from resume if provided
        user_skills = request.user_skills
        if not user_skills and request.resume_text:
            logger.info("Extracting skills from resume text")
            resume_ai = get_resume_ai()
            user_skills = await resume_ai.extract_skills(request.resume_text)
        
        if not user_skills:
            raise HTTPException(
                status_code=400,
                detail="Either user_skills or resume_text must be provided"
            )
        
        # Perform job matching
        job_match_ai = get_job_match_ai()
        matches = await job_match_ai.match_jobs(
            user_skills=user_skills,
            experience_years=request.experience_years,
            target_domain=request.target_domain
        )
        
        # Add metadata
        matches['user_skills_analyzed'] = user_skills
        matches['experience_years'] = request.experience_years
        matches['target_domain'] = request.target_domain or "All domains"
        
        formatter = get_response_formatter()
        return formatter.success(matches, "Job matching completed successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job matching failed: {e}")
        raise HTTPException(status_code=500, detail=f"Job matching failed: {str(e)}")

@router.post("/skill-gap-analysis")
async def analyze_skill_gap(
    request: SkillGapAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Detailed skill gap analysis for a specific role
    
    Provides:
    - Overall fit score
    - Matching skills
    - Missing critical skills with learning difficulty
    - Skill development priority
    - Timeline to readiness
    """
    try:
        logger.info(f"User {current_user['email']} analyzing skill gap for {request.target_role}")
        
        job_match_ai = get_job_match_ai()
        gap_analysis = await job_match_ai.analyze_skill_gap_for_role(
            user_skills=request.user_skills,
            target_role=request.target_role,
            target_domain=request.target_domain
        )
        
        formatter = get_response_formatter()
        return formatter.success(gap_analysis, "Skill gap analysis completed")
        
    except Exception as e:
        logger.error(f"Skill gap analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/domains")
async def get_available_domains(current_user: dict = Depends(get_current_user)):
    """Get list of available job domains"""
    job_match_ai = get_job_match_ai()
    domains = list(job_match_ai.job_maps.keys())
    
    formatter = get_response_formatter()
    return formatter.success({
        "domains": domains,
        "total_roles": sum(len(roles) for roles in job_match_ai.job_maps.values())
    }, "Available domains retrieved")

@router.get("/roles/{domain}")
async def get_roles_by_domain(
    domain: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all roles in a specific domain"""
    job_match_ai = get_job_match_ai()
    
    if domain not in job_match_ai.job_maps:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
    
    roles = job_match_ai.job_maps[domain]
    roles_info = [
        {
            "role": role_name,
            "required_skills": info["required"],
            "preferred_skills": info["preferred"],
            "experience": info["experience"]
        }
        for role_name, info in roles.items()
    ]
    
    formatter = get_response_formatter()
    return formatter.success({
        "domain": domain,
        "roles": roles_info
    }, f"Roles in {domain} retrieved")
