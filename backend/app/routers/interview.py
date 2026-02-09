from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ai.interview_ai import get_interview_ai
from utils.response_formatter import get_response_formatter
from core.security import get_current_user
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class InterviewStartRequest(BaseModel):
    role: str
    experience_level: str  # entry/mid/senior
    industry: Optional[str] = "Technology"
    num_questions: Optional[int] = 5

class AnswerEvaluationRequest(BaseModel):
    question: str
    category: str
    answer: str

class OverallFeedbackRequest(BaseModel):
    evaluations: List[dict]
    role: str

# Helper function to get user or use demo user
def get_user_or_demo(current_user: Optional[dict] = None):
    return current_user or {"email": "demo@vidyamitra.com", "id": "demo"}

@router.post("/start")
async def start_interview(
    request: InterviewStartRequest
):
    """
    Start mock interview session
    Scenario 2: AI-Driven Mock Interview
    
    Generates role-specific interview questions
    """
    try:
        user = get_user_or_demo()
        logger.info(f"User {user['email']} starting interview for {request.role}")
        
        interview_ai = get_interview_ai()
        questions = await interview_ai.generate_questions(
            role=request.role,
            experience_level=request.experience_level,
            industry=request.industry,
            num_questions=request.num_questions
        )
        
        formatter = get_response_formatter()
        return formatter.success({
            "session_id": f"interview_{user['email']}_{request.role}",
            "role": request.role,
            "experience_level": request.experience_level,
            "questions": questions,
            "total_questions": len(questions)
        }, "Interview session started")
        
    except Exception as e:
        logger.error(f"Interview start failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

@router.post("/answer")
async def evaluate_answer(
    request: AnswerEvaluationRequest
):
    """
    Evaluate candidate's answer
    
    Analyzes:
    - Confidence level
    - Clarity and communication
    - Technical accuracy
    - Tone and professionalism
    """
    try:
        user = get_user_or_demo()
        logger.info(f"User {user['email']} submitting answer for evaluation")
        
        interview_ai = get_interview_ai()
        evaluation = await interview_ai.evaluate_answer(
            question=request.question,
            category=request.category,
            answer=request.answer
        )
        
        formatter = get_response_formatter()
        return formatter.success(evaluation, "Answer evaluated successfully")
        
    except Exception as e:
        logger.error(f"Answer evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@router.post("/followup")
async def generate_followup(
    question: str,
    answer: str
):
    """Generate follow-up question based on answer"""
    try:
        interview_ai = get_interview_ai()
        followup = await interview_ai.generate_followup_question(question, answer)
        
        formatter = get_response_formatter()
        return formatter.success({"followup_question": followup}, "Follow-up generated")
        
    except Exception as e:
        logger.error(f"Follow-up generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def get_overall_feedback(
    request: OverallFeedbackRequest
):
    """
    Get overall interview performance feedback
    
    Provides:
    - Overall performance rating
    - Key strengths and weaknesses
    - Improvement plan
    - Readiness assessment
    """
    try:
        user = get_user_or_demo()
        logger.info(f"User {user['email']} requesting overall feedback")
        
        interview_ai = get_interview_ai()
        feedback = await interview_ai.generate_overall_feedback(
            evaluations=request.evaluations,
            role=request.role
        )
        
        formatter = get_response_formatter()
        return formatter.success(feedback, "Overall feedback generated")
        
    except Exception as e:
        logger.error(f"Feedback generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
