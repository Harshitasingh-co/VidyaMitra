"""
Property-based tests for Internship Discovery models

These tests validate universal properties that should hold for all valid inputs.
Uses Hypothesis for property-based testing with minimum 100 iterations per test.

Note: These tests validate the Pydantic model layer (serialization/deserialization).
For database-level round-trip tests, see test_profile_round_trip.py which requires
Supabase credentials to be configured.
"""
import pytest
from hypothesis import given, strategies as st, assume
from datetime import date, datetime
from typing import List

from app.models.internship import (
    StudentProfileCreate,
    StudentProfile,
    InternshipType,
    LocationPreference,
    CompensationPreference,
    VerificationStatus,
    RedFlagSeverity,
)


# ============================================================================
# Hypothesis Strategies for generating test data
# ============================================================================

# Strategy for valid graduation years (2024-2035)
graduation_year_strategy = st.integers(min_value=2024, max_value=2035)

# Strategy for valid semesters (1-8)
valid_semester_strategy = st.integers(min_value=1, max_value=8)

# Strategy for invalid semesters (outside 1-8 range)
invalid_semester_strategy = st.one_of(
    st.integers(max_value=0),
    st.integers(min_value=9)
)

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
# Property 1: Profile Data Round-Trip
# Feature: internship-discovery, Property 1: Profile Data Round-Trip
# Validates: Requirements 1.1, 1.3, 1.4, 1.6, 1.7, 1.8, 1.9
# ============================================================================

@pytest.mark.property
@pytest.mark.internship
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
def test_profile_data_round_trip(
    graduation_year: int,
    current_semester: int,
    degree: str,
    branch: str,
    skills: List[str],
    preferred_roles: List[str],
    internship_type: str,
    compensation_preference: str,
    target_companies: List[str],
    resume_url: str
):
    """
    Property 1: Profile Data Round-Trip (Model Layer)
    
    For any valid student profile data (graduation year, semester, degree, branch,
    skills, roles, preferences), creating a profile model and serializing/deserializing
    it should preserve all fields with equivalent data.
    
    This validates the Pydantic model layer:
    - All required fields are accepted (Requirements 1.1, 1.3)
    - Skills are preserved (Requirement 1.4)
    - Preferred roles are preserved (Requirement 1.6)
    - Internship type preference is preserved (Requirement 1.7)
    - Compensation preference is preserved (Requirement 1.8)
    - Target companies are preserved (Requirement 1.9)
    
    Note: For database-level round-trip testing (actual storage and retrieval),
    see test_profile_round_trip.py which requires Supabase configuration.
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
    
    # Verify all fields are preserved
    assert profile_data.graduation_year == graduation_year
    assert profile_data.current_semester == current_semester
    assert profile_data.degree == degree
    assert profile_data.branch == branch
    assert profile_data.skills == skills
    assert profile_data.preferred_roles == preferred_roles
    assert profile_data.internship_type == internship_type
    assert profile_data.compensation_preference == compensation_preference
    assert profile_data.target_companies == target_companies
    assert profile_data.resume_url == resume_url
    
    # Verify the model can be serialized and deserialized
    profile_dict = profile_data.model_dump()
    reconstructed = StudentProfileCreate(**profile_dict)
    
    # Verify reconstructed profile matches original
    assert reconstructed.graduation_year == graduation_year
    assert reconstructed.current_semester == current_semester
    assert reconstructed.degree == degree
    assert reconstructed.branch == branch
    assert reconstructed.skills == skills
    assert reconstructed.preferred_roles == preferred_roles
    assert reconstructed.internship_type == internship_type
    assert reconstructed.compensation_preference == compensation_preference
    assert reconstructed.target_companies == target_companies
    assert reconstructed.resume_url == resume_url


# ============================================================================
# Property 2: Semester Validation
# Feature: internship-discovery, Property 2: Semester Validation
# Validates: Requirements 1.2
# ============================================================================

@pytest.mark.property
@pytest.mark.internship
@given(semester=st.integers())
def test_semester_validation_property(semester: int):
    """
    Property 2: Semester Validation
    
    For any semester value, the system should accept values between 1 and 8
    (inclusive) and reject all other values, maintaining data integrity.
    
    This validates Requirement 1.2: Student can select current semester (1-8)
    """
    # Create minimal valid profile data
    profile_data = {
        "graduation_year": 2026,
        "current_semester": semester,
        "degree": "B.Tech",
        "branch": "Computer Science",
        "skills": ["Python"],
        "preferred_roles": ["Software Engineer"],
    }
    
    if 1 <= semester <= 8:
        # Valid semester: should accept
        try:
            profile = StudentProfileCreate(**profile_data)
            assert profile.current_semester == semester
            # Validation should pass
            assert True
        except Exception as e:
            pytest.fail(f"Valid semester {semester} was rejected: {e}")
    else:
        # Invalid semester: should reject
        with pytest.raises(Exception) as exc_info:
            profile = StudentProfileCreate(**profile_data)
        
        # Verify the error is related to validation
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in [
            "validation", "greater", "less", "between", "range", "semester"
        ]), f"Expected validation error for semester {semester}, got: {exc_info.value}"


# ============================================================================
# Additional Unit Tests for Edge Cases
# ============================================================================

@pytest.mark.unit
@pytest.mark.internship
def test_semester_boundary_values():
    """Test semester validation at boundary values"""
    # Test lower boundary (1)
    profile_data = {
        "graduation_year": 2026,
        "current_semester": 1,
        "degree": "B.Tech",
        "branch": "Computer Science",
        "skills": [],
        "preferred_roles": [],
    }
    profile = StudentProfileCreate(**profile_data)
    assert profile.current_semester == 1
    
    # Test upper boundary (8)
    profile_data["current_semester"] = 8
    profile = StudentProfileCreate(**profile_data)
    assert profile.current_semester == 8
    
    # Test just below lower boundary (0)
    profile_data["current_semester"] = 0
    with pytest.raises(Exception):
        StudentProfileCreate(**profile_data)
    
    # Test just above upper boundary (9)
    profile_data["current_semester"] = 9
    with pytest.raises(Exception):
        StudentProfileCreate(**profile_data)


@pytest.mark.unit
@pytest.mark.internship
def test_graduation_year_validation():
    """Test graduation year validation"""
    profile_data = {
        "graduation_year": 2026,
        "current_semester": 4,
        "degree": "B.Tech",
        "branch": "Computer Science",
        "skills": [],
        "preferred_roles": [],
    }
    
    # Valid year
    profile = StudentProfileCreate(**profile_data)
    assert profile.graduation_year == 2026
    
    # Year too early (before 2024)
    profile_data["graduation_year"] = 2023
    with pytest.raises(Exception):
        StudentProfileCreate(**profile_data)
    
    # Year too late (after 2035)
    profile_data["graduation_year"] = 2036
    with pytest.raises(Exception):
        StudentProfileCreate(**profile_data)


@pytest.mark.unit
@pytest.mark.internship
def test_empty_optional_fields():
    """Test that optional fields can be empty or None"""
    profile_data = {
        "graduation_year": 2026,
        "current_semester": 4,
        "degree": "B.Tech",
        "branch": "Computer Science",
        "skills": [],
        "preferred_roles": [],
        "internship_type": None,
        "compensation_preference": None,
        "target_companies": [],
        "resume_url": None
    }
    
    profile = StudentProfileCreate(**profile_data)
    assert profile.skills == []
    assert profile.preferred_roles == []
    assert profile.internship_type is None
    assert profile.compensation_preference is None
    assert profile.target_companies == []
    assert profile.resume_url is None


@pytest.mark.unit
@pytest.mark.internship
def test_enum_validation():
    """Test that enum fields only accept valid values"""
    profile_data = {
        "graduation_year": 2026,
        "current_semester": 4,
        "degree": "B.Tech",
        "branch": "Computer Science",
        "skills": [],
        "preferred_roles": [],
    }
    
    # Valid internship type
    profile_data["internship_type"] = "Remote"
    profile = StudentProfileCreate(**profile_data)
    assert profile.internship_type == "Remote"
    
    # Invalid internship type
    profile_data["internship_type"] = "InvalidType"
    with pytest.raises(Exception):
        StudentProfileCreate(**profile_data)
    
    # Valid compensation preference
    profile_data["internship_type"] = "Remote"
    profile_data["compensation_preference"] = "Paid"
    profile = StudentProfileCreate(**profile_data)
    assert profile.compensation_preference == "Paid"
    
    # Invalid compensation preference
    profile_data["compensation_preference"] = "InvalidPreference"
    with pytest.raises(Exception):
        StudentProfileCreate(**profile_data)


@pytest.mark.unit
@pytest.mark.internship
def test_required_fields_validation():
    """Test that required fields cannot be missing"""
    # Missing graduation_year
    with pytest.raises(Exception):
        StudentProfileCreate(
            current_semester=4,
            degree="B.Tech",
            branch="Computer Science",
            skills=[],
            preferred_roles=[]
        )
    
    # Missing current_semester
    with pytest.raises(Exception):
        StudentProfileCreate(
            graduation_year=2026,
            degree="B.Tech",
            branch="Computer Science",
            skills=[],
            preferred_roles=[]
        )
    
    # Missing degree
    with pytest.raises(Exception):
        StudentProfileCreate(
            graduation_year=2026,
            current_semester=4,
            branch="Computer Science",
            skills=[],
            preferred_roles=[]
        )
    
    # Missing branch
    with pytest.raises(Exception):
        StudentProfileCreate(
            graduation_year=2026,
            current_semester=4,
            degree="B.Tech",
            skills=[],
            preferred_roles=[]
        )
