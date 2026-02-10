"""
Unit tests for InternshipAI service

Tests cover:
- Skill extraction from resumes
- Career guidance generation
- Learning recommendations
- Error handling and retry logic
- AI service integration

Requirements: US-1 (1.5), US-5 (5.1-5.6)
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from ai.internship_ai import InternshipAI, get_internship_ai, retry_on_failure
import asyncio


@pytest.fixture
def internship_ai():
    """Create an InternshipAI instance with mocked LLM"""
    ai = InternshipAI()
    ai.llm = Mock()
    return ai


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing"""
    return """
    John Doe
    Software Engineer
    
    Skills:
    - Python, JavaScript, React, Node.js
    - Django, Flask, FastAPI
    - PostgreSQL, MongoDB
    - Git, Docker, AWS
    - Machine Learning, Data Analysis
    
    Experience:
    Built web applications using React and Django.
    Worked with REST APIs and microservices.
    """


@pytest.fixture
def sample_user_profile():
    """Sample user profile for career guidance"""
    return {
        "user_id": "user-123",
        "graduation_year": 2026,
        "current_semester": 4,
        "degree": "B.Tech",
        "branch": "Computer Science",
        "skills": ["Python", "JavaScript", "React", "SQL"]
    }


@pytest.fixture
def sample_internship():
    """Sample internship for career guidance"""
    return {
        "id": "int-123",
        "title": "Full Stack Developer Intern",
        "company": "TechCorp",
        "required_skills": ["Python", "Django", "React", "PostgreSQL"],
        "responsibilities": ["Build web applications", "Write tests", "Code reviews"]
    }


@pytest.fixture
def sample_skill_match():
    """Sample skill match for career guidance"""
    return {
        "match_percentage": 50,
        "matching_skills": ["Python", "React"],
        "missing_skills": ["Django", "PostgreSQL"]
    }


class TestSkillExtraction:
    """Tests for extract_skills_from_resume method"""
    
    @pytest.mark.asyncio
    async def test_extract_skills_success(self, internship_ai, sample_resume_text):
        """Test successful skill extraction from resume"""
        # Mock LLM response
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "skills": ["Python", "JavaScript", "React", "Django", "PostgreSQL", "Git", "Docker"]
        })
        
        skills = await internship_ai.extract_skills_from_resume(sample_resume_text)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
        assert "Python" in skills
        assert "JavaScript" in skills
        assert "React" in skills
        
        # Verify LLM was called
        internship_ai.llm.generate_json_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_skills_removes_duplicates(self, internship_ai, sample_resume_text):
        """Test that duplicate skills are removed"""
        # Mock LLM response with duplicates
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "skills": ["Python", "Python", "JavaScript", "React", "React", "Django"]
        })
        
        skills = await internship_ai.extract_skills_from_resume(sample_resume_text)
        
        # Check no duplicates
        assert len(skills) == len(set(skills))
        assert skills.count("Python") == 1
        assert skills.count("React") == 1
    
    @pytest.mark.asyncio
    async def test_extract_skills_empty_resume(self, internship_ai):
        """Test with empty resume text"""
        with pytest.raises(ValueError, match="Resume text cannot be empty"):
            await internship_ai.extract_skills_from_resume("")
    
    @pytest.mark.asyncio
    async def test_extract_skills_whitespace_only(self, internship_ai):
        """Test with whitespace-only resume text"""
        with pytest.raises(ValueError, match="Resume text cannot be empty"):
            await internship_ai.extract_skills_from_resume("   \n\t   ")
    
    @pytest.mark.asyncio
    async def test_extract_skills_invalid_response(self, internship_ai, sample_resume_text):
        """Test handling of invalid AI response"""
        # Mock LLM response without 'skills' field
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "data": ["Python", "JavaScript"]
        })
        
        with pytest.raises(ValueError, match="AI response missing 'skills' field"):
            await internship_ai.extract_skills_from_resume(sample_resume_text)
    
    @pytest.mark.asyncio
    async def test_extract_skills_non_list_response(self, internship_ai, sample_resume_text):
        """Test handling of non-list skills response"""
        # Mock LLM response with skills as string instead of list
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "skills": "Python, JavaScript, React"
        })
        
        with pytest.raises(ValueError, match="invalid format"):
            await internship_ai.extract_skills_from_resume(sample_resume_text)
    
    @pytest.mark.asyncio
    async def test_extract_skills_cleans_whitespace(self, internship_ai, sample_resume_text):
        """Test that skills are cleaned of extra whitespace"""
        # Mock LLM response with whitespace
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "skills": ["  Python  ", "JavaScript", "  React  ", "Django"]
        })
        
        skills = await internship_ai.extract_skills_from_resume(sample_resume_text)
        
        # All skills should be trimmed
        assert all(skill == skill.strip() for skill in skills)
        assert "Python" in skills
        assert "  Python  " not in skills
    
    @pytest.mark.asyncio
    async def test_extract_skills_filters_empty_strings(self, internship_ai, sample_resume_text):
        """Test that empty strings are filtered out"""
        # Mock LLM response with empty strings
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "skills": ["Python", "", "JavaScript", "   ", "React"]
        })
        
        skills = await internship_ai.extract_skills_from_resume(sample_resume_text)
        
        # No empty strings should be present
        assert "" not in skills
        assert all(skill.strip() for skill in skills)
        assert len(skills) == 3


class TestCareerGuidance:
    """Tests for generate_career_guidance method"""
    
    @pytest.mark.asyncio
    async def test_generate_guidance_success(
        self, internship_ai, sample_user_profile, sample_internship, sample_skill_match
    ):
        """Test successful career guidance generation"""
        # Mock LLM response
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "why_good_fit": "This internship is a great fit because you already have Python and React skills.",
            "skills_to_improve": ["Django", "PostgreSQL", "REST API"],
            "certifications": ["Django for Beginners", "PostgreSQL Certification"],
            "projects": ["Build a blog with Django", "Create a REST API", "Portfolio website"]
        })
        
        guidance = await internship_ai.generate_career_guidance(
            sample_user_profile, sample_internship, sample_skill_match
        )
        
        # Verify all required fields are present
        assert "why_good_fit" in guidance
        assert "skills_to_improve" in guidance
        assert "certifications" in guidance
        assert "projects" in guidance
        
        # Verify field types
        assert isinstance(guidance["why_good_fit"], str)
        assert isinstance(guidance["skills_to_improve"], list)
        assert isinstance(guidance["certifications"], list)
        assert isinstance(guidance["projects"], list)
        
        # Verify content
        assert len(guidance["why_good_fit"]) > 0
        assert len(guidance["skills_to_improve"]) > 0
        assert len(guidance["certifications"]) > 0
        assert len(guidance["projects"]) > 0
    
    @pytest.mark.asyncio
    async def test_generate_guidance_missing_user_profile(
        self, internship_ai, sample_internship, sample_skill_match
    ):
        """Test with missing user profile"""
        with pytest.raises(ValueError, match="user_profile, internship, and skill_match are required"):
            await internship_ai.generate_career_guidance(None, sample_internship, sample_skill_match)
    
    @pytest.mark.asyncio
    async def test_generate_guidance_missing_internship(
        self, internship_ai, sample_user_profile, sample_skill_match
    ):
        """Test with missing internship"""
        with pytest.raises(ValueError, match="user_profile, internship, and skill_match are required"):
            await internship_ai.generate_career_guidance(sample_user_profile, None, sample_skill_match)
    
    @pytest.mark.asyncio
    async def test_generate_guidance_missing_skill_match(
        self, internship_ai, sample_user_profile, sample_internship
    ):
        """Test with missing skill match"""
        with pytest.raises(ValueError, match="user_profile, internship, and skill_match are required"):
            await internship_ai.generate_career_guidance(sample_user_profile, sample_internship, None)
    
    @pytest.mark.asyncio
    async def test_generate_guidance_missing_required_field(
        self, internship_ai, sample_user_profile, sample_internship, sample_skill_match
    ):
        """Test handling of AI response missing required field"""
        # Mock LLM response missing 'projects' field
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "why_good_fit": "Great fit!",
            "skills_to_improve": ["Django"],
            "certifications": ["Django Cert"]
        })
        
        with pytest.raises(ValueError, match="AI response missing required field: projects"):
            await internship_ai.generate_career_guidance(
                sample_user_profile, sample_internship, sample_skill_match
            )
    
    @pytest.mark.asyncio
    async def test_generate_guidance_invalid_field_type(
        self, internship_ai, sample_user_profile, sample_internship, sample_skill_match
    ):
        """Test handling of invalid field types in AI response"""
        # Mock LLM response with string instead of list
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "why_good_fit": "Great fit!",
            "skills_to_improve": "Django, PostgreSQL",  # Should be list
            "certifications": ["Django Cert"],
            "projects": ["Project 1"]
        })
        
        with pytest.raises(ValueError, match="must be a list"):
            await internship_ai.generate_career_guidance(
                sample_user_profile, sample_internship, sample_skill_match
            )
    
    @pytest.mark.asyncio
    async def test_generate_guidance_handles_empty_lists(
        self, internship_ai, sample_user_profile, sample_internship, sample_skill_match
    ):
        """Test that empty lists in profile/internship are handled"""
        # Profile with empty skills
        profile = {**sample_user_profile, "skills": []}
        internship = {**sample_internship, "required_skills": [], "responsibilities": []}
        
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "why_good_fit": "Good opportunity to learn!",
            "skills_to_improve": ["Python", "Django"],
            "certifications": ["Python Certification"],
            "projects": ["Build a web app"]
        })
        
        guidance = await internship_ai.generate_career_guidance(
            profile, internship, sample_skill_match
        )
        
        # Should still generate guidance
        assert guidance is not None
        assert len(guidance["skills_to_improve"]) > 0


class TestLearningRecommendations:
    """Tests for generate_learning_recommendations method"""
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_success(self, internship_ai):
        """Test successful learning recommendations generation"""
        missing_skills = ["Django", "PostgreSQL", "Docker"]
        
        # Mock LLM response
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "recommendations": [
                {
                    "skill": "Django",
                    "estimated_time": "2 weeks",
                    "difficulty": "Medium",
                    "resources": ["Django Official Tutorial", "Django for Beginners"],
                    "priority": "High"
                },
                {
                    "skill": "PostgreSQL",
                    "estimated_time": "1 week",
                    "difficulty": "Easy",
                    "resources": ["PostgreSQL Tutorial", "SQL Basics"],
                    "priority": "High"
                },
                {
                    "skill": "Docker",
                    "estimated_time": "1 week",
                    "difficulty": "Medium",
                    "resources": ["Docker Documentation", "Docker for Beginners"],
                    "priority": "Medium"
                }
            ]
        })
        
        recommendations = await internship_ai.generate_learning_recommendations(missing_skills)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) == 3
        
        # Verify each recommendation has required fields
        for rec in recommendations:
            assert "skill" in rec
            assert "estimated_time" in rec
            assert "difficulty" in rec
            assert "resources" in rec
            assert "priority" in rec
            
            # Verify field types
            assert isinstance(rec["skill"], str)
            assert isinstance(rec["estimated_time"], str)
            assert isinstance(rec["difficulty"], str)
            assert isinstance(rec["resources"], list)
            assert isinstance(rec["priority"], str)
            
            # Verify valid values
            assert rec["difficulty"] in ["Easy", "Medium", "Hard"]
            assert rec["priority"] in ["High", "Medium", "Low"]
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_empty_skills(self, internship_ai):
        """Test with empty missing skills list"""
        recommendations = await internship_ai.generate_learning_recommendations([])
        
        assert recommendations == []
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_with_user_level(self, internship_ai):
        """Test recommendations with different user levels"""
        missing_skills = ["Python"]
        
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "recommendations": [
                {
                    "skill": "Python",
                    "estimated_time": "1 month",
                    "difficulty": "Easy",
                    "resources": ["Python for Beginners"],
                    "priority": "High"
                }
            ]
        })
        
        # Test with beginner level
        recommendations = await internship_ai.generate_learning_recommendations(
            missing_skills, user_level="beginner"
        )
        assert len(recommendations) == 1
        
        # Test with intermediate level
        recommendations = await internship_ai.generate_learning_recommendations(
            missing_skills, user_level="intermediate"
        )
        assert len(recommendations) == 1
        
        # Test with advanced level
        recommendations = await internship_ai.generate_learning_recommendations(
            missing_skills, user_level="advanced"
        )
        assert len(recommendations) == 1
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_invalid_response(self, internship_ai):
        """Test handling of invalid AI response"""
        missing_skills = ["Django"]
        
        # Mock LLM response without 'recommendations' field
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "data": []
        })
        
        with pytest.raises(ValueError, match="AI response missing 'recommendations' field"):
            await internship_ai.generate_learning_recommendations(missing_skills)
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_validates_difficulty(self, internship_ai):
        """Test that invalid difficulty values are corrected"""
        missing_skills = ["Django"]
        
        # Mock LLM response with invalid difficulty
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "recommendations": [
                {
                    "skill": "Django",
                    "estimated_time": "2 weeks",
                    "difficulty": "VeryHard",  # Invalid
                    "resources": ["Django Tutorial"],
                    "priority": "High"
                }
            ]
        })
        
        recommendations = await internship_ai.generate_learning_recommendations(missing_skills)
        
        # Should default to "Medium"
        assert recommendations[0]["difficulty"] == "Medium"
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_validates_priority(self, internship_ai):
        """Test that invalid priority values are corrected"""
        missing_skills = ["Django"]
        
        # Mock LLM response with invalid priority
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "recommendations": [
                {
                    "skill": "Django",
                    "estimated_time": "2 weeks",
                    "difficulty": "Medium",
                    "resources": ["Django Tutorial"],
                    "priority": "Critical"  # Invalid
                }
            ]
        })
        
        recommendations = await internship_ai.generate_learning_recommendations(missing_skills)
        
        # Should default to "Medium"
        assert recommendations[0]["priority"] == "Medium"
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_missing_required_field(self, internship_ai):
        """Test handling of missing required fields in recommendations"""
        missing_skills = ["Django"]
        
        # Mock LLM response missing 'resources' field
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "recommendations": [
                {
                    "skill": "Django",
                    "estimated_time": "2 weeks",
                    "difficulty": "Medium",
                    "priority": "High"
                }
            ]
        })
        
        with pytest.raises(ValueError, match="Recommendation missing required field: resources"):
            await internship_ai.generate_learning_recommendations(missing_skills)


class TestFraudAnalysis:
    """Tests for analyze_fraud_patterns method"""
    
    @pytest.mark.asyncio
    async def test_analyze_fraud_success(self, internship_ai):
        """Test successful fraud pattern analysis"""
        internship = {
            "id": "int-123",
            "title": "Software Intern",
            "company": "TechCorp",
            "company_domain": "techcorp.com",
            "platform": "Internshala",
            "stipend": "₹15,000/month",
            "responsibilities": ["Build APIs", "Write tests"]
        }
        
        # Mock LLM response
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "risk_level": "Low",
            "suspicious_indicators": [],
            "confidence": 85,
            "explanation": "Legitimate internship from verified company"
        })
        
        result = await internship_ai.analyze_fraud_patterns(internship)
        
        assert "risk_level" in result
        assert "suspicious_indicators" in result
        assert "confidence" in result
        assert result["risk_level"] in ["Low", "Medium", "High"]
        assert isinstance(result["suspicious_indicators"], list)
        assert isinstance(result["confidence"], int)
    
    @pytest.mark.asyncio
    async def test_analyze_fraud_high_risk(self, internship_ai):
        """Test fraud analysis for high-risk internship"""
        internship = {
            "id": "int-456",
            "title": "Easy Money Internship",
            "company": "QuickCash Inc",
            "company_domain": "quickcash@gmail.com",
            "platform": "Unknown",
            "stipend": "₹50,000/month",
            "responsibilities": ["No experience needed", "Work from home"]
        }
        
        # Mock LLM response
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "risk_level": "High",
            "suspicious_indicators": [
                "Unrealistic stipend for entry-level",
                "Gmail domain instead of company domain",
                "Red flag keywords: 'easy money', 'no experience needed'"
            ],
            "confidence": 90,
            "explanation": "Multiple red flags indicate potential scam"
        })
        
        result = await internship_ai.analyze_fraud_patterns(internship)
        
        assert result["risk_level"] == "High"
        assert len(result["suspicious_indicators"]) > 0
        assert result["confidence"] > 70
    
    @pytest.mark.asyncio
    async def test_analyze_fraud_handles_error(self, internship_ai):
        """Test that fraud analysis returns safe default on error"""
        internship = {"id": "int-123"}
        
        # Mock LLM to raise exception
        internship_ai.llm.generate_json_response = AsyncMock(
            side_effect=Exception("AI service unavailable")
        )
        
        result = await internship_ai.analyze_fraud_patterns(internship)
        
        # Should return safe default
        assert result["risk_level"] == "Low"
        assert result["suspicious_indicators"] == []
        assert result["confidence"] == 0
        assert "unavailable" in result["explanation"]


class TestRetryLogic:
    """Tests for retry_on_failure decorator"""
    
    @pytest.mark.asyncio
    async def test_retry_success_on_first_attempt(self):
        """Test that successful calls don't retry"""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.01)
        async def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await successful_function()
        
        assert result == "success"
        assert call_count == 1  # Should only be called once
    
    @pytest.mark.asyncio
    async def test_retry_success_on_second_attempt(self):
        """Test that function retries and succeeds"""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.01)
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        result = await flaky_function()
        
        assert result == "success"
        assert call_count == 2  # Should be called twice
    
    @pytest.mark.asyncio
    async def test_retry_exhausts_all_attempts(self):
        """Test that function retries max_retries times before failing"""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.01)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            await always_fails()
        
        assert call_count == 3  # Should be called 3 times
    
    @pytest.mark.asyncio
    async def test_retry_exponential_backoff(self):
        """Test that retry delay increases exponentially"""
        call_times = []
        
        @retry_on_failure(max_retries=3, delay=0.1)
        async def failing_function():
            call_times.append(asyncio.get_event_loop().time())
            raise Exception("Fail")
        
        try:
            await failing_function()
        except Exception:
            pass
        
        # Verify exponential backoff (delays should be ~0.1, ~0.2, ~0.4)
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            assert delay1 >= 0.1  # First delay
        
        if len(call_times) >= 3:
            delay2 = call_times[2] - call_times[1]
            assert delay2 >= 0.2  # Second delay (doubled)


class TestGetInternshipAI:
    """Tests for get_internship_ai factory function"""
    
    def test_get_internship_ai_returns_instance(self):
        """Test that factory function returns InternshipAI instance"""
        ai = get_internship_ai()
        assert isinstance(ai, InternshipAI)
    
    def test_get_internship_ai_has_llm(self):
        """Test that returned instance has LLM service"""
        ai = get_internship_ai()
        assert hasattr(ai, 'llm')
        assert ai.llm is not None


class TestErrorHandling:
    """Tests for error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_skill_extraction_timeout(self, internship_ai, sample_resume_text):
        """Test handling of AI service timeout"""
        # Mock LLM to raise timeout exception
        internship_ai.llm.generate_json_response = AsyncMock(
            side_effect=asyncio.TimeoutError("Request timeout")
        )
        
        with pytest.raises(ValueError, match="Failed to extract skills"):
            await internship_ai.extract_skills_from_resume(sample_resume_text)
    
    @pytest.mark.asyncio
    async def test_guidance_generation_malformed_response(
        self, internship_ai, sample_user_profile, sample_internship, sample_skill_match
    ):
        """Test handling of malformed AI response"""
        # Mock LLM to return malformed response
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "invalid": "response"
        })
        
        with pytest.raises(ValueError):
            await internship_ai.generate_career_guidance(
                sample_user_profile, sample_internship, sample_skill_match
            )
    
    @pytest.mark.asyncio
    async def test_learning_recommendations_non_list_resources(self, internship_ai):
        """Test handling of non-list resources in recommendations"""
        missing_skills = ["Django"]
        
        # Mock LLM response with resources as string
        internship_ai.llm.generate_json_response = AsyncMock(return_value={
            "recommendations": [
                {
                    "skill": "Django",
                    "estimated_time": "2 weeks",
                    "difficulty": "Medium",
                    "resources": "Django Tutorial",  # Should be list
                    "priority": "High"
                }
            ]
        })
        
        recommendations = await internship_ai.generate_learning_recommendations(missing_skills)
        
        # Should convert to empty list
        assert recommendations[0]["resources"] == []
