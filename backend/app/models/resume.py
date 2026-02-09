from pydantic import BaseModel
from typing import List, Optional

class ResumeUpload(BaseModel):
    content: str
    filename: str

class SkillGap(BaseModel):
    skill: str
    importance: str
    recommendation: str

class ResumeAnalysis(BaseModel):
    summary: str
    strengths: List[str]
    skill_gaps: List[SkillGap]
    recommended_courses: List[dict]
    overall_score: float
