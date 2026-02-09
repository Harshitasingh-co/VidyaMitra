from ai.llm import get_llm_service
from ai.prompts import RESUME_ANALYSIS_SYSTEM, RESUME_ANALYSIS_PROMPT
import logging

logger = logging.getLogger(__name__)

class ResumeAI:
    """AI service for resume analysis and evaluation"""
    
    def __init__(self):
        self.llm = get_llm_service()
    
    async def analyze_resume(self, resume_text: str, target_role: str = "General") -> dict:
        """
        Analyze resume and provide comprehensive feedback
        
        Args:
            resume_text: Extracted text from resume
            target_role: Target job role for analysis
            
        Returns:
            Dictionary with analysis results
        """
        try:
            logger.info(f"Analyzing resume for target role: {target_role}")
            
            user_prompt = RESUME_ANALYSIS_PROMPT.format(
                resume_text=resume_text,
                target_role=target_role
            )
            
            result = await self.llm.generate_json_response(
                system_prompt=RESUME_ANALYSIS_SYSTEM,
                user_prompt=user_prompt
            )
            
            logger.info(f"Resume analysis completed. ATS Score: {result.get('ats_score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            raise
    
    async def extract_skills(self, resume_text: str) -> list:
        """
        Extract skills from resume text
        
        Args:
            resume_text: Resume content
            
        Returns:
            List of identified skills
        """
        try:
            system_prompt = "You are a skill extraction expert. Extract technical and soft skills from resumes. Return valid JSON only."
            user_prompt = f"""Extract all skills from this resume:

{resume_text}

Return in this JSON format:
{{
    "technical_skills": ["<skill 1>", "<skill 2>"],
    "soft_skills": ["<skill 1>", "<skill 2>"],
    "tools": ["<tool 1>", "<tool 2>"]
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            
            # Flatten all skills
            all_skills = (
                result.get("technical_skills", []) +
                result.get("soft_skills", []) +
                result.get("tools", [])
            )
            
            return all_skills
            
        except Exception as e:
            logger.error(f"Skill extraction failed: {e}")
            return []
    
    async def compare_with_job_description(self, resume_text: str, job_description: str) -> dict:
        """
        Compare resume against job description
        
        Args:
            resume_text: Resume content
            job_description: Job posting description
            
        Returns:
            Match analysis
        """
        try:
            system_prompt = "You are an ATS system expert. Compare resumes against job descriptions. Return valid JSON only."
            user_prompt = f"""Compare this resume against the job description:

Resume:
{resume_text}

Job Description:
{job_description}

Return in this JSON format:
{{
    "match_percentage": <number 0-100>,
    "matching_keywords": ["<keyword 1>", "<keyword 2>"],
    "missing_keywords": ["<keyword 1>", "<keyword 2>"],
    "recommendations": ["<recommendation 1>", "<recommendation 2>"]
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Job comparison failed: {e}")
            raise

def get_resume_ai() -> ResumeAI:
    """Get ResumeAI instance"""
    return ResumeAI()
