"""
Matching Service - Skill matching and recommendation engine

This service handles skill matching calculations, learning path generation,
and internship ranking based on relevance to user profiles.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.models.internship import (
    SkillMatch,
    SkillMatchCreate,
    LearningPathItem,
    InternshipListing,
    StudentProfile,
)

logger = logging.getLogger(__name__)


class MatchingService:
    """Skill matching and recommendation engine"""
    
    # Learning resources by skill category
    LEARNING_RESOURCES = {
        # Programming Languages
        "python": [
            "Python Official Tutorial (python.org)",
            "Coursera: Python for Everybody",
            "Real Python Tutorials"
        ],
        "java": [
            "Oracle Java Tutorials",
            "Coursera: Java Programming and Software Engineering",
            "Codecademy: Learn Java"
        ],
        "javascript": [
            "MDN Web Docs: JavaScript Guide",
            "freeCodeCamp: JavaScript Algorithms",
            "Eloquent JavaScript (book)"
        ],
        "c++": [
            "LearnCpp.com",
            "Coursera: C++ For C Programmers",
            "C++ Reference Documentation"
        ],
        "c": [
            "Learn-C.org",
            "CS50: Introduction to Computer Science",
            "The C Programming Language (book)"
        ],
        
        # Web Development
        "react": [
            "React Official Documentation",
            "freeCodeCamp: Front End Development Libraries",
            "Scrimba: Learn React"
        ],
        "angular": [
            "Angular Official Tutorial",
            "Udemy: Angular - The Complete Guide",
            "Angular University Courses"
        ],
        "vue": [
            "Vue.js Official Guide",
            "Vue Mastery Courses",
            "freeCodeCamp: Vue.js Course"
        ],
        "node.js": [
            "Node.js Official Guides",
            "freeCodeCamp: Back End Development",
            "The Net Ninja: Node.js Tutorial"
        ],
        "django": [
            "Django Official Tutorial",
            "Django for Beginners (book)",
            "Coursera: Django for Everybody"
        ],
        "flask": [
            "Flask Official Tutorial",
            "Miguel Grinberg's Flask Mega-Tutorial",
            "Real Python: Flask Tutorials"
        ],
        
        # Databases
        "sql": [
            "SQLBolt Interactive Tutorial",
            "Khan Academy: Intro to SQL",
            "Mode Analytics: SQL Tutorial"
        ],
        "mongodb": [
            "MongoDB University",
            "MongoDB Official Documentation",
            "freeCodeCamp: MongoDB Course"
        ],
        "postgresql": [
            "PostgreSQL Official Tutorial",
            "PostgreSQL Exercises",
            "Udemy: The Complete PostgreSQL Bootcamp"
        ],
        
        # Data Science & ML
        "machine learning": [
            "Coursera: Machine Learning by Andrew Ng",
            "fast.ai: Practical Deep Learning",
            "Google's Machine Learning Crash Course"
        ],
        "data analysis": [
            "Coursera: Google Data Analytics Certificate",
            "DataCamp: Data Analyst Track",
            "Kaggle Learn: Data Analysis"
        ],
        "pandas": [
            "Pandas Official Documentation",
            "Kaggle Learn: Pandas",
            "Real Python: Pandas Tutorials"
        ],
        "numpy": [
            "NumPy Official Tutorial",
            "Coursera: Applied Data Science with Python",
            "DataCamp: Introduction to NumPy"
        ],
        
        # Cloud & DevOps
        "aws": [
            "AWS Training and Certification",
            "A Cloud Guru: AWS Certified Solutions Architect",
            "freeCodeCamp: AWS Certified Cloud Practitioner"
        ],
        "docker": [
            "Docker Official Get Started Guide",
            "Docker Mastery Course",
            "Play with Docker Classroom"
        ],
        "kubernetes": [
            "Kubernetes Official Tutorial",
            "Kubernetes for Beginners (KodeKloud)",
            "CNCF Kubernetes Fundamentals"
        ],
        
        # Tools & Frameworks
        "git": [
            "Git Official Documentation",
            "GitHub Learning Lab",
            "Atlassian Git Tutorial"
        ],
        "rest api": [
            "RESTful API Design Tutorial",
            "Postman Learning Center",
            "freeCodeCamp: APIs for Beginners"
        ],
        "graphql": [
            "GraphQL Official Tutorial",
            "How to GraphQL",
            "Apollo GraphQL Tutorials"
        ],
        
        # Default for unknown skills
        "default": [
            "Coursera: Search for relevant courses",
            "Udemy: Search for skill-specific courses",
            "YouTube: Search for tutorials",
            "Official documentation for the technology"
        ]
    }
    
    # Estimated learning times by difficulty
    LEARNING_TIMES = {
        "easy": "1-2 weeks",
        "medium": "3-4 weeks",
        "hard": "6-8 weeks"
    }
    
    # Skill difficulty mapping (can be expanded)
    SKILL_DIFFICULTY = {
        # Easy skills (1-2 weeks)
        "git": "easy",
        "html": "easy",
        "css": "easy",
        "sql": "easy",
        
        # Medium skills (3-4 weeks)
        "python": "medium",
        "javascript": "medium",
        "react": "medium",
        "node.js": "medium",
        "django": "medium",
        "flask": "medium",
        "rest api": "medium",
        "mongodb": "medium",
        "postgresql": "medium",
        
        # Hard skills (6-8 weeks)
        "machine learning": "hard",
        "data science": "hard",
        "kubernetes": "hard",
        "aws": "hard",
        "system design": "hard",
        "distributed systems": "hard",
    }
    
    def __init__(self, db_client=None):
        """
        Initialize the matching service
        
        Args:
            db_client: Optional database client for caching results
        """
        self.db = db_client
        logger.info("MatchingService initialized")
    
    def _normalize_skill(self, skill: str) -> str:
        """
        Normalize skill name for comparison
        
        Args:
            skill: Raw skill name
            
        Returns:
            Normalized skill name (lowercase, trimmed)
        """
        return skill.lower().strip()
    
    def _get_skill_difficulty(self, skill: str) -> str:
        """
        Determine difficulty level for a skill
        
        Args:
            skill: Skill name
            
        Returns:
            Difficulty level: "easy", "medium", or "hard"
        """
        normalized_skill = self._normalize_skill(skill)
        return self.SKILL_DIFFICULTY.get(normalized_skill, "medium")
    
    def _get_learning_resources(self, skill: str) -> List[str]:
        """
        Get learning resources for a skill
        
        Args:
            skill: Skill name
            
        Returns:
            List of learning resource URLs/names
        """
        normalized_skill = self._normalize_skill(skill)
        
        # Try exact match first
        if normalized_skill in self.LEARNING_RESOURCES:
            return self.LEARNING_RESOURCES[normalized_skill]
        
        # Try partial match (e.g., "react.js" matches "react")
        # Only match if the key is a substring of the skill or vice versa
        # and the match is substantial (at least 3 characters)
        for key in self.LEARNING_RESOURCES:
            if len(key) >= 3:  # Only consider keys with at least 3 characters
                if key in normalized_skill or normalized_skill in key:
                    # Ensure it's a substantial match (at least 50% of the shorter string)
                    shorter_len = min(len(key), len(normalized_skill))
                    if shorter_len >= 3:  # Minimum 3 character match
                        return self.LEARNING_RESOURCES[key]
        
        # Return default resources
        return self.LEARNING_RESOURCES["default"]
    
    def _prioritize_skill(self, skill: str, required_skills: List[str]) -> str:
        """
        Determine priority level for learning a skill
        
        Args:
            skill: Skill to prioritize
            required_skills: List of required skills for the internship
            
        Returns:
            Priority level: "High", "Medium", or "Low"
        """
        normalized_skill = self._normalize_skill(skill)
        normalized_required = [self._normalize_skill(s) for s in required_skills]
        
        # High priority if it's a required skill
        if normalized_skill in normalized_required:
            return "High"
        
        # Medium priority for preferred skills
        return "Medium"
    
    async def calculate_skill_match(
        self,
        user_skills: List[str],
        required_skills: List[str],
        preferred_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate skill match percentage between user skills and internship requirements
        
        Algorithm:
        1. Normalize all skills (lowercase, trim)
        2. Calculate intersection (matching skills)
        3. Calculate difference (missing required skills)
        4. Calculate match percentage:
           - Required skills: 70% weight
           - Preferred skills: 30% weight
           - Match % = (matched_required / total_required) * 0.7 + (matched_preferred / total_preferred) * 0.3
        
        Args:
            user_skills: List of user's skills
            required_skills: List of required skills for internship
            preferred_skills: Optional list of preferred skills
            
        Returns:
            Dictionary with:
            - match_percentage: int (0-100)
            - matching_skills: List[str]
            - missing_skills: List[str]
        """
        logger.info(f"Calculating skill match for {len(user_skills)} user skills vs {len(required_skills)} required skills")
        
        # Handle empty lists
        if not required_skills:
            logger.warning("No required skills provided, returning 100% match")
            return {
                "match_percentage": 100,
                "matching_skills": [],
                "missing_skills": []
            }
        
        if not user_skills:
            logger.warning("No user skills provided, returning 0% match")
            return {
                "match_percentage": 0,
                "matching_skills": [],
                "missing_skills": required_skills
            }
        
        # Normalize skills
        user_skills_normalized = set(self._normalize_skill(s) for s in user_skills)
        required_skills_normalized = set(self._normalize_skill(s) for s in required_skills)
        preferred_skills_normalized = set(self._normalize_skill(s) for s in (preferred_skills or []))
        
        # Calculate matching and missing skills for required
        matching_required = user_skills_normalized.intersection(required_skills_normalized)
        missing_required = required_skills_normalized.difference(user_skills_normalized)
        
        # Calculate required skills match percentage
        required_match_pct = (len(matching_required) / len(required_skills_normalized)) * 100
        
        # Calculate preferred skills match if provided
        preferred_match_pct = 0
        matching_preferred = set()
        if preferred_skills_normalized:
            matching_preferred = user_skills_normalized.intersection(preferred_skills_normalized)
            preferred_match_pct = (len(matching_preferred) / len(preferred_skills_normalized)) * 100
        
        # Calculate weighted match percentage
        # Required: 70% weight, Preferred: 30% weight
        if preferred_skills_normalized:
            match_percentage = int((required_match_pct * 0.7) + (preferred_match_pct * 0.3))
        else:
            # If no preferred skills, use only required skills
            match_percentage = int(required_match_pct)
        
        # Ensure percentage is within bounds [0, 100]
        match_percentage = max(0, min(100, match_percentage))
        
        # Get original case for matching skills
        all_matching = matching_required.union(matching_preferred)
        matching_skills_original = [
            skill for skill in (required_skills + (preferred_skills or []))
            if self._normalize_skill(skill) in all_matching
        ]
        
        # Get original case for missing skills
        missing_skills_original = [
            skill for skill in required_skills
            if self._normalize_skill(skill) in missing_required
        ]
        
        logger.info(f"Match calculation complete: {match_percentage}% ({len(matching_skills_original)} matching, {len(missing_skills_original)} missing)")
        
        return {
            "match_percentage": match_percentage,
            "matching_skills": matching_skills_original,
            "missing_skills": missing_skills_original
        }
    
    async def generate_learning_path(
        self,
        missing_skills: List[str],
        required_skills: Optional[List[str]] = None
    ) -> List[LearningPathItem]:
        """
        Generate learning path for missing skills
        
        Creates a structured learning plan with:
        - Skill name
        - Estimated learning time based on difficulty
        - Difficulty level
        - Learning resources
        - Priority (High for required, Medium for preferred)
        
        Args:
            missing_skills: List of skills the user needs to learn
            required_skills: Optional list of required skills (for prioritization)
            
        Returns:
            List of LearningPathItem objects
        """
        logger.info(f"Generating learning path for {len(missing_skills)} missing skills")
        
        if not missing_skills:
            logger.info("No missing skills, returning empty learning path")
            return []
        
        learning_path = []
        required_skills = required_skills or []
        
        for skill in missing_skills:
            # Determine difficulty and time
            difficulty = self._get_skill_difficulty(skill)
            estimated_time = self.LEARNING_TIMES.get(difficulty, "3-4 weeks")
            
            # Get learning resources
            resources = self._get_learning_resources(skill)
            
            # Determine priority
            priority = self._prioritize_skill(skill, required_skills)
            
            # Create learning path item
            item = LearningPathItem(
                skill=skill,
                estimated_time=estimated_time,
                difficulty=difficulty.capitalize(),
                resources=resources,
                priority=priority
            )
            
            learning_path.append(item)
            logger.debug(f"Added learning path item for {skill}: {difficulty}, {estimated_time}, priority {priority}")
        
        # Sort by priority (High first, then Medium, then Low)
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        learning_path.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        logger.info(f"Learning path generated with {len(learning_path)} items")
        return learning_path
    
    async def rank_internships(
        self,
        user_profile: StudentProfile,
        internships: List[InternshipListing]
    ) -> List[Dict[str, Any]]:
        """
        Rank internships by relevance to user profile
        
        Ranking algorithm:
        1. Calculate skill match for each internship
        2. Sort by match percentage (descending)
        3. Return internships with match scores
        
        Args:
            user_profile: User's profile with skills and preferences
            internships: List of internship listings
            
        Returns:
            List of internships with match scores, sorted by relevance
        """
        logger.info(f"Ranking {len(internships)} internships for user")
        
        if not internships:
            logger.warning("No internships to rank")
            return []
        
        ranked_internships = []
        
        for internship in internships:
            # Calculate skill match
            match_result = await self.calculate_skill_match(
                user_skills=user_profile.skills,
                required_skills=internship.required_skills,
                preferred_skills=internship.preferred_skills
            )
            
            # Create ranked entry
            ranked_entry = {
                "internship": internship,
                "match_percentage": match_result["match_percentage"],
                "matching_skills": match_result["matching_skills"],
                "missing_skills": match_result["missing_skills"]
            }
            
            ranked_internships.append(ranked_entry)
            logger.debug(f"Ranked {internship.title}: {match_result['match_percentage']}% match")
        
        # Sort by match percentage (descending)
        ranked_internships.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        logger.info(f"Ranking complete. Top match: {ranked_internships[0]['match_percentage']}%")
        return ranked_internships
    
    async def create_skill_match(
        self,
        user_id: str,
        internship_id: str,
        user_skills: List[str],
        required_skills: List[str],
        preferred_skills: Optional[List[str]] = None
    ) -> SkillMatch:
        """
        Create a complete skill match record with learning path
        
        This is a convenience method that combines skill matching and
        learning path generation into a single SkillMatch object.
        
        Args:
            user_id: User's ID
            internship_id: Internship ID
            user_skills: User's skills
            required_skills: Required skills for internship
            preferred_skills: Optional preferred skills
            
        Returns:
            Complete SkillMatch object
        """
        logger.info(f"Creating skill match for user {user_id} and internship {internship_id}")
        
        # Calculate skill match
        match_result = await self.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills
        )
        
        # Generate learning path for missing skills
        learning_path = await self.generate_learning_path(
            missing_skills=match_result["missing_skills"],
            required_skills=required_skills
        )
        
        # Create SkillMatch object
        skill_match = SkillMatch(
            id=f"{user_id}_{internship_id}_match",  # Temporary ID
            user_id=user_id,
            internship_id=internship_id,
            match_percentage=match_result["match_percentage"],
            matching_skills=match_result["matching_skills"],
            missing_skills=match_result["missing_skills"],
            learning_path=learning_path,
            created_at=datetime.now()
        )
        
        logger.info(f"Skill match created: {match_result['match_percentage']}% match with {len(learning_path)} learning items")
        return skill_match
