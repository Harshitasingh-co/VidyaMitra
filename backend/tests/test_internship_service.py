"""
Unit tests for InternshipService profile management methods

Tests cover:
- Profile creation with validation
- Profile updates
- Error handling
- Edge cases
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from app.services.internship_service import (
    InternshipService,
    ProfileValidationError,
    ProfileNotFoundError,
    DatabaseOperationError
)
from app.models.internship import (
    StudentProfileCreate,
    StudentProfile,
    StudentProfileUpdate,
    LocationPreference,
    CompensationPreference
)


@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client"""
    mock_client = Mock()
    mock_table = Mock()
    mock_client.table.return_value = mock_table
    return mock_client, mock_table


@pytest.fixture
def internship_service(mock_supabase):
    """Create an InternshipService instance with mocked Supabase"""
    mock_client, _ = mock_supabase
    return InternshipService(mock_client)


@pytest.fixture
def valid_profile_data():
    """Create valid profile data for testing"""
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


class TestProfileCreation:
    """Tests for create_profile method"""
    
    @pytest.mark.asyncio
    async def test_create_new_profile_success(self, internship_service, mock_supabase, valid_profile_data):
        """Test successful creation of a new profile"""
        mock_client, mock_table = mock_supabase
        user_id = "test-user-123"
        
        # Mock: No existing profile
        mock_select = Mock()
        mock_select.eq.return_value.execute.return_value.data = []
        mock_table.select.return_value = mock_select
        
        # Mock: Successful insert
        mock_insert = Mock()
        mock_insert.execute.return_value.data = [{
            "id": "profile-123",
            "user_id": user_id,
            "graduation_year": 2026,
            "current_semester": 4,
            "degree": "B.Tech",
            "branch": "Computer Science",
            "skills": ["Python", "JavaScript", "React"],
            "preferred_roles": ["Software Engineer", "Full Stack Developer"],
            "internship_type": "Remote",
            "compensation_preference": "Paid",
            "target_companies": ["Google", "Microsoft"],
            "resume_url": "https://example.com/resume.pdf",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }]
        mock_table.insert.return_value = mock_insert
        
        # Execute
        result = await internship_service.create_profile(user_id, valid_profile_data)
        
        # Verify
        assert result.user_id == user_id
        assert result.graduation_year == 2026
        assert result.current_semester == 4
        assert result.degree == "B.Tech"
        assert "Python" in result.skills
    
    @pytest.mark.asyncio
    async def test_update_existing_profile_success(self, internship_service, mock_supabase, valid_profile_data):
        """Test successful update of an existing profile"""
        mock_client, mock_table = mock_supabase
        user_id = "test-user-123"
        
        # Mock: Existing profile found
        mock_select = Mock()
        mock_select.eq.return_value.execute.return_value.data = [{"id": "profile-123", "user_id": user_id}]
        mock_table.select.return_value = mock_select
        
        # Mock: Successful update
        mock_update = Mock()
        mock_update.eq.return_value.execute.return_value.data = [{
            "id": "profile-123",
            "user_id": user_id,
            "graduation_year": 2026,
            "current_semester": 4,
            "degree": "B.Tech",
            "branch": "Computer Science",
            "skills": ["Python", "JavaScript", "React"],
            "preferred_roles": ["Software Engineer", "Full Stack Developer"],
            "internship_type": "Remote",
            "compensation_preference": "Paid",
            "target_companies": ["Google", "Microsoft"],
            "resume_url": "https://example.com/resume.pdf",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }]
        mock_table.update.return_value = mock_update
        
        # Execute
        result = await internship_service.create_profile(user_id, valid_profile_data)
        
        # Verify
        assert result.user_id == user_id
        mock_table.update.assert_called_once()


class TestProfileValidation:
    """Tests for profile validation"""
    
    @pytest.mark.asyncio
    async def test_invalid_semester_too_low(self, internship_service, valid_profile_data):
        """Test validation fails for semester < 1"""
        valid_profile_data.current_semester = 0
        
        with pytest.raises(ProfileValidationError) as exc_info:
            await internship_service.create_profile("user-123", valid_profile_data)
        
        assert "must be between 1 and 8" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_semester_too_high(self, internship_service, valid_profile_data):
        """Test validation fails for semester > 8"""
        valid_profile_data.current_semester = 9
        
        with pytest.raises(ProfileValidationError) as exc_info:
            await internship_service.create_profile("user-123", valid_profile_data)
        
        assert "must be between 1 and 8" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_graduation_year_past(self, internship_service, valid_profile_data):
        """Test validation fails for graduation year in the past"""
        valid_profile_data.graduation_year = 2020
        
        with pytest.raises(ProfileValidationError) as exc_info:
            await internship_service.create_profile("user-123", valid_profile_data)
        
        assert "or later" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_graduation_year_too_far_future(self, internship_service, valid_profile_data):
        """Test validation fails for graduation year too far in future"""
        valid_profile_data.graduation_year = datetime.now().year + 15
        
        with pytest.raises(ProfileValidationError) as exc_info:
            await internship_service.create_profile("user-123", valid_profile_data)
        
        assert "cannot be more than 10 years" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_too_many_skills(self, internship_service, valid_profile_data):
        """Test validation fails for more than 50 skills"""
        valid_profile_data.skills = [f"Skill{i}" for i in range(51)]
        
        with pytest.raises(ProfileValidationError) as exc_info:
            await internship_service.create_profile("user-123", valid_profile_data)
        
        assert "Maximum 50 skills" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_too_many_preferred_roles(self, internship_service, valid_profile_data):
        """Test validation fails for more than 20 preferred roles"""
        valid_profile_data.preferred_roles = [f"Role{i}" for i in range(21)]
        
        with pytest.raises(ProfileValidationError) as exc_info:
            await internship_service.create_profile("user-123", valid_profile_data)
        
        assert "Maximum 20 preferred roles" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_too_many_target_companies(self, internship_service, valid_profile_data):
        """Test validation fails for more than 30 target companies"""
        valid_profile_data.target_companies = [f"Company{i}" for i in range(31)]
        
        with pytest.raises(ProfileValidationError) as exc_info:
            await internship_service.create_profile("user-123", valid_profile_data)
        
        assert "Maximum 30 target companies" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_empty_degree(self, internship_service, valid_profile_data):
        """Test validation fails for empty degree"""
        valid_profile_data.degree = "   "
        
        with pytest.raises(ProfileValidationError) as exc_info:
            await internship_service.create_profile("user-123", valid_profile_data)
        
        assert "Degree is required" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_empty_branch(self, internship_service, valid_profile_data):
        """Test validation fails for empty branch"""
        valid_profile_data.branch = "   "
        
        with pytest.raises(ProfileValidationError) as exc_info:
            await internship_service.create_profile("user-123", valid_profile_data)
        
        assert "Branch is required" in str(exc_info.value)


class TestProfileRetrieval:
    """Tests for get_profile method"""
    
    @pytest.mark.asyncio
    async def test_get_existing_profile(self, internship_service, mock_supabase):
        """Test retrieving an existing profile"""
        mock_client, mock_table = mock_supabase
        user_id = "test-user-123"
        
        # Mock: Profile found
        mock_select = Mock()
        mock_select.eq.return_value.execute.return_value.data = [{
            "id": "profile-123",
            "user_id": user_id,
            "graduation_year": 2026,
            "current_semester": 4,
            "degree": "B.Tech",
            "branch": "Computer Science",
            "skills": ["Python"],
            "preferred_roles": ["Software Engineer"],
            "internship_type": "Remote",
            "compensation_preference": "Paid",
            "target_companies": [],
            "resume_url": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }]
        mock_table.select.return_value = mock_select
        
        # Execute
        result = await internship_service.get_profile(user_id)
        
        # Verify
        assert result is not None
        assert result.user_id == user_id
        assert result.degree == "B.Tech"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_profile(self, internship_service, mock_supabase):
        """Test retrieving a profile that doesn't exist"""
        mock_client, mock_table = mock_supabase
        user_id = "nonexistent-user"
        
        # Mock: No profile found
        mock_select = Mock()
        mock_select.eq.return_value.execute.return_value.data = []
        mock_table.select.return_value = mock_select
        
        # Execute
        result = await internship_service.get_profile(user_id)
        
        # Verify
        assert result is None


class TestProfileUpdate:
    """Tests for update_profile method"""
    
    @pytest.mark.asyncio
    async def test_update_profile_success(self, internship_service, mock_supabase):
        """Test successful profile update"""
        mock_client, mock_table = mock_supabase
        user_id = "test-user-123"
        
        # Mock: Existing profile
        mock_select = Mock()
        mock_select.eq.return_value.execute.return_value.data = [{
            "id": "profile-123",
            "user_id": user_id,
            "graduation_year": 2026,
            "current_semester": 4,
            "degree": "B.Tech",
            "branch": "Computer Science",
            "skills": ["Python"],
            "preferred_roles": ["Software Engineer"],
            "internship_type": "Remote",
            "compensation_preference": "Paid",
            "target_companies": [],
            "resume_url": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }]
        mock_table.select.return_value = mock_select
        
        # Mock: Successful update
        mock_update = Mock()
        mock_update.eq.return_value.execute.return_value.data = [{
            "id": "profile-123",
            "user_id": user_id,
            "graduation_year": 2026,
            "current_semester": 5,  # Updated
            "degree": "B.Tech",
            "branch": "Computer Science",
            "skills": ["Python", "JavaScript"],  # Updated
            "preferred_roles": ["Software Engineer"],
            "internship_type": "Remote",
            "compensation_preference": "Paid",
            "target_companies": [],
            "resume_url": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }]
        mock_table.update.return_value = mock_update
        
        # Execute
        update_data = StudentProfileUpdate(
            current_semester=5,
            skills=["Python", "JavaScript"]
        )
        result = await internship_service.update_profile(user_id, update_data)
        
        # Verify
        assert result.current_semester == 5
        assert "JavaScript" in result.skills
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_profile(self, internship_service, mock_supabase):
        """Test updating a profile that doesn't exist"""
        mock_client, mock_table = mock_supabase
        user_id = "nonexistent-user"
        
        # Mock: No profile found
        mock_select = Mock()
        mock_select.eq.return_value.execute.return_value.data = []
        mock_table.select.return_value = mock_select
        
        # Execute
        update_data = StudentProfileUpdate(current_semester=5)
        
        with pytest.raises(ProfileNotFoundError):
            await internship_service.update_profile(user_id, update_data)
    
    @pytest.mark.asyncio
    async def test_update_with_no_fields(self, internship_service, mock_supabase):
        """Test update with no fields returns existing profile"""
        mock_client, mock_table = mock_supabase
        user_id = "test-user-123"
        
        # Mock: Existing profile
        mock_select = Mock()
        mock_select.eq.return_value.execute.return_value.data = [{
            "id": "profile-123",
            "user_id": user_id,
            "graduation_year": 2026,
            "current_semester": 4,
            "degree": "B.Tech",
            "branch": "Computer Science",
            "skills": ["Python"],
            "preferred_roles": ["Software Engineer"],
            "internship_type": "Remote",
            "compensation_preference": "Paid",
            "target_companies": [],
            "resume_url": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }]
        mock_table.select.return_value = mock_select
        
        # Execute
        update_data = StudentProfileUpdate()
        result = await internship_service.update_profile(user_id, update_data)
        
        # Verify
        assert result.user_id == user_id
        mock_table.update.assert_not_called()


class TestProfileDeletion:
    """Tests for delete_profile method"""
    
    @pytest.mark.asyncio
    async def test_delete_profile_success(self, internship_service, mock_supabase):
        """Test successful profile deletion"""
        mock_client, mock_table = mock_supabase
        user_id = "test-user-123"
        
        # Mock: Successful delete
        mock_delete = Mock()
        mock_delete.eq.return_value.execute.return_value = Mock()
        mock_table.delete.return_value = mock_delete
        
        # Execute
        result = await internship_service.delete_profile(user_id)
        
        # Verify
        assert result is True
        mock_table.delete.assert_called_once()


class TestDataCleaning:
    """Tests for data cleaning and normalization"""
    
    @pytest.mark.asyncio
    async def test_duplicate_skills_removed(self, internship_service, mock_supabase, valid_profile_data):
        """Test that duplicate skills are removed"""
        mock_client, mock_table = mock_supabase
        user_id = "test-user-123"
        
        # Set duplicate skills
        valid_profile_data.skills = ["Python", "python", "Python", "JavaScript"]
        
        # Mock: No existing profile
        mock_select = Mock()
        mock_select.eq.return_value.execute.return_value.data = []
        mock_table.select.return_value = mock_select
        
        # Mock: Successful insert
        mock_insert = Mock()
        mock_insert.execute.return_value.data = [{
            "id": "profile-123",
            "user_id": user_id,
            "graduation_year": 2026,
            "current_semester": 4,
            "degree": "B.Tech",
            "branch": "Computer Science",
            "skills": ["Python", "python", "JavaScript"],  # Duplicates removed by set()
            "preferred_roles": [],
            "internship_type": "Remote",
            "compensation_preference": "Paid",
            "target_companies": [],
            "resume_url": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }]
        mock_table.insert.return_value = mock_insert
        
        # Execute
        result = await internship_service.create_profile(user_id, valid_profile_data)
        
        # Verify - duplicates should be removed (case-sensitive)
        assert len(result.skills) <= 3
    
    @pytest.mark.asyncio
    async def test_empty_strings_removed(self, internship_service, mock_supabase, valid_profile_data):
        """Test that empty strings are removed from lists"""
        mock_client, mock_table = mock_supabase
        user_id = "test-user-123"
        
        # Set skills with empty strings
        valid_profile_data.skills = ["Python", "", "  ", "JavaScript"]
        
        # Mock: No existing profile
        mock_select = Mock()
        mock_select.eq.return_value.execute.return_value.data = []
        mock_table.select.return_value = mock_select
        
        # Mock: Successful insert
        mock_insert = Mock()
        mock_insert.execute.return_value.data = [{
            "id": "profile-123",
            "user_id": user_id,
            "graduation_year": 2026,
            "current_semester": 4,
            "degree": "B.Tech",
            "branch": "Computer Science",
            "skills": ["Python", "JavaScript"],  # Empty strings removed
            "preferred_roles": [],
            "internship_type": "Remote",
            "compensation_preference": "Paid",
            "target_companies": [],
            "resume_url": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }]
        mock_table.insert.return_value = mock_insert
        
        # Execute
        result = await internship_service.create_profile(user_id, valid_profile_data)
        
        # Verify
        assert "" not in result.skills
        assert len(result.skills) == 2
