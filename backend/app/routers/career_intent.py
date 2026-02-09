from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.models.career_intent import CareerIntent, CareerIntentResponse, ContextAwareResumeRequest
from app.services.career_intent_service import get_career_intent_service
from ai.context_aware_resume_ai import get_context_aware_resume_ai
from utils.pdf_parser import get_document_parser
from utils.response_formatter import get_response_formatter
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/career-intent", response_model=CareerIntentResponse)
async def submit_career_intent(intent: CareerIntent):
    """
    Step 1: Collect user's career intent before resume analysis
    
    This endpoint captures:
    - Desired role
    - Experience level
    - Target companies
    - Preferred industries
    
    Returns an intent_id to be used in resume analysis
    """
    try:
        logger.info(f"Receiving career intent: {intent.desired_role} ({intent.experience_level})")
        
        # Validate inputs
        if not intent.desired_role or len(intent.desired_role.strip()) < 2:
            raise HTTPException(status_code=400, detail="Desired role is required")
        
        if not intent.experience_level:
            raise HTTPException(status_code=400, detail="Experience level is required")
        
        if not intent.target_companies or len(intent.target_companies) == 0:
            raise HTTPException(status_code=400, detail="At least one target company type is required")
        
        # Store intent
        intent_service = get_career_intent_service()
        intent_id = intent_service.store_intent(intent)
        
        return CareerIntentResponse(
            intent_id=intent_id,
            message="Career intent captured successfully",
            next_step="Upload your resume for context-aware analysis"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process career intent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process intent: {str(e)}")

@router.get("/career-intent/{intent_id}")
async def get_career_intent(intent_id: str):
    """
    Retrieve stored career intent by ID
    """
    try:
        intent_service = get_career_intent_service()
        intent = intent_service.get_intent(intent_id)
        
        if not intent:
            raise HTTPException(status_code=404, detail="Career intent not found or expired")
        
        formatter = get_response_formatter()
        return formatter.success(intent.model_dump(), "Career intent retrieved")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve career intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/context-aware-analyze")
async def context_aware_resume_analysis(request: ContextAwareResumeRequest):
    """
    Step 2: Analyze resume with career context
    
    This endpoint performs context-aware resume analysis using:
    - Resume text
    - Career intent (either by intent_id or direct object)
    
    Returns:
    - Role fit score
    - Skill gap analysis (existing, missing, partially matching)
    - Technical skills required with importance levels
    - Certification recommendations with links
    - Project ideas with datasets and resume bullets
    - Company-specific advice
    - ATS optimization suggestions
    """
    try:
        # Get career intent
        career_intent = None
        
        if request.intent_id:
            # Retrieve from storage
            intent_service = get_career_intent_service()
            career_intent = intent_service.get_intent(request.intent_id)
            
            if not career_intent:
                raise HTTPException(
                    status_code=404,
                    detail="Career intent not found. Please submit career intent first."
                )
        elif request.career_intent:
            # Use provided intent directly
            career_intent = request.career_intent
        else:
            raise HTTPException(
                status_code=400,
                detail="Either intent_id or career_intent must be provided"
            )
        
        logger.info(
            f"Context-aware analysis for {career_intent.desired_role} "
            f"({career_intent.experience_level})"
        )
        
        # Validate resume text
        if not request.resume_text or len(request.resume_text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Resume text is too short. Please provide a complete resume."
            )
        
        # Perform context-aware analysis
        resume_ai = get_context_aware_resume_ai()
        analysis = await resume_ai.analyze_with_context(
            resume_text=request.resume_text,
            career_intent=career_intent
        )
        
        formatter = get_response_formatter()
        return formatter.success(
            analysis,
            "Context-aware resume analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Context-aware analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/upload-with-intent")
async def upload_resume_with_intent(
    file: UploadFile = File(...),
    intent_id: Optional[str] = None
):
    """
    Combined endpoint: Upload resume and optionally link to career intent
    
    This is a convenience endpoint that:
    1. Uploads and extracts text from resume
    2. If intent_id is provided, automatically performs context-aware analysis
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
        
        # Read and extract text
        content = await file.read()
        parser = get_document_parser()
        text_content = parser.extract_text(content, file.filename)
        
        if not text_content or len(text_content) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from file"
            )
        
        result = {
            "filename": file.filename,
            "text_length": len(text_content),
            "text_preview": text_content[:500] + "..." if len(text_content) > 500 else text_content,
            "full_text": text_content
        }
        
        # If intent_id provided, perform analysis automatically
        if intent_id:
            intent_service = get_career_intent_service()
            career_intent = intent_service.get_intent(intent_id)
            
            if career_intent:
                logger.info(f"Performing automatic context-aware analysis with intent: {intent_id}")
                
                resume_ai = get_context_aware_resume_ai()
                analysis = await resume_ai.analyze_with_context(
                    resume_text=text_content,
                    career_intent=career_intent
                )
                
                result["analysis"] = analysis
                result["message"] = "Resume uploaded and analyzed with career context"
            else:
                logger.warning(f"Intent ID {intent_id} not found, skipping analysis")
                result["message"] = "Resume uploaded successfully (intent not found)"
        else:
            result["message"] = "Resume uploaded successfully. Submit for analysis next."
        
        formatter = get_response_formatter()
        return formatter.success(result, result["message"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/skill-gap-details")
async def get_detailed_skill_gap(
    request: dict
):
    """
    Get detailed skill gap analysis with learning paths
    
    This endpoint provides:
    - Critical vs nice-to-have gaps
    - Learning resources for each gap
    - Week-by-week learning roadmap
    """
    try:
        existing_skills = request.get('existing_skills', [])
        required_skills = request.get('required_skills', [])
        desired_role = request.get('desired_role', '')
        
        resume_ai = get_context_aware_resume_ai()
        gap_analysis = await resume_ai.get_skill_gap_details(
            existing_skills=existing_skills,
            required_skills=required_skills,
            desired_role=desired_role
        )
        
        formatter = get_response_formatter()
        return formatter.success(gap_analysis, "Skill gap analysis completed")
        
    except Exception as e:
        logger.error(f"Skill gap analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
