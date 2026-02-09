from ai.llm import get_llm_service
from ai.prompts import CONTEXT_AWARE_RESUME_SYSTEM, CONTEXT_AWARE_RESUME_PROMPT
from app.models.career_intent import CareerIntent
import logging

logger = logging.getLogger(__name__)

class ContextAwareResumeAI:
    """AI service for context-aware resume analysis based on career intent"""
    
    def __init__(self):
        self.llm = get_llm_service()
    
    async def analyze_with_context(
        self,
        resume_text: str,
        career_intent: CareerIntent
    ) -> dict:
        """
        Analyze resume with career context for personalized recommendations
        
        Args:
            resume_text: Extracted text from resume
            career_intent: User's career goals and preferences
            
        Returns:
            Comprehensive context-aware analysis with certifications, projects, and skill gaps
        """
        try:
            logger.info(
                f"Context-aware analysis: {career_intent.desired_role} "
                f"({career_intent.experience_level}) for {', '.join(career_intent.target_companies)}"
            )
            
            # Format career intent for prompt
            target_companies_str = ", ".join(career_intent.target_companies)
            preferred_industries_str = ", ".join(career_intent.preferred_industries) if career_intent.preferred_industries else "Any"
            
            user_prompt = CONTEXT_AWARE_RESUME_PROMPT.format(
                resume_text=resume_text,
                desired_role=career_intent.desired_role,
                experience_level=career_intent.experience_level,
                target_companies=target_companies_str,
                preferred_industries=preferred_industries_str
            )
            
            result = await self.llm.generate_json_response(
                system_prompt=CONTEXT_AWARE_RESUME_SYSTEM,
                user_prompt=user_prompt
            )
            
            # Add metadata
            result['career_intent'] = {
                "desired_role": career_intent.desired_role,
                "experience_level": career_intent.experience_level,
                "target_companies": career_intent.target_companies
            }
            
            logger.info(
                f"Context-aware analysis completed. "
                f"Role fit: {result.get('role_fit_score', 'N/A')}%, "
                f"Missing skills: {len(result.get('missing_skills', []))}, "
                f"Certifications: {len(result.get('certifications', []))}, "
                f"Projects: {len(result.get('projects', []))}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Context-aware resume analysis failed: {e}")
            raise
    
    async def get_skill_gap_details(
        self,
        existing_skills: list,
        required_skills: list,
        desired_role: str
    ) -> dict:
        """
        Get detailed skill gap analysis with learning paths
        
        Args:
            existing_skills: Skills found in resume
            required_skills: Skills needed for target role
            desired_role: Target job role
            
        Returns:
            Detailed skill gap analysis
        """
        try:
            system_prompt = """You are a technical skills analyst.
Provide detailed skill gap analysis with learning recommendations.
Return valid JSON only."""
            
            user_prompt = f"""Analyze the skill gap:

Existing Skills: {', '.join(existing_skills)}
Required Skills: {', '.join(required_skills)}
Target Role: {desired_role}

Return in this JSON format:
{{
    "gap_summary": "<brief summary>",
    "critical_gaps": [
        {{
            "skill": "<skill name>",
            "why_critical": "<explanation>",
            "learning_resources": ["<resource 1>", "<resource 2>"],
            "estimated_time": "<time to learn>"
        }}
    ],
    "nice_to_have_gaps": [
        {{
            "skill": "<skill name>",
            "benefit": "<why useful>",
            "priority": "<High/Medium/Low>"
        }}
    ],
    "learning_roadmap": [
        {{
            "week": <1-12>,
            "focus": "<what to learn>",
            "resources": ["<resource 1>", "<resource 2>"]
        }}
    ]
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Skill gap analysis failed: {e}")
            raise

def get_context_aware_resume_ai() -> ContextAwareResumeAI:
    """Get ContextAwareResumeAI instance"""
    return ContextAwareResumeAI()
