from ai.llm import get_llm_service
from ai.prompts import (
    CAREER_PATH_SYSTEM,
    CAREER_PATH_PROMPT,
    SKILL_GAP_SYSTEM,
    SKILL_GAP_PROMPT
)
from typing import List
import logging

logger = logging.getLogger(__name__)

class CareerAI:
    """AI service for career path recommendations and upskilling plans"""
    
    def __init__(self):
        self.llm = get_llm_service()
    
    async def generate_career_roadmap(
        self,
        current_role: str,
        target_role: str,
        current_skills: List[str],
        experience_years: int
    ) -> dict:
        """
        Generate comprehensive career transition roadmap
        
        Args:
            current_role: Current job role
            target_role: Desired job role
            current_skills: List of current skills
            experience_years: Years of experience
            
        Returns:
            Detailed career roadmap with learning path
        """
        try:
            logger.info(f"Generating career roadmap: {current_role} -> {target_role}")
            
            skills_str = ", ".join(current_skills)
            
            user_prompt = CAREER_PATH_PROMPT.format(
                current_role=current_role,
                target_role=target_role,
                current_skills=skills_str,
                experience_years=experience_years
            )
            
            result = await self.llm.generate_json_response(
                system_prompt=CAREER_PATH_SYSTEM,
                user_prompt=user_prompt
            )
            
            logger.info(f"Career roadmap generated. Timeline: {result.get('estimated_timeline', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"Career roadmap generation failed: {e}")
            raise
    
    async def analyze_skill_gap(
        self,
        current_skills: List[str],
        target_role: str
    ) -> dict:
        """
        Analyze skill gaps for target role
        
        Args:
            current_skills: List of current skills
            target_role: Target job role
            
        Returns:
            Skill gap analysis
        """
        try:
            logger.info(f"Analyzing skill gap for: {target_role}")
            
            skills_str = ", ".join(current_skills)
            
            user_prompt = SKILL_GAP_PROMPT.format(
                current_skills=skills_str,
                target_role=target_role
            )
            
            result = await self.llm.generate_json_response(
                system_prompt=SKILL_GAP_SYSTEM,
                user_prompt=user_prompt
            )
            
            logger.info(f"Skill gap analyzed. Match: {result.get('skill_match_percentage', 'N/A')}%")
            return result
            
        except Exception as e:
            logger.error(f"Skill gap analysis failed: {e}")
            raise
    
    async def get_role_requirements(self, role: str) -> dict:
        """
        Get detailed requirements for a specific role
        
        Args:
            role: Job role to analyze
            
        Returns:
            Role requirements and expectations
        """
        try:
            system_prompt = "You are a career expert. Provide detailed role requirements. Return valid JSON only."
            user_prompt = f"""Provide detailed requirements for this role: {role}

Return in this JSON format:
{{
    "role": "{role}",
    "required_skills": ["<skill 1>", "<skill 2>"],
    "preferred_skills": ["<skill 1>", "<skill 2>"],
    "typical_responsibilities": ["<responsibility 1>", "<responsibility 2>"],
    "education_requirements": "<requirements>",
    "experience_range": "<X-Y years>",
    "salary_range": "<range>",
    "growth_potential": "<high/medium/low>",
    "industry_demand": "<high/medium/low>"
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Role requirements fetch failed: {e}")
            raise
    
    async def suggest_learning_resources(
        self,
        skills_to_learn: List[str],
        learning_style: str = "mixed"
    ) -> dict:
        """
        Suggest learning resources for specific skills
        
        Args:
            skills_to_learn: List of skills to acquire
            learning_style: preferred learning style (video/reading/interactive/mixed)
            
        Returns:
            Curated learning resource suggestions
        """
        try:
            skills_str = ", ".join(skills_to_learn)
            
            system_prompt = "You are a learning advisor. Suggest effective learning resources. Return valid JSON only."
            user_prompt = f"""Suggest learning resources for these skills: {skills_str}
Learning style preference: {learning_style}

Return in this JSON format:
{{
    "resources": [
        {{
            "skill": "<skill name>",
            "resource_type": "<course/book/tutorial/certification>",
            "platform": "<platform name>",
            "title": "<resource title>",
            "difficulty": "<beginner/intermediate/advanced>",
            "estimated_duration": "<duration>",
            "search_keywords": "<keywords for finding this resource>"
        }}
    ]
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Learning resource suggestion failed: {e}")
            raise

def get_career_ai() -> CareerAI:
    """Get CareerAI instance"""
    return CareerAI()
