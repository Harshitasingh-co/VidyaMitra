from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CareerIntent(BaseModel):
    """Model for capturing user's career intent before resume analysis"""
    desired_role: str = Field(..., description="Target job role (e.g., 'Data Analyst')")
    experience_level: str = Field(..., description="Experience level (e.g., '0-2 years', '3-5 years', '5+ years')")
    target_companies: List[str] = Field(..., description="Types of companies (e.g., ['Product-based', 'Startups'])")
    preferred_industries: Optional[List[str]] = Field(default=[], description="Preferred industries")
    location_preference: Optional[str] = Field(default="Any", description="Location preference")
    
    class Config:
        json_schema_extra = {
            "example": {
                "desired_role": "Data Analyst",
                "experience_level": "0-2 years",
                "target_companies": ["Product-based companies", "Startups"],
                "preferred_industries": ["Tech", "E-commerce"],
                "location_preference": "Remote"
            }
        }

class CareerIntentResponse(BaseModel):
    """Response model for career intent submission"""
    intent_id: str
    message: str
    next_step: str = "Upload your resume for context-aware analysis"

class ContextAwareResumeRequest(BaseModel):
    """Request model for context-aware resume analysis"""
    resume_text: str
    intent_id: Optional[str] = None
    career_intent: Optional[CareerIntent] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "resume_text": "John Doe\nData Analyst...",
                "career_intent": {
                    "desired_role": "Data Analyst",
                    "experience_level": "0-2 years",
                    "target_companies": ["Product-based companies"]
                }
            }
        }
