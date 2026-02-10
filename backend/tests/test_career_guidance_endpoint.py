"""
Integration test for career guidance endpoint

This test verifies that the GET /api/internships/{internship_id}/guidance endpoint
works correctly by integrating with the AI service.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
from fastapi import HTTPException

from app.routers.internship import get_career_guidance
from app.models.internship import (
    StudentProfile,
    LocationPreference,
    CompensationPreference,
)


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    return {"email": "test@example.com", "sub": "test@example.com"}


@pytest.fixture
def sample_profile():
    """Sample user profile"""
    return StudentProfile(
        id="123e4567-e89b-12d3-a456-426614174000",
        user_id="test@example.com",
        graduation_year=2026,
        current_semester=4,
        degree="B.Tech",
        branch="Computer Science",
        skills=["Python", "JavaScript", "React"],
        preferred_roles=["Software Engineer", "Full Stack Developer"],
        internship_type=LocationPreference.REMOTE,
        compensation_preference=CompensationPreference.PAID,
        target_companies=["Google", "Microsoft"],
        resume_url=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def sample_internship():
    """Sample internship listing"""
    return {
        "id": "internship-123",
        "title": "Software Engineering Intern",
        "company": "TechCorp",
        "required_skills": ["Python", "JavaScript", "Django", "REST API"],
        "preferred_skills": ["React", "Docker"],
        "responsibilities": [
            "Build REST APIs using Django",
            "Write unit tests",
            "Collaborate with team"
        ],
        "location": "Remote",
        "stipend": "₹15,000/month"
    }


@pytest.fixture
def sample_skill_match():
    """Sample skill match data"""
    return {
        "match_percentage": 75,
        "matching_skills": ["Python", "JavaScript", "React"],
        "missing_skills": ["Django", "REST API"],
        "learning_path": [
            {
                "skill": "Django",
                "estimated_time": "3-4 weeks",
                "difficulty": "Medium",
                "resources": [
                    "Django Official Tutorial",
                    "Django for Beginners (book)"
                ],
                "priority": "High"
            }
        ]
    }


@pytest.fixture
def sample_guidance():
    """Sample AI-generated career guidance"""
    return {
        "why_good_fit": "This internship is a great fit for you because you already have strong skills in Python and JavaScript, which are core requirements. As a 4th semester B.Tech Computer Science student, this is the perfect time to gain hands-on experience with web development frameworks like Django.",
        "skills_to_improve": ["Django", "REST API", "Docker"],
        "certifications": [
            "Django for Everybody Specialization (Coursera)",
            "REST API Design Certification"
        ],
        "projects": [
            "Build a blog application with Django and REST API",
            "Create a task management system with user authentication",
            "Develop a portfolio website with Django backend"
        ]
    }


class TestCareerGuidanceEndpoint:
    """Test suite for career guidance endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_career_guidance_success(
        self,
        mock_user,
        sample_profile,
        sample_internship,
        sample_skill_match,
        sample_guidance
    ):
        """Test successful career guidance generation"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile)
        
        # Mock Supabase client with simpler approach
        mock_supabase = MagicMock()
        
        # Create mock results
        mock_internship_result = MagicMock()
        mock_internship_result.data = [sample_internship]
        
        mock_skill_match_result = MagicMock()
        mock_skill_match_result.data = [sample_skill_match]
        
        # Track which call we're on
        call_tracker = {'count': 0}
        
        def mock_execute():
            call_tracker['count'] += 1
            if call_tracker['count'] == 1:
                return mock_internship_result
            else:
                return mock_skill_match_result
        
        # Setup the mock chain
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute = mock_execute
        
        # Mock AI service
        mock_ai_service = Mock()
        mock_ai_service.generate_career_guidance = AsyncMock(return_value=sample_guidance)
        
        # Patch dependencies
        with patch('app.routers.internship.supabase', mock_supabase), \
             patch('ai.internship_ai.get_internship_ai', return_value=mock_ai_service):
            
            # Call endpoint
            result = await get_career_guidance(
                internship_id="internship-123",
                current_user=mock_user,
                service=mock_service
            )
            
            # Assertions
            assert result["success"] is True
            assert "data" in result
            
            # Verify guidance structure
            guidance_data = result["data"]
            assert "why_good_fit" in guidance_data
            assert "skills_to_improve" in guidance_data
            assert "certifications" in guidance_data
            assert "projects" in guidance_data
            
            # Verify content
            assert len(guidance_data["why_good_fit"]) > 0
            assert len(guidance_data["skills_to_improve"]) > 0
            assert len(guidance_data["certifications"]) > 0
            assert len(guidance_data["projects"]) > 0
            
            # Verify service calls
            mock_service.get_profile.assert_called_once_with("test@example.com")
            mock_ai_service.generate_career_guidance.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_career_guidance_no_profile(
        self,
        mock_user
    ):
        """Test career guidance when user has no profile"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=None)
        
        # Call endpoint and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await get_career_guidance(
                internship_id="internship-123",
                current_user=mock_user,
                service=mock_service
            )
        
        # Assertions
        assert exc_info.value.status_code == 404
        assert "PROFILE_NOT_FOUND" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_career_guidance_internship_not_found(
        self,
        mock_user,
        sample_profile
    ):
        """Test career guidance when internship doesn't exist"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile)
        
        # Mock Supabase client - no internship found
        mock_supabase = MagicMock()
        mock_internship_result = MagicMock()
        mock_internship_result.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_internship_result
        
        # Patch dependencies
        with patch('app.routers.internship.supabase', mock_supabase):
            
            # Call endpoint and expect exception
            with pytest.raises(HTTPException) as exc_info:
                await get_career_guidance(
                    internship_id="nonexistent-123",
                    current_user=mock_user,
                    service=mock_service
                )
            
            # Assertions
            assert exc_info.value.status_code == 404
            assert "INTERNSHIP_NOT_FOUND" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_career_guidance_ai_service_error(
        self,
        mock_user,
        sample_profile,
        sample_internship,
        sample_skill_match
    ):
        """Test career guidance when AI service fails"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile)
        
        # Mock Supabase client
        mock_supabase = MagicMock()
        mock_internship_result = MagicMock()
        mock_internship_result.data = [sample_internship]
        mock_skill_match_result = MagicMock()
        mock_skill_match_result.data = [sample_skill_match]
        
        # Setup call chain
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_eq = MagicMock()
        
        call_count = [0]
        def execute_side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_internship_result
            else:
                return mock_skill_match_result
        
        mock_eq.execute = execute_side_effect
        mock_table.select.return_value.eq.return_value = mock_eq
        
        # Mock AI service - raise error
        mock_ai_service = Mock()
        mock_ai_service.generate_career_guidance = AsyncMock(
            side_effect=ValueError("AI service temporarily unavailable")
        )
        
        # Patch dependencies
        with patch('app.routers.internship.supabase', mock_supabase), \
             patch('ai.internship_ai.get_internship_ai', return_value=mock_ai_service):
            
            # Call endpoint and expect exception
            with pytest.raises(HTTPException) as exc_info:
                await get_career_guidance(
                    internship_id="internship-123",
                    current_user=mock_user,
                    service=mock_service
                )
            
            # Assertions
            assert exc_info.value.status_code == 503
            assert "AI_SERVICE_ERROR" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_career_guidance_calculates_skill_match_if_not_cached(
        self,
        mock_user,
        sample_profile,
        sample_internship,
        sample_guidance
    ):
        """Test that career guidance works even when skill match is not cached"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile)
        
        # Mock Supabase client
        mock_supabase = MagicMock()
        mock_internship_result = MagicMock()
        mock_internship_result.data = [sample_internship]
        
        # Mock skill match lookup - NOT cached (empty result)
        mock_skill_match_result = MagicMock()
        mock_skill_match_result.data = []
        
        # Track which call we're on
        call_tracker = {'count': 0}
        
        def mock_execute():
            call_tracker['count'] += 1
            if call_tracker['count'] == 1:
                return mock_internship_result
            else:
                return mock_skill_match_result
        
        # Setup the mock chain
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute = mock_execute
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()
        
        # Mock matching service
        from app.models.internship import SkillMatch, LearningPathItem
        mock_skill_match_obj = SkillMatch(
            id="match-123",
            user_id="test@example.com",
            internship_id="internship-123",
            match_percentage=75,
            matching_skills=["Python", "JavaScript", "React"],
            missing_skills=["Django", "REST API"],
            learning_path=[
                LearningPathItem(
                    skill="Django",
                    estimated_time="3-4 weeks",
                    difficulty="Medium",
                    resources=["Django Tutorial"],
                    priority="High"
                )
            ],
            created_at=datetime.now()
        )
        
        mock_matching_service = Mock()
        mock_matching_service.create_skill_match = AsyncMock(return_value=mock_skill_match_obj)
        
        # Mock AI service
        mock_ai_service = Mock()
        mock_ai_service.generate_career_guidance = AsyncMock(return_value=sample_guidance)
        
        # Patch dependencies - need to patch where it's imported
        with patch('app.routers.internship.supabase', mock_supabase), \
             patch('ai.internship_ai.get_internship_ai', return_value=mock_ai_service), \
             patch('app.services.matching_service.MatchingService', return_value=mock_matching_service):
            
            # Call endpoint
            result = await get_career_guidance(
                internship_id="internship-123",
                current_user=mock_user,
                service=mock_service
            )
            
            # Assertions - just verify it works
            assert result["success"] is True
            assert "data" in result
            
            # Verify AI service was called
            mock_ai_service.generate_career_guidance.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_career_guidance_response_structure(
        self,
        mock_user,
        sample_profile,
        sample_internship,
        sample_skill_match,
        sample_guidance
    ):
        """Test that career guidance response has correct structure"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile)
        
        # Mock Supabase client
        mock_supabase = MagicMock()
        mock_internship_result = MagicMock()
        mock_internship_result.data = [sample_internship]
        mock_skill_match_result = MagicMock()
        mock_skill_match_result.data = [sample_skill_match]
        
        # Setup call chain
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_eq = MagicMock()
        
        call_count = [0]
        def execute_side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_internship_result
            else:
                return mock_skill_match_result
        
        mock_eq.execute = execute_side_effect
        mock_table.select.return_value.eq.return_value = mock_eq
        
        # Mock AI service
        mock_ai_service = Mock()
        mock_ai_service.generate_career_guidance = AsyncMock(return_value=sample_guidance)
        
        # Patch dependencies
        with patch('app.routers.internship.supabase', mock_supabase), \
             patch('ai.internship_ai.get_internship_ai', return_value=mock_ai_service):
            
            # Call endpoint
            result = await get_career_guidance(
                internship_id="internship-123",
                current_user=mock_user,
                service=mock_service
            )
            
            # Assertions - verify response structure
            assert result["success"] is True
            assert "data" in result
            assert "message" in result
            
            # Verify all required fields are present
            data = result["data"]
            assert "why_good_fit" in data
            assert "skills_to_improve" in data
            assert "certifications" in data
            assert "projects" in data
            
            # Verify field types
            assert isinstance(data["why_good_fit"], str)
            assert isinstance(data["skills_to_improve"], list)
            assert isinstance(data["certifications"], list)
            assert isinstance(data["projects"], list)
            
            # Verify lists are not empty
            assert len(data["skills_to_improve"]) > 0
            assert len(data["certifications"]) > 0
            assert len(data["projects"]) > 0
