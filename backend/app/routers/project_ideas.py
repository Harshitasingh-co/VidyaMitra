"""
API endpoints for AI Project Idea Generator
Feature 5: Resume Booster Projects
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ai.project_generator_ai import get_project_generator_ai
from utils.response_formatter import get_response_formatter
from core.security import get_current_user
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ProjectGenerationRequest(BaseModel):
    target_role: str
    missing_skills: List[str]
    experience_level: str  # entry/mid/senior
    num_projects: Optional[int] = 3

class SkillProjectRequest(BaseModel):
    skill: str
    target_role: str
    experience_level: str

class ProjectEnhancementRequest(BaseModel):
    project_description: str
    missing_skills: List[str]

class PortfolioStrategyRequest(BaseModel):
    target_role: str
    current_projects: Optional[List[str]] = []
    missing_skills: List[str]

@router.post("/generate")
async def generate_projects(
    request: ProjectGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    AI Project Idea Generator (Resume Booster)
    Feature 5: Generate personalized, resume-ready project ideas
    
    Generates projects that:
    - Cover missing skills
    - Are realistic and achievable
    - Add measurable resume impact
    - Include implementation steps
    - Provide resume bullet points
    """
    try:
        logger.info(f"User {current_user['email']} generating {request.num_projects} projects for {request.target_role}")
        
        # Validate experience level
        valid_levels = ["entry", "mid", "senior"]
        if request.experience_level.lower() not in valid_levels:
            raise HTTPException(
                status_code=400,
                detail=f"experience_level must be one of: {', '.join(valid_levels)}"
            )
        
        # Generate projects
        project_gen_ai = get_project_generator_ai()
        projects = await project_gen_ai.generate_projects(
            target_role=request.target_role,
            missing_skills=request.missing_skills,
            experience_level=request.experience_level,
            num_projects=request.num_projects
        )
        
        # Add metadata
        projects['request_info'] = {
            "target_role": request.target_role,
            "skills_to_cover": request.missing_skills,
            "experience_level": request.experience_level,
            "projects_generated": len(projects.get('projects', []))
        }
        
        formatter = get_response_formatter()
        return formatter.success(projects, "Project ideas generated successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Project generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Project generation failed: {str(e)}")

@router.post("/skill-project")
async def generate_skill_project(
    request: SkillProjectRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a focused project for a specific skill
    
    Creates a detailed project that demonstrates mastery of one skill
    with step-by-step implementation guide
    """
    try:
        logger.info(f"User {current_user['email']} generating project for skill: {request.skill}")
        
        project_gen_ai = get_project_generator_ai()
        project = await project_gen_ai.generate_project_for_specific_skill(
            skill=request.skill,
            target_role=request.target_role,
            experience_level=request.experience_level
        )
        
        formatter = get_response_formatter()
        return formatter.success(project, f"Project for {request.skill} generated")
        
    except Exception as e:
        logger.error(f"Skill project generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhance-project")
async def enhance_project(
    request: ProjectEnhancementRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Suggest enhancements to existing project
    
    Provides suggestions to add more skills to an existing project
    """
    try:
        logger.info(f"User {current_user['email']} requesting project enhancements")
        
        project_gen_ai = get_project_generator_ai()
        enhancements = await project_gen_ai.enhance_existing_project(
            project_description=request.project_description,
            missing_skills=request.missing_skills
        )
        
        formatter = get_response_formatter()
        return formatter.success(enhancements, "Project enhancements suggested")
        
    except Exception as e:
        logger.error(f"Project enhancement failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio-strategy")
async def generate_portfolio_strategy(
    request: PortfolioStrategyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate overall portfolio strategy
    
    Provides:
    - Portfolio assessment
    - Recommended projects
    - Presentation tips
    - GitHub profile improvements
    - Timeline
    """
    try:
        logger.info(f"User {current_user['email']} generating portfolio strategy")
        
        project_gen_ai = get_project_generator_ai()
        strategy = await project_gen_ai.generate_portfolio_strategy(
            target_role=request.target_role,
            current_projects=request.current_projects,
            missing_skills=request.missing_skills
        )
        
        formatter = get_response_formatter()
        return formatter.success(strategy, "Portfolio strategy generated")
        
    except Exception as e:
        logger.error(f"Portfolio strategy generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrated-workflow")
async def integrated_workflow(
    resume_text: str,
    target_role: str,
    experience_years: int,
    experience_level: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Integrated workflow: Resume → Job Match → Project Ideas
    
    Complete flow:
    1. Extract skills from resume
    2. Match to jobs and find gaps
    3. Generate projects to close gaps
    """
    try:
        logger.info(f"User {current_user['email']} starting integrated workflow")
        
        from ai.resume_ai import get_resume_ai
        from ai.job_match_ai import get_job_match_ai
        
        # Step 1: Extract skills
        resume_ai = get_resume_ai()
        user_skills = await resume_ai.extract_skills(resume_text)
        
        # Step 2: Match jobs
        job_match_ai = get_job_match_ai()
        job_matches = await job_match_ai.match_jobs(
            user_skills=user_skills,
            experience_years=experience_years,
            target_domain=None
        )
        
        # Step 3: Find best match and get missing skills
        best_match = None
        if job_matches.get('job_matches'):
            # Find the match for target role or best overall
            for match in job_matches['job_matches']:
                if match['role'] == target_role:
                    best_match = match
                    break
            if not best_match:
                best_match = job_matches['job_matches'][0]
        
        if not best_match:
            raise HTTPException(status_code=404, detail="No suitable job matches found")
        
        missing_skills = best_match.get('missing_critical_skills', []) + best_match.get('missing_preferred_skills', [])[:2]
        
        # Step 4: Generate projects
        project_gen_ai = get_project_generator_ai()
        projects = await project_gen_ai.generate_projects(
            target_role=target_role,
            missing_skills=missing_skills,
            experience_level=experience_level,
            num_projects=3
        )
        
        # Compile results
        result = {
            "step_1_skills_extracted": {
                "skills": user_skills,
                "total_skills": len(user_skills)
            },
            "step_2_job_match": {
                "best_match": best_match,
                "all_matches": job_matches.get('job_matches', [])[:5]
            },
            "step_3_projects": projects,
            "workflow_summary": {
                "current_fit_score": best_match.get('fit_score', 0),
                "skills_to_develop": missing_skills,
                "projects_to_complete": len(projects.get('projects', [])),
                "estimated_improvement": "+15-25 fit score points"
            }
        }
        
        formatter = get_response_formatter()
        return formatter.success(result, "Integrated workflow completed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Integrated workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
