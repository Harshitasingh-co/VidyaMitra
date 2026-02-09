"""
AI service for generating resume-worthy project ideas
Feature 5: AI Project Idea Generator (Resume Booster)
"""
from ai.llm import get_llm_service
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class ProjectGeneratorAI:
    """AI service for generating personalized project ideas"""
    
    def __init__(self):
        self.llm = get_llm_service()
    
    async def generate_projects(
        self,
        target_role: str,
        missing_skills: List[str],
        experience_level: str,
        num_projects: int = 3
    ) -> dict:
        """
        Generate personalized, resume-ready project ideas
        
        Args:
            target_role: Target job role
            missing_skills: Skills to be covered by projects
            experience_level: User's experience level (entry/mid/senior)
            num_projects: Number of projects to generate
            
        Returns:
            Project ideas with implementation details
        """
        try:
            logger.info(f"Generating {num_projects} projects for {target_role}")
            
            system_prompt = """You are an expert career coach and technical mentor.
Generate realistic, resume-worthy project ideas that directly address skill gaps.
Projects must be practical, achievable, and add measurable value to resumes.
You MUST return valid JSON only."""
            
            user_prompt = f"""Generate {num_projects} resume-worthy project ideas:

Target Role: {target_role}
Missing Skills to Cover: {', '.join(missing_skills)}
Experience Level: {experience_level}

Requirements for each project:
1. Must use at least 2-3 of the missing skills
2. Must be realistic and achievable
3. Must have clear, measurable outcomes
4. Must be resume-worthy (not toy projects)
5. Should take 2-6 weeks to complete

Return in this JSON format:
{{
    "projects": [
        {{
            "title": "<compelling project title>",
            "skills_covered": ["<skill 1>", "<skill 2>", "<skill 3>"],
            "description": "<2-3 sentence project description>",
            "tech_stack": ["<technology 1>", "<technology 2>"],
            "key_features": ["<feature 1>", "<feature 2>", "<feature 3>"],
            "resume_bullet_points": [
                "<achievement-focused bullet point 1>",
                "<achievement-focused bullet point 2>",
                "<achievement-focused bullet point 3>"
            ],
            "estimated_time": "<X weeks>",
            "difficulty": "<beginner/intermediate/advanced>",
            "impact_on_fit_score": "<+X points>",
            "implementation_steps": [
                {{
                    "step": <1-5>,
                    "task": "<what to do>",
                    "duration": "<X days>"
                }}
            ],
            "learning_resources": [
                {{
                    "type": "<course/tutorial/documentation>",
                    "topic": "<what to learn>",
                    "search_keywords": "<keywords for finding resources>"
                }}
            ],
            "portfolio_value": "<high/medium/low>",
            "interview_talking_points": ["<point 1>", "<point 2>"]
        }}
    ]
}}

Make projects specific to {target_role}. Avoid generic projects.
Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            
            projects = result.get("projects", [])
            logger.info(f"Generated {len(projects)} project ideas")
            
            return result
            
        except Exception as e:
            logger.error(f"Project generation failed: {e}")
            raise
    
    async def generate_project_for_specific_skill(
        self,
        skill: str,
        target_role: str,
        experience_level: str
    ) -> dict:
        """
        Generate a focused project for a specific skill
        
        Args:
            skill: Specific skill to focus on
            target_role: Target job role
            experience_level: User's experience level
            
        Returns:
            Detailed project idea
        """
        try:
            logger.info(f"Generating project for skill: {skill}")
            
            system_prompt = """You are an expert technical mentor.
Create a focused, practical project that demonstrates mastery of a specific skill.
You MUST return valid JSON only."""
            
            user_prompt = f"""Create a resume-worthy project focused on this skill:

Skill to Master: {skill}
Target Role: {target_role}
Experience Level: {experience_level}

Return in this JSON format:
{{
    "project": {{
        "title": "<project title>",
        "primary_skill": "{skill}",
        "supporting_skills": ["<skill 1>", "<skill 2>"],
        "description": "<detailed description>",
        "tech_stack": ["<technology 1>", "<technology 2>"],
        "key_features": ["<feature 1>", "<feature 2>", "<feature 3>"],
        "resume_bullet_points": [
            "<achievement 1>",
            "<achievement 2>",
            "<achievement 3>"
        ],
        "estimated_time": "<X weeks>",
        "difficulty": "<beginner/intermediate/advanced>",
        "step_by_step_guide": [
            {{
                "phase": "<phase name>",
                "tasks": ["<task 1>", "<task 2>"],
                "duration": "<X days>",
                "deliverable": "<what you'll have>"
            }}
        ],
        "success_criteria": ["<criterion 1>", "<criterion 2>"],
        "portfolio_presentation": "<how to showcase this project>",
        "github_readme_template": "<brief template for README>"
    }}
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Skill-specific project generation failed: {e}")
            raise
    
    async def enhance_existing_project(
        self,
        project_description: str,
        missing_skills: List[str]
    ) -> dict:
        """
        Suggest enhancements to existing project to cover more skills
        
        Args:
            project_description: Description of existing project
            missing_skills: Additional skills to incorporate
            
        Returns:
            Enhancement suggestions
        """
        try:
            logger.info("Generating project enhancement suggestions")
            
            system_prompt = """You are a technical mentor helping improve project portfolios.
Suggest practical enhancements that add real value.
You MUST return valid JSON only."""
            
            user_prompt = f"""Suggest enhancements to this project:

Current Project: {project_description}
Skills to Add: {', '.join(missing_skills)}

Return in this JSON format:
{{
    "enhancements": [
        {{
            "enhancement": "<what to add>",
            "skills_covered": ["<skill 1>", "<skill 2>"],
            "implementation_effort": "<low/medium/high>",
            "value_added": "<why this matters>",
            "new_resume_bullet": "<updated achievement statement>",
            "estimated_time": "<X days/weeks>"
        }}
    ],
    "prioritized_enhancement": "<which to do first and why>"
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Project enhancement failed: {e}")
            raise
    
    async def generate_portfolio_strategy(
        self,
        target_role: str,
        current_projects: List[str],
        missing_skills: List[str]
    ) -> dict:
        """
        Generate overall portfolio strategy
        
        Args:
            target_role: Target job role
            current_projects: List of existing projects
            missing_skills: Skills not yet demonstrated
            
        Returns:
            Portfolio strategy and recommendations
        """
        try:
            logger.info("Generating portfolio strategy")
            
            system_prompt = """You are a career strategist specializing in technical portfolios.
Create actionable portfolio strategies that maximize job readiness.
You MUST return valid JSON only."""
            
            user_prompt = f"""Create a portfolio strategy:

Target Role: {target_role}
Current Projects: {', '.join(current_projects) if current_projects else 'None'}
Missing Skills: {', '.join(missing_skills)}

Return in this JSON format:
{{
    "portfolio_assessment": {{
        "current_strength": "<assessment>",
        "gaps": ["<gap 1>", "<gap 2>"],
        "competitive_advantage": "<what stands out>"
    }},
    "recommended_projects": [
        {{
            "project_type": "<type>",
            "priority": "<high/medium/low>",
            "skills_demonstrated": ["<skill 1>", "<skill 2>"],
            "why_important": "<reason>",
            "suggested_title": "<project idea>"
        }}
    ],
    "portfolio_presentation_tips": ["<tip 1>", "<tip 2>"],
    "github_profile_improvements": ["<improvement 1>", "<improvement 2>"],
    "timeline": "<X weeks to complete portfolio>"
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Portfolio strategy generation failed: {e}")
            raise

def get_project_generator_ai() -> ProjectGeneratorAI:
    """Get ProjectGeneratorAI instance"""
    return ProjectGeneratorAI()
