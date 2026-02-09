"""
AI service for skill-to-job matching
Feature 4: AI Skill-to-Job Matching Engine
"""
from ai.llm import get_llm_service
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Comprehensive job role skill maps
JOB_ROLE_SKILL_MAPS = {
    "Data Science": {
        "Junior Data Analyst": {
            "required": ["SQL", "Excel", "Data Cleaning", "Basic Statistics"],
            "preferred": ["Python", "Power BI", "Tableau"],
            "experience": "0-2 years"
        },
        "Data Analyst": {
            "required": ["SQL", "Python", "Data Visualization", "Statistics"],
            "preferred": ["Power BI", "Tableau", "R", "ETL"],
            "experience": "2-4 years"
        },
        "Data Scientist": {
            "required": ["Python", "Machine Learning", "Statistics", "SQL", "Data Visualization"],
            "preferred": ["TensorFlow", "PyTorch", "Deep Learning", "Big Data"],
            "experience": "3-5 years"
        },
        "Senior Data Scientist": {
            "required": ["Python", "Machine Learning", "Deep Learning", "MLOps", "Statistics"],
            "preferred": ["TensorFlow", "PyTorch", "Spark", "Cloud Platforms"],
            "experience": "5+ years"
        }
    },
    "Web Development": {
        "Junior Frontend Developer": {
            "required": ["HTML", "CSS", "JavaScript", "React"],
            "preferred": ["TypeScript", "Git", "Responsive Design"],
            "experience": "0-2 years"
        },
        "Frontend Developer": {
            "required": ["HTML", "CSS", "JavaScript", "React", "TypeScript"],
            "preferred": ["Next.js", "Redux", "Testing", "CI/CD"],
            "experience": "2-4 years"
        },
        "Full Stack Developer": {
            "required": ["JavaScript", "React", "Node.js", "SQL", "REST APIs"],
            "preferred": ["TypeScript", "MongoDB", "Docker", "AWS"],
            "experience": "3-5 years"
        },
        "Senior Full Stack Developer": {
            "required": ["JavaScript", "React", "Node.js", "Databases", "System Design", "Cloud"],
            "preferred": ["Microservices", "Kubernetes", "CI/CD", "Architecture"],
            "experience": "5+ years"
        }
    },
    "Business": {
        "Business Analyst": {
            "required": ["Excel", "SQL", "Data Analysis", "Stakeholder Management"],
            "preferred": ["Tableau", "Power BI", "JIRA", "Agile"],
            "experience": "2-4 years"
        },
        "Product Manager": {
            "required": ["Product Strategy", "Stakeholder Management", "Agile", "Data Analysis"],
            "preferred": ["SQL", "A/B Testing", "UX Design", "Roadmapping"],
            "experience": "3-5 years"
        },
        "Management Consultant": {
            "required": ["Business Strategy", "Data Analysis", "Presentation", "Excel"],
            "preferred": ["SQL", "Financial Modeling", "Market Research"],
            "experience": "2-5 years"
        }
    },
    "Cloud & DevOps": {
        "Cloud Engineer": {
            "required": ["AWS", "Linux", "Networking", "Infrastructure as Code"],
            "preferred": ["Terraform", "Docker", "Kubernetes", "Python"],
            "experience": "2-4 years"
        },
        "DevOps Engineer": {
            "required": ["CI/CD", "Docker", "Kubernetes", "Linux", "Scripting"],
            "preferred": ["AWS", "Terraform", "Monitoring", "Git"],
            "experience": "3-5 years"
        }
    }
}

class JobMatchAI:
    """AI service for skill-to-job matching"""
    
    def __init__(self):
        self.llm = get_llm_service()
        self.job_maps = JOB_ROLE_SKILL_MAPS
    
    async def match_jobs(
        self,
        user_skills: List[str],
        experience_years: int,
        target_domain: Optional[str] = None
    ) -> dict:
        """
        Match user skills to job roles and calculate fit scores
        
        Args:
            user_skills: List of user's current skills
            experience_years: Years of experience
            target_domain: Optional domain filter (Data Science, Web Development, etc.)
            
        Returns:
            Job matches with fit scores and gap analysis
        """
        try:
            logger.info(f"Matching jobs for {len(user_skills)} skills, {experience_years} years exp")
            
            # Normalize skills for comparison
            normalized_user_skills = [skill.lower().strip() for skill in user_skills]
            
            # Determine which domains to check
            domains_to_check = [target_domain] if target_domain and target_domain in self.job_maps else self.job_maps.keys()
            
            # Build context for AI
            all_roles_info = []
            for domain in domains_to_check:
                for role, requirements in self.job_maps[domain].items():
                    all_roles_info.append({
                        "domain": domain,
                        "role": role,
                        "required_skills": requirements["required"],
                        "preferred_skills": requirements["preferred"],
                        "experience": requirements["experience"]
                    })
            
            # Use AI to analyze matches
            system_prompt = """You are an expert career counselor and technical recruiter.
Analyze user skills against job role requirements and provide accurate fit scores.
You MUST return valid JSON only."""
            
            user_prompt = f"""Analyze job fit for this candidate:

User Skills: {', '.join(user_skills)}
Experience: {experience_years} years

Available Job Roles:
{self._format_roles_for_prompt(all_roles_info)}

For each role, calculate:
1. Fit score (0-100) based on:
   - Required skills match (70% weight)
   - Preferred skills match (20% weight)
   - Experience level match (10% weight)
2. Identify matching skills
3. Identify missing critical skills
4. Provide specific, actionable recommendation

Return in this JSON format:
{{
    "job_matches": [
        {{
            "role": "<role name>",
            "domain": "<domain>",
            "fit_score": <number 0-100>,
            "matching_skills": ["<skill 1>", "<skill 2>"],
            "missing_critical_skills": ["<skill 1>", "<skill 2>"],
            "missing_preferred_skills": ["<skill 1>", "<skill 2>"],
            "quick_wins": ["<skill that's easy to learn and high impact>"],
            "recommendation": "<specific advice to improve fit>",
            "experience_match": "<under/meets/exceeds>"
        }}
    ]
}}

Only include roles with fit_score >= 40. Sort by fit_score descending.
Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            
            # Validate and enhance results
            job_matches = result.get("job_matches", [])
            logger.info(f"Found {len(job_matches)} job matches")
            
            return result
            
        except Exception as e:
            logger.error(f"Job matching failed: {e}")
            raise
    
    async def analyze_skill_gap_for_role(
        self,
        user_skills: List[str],
        target_role: str,
        target_domain: Optional[str] = None
    ) -> dict:
        """
        Detailed skill gap analysis for a specific role
        
        Args:
            user_skills: User's current skills
            target_role: Specific job role to analyze
            target_domain: Domain of the role
            
        Returns:
            Detailed gap analysis
        """
        try:
            logger.info(f"Analyzing skill gap for role: {target_role}")
            
            # Find role requirements
            role_requirements = None
            found_domain = None
            
            if target_domain and target_domain in self.job_maps:
                if target_role in self.job_maps[target_domain]:
                    role_requirements = self.job_maps[target_domain][target_role]
                    found_domain = target_domain
            else:
                # Search all domains
                for domain, roles in self.job_maps.items():
                    if target_role in roles:
                        role_requirements = roles[target_role]
                        found_domain = domain
                        break
            
            if not role_requirements:
                # Use AI to analyze unknown role
                return await self._analyze_custom_role(user_skills, target_role)
            
            system_prompt = """You are a technical skills analyst.
Provide detailed skill gap analysis for career transitions.
You MUST return valid JSON only."""
            
            user_prompt = f"""Analyze skill gap for this career goal:

User Skills: {', '.join(user_skills)}
Target Role: {target_role}
Domain: {found_domain}

Role Requirements:
- Required Skills: {', '.join(role_requirements['required'])}
- Preferred Skills: {', '.join(role_requirements['preferred'])}
- Experience Level: {role_requirements['experience']}

Provide detailed analysis in this JSON format:
{{
    "role": "{target_role}",
    "domain": "{found_domain}",
    "overall_fit": <number 0-100>,
    "matching_skills": ["<skill 1>", "<skill 2>"],
    "missing_critical_skills": [
        {{
            "skill": "<skill name>",
            "importance": "<critical/important/nice-to-have>",
            "learning_difficulty": "<easy/medium/hard>",
            "estimated_time": "<X weeks/months>",
            "why_needed": "<specific reason>"
        }}
    ],
    "skill_development_priority": [
        {{
            "skill": "<skill name>",
            "priority_rank": <1-10>,
            "impact_on_fit": "<+X points>",
            "learning_path": "<brief guidance>"
        }}
    ],
    "transferable_strengths": ["<strength 1>", "<strength 2>"],
    "readiness_assessment": "<ready/needs_preparation/significant_gap>",
    "timeline_to_ready": "<X weeks/months>"
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Skill gap analysis failed: {e}")
            raise
    
    async def _analyze_custom_role(self, user_skills: List[str], target_role: str) -> dict:
        """Analyze skill gap for roles not in predefined maps"""
        system_prompt = """You are a career expert analyzing skill requirements for job roles.
You MUST return valid JSON only."""
        
        user_prompt = f"""Analyze skill requirements and gaps for this role:

User Skills: {', '.join(user_skills)}
Target Role: {target_role}

Provide analysis in this JSON format:
{{
    "role": "{target_role}",
    "domain": "<inferred domain>",
    "overall_fit": <number 0-100>,
    "matching_skills": ["<skill 1>", "<skill 2>"],
    "missing_critical_skills": [
        {{
            "skill": "<skill name>",
            "importance": "<critical/important/nice-to-have>",
            "learning_difficulty": "<easy/medium/hard>",
            "estimated_time": "<X weeks/months>",
            "why_needed": "<specific reason>"
        }}
    ],
    "readiness_assessment": "<ready/needs_preparation/significant_gap>",
    "timeline_to_ready": "<X weeks/months>"
}}

Return ONLY the JSON object."""
        
        result = await self.llm.generate_json_response(system_prompt, user_prompt)
        return result
    
    def _format_roles_for_prompt(self, roles_info: List[dict]) -> str:
        """Format role information for AI prompt"""
        formatted = []
        for role in roles_info:
            formatted.append(
                f"- {role['role']} ({role['domain']})\n"
                f"  Required: {', '.join(role['required_skills'])}\n"
                f"  Preferred: {', '.join(role['preferred_skills'])}\n"
                f"  Experience: {role['experience']}"
            )
        return "\n\n".join(formatted)

def get_job_match_ai() -> JobMatchAI:
    """Get JobMatchAI instance"""
    return JobMatchAI()
