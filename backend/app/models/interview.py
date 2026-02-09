from pydantic import BaseModel
from typing import List, Optional

class InterviewRequest(BaseModel):
    role: str
    experience_level: str
    industry: Optional[str] = None

class InterviewQuestion(BaseModel):
    question: str
    category: str

class InterviewResponse(BaseModel):
    question_id: str
    answer: str

class InterviewFeedback(BaseModel):
    overall_score: float
    tone_analysis: str
    confidence_level: str
    content_accuracy: float
    strengths: List[str]
    improvements: List[str]
    detailed_feedback: str
