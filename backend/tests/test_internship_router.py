"""
Tests for Internship Router API endpoints

Tests the profile management endpoints:
- POST /api/internships/profile (create/update)
- GET /api/internships/profile (retrieve)
- PATCH /api/internships/profile (partial update)
- POST /api/internships/{internship_id}/match (skill matching)
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
from fastapi import HTTPException

from app.routers.internship import (
    create_or_update_profile,
    get_profile,
    update_profile,
    calculate_skill_match,
)
from app.models.internship import (
    StudentProfile,
    StudentProfileCreate,
    StudentProfileUpdate,
    LocationPreference,
    CompensationPreference,
    SkillMatch,
    LearningPathItem,
)
from app.services.internship_service import (
    ProfileValidationError,
    ProfileNotFoundError,
    DatabaseOperationError,
)


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    return {"email": "test@example.com", "sub": "test@example.com"}


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing"""
    return StudentProfileCreate(
        graduation_year=2026,
        current_semester=4,
        degree="B.Tech",
        branch="Computer Science",
        skills=["Python", "JavaScript", "React"],
        preferred_roles=["Software Engineer", "Full Stack Developer"],
        internship_type=LocationPreference.REMOTE,
        compensation_preference=CompensationPreference.PAID,
        target_companies=["Google", "Microsoft"],
        resume_url="https://example.com/resume.pdf"
    )


@pytest.fixture
def sample_profile_response():
    """Sample profile response from service"""
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
        resume_url="https://example.com/resume.pdf",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


class TestProfileEndpoints:
    """Test suite for profile management endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_profile_success(
        self,
        mock_user,
        sample_profile_data,
        sample_profile_response
    ):
        """Test successful profile creation"""
        # Setup mocks
        mock_service = Mock()
        mock_service.create_profile = AsyncMock(return_value=sample_profile_response)
        
        # Call endpoint function directly
        result = await create_or_update_profile(
            profile=sample_profile_data,
            current_user=mock_user,
            service=mock_service
        )
        
        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["graduation_year"] == 2026
        assert result["data"]["current_semester"] == 4
        assert result["data"]["degree"] == "B.Tech"
        
        # Verify service was called correctly
        mock_service.create_profile.assert_called_once()
        call_args = mock_service.create_profile.call_args
        assert call_args[0][0] == "test@example.com"  # user_id
        assert call_args[0][1] == sample_profile_data  # profile_data
    
    @pytest.mark.asyncio
    async def test_create_profile_validation_error(
        self,
        mock_user,
        sample_profile_data
    ):
        """Test profile creation with validation error"""
        # Setup mocks
        mock_service = Mock()
        mock_service.create_profile = AsyncMock(
            side_effect=ProfileValidationError("Current semester must be between 1 and 8")
        )
        
        # Call endpoint function and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await create_or_update_profile(
                profile=sample_profile_data,
                current_user=mock_user,
                service=mock_service
            )
        
        # Assertions
        assert exc_info.value.status_code == 400
        assert "VALIDATION_ERROR" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_profile_success(
        self,
        mock_user,
        sample_profile_response
    ):
        """Test successful profile retrieval"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile_response)
        
        # Call endpoint function directly
        result = await get_profile(
            current_user=mock_user,
            service=mock_service
        )
        
        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["user_id"] == "test@example.com"
        
        # Verify service was called correctly
        mock_service.get_profile.assert_called_once_with("test@example.com")
    
    @pytest.mark.asyncio
    async def test_get_profile_not_found(
        self,
        mock_user
    ):
        """Test profile retrieval when profile doesn't exist"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=None)
        
        # Call endpoint function and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await get_profile(
                current_user=mock_user,
                service=mock_service
            )
        
        # Assertions
        assert exc_info.value.status_code == 404
        assert "PROFILE_NOT_FOUND" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_profile_success(
        self,
        mock_user,
        sample_profile_response
    ):
        """Test successful profile update"""
        # Setup mocks
        mock_service = Mock()
        
        # Create updated profile
        updated_profile = sample_profile_response.model_copy()
        updated_profile.current_semester = 5
        updated_profile.skills = ["Python", "JavaScript", "React", "Node.js"]
        
        mock_service.update_profile = AsyncMock(return_value=updated_profile)
        
        # Create update data
        update_data = StudentProfileUpdate(
            current_semester=5,
            skills=["Python", "JavaScript", "React", "Node.js"]
        )
        
        # Call endpoint function directly
        result = await update_profile(
            profile_update=update_data,
            current_user=mock_user,
            service=mock_service
        )
        
        # Assertions
        assert result["success"] is True
        assert result["data"]["current_semester"] == 5
        assert len(result["data"]["skills"]) == 4
        
        # Verify service was called correctly
        mock_service.update_profile.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_profile_not_found(
        self,
        mock_user
    ):
        """Test profile update when profile doesn't exist"""
        # Setup mocks
        mock_service = Mock()
        mock_service.update_profile = AsyncMock(
            side_effect=ProfileNotFoundError("Profile not found for user: test@example.com")
        )
        
        # Create update data
        update_data = StudentProfileUpdate(current_semester=5)
        
        # Call endpoint function and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await update_profile(
                profile_update=update_data,
                current_user=mock_user,
                service=mock_service
            )
        
        # Assertions
        assert exc_info.value.status_code == 404
        assert "PROFILE_NOT_FOUND" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_database_error_handling(
        self,
        mock_user,
        sample_profile_data
    ):
        """Test handling of database errors"""
        # Setup mocks
        mock_service = Mock()
        mock_service.create_profile = AsyncMock(
            side_effect=DatabaseOperationError("Database connection failed")
        )
        
        # Call endpoint function and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await create_or_update_profile(
                profile=sample_profile_data,
                current_user=mock_user,
                service=mock_service
            )
        
        # Assertions
        assert exc_info.value.status_code == 500
        assert "DATABASE_ERROR" in str(exc_info.value.detail)


class TestSkillMatchEndpoint:
    """Test suite for skill matching endpoint"""
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return {"email": "test@example.com", "sub": "test@example.com"}
    
    @pytest.fixture
    def sample_profile(self):
        """Sample user profile"""
        return StudentProfile(
            id="123e4567-e89b-12d3-a456-426614174000",
            user_id="test@example.com",
            graduation_year=2026,
            current_semester=4,
            degree="B.Tech",
            branch="Computer Science",
            skills=["Python", "JavaScript", "React"],
            preferred_roles=["Software Engineer"],
            internship_type=LocationPreference.REMOTE,
            compensation_preference=CompensationPreference.PAID,
            target_companies=[],
            resume_url=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_internship(self):
        """Sample internship listing"""
        return {
            "id": "internship-123",
            "title": "Software Engineering Intern",
            "company": "TechCorp",
            "required_skills": ["Python", "JavaScript", "Django", "REST API"],
            "preferred_skills": ["React", "Docker"],
            "location": "Remote",
            "stipend": "₹15,000/month"
        }
    
    @pytest.fixture
    def sample_skill_match(self):
        """Sample skill match result"""
        return SkillMatch(
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
                    resources=[
                        "Django Official Tutorial",
                        "Django for Beginners (book)",
                        "Coursera: Django for Everybody"
                    ],
                    priority="High"
                ),
                LearningPathItem(
                    skill="REST API",
                    estimated_time="3-4 weeks",
                    difficulty="Medium",
                    resources=[
                        "RESTful API Design Tutorial",
                        "Postman Learning Center",
                        "freeCodeCamp: APIs for Beginners"
                    ],
                    priority="High"
                )
            ],
            created_at=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_calculate_skill_match_success(
        self,
        mock_user,
        sample_profile,
        sample_internship,
        sample_skill_match
    ):
        """Test successful skill match calculation"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile)
        
        # Mock Supabase client
        mock_supabase = MagicMock()
        mock_internship_result = MagicMock()
        mock_internship_result.data = [sample_internship]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_internship_result
        
        # Mock skill match result
        mock_match_result = MagicMock()
        mock_match_result.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_match_result
        
        # Mock matching service
        mock_matching_service = Mock()
        mock_matching_service.create_skill_match = AsyncMock(return_value=sample_skill_match)
        
        # Patch dependencies
        with patch('app.routers.internship.supabase', mock_supabase), \
             patch('app.services.matching_service.MatchingService', return_value=mock_matching_service):
            
            # Call endpoint
            result = await calculate_skill_match(
                internship_id="internship-123",
                current_user=mock_user,
                service=mock_service
            )
            
            # Assertions
            assert result["success"] is True
            assert "data" in result
            assert result["data"]["match_percentage"] == 75
            assert len(result["data"]["matching_skills"]) == 3
            assert len(result["data"]["missing_skills"]) == 2
            assert len(result["data"]["learning_path"]) == 2
            
            # Verify service calls
            mock_service.get_profile.assert_called_once_with("test@example.com")
            mock_matching_service.create_skill_match.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_skill_match_no_profile(
        self,
        mock_user
    ):
        """Test skill match calculation when user has no profile"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=None)
        
        # Call endpoint and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await calculate_skill_match(
                internship_id="internship-123",
                current_user=mock_user,
                service=mock_service
            )
        
        # Assertions
        assert exc_info.value.status_code == 404
        assert "PROFILE_NOT_FOUND" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_calculate_skill_match_internship_not_found(
        self,
        mock_user,
        sample_profile
    ):
        """Test skill match calculation when internship doesn't exist"""
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
                await calculate_skill_match(
                    internship_id="nonexistent-123",
                    current_user=mock_user,
                    service=mock_service
                )
            
            # Assertions
            assert exc_info.value.status_code == 404
            assert "INTERNSHIP_NOT_FOUND" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_calculate_skill_match_100_percent(
        self,
        mock_user,
        sample_profile,
        sample_internship
    ):
        """Test skill match with 100% match"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile)
        
        # Modify internship to only require skills user has
        internship_with_matching_skills = sample_internship.copy()
        internship_with_matching_skills["required_skills"] = ["Python", "JavaScript"]
        internship_with_matching_skills["preferred_skills"] = ["React"]
        
        # Mock Supabase client
        mock_supabase = MagicMock()
        mock_internship_result = MagicMock()
        mock_internship_result.data = [internship_with_matching_skills]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_internship_result
        
        # Mock skill match result
        mock_match_result = MagicMock()
        mock_match_result.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_match_result
        
        # Create 100% match result
        perfect_match = SkillMatch(
            id="match-123",
            user_id="test@example.com",
            internship_id="internship-123",
            match_percentage=100,
            matching_skills=["Python", "JavaScript", "React"],
            missing_skills=[],
            learning_path=[],
            created_at=datetime.now()
        )
        
        # Mock matching service
        mock_matching_service = Mock()
        mock_matching_service.create_skill_match = AsyncMock(return_value=perfect_match)
        
        # Patch dependencies
        with patch('app.routers.internship.supabase', mock_supabase), \
             patch('app.services.matching_service.MatchingService', return_value=mock_matching_service):
            
            # Call endpoint
            result = await calculate_skill_match(
                internship_id="internship-123",
                current_user=mock_user,
                service=mock_service
            )
            
            # Assertions
            assert result["success"] is True
            assert result["data"]["match_percentage"] == 100
            assert len(result["data"]["missing_skills"]) == 0
            assert len(result["data"]["learning_path"]) == 0
    
    @pytest.mark.asyncio
    async def test_calculate_skill_match_caching(
        self,
        mock_user,
        sample_profile,
        sample_internship,
        sample_skill_match
    ):
        """Test that skill match results are cached in database"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile)
        
        # Mock Supabase client
        mock_supabase = MagicMock()
        mock_internship_result = MagicMock()
        mock_internship_result.data = [sample_internship]
        
        # Mock existing match check (no existing match)
        mock_existing_match = MagicMock()
        mock_existing_match.data = []
        
        # Mock insert result
        mock_insert_result = MagicMock()
        
        # Setup call chain
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        
        # For internship lookup
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_internship_result
        
        # For skill match check and insert
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_existing_match
        mock_table.insert.return_value.execute.return_value = mock_insert_result
        
        # Mock matching service
        mock_matching_service = Mock()
        mock_matching_service.create_skill_match = AsyncMock(return_value=sample_skill_match)
        
        # Patch dependencies
        with patch('app.routers.internship.supabase', mock_supabase), \
             patch('app.services.matching_service.MatchingService', return_value=mock_matching_service):
            
            # Call endpoint
            result = await calculate_skill_match(
                internship_id="internship-123",
                current_user=mock_user,
                service=mock_service
            )
            
            # Assertions
            assert result["success"] is True
            
            # Verify insert was called (caching)
            mock_table.insert.assert_called_once()
            insert_call_args = mock_table.insert.call_args[0][0]
            assert insert_call_args["user_id"] == "test@example.com"
            assert insert_call_args["internship_id"] == "internship-123"
            assert insert_call_args["match_percentage"] == 75




class TestCalendarEndpoint:
    """Test suite for calendar endpoint"""
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return {"email": "test@example.com", "sub": "test@example.com"}
    
    @pytest.fixture
    def sample_profile_semester_4(self):
        """Sample user profile in semester 4"""
        return StudentProfile(
            id="123e4567-e89b-12d3-a456-426614174000",
            user_id="test@example.com",
            graduation_year=2026,
            current_semester=4,
            degree="B.Tech",
            branch="Computer Science",
            skills=["Python", "JavaScript", "React"],
            preferred_roles=["Software Engineer"],
            internship_type=LocationPreference.REMOTE,
            compensation_preference=CompensationPreference.PAID,
            target_companies=[],
            resume_url=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_profile_semester_1(self):
        """Sample user profile in semester 1"""
        return StudentProfile(
            id="123e4567-e89b-12d3-a456-426614174001",
            user_id="test@example.com",
            graduation_year=2027,
            current_semester=1,
            degree="B.Tech",
            branch="Computer Science",
            skills=["Python"],
            preferred_roles=["Software Engineer"],
            internship_type=LocationPreference.REMOTE,
            compensation_preference=CompensationPreference.PAID,
            target_companies=[],
            resume_url=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_get_calendar_success_semester_4(
        self,
        mock_user,
        sample_profile_semester_4
    ):
        """Test successful calendar retrieval for semester 4"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile_semester_4)
        
        # Import endpoint function
        from app.routers.internship import get_internship_calendar
        
        # Call endpoint
        result = await get_internship_calendar(
            current_user=mock_user,
            service=mock_service
        )
        
        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["semester"] == 4
        assert result["data"]["focus"] == "Summer Internships"
        assert result["data"]["apply_window"] == "Jan-Mar"
        assert result["data"]["internship_period"] == "May-Jul"
        assert "current_status" in result["data"]
        assert "upcoming_deadlines" in result["data"]
        
        # Verify service was called correctly
        mock_service.get_profile.assert_called_once_with("test@example.com")
    
    @pytest.mark.asyncio
    async def test_get_calendar_success_semester_1(
        self,
        mock_user,
        sample_profile_semester_1
    ):
        """Test successful calendar retrieval for semester 1 (skill building)"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile_semester_1)
        
        # Import endpoint function
        from app.routers.internship import get_internship_calendar
        
        # Call endpoint
        result = await get_internship_calendar(
            current_user=mock_user,
            service=mock_service
        )
        
        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["semester"] == 1
        assert result["data"]["focus"] == "Skill Building"
        assert "skill" in result["data"]["recommendation"].lower()
        assert len(result["data"]["upcoming_deadlines"]) == 0
        
        # Verify service was called correctly
        mock_service.get_profile.assert_called_once_with("test@example.com")
    
    @pytest.mark.asyncio
    async def test_get_calendar_no_profile(
        self,
        mock_user
    ):
        """Test calendar retrieval when user has no profile"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=None)
        
        # Import endpoint function
        from app.routers.internship import get_internship_calendar
        
        # Call endpoint and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await get_internship_calendar(
                current_user=mock_user,
                service=mock_service
            )
        
        # Assertions
        assert exc_info.value.status_code == 404
        assert "PROFILE_NOT_FOUND" in str(exc_info.value.detail)
        assert "create a profile" in str(exc_info.value.detail).lower()
    
    @pytest.mark.asyncio
    async def test_get_calendar_all_semesters(
        self,
        mock_user
    ):
        """Test calendar retrieval for all semesters (1-8)"""
        # Import endpoint function
        from app.routers.internship import get_internship_calendar
        
        for semester in range(1, 9):
            # Create profile for this semester
            profile = StudentProfile(
                id=f"123e4567-e89b-12d3-a456-42661417400{semester}",
                user_id="test@example.com",
                graduation_year=2026,
                current_semester=semester,
                degree="B.Tech",
                branch="Computer Science",
                skills=["Python"],
                preferred_roles=["Software Engineer"],
                internship_type=LocationPreference.REMOTE,
                compensation_preference=CompensationPreference.PAID,
                target_companies=[],
                resume_url=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Setup mocks
            mock_service = Mock()
            mock_service.get_profile = AsyncMock(return_value=profile)
            
            # Call endpoint
            result = await get_internship_calendar(
                current_user=mock_user,
                service=mock_service
            )
            
            # Assertions
            assert result["success"] is True
            assert result["data"]["semester"] == semester
            assert "focus" in result["data"]
            assert "recommendation" in result["data"]
            assert "current_status" in result["data"]
    
    @pytest.mark.asyncio
    async def test_get_calendar_includes_deadlines(
        self,
        mock_user,
        sample_profile_semester_4
    ):
        """Test that calendar includes upcoming deadlines"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile_semester_4)
        
        # Import endpoint function
        from app.routers.internship import get_internship_calendar
        
        # Call endpoint
        result = await get_internship_calendar(
            current_user=mock_user,
            service=mock_service
        )
        
        # Assertions
        assert result["success"] is True
        assert "upcoming_deadlines" in result["data"]
        
        # For semester 4, there should be deadlines
        deadlines = result["data"]["upcoming_deadlines"]
        assert len(deadlines) > 0
        
        # Check deadline structure
        for deadline in deadlines:
            assert "type" in deadline
            assert "month" in deadline
            assert "description" in deadline
    
    @pytest.mark.asyncio
    async def test_get_calendar_database_error(
        self,
        mock_user
    ):
        """Test handling of database errors"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(
            side_effect=DatabaseOperationError("Database connection failed")
        )
        
        # Import endpoint function
        from app.routers.internship import get_internship_calendar
        
        # Call endpoint and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await get_internship_calendar(
                current_user=mock_user,
                service=mock_service
            )
        
        # Assertions
        assert exc_info.value.status_code == 500
        # The endpoint catches DatabaseOperationError as a general exception
        assert "INTERNAL_ERROR" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_calendar_response_format(
        self,
        mock_user,
        sample_profile_semester_4
    ):
        """Test that calendar response has correct format"""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_profile = AsyncMock(return_value=sample_profile_semester_4)
        
        # Import endpoint function
        from app.routers.internship import get_internship_calendar
        
        # Call endpoint
        result = await get_internship_calendar(
            current_user=mock_user,
            service=mock_service
        )
        
        # Assertions - check all required fields
        assert result["success"] is True
        data = result["data"]
        
        # Required fields
        assert "semester" in data
        assert "focus" in data
        assert "description" in data
        assert "recommendation" in data
        assert "current_status" in data
        assert "upcoming_deadlines" in data
        
        # Semester-specific fields (for semester 4)
        assert "apply_window" in data
        assert "internship_period" in data
        assert "apply_months" in data
        assert "internship_months" in data
        
        # Type checks
        assert isinstance(data["semester"], int)
        assert isinstance(data["focus"], str)
        assert isinstance(data["upcoming_deadlines"], list)
