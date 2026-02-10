"""
AI services for internship discovery module

Provides AI-powered functionality for:
- Skill extraction from resumes
- Career guidance generation
- Learning recommendations
- Fraud pattern analysis
"""

from ai.llm import get_llm_service
from typing import List, Dict
import logging
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry AI calls with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (doubles each time)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}"
                    )
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= 2  # Exponential backoff
            
            # All retries exhausted
            logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_exception
        
        return wrapper
    return decorator


class InternshipAI:
    """AI-powered internship analysis and guidance"""
    
    def __init__(self):
        self.llm = get_llm_service()
    
    @retry_on_failure(max_retries=3, delay=1.0)
    async def extract_skills_from_resume(self, resume_text: str) -> List[str]:
        """
        Extract skills from resume using NLP
        
        Args:
            resume_text: Text content of the resume
            
        Returns:
            List of extracted skills
            
        Raises:
            ValueError: If resume text is empty or AI fails to extract skills
        """
        try:
            if not resume_text or not resume_text.strip():
                raise ValueError("Resume text cannot be empty")
            
            logger.info("Extracting skills from resume")
            
            system_prompt = """You are an expert resume analyzer. Extract technical and professional skills from resumes.
Focus on:
- Programming languages (Python, Java, JavaScript, etc.)
- Frameworks and libraries (React, Django, Spring, etc.)
- Tools and technologies (Git, Docker, AWS, etc.)
- Databases (MySQL, PostgreSQL, MongoDB, etc.)
- Soft skills (Communication, Leadership, etc.)
- Domain knowledge (Machine Learning, Data Analysis, etc.)

Return ONLY valid JSON with no markdown formatting."""
            
            user_prompt = f"""Extract all skills from this resume:

{resume_text}

Return in this JSON format:
{{
    "skills": ["<skill 1>", "<skill 2>", "<skill 3>", ...]
}}

Return ONLY the JSON object with a list of skills. Be comprehensive but avoid duplicates."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            
            if "skills" not in result or not isinstance(result["skills"], list):
                raise ValueError("AI response missing 'skills' field or invalid format")
            
            skills = result["skills"]
            
            # Clean and deduplicate skills
            skills = [skill.strip() for skill in skills if skill and skill.strip()]
            skills = list(dict.fromkeys(skills))  # Remove duplicates while preserving order
            
            logger.info(f"Extracted {len(skills)} skills from resume")
            return skills
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Skill extraction failed: {e}")
            raise ValueError(f"Failed to extract skills from resume: {str(e)}")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    async def generate_career_guidance(
        self,
        user_profile: Dict,
        internship: Dict,
        skill_match: Dict
    ) -> Dict:
        """
        Generate personalized career guidance
        
        Args:
            user_profile: Student profile with skills, semester, degree, etc.
            internship: Internship listing details
            skill_match: Skill match analysis with matching/missing skills
            
        Returns:
            Career guidance with:
            - why_good_fit: Explanation of why internship fits the user
            - skills_to_improve: List of skills to focus on
            - certifications: Recommended certifications
            - projects: Project ideas to strengthen resume
            
        Raises:
            ValueError: If required fields are missing or AI fails
        """
        try:
            # Validate inputs
            if not user_profile or not internship or not skill_match:
                raise ValueError("user_profile, internship, and skill_match are required")
            
            logger.info(
                f"Generating career guidance for user {user_profile.get('user_id')} "
                f"and internship {internship.get('id')}"
            )
            
            # Extract relevant information
            user_skills = user_profile.get("skills", [])
            semester = user_profile.get("current_semester", 0)
            degree = user_profile.get("degree", "")
            branch = user_profile.get("branch", "")
            
            internship_title = internship.get("title", "")
            company = internship.get("company", "")
            required_skills = internship.get("required_skills", [])
            responsibilities = internship.get("responsibilities", [])
            
            matching_skills = skill_match.get("matching_skills", [])
            missing_skills = skill_match.get("missing_skills", [])
            match_percentage = skill_match.get("match_percentage", 0)
            
            system_prompt = """You are an expert career counselor specializing in student internships.
Provide personalized, actionable, and encouraging career guidance.
Be conversational and supportive, not robotic.
Focus on practical steps the student can take to improve their chances."""
            
            user_prompt = f"""Generate personalized career guidance for this student and internship:

STUDENT PROFILE:
- Degree: {degree} in {branch}
- Current Semester: {semester}
- Current Skills: {', '.join(user_skills)}

INTERNSHIP:
- Title: {internship_title}
- Company: {company}
- Required Skills: {', '.join(required_skills)}
- Responsibilities: {', '.join(responsibilities)}

SKILL MATCH ANALYSIS:
- Match Percentage: {match_percentage}%
- Matching Skills: {', '.join(matching_skills)}
- Missing Skills: {', '.join(missing_skills)}

Provide guidance in this JSON format:
{{
    "why_good_fit": "<2-3 sentences explaining why this internship is a good fit for the student based on their current skills, semester, and career trajectory>",
    "skills_to_improve": ["<skill 1>", "<skill 2>", "<skill 3>"],
    "certifications": ["<certification 1>", "<certification 2>"],
    "projects": ["<project idea 1>", "<project idea 2>", "<project idea 3>"]
}}

Guidelines:
- why_good_fit: Be encouraging and specific. Mention their matching skills and how the internship aligns with their semester/degree.
- skills_to_improve: Focus on the missing skills that are most important for this role. Prioritize 3-5 skills.
- certifications: Suggest relevant certifications that would strengthen their application (e.g., AWS Certified Developer, Google Analytics, etc.)
- projects: Suggest 3-4 practical project ideas they can build to demonstrate the missing skills. Be specific and realistic.

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            
            # Validate response structure
            required_fields = ["why_good_fit", "skills_to_improve", "certifications", "projects"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"AI response missing required field: {field}")
            
            # Ensure lists are actually lists
            for field in ["skills_to_improve", "certifications", "projects"]:
                if not isinstance(result[field], list):
                    raise ValueError(f"Field '{field}' must be a list")
            
            logger.info("Career guidance generated successfully")
            return result
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Career guidance generation failed: {e}")
            raise ValueError(f"Failed to generate career guidance: {str(e)}")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    async def generate_learning_recommendations(
        self,
        missing_skills: List[str],
        user_level: str = "beginner"
    ) -> List[Dict]:
        """
        Generate personalized learning path for missing skills
        
        Args:
            missing_skills: List of skills the user needs to learn
            user_level: User's experience level (beginner/intermediate/advanced)
            
        Returns:
            List of learning recommendations with:
            - skill: Skill name
            - estimated_time: Time to learn (e.g., "2 weeks")
            - difficulty: Difficulty level (Easy/Medium/Hard)
            - resources: List of learning resources
            - priority: Priority level (High/Medium/Low)
            
        Raises:
            ValueError: If missing_skills is empty or AI fails
        """
        try:
            if not missing_skills:
                return []
            
            logger.info(f"Generating learning recommendations for {len(missing_skills)} skills")
            
            system_prompt = """You are a learning advisor specializing in technical skill development.
Provide realistic, practical learning recommendations with accurate time estimates.
Consider the user's current level when suggesting resources and timelines."""
            
            skills_str = ", ".join(missing_skills)
            
            user_prompt = f"""Generate learning recommendations for these skills: {skills_str}
User's current level: {user_level}

Return in this JSON format:
{{
    "recommendations": [
        {{
            "skill": "<skill name>",
            "estimated_time": "<time estimate like '2 weeks', '1 month', '3 days'>",
            "difficulty": "<Easy|Medium|Hard>",
            "resources": ["<resource 1>", "<resource 2>", "<resource 3>"],
            "priority": "<High|Medium|Low>"
        }}
    ]
}}

Guidelines:
- estimated_time: Be realistic. Basic skills: 1-2 weeks, intermediate: 1-2 months, advanced: 2-4 months
- difficulty: Easy (basic syntax/tools), Medium (frameworks/libraries), Hard (advanced concepts/architectures)
- resources: Suggest 3-5 specific, high-quality resources (courses, tutorials, documentation, books)
- priority: High for fundamental/required skills, Medium for nice-to-have, Low for optional

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            
            if "recommendations" not in result or not isinstance(result["recommendations"], list):
                raise ValueError("AI response missing 'recommendations' field or invalid format")
            
            recommendations = result["recommendations"]
            
            # Validate each recommendation
            for rec in recommendations:
                required_fields = ["skill", "estimated_time", "difficulty", "resources", "priority"]
                for field in required_fields:
                    if field not in rec:
                        raise ValueError(f"Recommendation missing required field: {field}")
                
                # Validate difficulty and priority values
                if rec["difficulty"] not in ["Easy", "Medium", "Hard"]:
                    rec["difficulty"] = "Medium"  # Default
                
                if rec["priority"] not in ["High", "Medium", "Low"]:
                    rec["priority"] = "Medium"  # Default
                
                # Ensure resources is a list
                if not isinstance(rec["resources"], list):
                    rec["resources"] = []
            
            logger.info(f"Generated {len(recommendations)} learning recommendations")
            return recommendations
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Learning recommendations generation failed: {e}")
            raise ValueError(f"Failed to generate learning recommendations: {str(e)}")
    
    async def analyze_fraud_patterns(self, internship: Dict) -> Dict:
        """
        Use AI to detect subtle fraud patterns in internship listings
        
        This is an optional enhancement that uses AI to detect fraud patterns
        that might not be caught by rule-based verification.
        
        Args:
            internship: Internship listing details
            
        Returns:
            Fraud analysis with:
            - risk_level: Risk assessment (Low/Medium/High)
            - suspicious_indicators: List of suspicious patterns found
            - confidence: Confidence score (0-100)
            
        Note: This is a supplementary check. Primary verification should use
        rule-based verification_service.py
        """
        try:
            logger.info(f"Analyzing fraud patterns for internship {internship.get('id')}")
            
            # Extract relevant fields
            title = internship.get("title", "")
            company = internship.get("company", "")
            stipend = internship.get("stipend", "")
            responsibilities = internship.get("responsibilities", [])
            company_domain = internship.get("company_domain", "")
            platform = internship.get("platform", "")
            
            system_prompt = """You are a fraud detection expert specializing in internship scams.
Analyze internship listings for suspicious patterns, unrealistic promises, and red flags.
Be thorough but not overly cautious - legitimate internships should not be flagged."""
            
            user_prompt = f"""Analyze this internship listing for potential fraud indicators:

INTERNSHIP DETAILS:
- Title: {title}
- Company: {company}
- Company Domain: {company_domain}
- Platform: {platform}
- Stipend: {stipend}
- Responsibilities: {', '.join(responsibilities)}

Look for:
- Unrealistic stipend amounts
- Vague or generic job descriptions
- Suspicious company names or domains
- Red flag keywords (guaranteed, easy money, no experience needed, etc.)
- Inconsistencies in the listing

Return in this JSON format:
{{
    "risk_level": "<Low|Medium|High>",
    "suspicious_indicators": ["<indicator 1>", "<indicator 2>"],
    "confidence": <0-100>,
    "explanation": "<brief explanation of the assessment>"
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            
            # Validate response
            if "risk_level" not in result:
                result["risk_level"] = "Low"
            if "suspicious_indicators" not in result:
                result["suspicious_indicators"] = []
            if "confidence" not in result:
                result["confidence"] = 50
            
            logger.info(f"Fraud analysis complete. Risk level: {result['risk_level']}")
            return result
            
        except Exception as e:
            logger.error(f"Fraud pattern analysis failed: {e}")
            # Return safe default on error
            return {
                "risk_level": "Low",
                "suspicious_indicators": [],
                "confidence": 0,
                "explanation": "Analysis unavailable"
            }


def get_internship_ai() -> InternshipAI:
    """Get InternshipAI instance"""
    return InternshipAI()
