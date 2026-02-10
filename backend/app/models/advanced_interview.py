from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime

class PreInterviewContext(BaseModel):
    """Context gathered before interview starts"""
    user_id: str
    resume_analysis: Optional[Dict] = None
    existing_skills: List[str] = []
    missing_skills: List[str] = []
    desired_role: str
    experience_level: str
    target_companies: List[str] = []

class InterviewConfig(BaseModel):
    """Dynamic interview configuration based on user context"""
    technical_weight: float = Field(default=40.0, ge=0, le=100)
    aptitude_weight: float = Field(default=30.0, ge=0, le=100)
    soft_skills_weight: float = Field(default=30.0, ge=0, le=100)
    difficulty_level: Literal["easy", "medium", "hard"] = "medium"
    skills_to_test: List[str] = []
    total_questions: int = Field(default=10, ge=1, le=50)

class AdvancedInterviewStartRequest(BaseModel):
    """Request to start advanced interview"""
    interview_type: Literal["full", "technical", "aptitude", "soft-skills"] = "full"
    user_context: Optional[PreInterviewContext] = None
    custom_config: Optional[InterviewConfig] = None

class InterviewRules(BaseModel):
    """Anti-cheating rules and constraints"""
    time_limit_per_question: int = Field(default=300, description="Seconds")
    allow_tab_switch: bool = False
    allow_paste: bool = False
    max_tab_switches: int = 3
    track_time: bool = True

class TechnicalQuestionRequest(BaseModel):
    """Request for technical/coding question"""
    session_id: str
    question_number: int

class TechnicalSubmitRequest(BaseModel):
    """Submit technical answer"""
    session_id: str
    question_id: str
    approach_explanation: str
    code_solution: Optional[str] = None
    time_taken: int  # seconds
    tab_switches: int = 0
    paste_attempts: int = 0

class AptitudeQuestionRequest(BaseModel):
    """Request for aptitude question"""
    session_id: str
    question_number: int

class AptitudeSubmitRequest(BaseModel):
    """Submit aptitude answer"""
    session_id: str
    question_id: str
    answer: str
    reasoning: str
    time_taken: int

class SoftSkillsQuestionRequest(BaseModel):
    """Request for soft skills question"""
    session_id: str
    question_number: int
    previous_answer: Optional[str] = None  # For adaptive follow-ups

class SoftSkillsSubmitRequest(BaseModel):
    """Submit soft skills answer"""
    session_id: str
    question_id: str
    answer: str
    time_taken: int

class CheatingFlags(BaseModel):
    """Anti-cheating detection results"""
    tab_switches: int = 0
    paste_attempts: int = 0
    suspicious_speed: bool = False
    identical_answers: bool = False
    severity: Literal["none", "low", "medium", "high"] = "none"

class InterviewReport(BaseModel):
    """Comprehensive interview report"""
    session_id: str
    overall_score: float
    technical: Optional[Dict] = None
    aptitude: Optional[Dict] = None
    soft_skills: Optional[Dict] = None
    cheating_flags: CheatingFlags
    next_actions: List[str]
    interview_duration: int  # seconds
    completed_at: datetime
    readiness_level: Literal["ready", "needs_practice", "needs_significant_improvement"]
