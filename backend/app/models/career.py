from pydantic import BaseModel
from typing import List, Optional

class CareerPathRequest(BaseModel):
    current_role: str
    target_role: str
    skills: List[str]
    experience_years: int

class LearningStep(BaseModel):
    title: str
    description: str
    duration: str
    resources: List[str]

class CareerPathRecommendation(BaseModel):
    target_role: str
    transferable_skills: List[str]
    skills_to_acquire: List[str]
    learning_path: List[LearningStep]
    certifications: List[str]
    estimated_timeline: str
