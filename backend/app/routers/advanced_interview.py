from fastapi import APIRouter, HTTPException
from app.models.advanced_interview import (
    AdvancedInterviewStartRequest,
    PreInterviewContext,
    InterviewRules,
    TechnicalQuestionRequest,
    TechnicalSubmitRequest,
    AptitudeQuestionRequest,
    AptitudeSubmitRequest,
    SoftSkillsQuestionRequest,
    SoftSkillsSubmitRequest
)
from ai.advanced_interview_ai import get_advanced_interview_ai
from app.services.interview_session_service import get_interview_session_service
from utils.response_formatter import get_response_formatter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/start")
async def start_advanced_interview(request: AdvancedInterviewStartRequest):
    """
    Start advanced adaptive interview
    
    Features:
    - Pre-interview intelligence gathering
    - Dynamic difficulty and weight adjustment
    - Anti-cheating rules setup
    - Skill-aware question selection
    """
    try:
        logger.info(f"Starting advanced interview: type={request.interview_type}")
        
        interview_ai = get_advanced_interview_ai()
        session_service = get_interview_session_service()
        
        # Generate interview configuration based on context
        if request.user_context:
            config = interview_ai.generate_interview_config(request.user_context)
        elif request.custom_config:
            config = request.custom_config
        else:
            # Default configuration
            from app.models.advanced_interview import InterviewConfig
            config = InterviewConfig()
        
        # Create session
        user_id = request.user_context.user_id if request.user_context else "demo_user"
        session_id = session_service.create_session(
            user_id=user_id,
            interview_type=request.interview_type,
            config=config.dict()
        )
        
        # Define interview rules
        rules = InterviewRules()
        
        # Calculate question distribution
        total_questions = config.total_questions
        
        if request.interview_type == "full":
            tech_questions = int(total_questions * (config.technical_weight / 100))
            apt_questions = int(total_questions * (config.aptitude_weight / 100))
            soft_questions = total_questions - tech_questions - apt_questions
        elif request.interview_type == "technical":
            tech_questions = total_questions
            apt_questions = 0
            soft_questions = 0
        elif request.interview_type == "aptitude":
            tech_questions = 0
            apt_questions = total_questions
            soft_questions = 0
        else:  # soft-skills
            tech_questions = 0
            apt_questions = 0
            soft_questions = total_questions
        
        # Store question distribution in session
        session_service.update_session(session_id, {
            "question_distribution": {
                "technical": tech_questions,
                "aptitude": apt_questions,
                "soft_skills": soft_questions
            }
        })
        
        formatter = get_response_formatter()
        return formatter.success({
            "session_id": session_id,
            "interview_type": request.interview_type,
            "config": config.dict(),
            "rules": rules.dict(),
            "question_distribution": {
                "technical": tech_questions,
                "aptitude": apt_questions,
                "soft_skills": soft_questions
            },
            "total_questions": total_questions,
            "message": "Interview session created. Follow the rules strictly.",
            "next_step": "Request first question using appropriate endpoint"
        }, "Interview started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/technical/question")
async def get_technical_question(request: TechnicalQuestionRequest):
    """
    Get technical/coding question
    
    Process:
    1. Candidate explains approach first
    2. Then writes code
    3. Anti-cheating monitoring active
    """
    try:
        logger.info(f"Getting technical question for session {request.session_id}")
        
        session_service = get_interview_session_service()
        session = session_service.get_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        interview_ai = get_advanced_interview_ai()
        config = session["config"]
        
        # Get skill to test
        skills_to_test = config.get("skills_to_test", ["Problem Solving"])
        skill_index = (request.question_number - 1) % len(skills_to_test)
        skill = skills_to_test[skill_index]
        
        # Generate question
        question = await interview_ai.generate_technical_question(
            skill=skill,
            difficulty=config.get("difficulty_level", "medium"),
            question_number=request.question_number,
            context=None  # Can pass user context if needed
        )
        
        formatter = get_response_formatter()
        return formatter.success({
            "question": question,
            "instructions": [
                "First, explain your approach in detail",
                "Then write your code solution",
                "Do not switch tabs or paste code",
                "Time limit will be enforced"
            ],
            "anti_cheat_active": True
        }, "Technical question generated")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get technical question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/technical/submit")
async def submit_technical_answer(request: TechnicalSubmitRequest):
    """
    Submit and evaluate technical answer
    
    Evaluates:
    - Approach explanation quality
    - Code correctness
    - Edge case handling
    - Time/space complexity
    - Code readability
    """
    try:
        logger.info(f"Submitting technical answer for session {request.session_id}")
        
        session_service = get_interview_session_service()
        session = session_service.get_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update cheating indicators
        if request.tab_switches > 0:
            session_service.increment_cheating_indicator(request.session_id, "tab_switches")
        if request.paste_attempts > 0:
            session_service.increment_cheating_indicator(request.session_id, "paste_attempts")
        
        interview_ai = get_advanced_interview_ai()
        
        # Get the question (would be stored in session in production)
        # For now, we'll evaluate based on what's provided
        question = {"question_id": request.question_id, "time_limit": 300}
        
        evaluation = await interview_ai.evaluate_technical_answer(
            question=question,
            approach_explanation=request.approach_explanation,
            code_solution=request.code_solution,
            time_taken=request.time_taken,
            cheating_indicators={
                "tab_switches": request.tab_switches,
                "paste_attempts": request.paste_attempts
            }
        )
        
        # Store evaluation
        session_service.add_evaluation(request.session_id, "technical", evaluation)
        
        formatter = get_response_formatter()
        return formatter.success(evaluation, "Technical answer evaluated")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to evaluate technical answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/aptitude/question")
async def get_aptitude_question(request: AptitudeQuestionRequest):
    """
    Get aptitude question
    
    Features:
    - Time-bound questions
    - Requires reasoning explanation
    - Multiple choice format
    """
    try:
        logger.info(f"Getting aptitude question for session {request.session_id}")
        
        session_service = get_interview_session_service()
        session = session_service.get_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        interview_ai = get_advanced_interview_ai()
        config = session["config"]
        
        question = await interview_ai.generate_aptitude_question(
            difficulty=config.get("difficulty_level", "medium"),
            question_number=request.question_number
        )
        
        # Don't send correct answer to frontend
        question_for_client = question.copy()
        question_for_client.pop("correct_answer", None)
        question_for_client.pop("explanation", None)
        
        # Store question in session for validation
        session_service.update_session(request.session_id, {
            f"aptitude_q_{request.question_number}": question
        })
        
        formatter = get_response_formatter()
        return formatter.success({
            "question": question_for_client,
            "instructions": [
                "Select the correct answer",
                "Explain your reasoning",
                "Time limit will be enforced"
            ]
        }, "Aptitude question generated")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get aptitude question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/aptitude/submit")
async def submit_aptitude_answer(request: AptitudeSubmitRequest):
    """
    Submit and evaluate aptitude answer
    
    Evaluates:
    - Correctness
    - Reasoning quality
    - Speed vs accuracy
    """
    try:
        logger.info(f"Submitting aptitude answer for session {request.session_id}")
        
        session_service = get_interview_session_service()
        session = session_service.get_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get stored question
        question_key = f"aptitude_q_{request.question_id.split('_')[1]}"
        question = session.get(question_key)
        
        if not question:
            raise HTTPException(status_code=400, detail="Question not found in session")
        
        interview_ai = get_advanced_interview_ai()
        
        evaluation = await interview_ai.evaluate_aptitude_answer(
            question=question,
            answer=request.answer,
            reasoning=request.reasoning,
            time_taken=request.time_taken
        )
        
        # Store evaluation
        session_service.add_evaluation(request.session_id, "aptitude", evaluation)
        
        formatter = get_response_formatter()
        return formatter.success(evaluation, "Aptitude answer evaluated")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to evaluate aptitude answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/soft-skills/question")
async def get_soft_skills_question(request: SoftSkillsQuestionRequest):
    """
    Get behavioral/situational soft skills question
    
    Features:
    - Adaptive follow-ups based on previous answers
    - STAR method evaluation
    - Professional interviewer behavior
    """
    try:
        logger.info(f"Getting soft skills question for session {request.session_id}")
        
        session_service = get_interview_session_service()
        session = session_service.get_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        interview_ai = get_advanced_interview_ai()
        
        question = await interview_ai.generate_soft_skills_question(
            question_number=request.question_number,
            previous_answer=request.previous_answer,
            context=None  # Can pass user context if needed
        )
        
        formatter = get_response_formatter()
        return formatter.success({
            "question": question,
            "instructions": [
                "Use the STAR method (Situation, Task, Action, Result)",
                "Be specific and provide examples",
                "Focus on your role and impact"
            ],
            "star_method_guide": {
                "Situation": "Describe the context",
                "Task": "Explain your responsibility",
                "Action": "Detail what you did",
                "Result": "Share the outcome and impact"
            }
        }, "Soft skills question generated")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get soft skills question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/soft-skills/submit")
async def submit_soft_skills_answer(request: SoftSkillsSubmitRequest):
    """
    Submit and evaluate soft skills answer
    
    Evaluates:
    - Clarity and structure
    - STAR method usage
    - Communication quality
    - Confidence and impact
    """
    try:
        logger.info(f"Submitting soft skills answer for session {request.session_id}")
        
        session_service = get_interview_session_service()
        session = session_service.get_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        interview_ai = get_advanced_interview_ai()
        
        # Get the question (would be stored in session in production)
        question = {"question_id": request.question_id, "question_type": "behavioral"}
        
        evaluation = await interview_ai.evaluate_soft_skills_answer(
            question=question,
            answer=request.answer,
            time_taken=request.time_taken
        )
        
        # Store evaluation
        session_service.add_evaluation(request.session_id, "soft_skills", evaluation)
        
        formatter = get_response_formatter()
        return formatter.success(evaluation, "Soft skills answer evaluated")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to evaluate soft skills answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{session_id}")
async def get_interview_report(session_id: str):
    """
    Get comprehensive interview report
    
    Includes:
    - Overall weighted score
    - Section-wise breakdown (technical, aptitude, soft skills)
    - Strengths and weaknesses
    - Cheating flags
    - Priority skills to improve
    - Next actions
    - Readiness assessment
    """
    try:
        logger.info(f"Generating report for session {session_id}")
        
        session_service = get_interview_session_service()
        session = session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Mark session as completed
        session_service.complete_session(session_id)
        
        interview_ai = get_advanced_interview_ai()
        
        # Get evaluations
        technical_evals = session.get("technical_evaluations", [])
        aptitude_evals = session.get("aptitude_evaluations", [])
        soft_skills_evals = session.get("soft_skills_evaluations", [])
        
        # Detect cheating
        cheating_indicators = session.get("cheating_indicators", {})
        cheating_flags = interview_ai.detect_cheating(
            tab_switches=cheating_indicators.get("tab_switches", 0),
            paste_attempts=cheating_indicators.get("paste_attempts", 0),
            time_taken=session.get("duration", 0),
            expected_time=session["config"].get("total_questions", 10) * 300,
            answer_similarity=None
        )
        
        # Generate report
        from app.models.advanced_interview import InterviewConfig
        config = InterviewConfig(**session["config"])
        
        report = await interview_ai.generate_interview_report(
            session_data=session,
            technical_evaluations=technical_evals,
            aptitude_evaluations=aptitude_evals,
            soft_skills_evaluations=soft_skills_evals,
            cheating_flags=cheating_flags,
            config=config
        )
        
        formatter = get_response_formatter()
        return formatter.success(report, "Interview report generated")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get current session status and progress"""
    try:
        session_service = get_interview_session_service()
        session = session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        formatter = get_response_formatter()
        return formatter.success({
            "session_id": session_id,
            "status": session["status"],
            "current_question": session.get("current_question", 0),
            "questions_answered": {
                "technical": len(session.get("technical_evaluations", [])),
                "aptitude": len(session.get("aptitude_evaluations", [])),
                "soft_skills": len(session.get("soft_skills_evaluations", []))
            },
            "cheating_indicators": session.get("cheating_indicators", {})
        }, "Session status retrieved")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
