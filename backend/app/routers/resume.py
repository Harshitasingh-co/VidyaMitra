from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from ai.resume_ai import get_resume_ai
from utils.pdf_parser import get_document_parser
from utils.response_formatter import get_response_formatter
from services.youtube_service import get_youtube_service
from services.google_service import get_google_service
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    target_role: Optional[str] = "General"

class JobMatchRequest(BaseModel):
    resume_text: str
    job_description: str

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...)
):
    """
    Upload and extract text from resume file
    Supports: PDF, DOCX, TXT
    """
    try:
        logger.info(f"Uploading resume: {file.filename}")
        
        # Validate file type
        allowed_extensions = ['pdf', 'docx', 'doc', 'txt']
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Extract text
        parser = get_document_parser()
        text_content = parser.extract_text(content, file.filename)
        
        if not text_content or len(text_content) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from file"
            )
        
        formatter = get_response_formatter()
        return formatter.success({
            "filename": file.filename,
            "text_length": len(text_content),
            "text_preview": text_content[:500] + "..." if len(text_content) > 500 else text_content,
            "full_text": text_content
        }, "Resume uploaded and processed successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/analyze")
async def analyze_resume(
    request: ResumeAnalysisRequest
):
    """
    Analyze resume using AI
    Scenario 1: Personalized Resume Evaluation and Skill Mapping
    
    Returns:
    - ATS score
    - Strengths and weaknesses
    - Skill gaps
    - Learning recommendations
    """
    try:
        logger.info(f"Analyzing resume for role: {request.target_role}")
        
        # AI Analysis
        resume_ai = get_resume_ai()
        analysis = await resume_ai.analyze_resume(
            resume_text=request.resume_text,
            target_role=request.target_role
        )
        
        # Fetch learning resources for missing skills (optional - won't fail if YouTube API not configured)
        missing_skills = analysis.get('missing_skills', [])
        learning_resources = []
        
        if missing_skills:
            try:
                youtube_service = get_youtube_service()
                for skill in missing_skills[:3]:  # Top 3 skills
                    try:
                        videos = await youtube_service.search_videos(skill, max_results=3)
                        if videos:
                            learning_resources.append({
                                "skill": skill,
                                "videos": videos
                            })
                    except Exception as e:
                        logger.warning(f"Failed to fetch videos for {skill}: {e}")
            except Exception as e:
                logger.warning(f"YouTube service not available: {e}")
        
        analysis['external_resources'] = learning_resources
        
        formatter = get_response_formatter()
        return formatter.success(analysis, "Resume analyzed successfully")
        
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/extract-skills")
async def extract_skills(
    request: ResumeAnalysisRequest
):
    """Extract skills from resume"""
    try:
        resume_ai = get_resume_ai()
        skills = await resume_ai.extract_skills(request.resume_text)
        
        formatter = get_response_formatter()
        return formatter.success({"skills": skills}, "Skills extracted successfully")
        
    except Exception as e:
        logger.error(f"Skill extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match-job")
async def match_job_description(
    request: JobMatchRequest
):
    """Compare resume against job description"""
    try:
        resume_ai = get_resume_ai()
        match_result = await resume_ai.compare_with_job_description(
            resume_text=request.resume_text,
            job_description=request.job_description
        )
        
        formatter = get_response_formatter()
        return formatter.success(match_result, "Job match analysis completed")
        
    except Exception as e:
        logger.error(f"Job matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
