"""
Property-based test for Profile Data Round-Trip

This test validates Property 1: Profile Data Round-Trip
For any valid student profile data, storing the profile and then retrieving it
should return equivalent data with all fields preserved.

Validates: Requirements 1.1, 1.3, 1.4, 1.6, 1.7, 1.8, 1.9
"""
import pytest
import os
import uuid
from hypothesis import given, strategies as st, settings, assume
from typing import List
from supabase import create_client, Client

from app.models.internship import (
    StudentProfileCreate,
    StudentProfile,
    LocationPreference,
    CompensationPreference,
)
from app.services.internship_service import InternshipService


# ============================================================================
# Hypothesis Strategies for generating test data
# ============================================================================

# Strategy for valid graduation years (2024-2035)
graduation_year_strategy = st.integers(min_value=2024, max_value=2035)

# Strategy for valid semesters (1-8)
valid_semester_strategy = st.integers(min_value=1, max_value=8)

# Strategy for degree names
degree_strategy = st.sampled_from(["B.Tech", "M.Tech", "BCA", "MCA", "B.Sc", "M.Sc"])

# Strategy for branch names
branch_strategy = st.sampled_from([
    "Computer Science",
    "Information Technology",
    "Electronics",
    "Mechanical",
    "Civil",
    "Data Science"
])

# Strategy for skills (list of strings)
skills_strategy = st.lists(
    st.sampled_from([
        "Python", "Java", "JavaScript", "C++", "SQL", "React", "Node.js",
        "Django", "Flask", "AWS", "Docker", "Kubernetes", "Git"
    ]),
    min_size=0,
    max_size=10,
    unique=True
)

# Strategy for roles
roles_strategy = st.lists(
    st.sampled_from([
        "Software Engineer", "Data Analyst", "Data Scientist",
        "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "DevOps Engineer", "ML Engineer"
    ]),
    min_size=0,
    max_size=5,
    unique=True
)

# Strategy for company names
companies_strategy = st.lists(
    st.sampled_from([
        "Google", "Microsoft", "Amazon", "Apple", "Meta",
        "Netflix", "Tesla", "Adobe", "Salesforce"
    ]),
    min_size=0,
    max_size=5,
    unique=True
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def supabase_client():
    """
    Create a Supabase client for testing
    
    Note: This requires SUPABASE_URL and SUPABASE_KEY to be set in environment
    If not available, tests will be skipped
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key or \
       supabase_url.startswith('your-') or supabase_key.startswith('your-'):
        pytest.skip("Supabase credentials not configured for testing")
    
    client = create_client(supabase_url, supabase_key)
    return client


@pytest.fixture
def internship_service(supabase_client):
    """Create an internship service instance"""
    return InternshipService(supabase_client)


@pytest.fixture
def test_user_id():
    """Generate a unique test user ID for each test"""
    return str(uuid.uuid4())


@pytest.fixture
async def cleanup_profile(supabase_client, test_user_id):
    """Cleanup fixture to remove test data after each test"""
    yield
    # Cleanup: Delete the test profile after the test
    try:
        supabase_client.table('student_profiles').delete().eq('user_id', test_user_id).execute()
    except Exception:
        pass  # Ignore cleanup errors


# ============================================================================
# Property 1: Profile Data Round-Trip
# Feature: internship-discovery, Property 1: Profile Data Round-Trip
# Validates: Requirements 1.1, 1.3, 1.4, 1.6, 1.7, 1.8, 1.9
# ============================================================================

@pytest.mark.property
@pytest.mark.internship
@pytest.mark.asyncio
@settings(max_examples=100, deadline=None)
@given(
    graduation_year=graduation_year_strategy,
    current_semester=valid_semester_strategy,
    degree=degree_strategy,
    branch=branch_strategy,
    skills=skills_strategy,
    preferred_roles=roles_strategy,
    internship_type=st.sampled_from([e.value for e in LocationPreference]),
    compensation_preference=st.sampled_from([e.value for e in CompensationPreference]),
    target_companies=companies_strategy,
    resume_url=st.one_of(st.none(), st.just("https://example.com/resume.pdf"))
)
async def test_profile_data_round_trip_database(
    graduation_year: int,
    current_semester: int,
    degree: str,
    branch: str,
    skills: List[str],
    preferred_roles: List[str],
    internship_type: str,
    compensation_preference: str,
    target_companies: List[str],
    resume_url: str,
    internship_service,
    test_user_id,
    cleanup_profile
):
    """
    Property 1: Profile Data Round-Trip (Database)
    
    For any valid student profile data (graduation year, semester, degree, branch,
    skills, roles, preferences), storing the profile in the database and then
    retrieving it should return equivalent data with all fields preserved.
    
    This validates that:
    - All required fields are stored and retrieved correctly (Requirements 1.1, 1.3)
    - Skills are preserved (Requirement 1.4)
    - Preferred roles are preserved (Requirement 1.6)
    - Internship type preference is preserved (Requirement 1.7)
    - Compensation preference is preserved (Requirement 1.8)
    - Target companies are preserved (Requirement 1.9)
    """
    # Create profile data
    profile_data = StudentProfileCreate(
        graduation_year=graduation_year,
        current_semester=current_semester,
        degree=degree,
        branch=branch,
        skills=skills,
        preferred_roles=preferred_roles,
        internship_type=internship_type,
        compensation_preference=compensation_preference,
        target_companies=target_companies,
        resume_url=resume_url
    )
    
    # Store the profile in the database
    created_profile = await internship_service.create_profile(test_user_id, profile_data)
    
    # Verify the created profile has all fields
    assert created_profile is not None
    assert created_profile.user_id == test_user_id
    assert created_profile.graduation_year == graduation_year
    assert created_profile.current_semester == current_semester
    assert created_profile.degree == degree
    assert created_profile.branch == branch
    assert created_profile.skills == skills
    assert created_profile.preferred_roles == preferred_roles
    
    # Handle enum comparison
    if internship_type:
        assert created_profile.internship_type == internship_type or \
               (hasattr(created_profile.internship_type, 'value') and 
                created_profile.internship_type.value == internship_type)
    else:
        assert created_profile.internship_type is None
    
    if compensation_preference:
        assert created_profile.compensation_preference == compensation_preference or \
               (hasattr(created_profile.compensation_preference, 'value') and 
                created_profile.compensation_preference.value == compensation_preference)
    else:
        assert created_profile.compensation_preference is None
    
    assert created_profile.target_companies == target_companies
    assert created_profile.resume_url == resume_url
    
    # Retrieve the profile from the database
    retrieved_profile = await internship_service.get_profile(test_user_id)
    
    # Verify the retrieved profile matches the original data
    assert retrieved_profile is not None
    assert retrieved_profile.user_id == test_user_id
    assert retrieved_profile.graduation_year == graduation_year
    assert retrieved_profile.current_semester == current_semester
    assert retrieved_profile.degree == degree
    assert retrieved_profile.branch == branch
    assert retrieved_profile.skills == skills
    assert retrieved_profile.preferred_roles == preferred_roles
    
    # Handle enum comparison for retrieved profile
    if internship_type:
        assert retrieved_profile.internship_type == internship_type or \
               (hasattr(retrieved_profile.internship_type, 'value') and 
                retrieved_profile.internship_type.value == internship_type)
    else:
        assert retrieved_profile.internship_type is None
    
    if compensation_preference:
        assert retrieved_profile.compensation_preference == compensation_preference or \
               (hasattr(retrieved_profile.compensation_preference, 'value') and 
                retrieved_profile.compensation_preference.value == compensation_preference)
    else:
        assert retrieved_profile.compensation_preference is None
    
    assert retrieved_profile.target_companies == target_companies
    assert retrieved_profile.resume_url == resume_url
    
    # Verify that created and retrieved profiles are equivalent
    assert created_profile.graduation_year == retrieved_profile.graduation_year
    assert created_profile.current_semester == retrieved_profile.current_semester
    assert created_profile.degree == retrieved_profile.degree
    assert created_profile.branch == retrieved_profile.branch
    assert created_profile.skills == retrieved_profile.skills
    assert created_profile.preferred_roles == retrieved_profile.preferred_roles
    assert created_profile.target_companies == retrieved_profile.target_companies
    assert created_profile.resume_url == retrieved_profile.resume_url


# ============================================================================
# Additional Unit Tests for Round-Trip Edge Cases
# ============================================================================

@pytest.mark.unit
@pytest.mark.internship
@pytest.mark.asyncio
async def test_profile_round_trip_with_empty_lists(internship_service, test_user_id, cleanup_profile):
    """Test round-trip with empty optional list fields"""
    profile_data = StudentProfileCreate(
        graduation_year=2026,
        current_semester=4,
        degree="B.Tech",
        branch="Computer Science",
        skills=[],
        preferred_roles=[],
        target_companies=[],
        internship_type=None,
        compensation_preference=None,
        resume_url=None
    )
    
    # Store and retrieve
    created = await internship_service.create_profile(test_user_id, profile_data)
    retrieved = await internship_service.get_profile(test_user_id)
    
    # Verify empty lists are preserved
    assert retrieved.skills == []
    assert retrieved.preferred_roles == []
    assert retrieved.target_companies == []
    assert retrieved.internship_type is None
    assert retrieved.compensation_preference is None
    assert retrieved.resume_url is None


@pytest.mark.unit
@pytest.mark.internship
@pytest.mark.asyncio
async def test_profile_round_trip_with_all_fields(internship_service, test_user_id, cleanup_profile):
    """Test round-trip with all fields populated"""
    profile_data = StudentProfileCreate(
        graduation_year=2026,
        current_semester=4,
        degree="B.Tech",
        branch="Computer Science",
        skills=["Python", "SQL", "React"],
        preferred_roles=["Software Engineer", "Data Analyst"],
        internship_type="Remote",
        compensation_preference="Paid",
        target_companies=["Google", "Microsoft"],
        resume_url="https://example.com/resume.pdf"
    )
    
    # Store and retrieve
    created = await internship_service.create_profile(test_user_id, profile_data)
    retrieved = await internship_service.get_profile(test_user_id)
    
    # Verify all fields are preserved
    assert retrieved.graduation_year == 2026
    assert retrieved.current_semester == 4
    assert retrieved.degree == "B.Tech"
    assert retrieved.branch == "Computer Science"
    assert retrieved.skills == ["Python", "SQL", "React"]
    assert retrieved.preferred_roles == ["Software Engineer", "Data Analyst"]
    assert retrieved.target_companies == ["Google", "Microsoft"]
    assert retrieved.resume_url == "https://example.com/resume.pdf"


@pytest.mark.unit
@pytest.mark.internship
@pytest.mark.asyncio
async def test_profile_update_preserves_unchanged_fields(internship_service, test_user_id, cleanup_profile):
    """Test that updating a profile preserves fields that weren't changed"""
    # Create initial profile
    initial_data = StudentProfileCreate(
        graduation_year=2026,
        current_semester=4,
        degree="B.Tech",
        branch="Computer Science",
        skills=["Python", "SQL"],
        preferred_roles=["Software Engineer"],
        internship_type="Remote",
        compensation_preference="Paid",
        target_companies=["Google"],
        resume_url="https://example.com/resume.pdf"
    )
    
    created = await internship_service.create_profile(test_user_id, initial_data)
    
    # Update only the skills
    from app.models.internship import StudentProfileUpdate
    update_data = StudentProfileUpdate(
        skills=["Python", "SQL", "JavaScript"]
    )
    
    updated = await internship_service.update_profile(test_user_id, update_data)
    
    # Verify skills were updated
    assert updated.skills == ["Python", "SQL", "JavaScript"]
    
    # Verify other fields were preserved
    assert updated.graduation_year == 2026
    assert updated.current_semester == 4
    assert updated.degree == "B.Tech"
    assert updated.branch == "Computer Science"
    assert updated.preferred_roles == ["Software Engineer"]
    assert updated.target_companies == ["Google"]
    assert updated.resume_url == "https://example.com/resume.pdf"


@pytest.mark.unit
@pytest.mark.internship
@pytest.mark.asyncio
async def test_profile_not_found(internship_service):
    """Test retrieving a non-existent profile returns None"""
    non_existent_user_id = str(uuid.uuid4())
    profile = await internship_service.get_profile(non_existent_user_id)
    assert profile is None
