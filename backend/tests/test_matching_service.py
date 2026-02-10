"""
Unit tests for MatchingService

Tests cover:
- Skill match calculation with various scenarios
- Learning path generation
- Internship ranking
- Edge cases and error handling
- Property-based tests for universal correctness properties
"""

import pytest
from unittest.mock import Mock
from datetime import datetime
import uuid
from hypothesis import given, strategies as st, settings
from app.services.matching_service import MatchingService
from app.models.internship import (
    StudentProfile,
    InternshipListing,
    InternshipType,
    VerificationStatus,
    LocationPreference,
    CompensationPreference,
    LearningPathItem,
    SkillMatch
)


@pytest.fixture
def matching_service():
    """Create a MatchingService instance"""
    return MatchingService()


@pytest.fixture
def sample_user_profile():
    """Create a sample user profile for testing"""
    return StudentProfile(
        id="profile-123",
        user_id="user-123",
        graduation_year=2026,
        current_semester=4,
        degree="B.Tech",
        branch="Computer Science",
        skills=["Python", "JavaScript", "React", "SQL"],
        preferred_roles=["Software Engineer", "Full Stack Developer"],
        internship_type=LocationPreference.REMOTE,
        compensation_preference=CompensationPreference.PAID,
        target_companies=["Google", "Microsoft"],
        resume_url="https://example.com/resume.pdf",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def sample_internship():
    """Create a sample internship listing for testing"""
    return InternshipListing(
        id="internship-123",
        title="Software Engineering Intern",
        company="TechCorp",
        company_domain="techcorp.com",
        platform="Internshala",
        location="Remote",
        internship_type=InternshipType.SUMMER,
        duration="2-3 months",
        stipend="₹15,000/month",
        required_skills=["Python", "Django", "REST API"],
        preferred_skills=["React", "PostgreSQL"],
        responsibilities=["Build APIs", "Write tests"],
        verification_status=VerificationStatus.VERIFIED,
        trust_score=85,
        red_flags=[],
        posted_date=datetime.now().date(),
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


class TestSkillMatchCalculation:
    """Tests for calculate_skill_match method"""
    
    @pytest.mark.asyncio
    async def test_100_percent_match(self, matching_service):
        """Test 100% skill match when user has all required skills"""
        user_skills = ["Python", "Django", "REST API"]
        required_skills = ["Python", "Django", "REST API"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        assert result["match_percentage"] == 100
        assert len(result["matching_skills"]) == 3
        assert len(result["missing_skills"]) == 0
        assert set(result["matching_skills"]) == set(required_skills)
    
    @pytest.mark.asyncio
    async def test_0_percent_match(self, matching_service):
        """Test 0% skill match when user has no required skills"""
        user_skills = ["Java", "Spring", "Hibernate"]
        required_skills = ["Python", "Django", "REST API"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        assert result["match_percentage"] == 0
        assert len(result["matching_skills"]) == 0
        assert len(result["missing_skills"]) == 3
        assert set(result["missing_skills"]) == set(required_skills)
    
    @pytest.mark.asyncio
    async def test_partial_match(self, matching_service):
        """Test partial skill match"""
        user_skills = ["Python", "JavaScript", "React"]
        required_skills = ["Python", "Django", "REST API"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # 1 out of 3 required skills = 33%
        assert result["match_percentage"] == 33
        assert "Python" in result["matching_skills"]
        assert "Django" in result["missing_skills"]
        assert "REST API" in result["missing_skills"]
    
    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self, matching_service):
        """Test that skill matching is case-insensitive"""
        user_skills = ["python", "JAVASCRIPT", "React"]
        required_skills = ["Python", "JavaScript", "react"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        assert result["match_percentage"] == 100
        assert len(result["matching_skills"]) == 3
    
    @pytest.mark.asyncio
    async def test_with_preferred_skills(self, matching_service):
        """Test skill matching with both required and preferred skills"""
        user_skills = ["Python", "Django", "React", "PostgreSQL"]
        required_skills = ["Python", "Django"]
        preferred_skills = ["React", "PostgreSQL"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills
        )
        
        # 100% required (2/2) * 0.7 + 100% preferred (2/2) * 0.3 = 100%
        assert result["match_percentage"] == 100
        assert len(result["matching_skills"]) == 4
        assert len(result["missing_skills"]) == 0
    
    @pytest.mark.asyncio
    async def test_partial_required_full_preferred(self, matching_service):
        """Test partial required match with full preferred match"""
        user_skills = ["Python", "React", "PostgreSQL"]
        required_skills = ["Python", "Django"]
        preferred_skills = ["React", "PostgreSQL"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills
        )
        
        # 50% required (1/2) * 0.7 + 100% preferred (2/2) * 0.3 = 35 + 30 = 65%
        assert result["match_percentage"] == 65
        assert "Python" in result["matching_skills"]
        assert "Django" in result["missing_skills"]
    
    @pytest.mark.asyncio
    async def test_empty_user_skills(self, matching_service):
        """Test with empty user skills list"""
        user_skills = []
        required_skills = ["Python", "Django", "REST API"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        assert result["match_percentage"] == 0
        assert len(result["matching_skills"]) == 0
        assert len(result["missing_skills"]) == 3
    
    @pytest.mark.asyncio
    async def test_empty_required_skills(self, matching_service):
        """Test with empty required skills list"""
        user_skills = ["Python", "Django", "REST API"]
        required_skills = []
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        assert result["match_percentage"] == 100
        assert len(result["matching_skills"]) == 0
        assert len(result["missing_skills"]) == 0
    
    @pytest.mark.asyncio
    async def test_whitespace_handling(self, matching_service):
        """Test that whitespace is properly handled"""
        user_skills = ["  Python  ", "Django", "REST API  "]
        required_skills = ["Python", "  Django  ", "REST API"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        assert result["match_percentage"] == 100
        assert len(result["matching_skills"]) == 3


class TestLearningPathGeneration:
    """Tests for generate_learning_path method"""
    
    @pytest.mark.asyncio
    async def test_generate_learning_path_basic(self, matching_service):
        """Test basic learning path generation"""
        missing_skills = ["Django", "REST API"]
        
        learning_path = await matching_service.generate_learning_path(missing_skills)
        
        assert len(learning_path) == 2
        assert all(isinstance(item, LearningPathItem) for item in learning_path)
        assert learning_path[0].skill in missing_skills
        assert learning_path[1].skill in missing_skills
    
    @pytest.mark.asyncio
    async def test_learning_path_has_resources(self, matching_service):
        """Test that learning path items have resources"""
        missing_skills = ["Python", "Django"]
        
        learning_path = await matching_service.generate_learning_path(missing_skills)
        
        for item in learning_path:
            assert len(item.resources) > 0
            assert item.estimated_time is not None
            assert item.difficulty in ["Easy", "Medium", "Hard"]
            assert item.priority in ["High", "Medium", "Low"]
    
    @pytest.mark.asyncio
    async def test_learning_path_prioritization(self, matching_service):
        """Test that required skills get high priority"""
        missing_skills = ["Django", "React"]
        required_skills = ["Django", "Python"]
        
        learning_path = await matching_service.generate_learning_path(
            missing_skills=missing_skills,
            required_skills=required_skills
        )
        
        # Django is required, so it should have high priority
        django_item = next(item for item in learning_path if item.skill == "Django")
        assert django_item.priority == "High"
        
        # React is not required, so it should have medium priority
        react_item = next(item for item in learning_path if item.skill == "React")
        assert react_item.priority == "Medium"
    
    @pytest.mark.asyncio
    async def test_learning_path_sorted_by_priority(self, matching_service):
        """Test that learning path is sorted by priority"""
        missing_skills = ["React", "Django", "AWS"]
        required_skills = ["Django"]
        
        learning_path = await matching_service.generate_learning_path(
            missing_skills=missing_skills,
            required_skills=required_skills
        )
        
        # High priority items should come first
        priorities = [item.priority for item in learning_path]
        # Django (High) should come before React and AWS (Medium)
        assert priorities[0] == "High"
    
    @pytest.mark.asyncio
    async def test_empty_missing_skills(self, matching_service):
        """Test with empty missing skills list"""
        missing_skills = []
        
        learning_path = await matching_service.generate_learning_path(missing_skills)
        
        assert len(learning_path) == 0
    
    @pytest.mark.asyncio
    async def test_unknown_skill_gets_default_resources(self, matching_service):
        """Test that unknown skills get default resources"""
        missing_skills = ["XYZ_UnknownTech_9999"]
        
        learning_path = await matching_service.generate_learning_path(missing_skills)
        
        assert len(learning_path) == 1
        assert len(learning_path[0].resources) > 0
        # Should get default resources (check if any default resource is present)
        default_keywords = ["Coursera", "Udemy", "YouTube", "Official documentation"]
        assert any(keyword in resource for resource in learning_path[0].resources for keyword in default_keywords)


class TestInternshipRanking:
    """Tests for rank_internships method"""
    
    @pytest.mark.asyncio
    async def test_rank_internships_by_match_score(self, matching_service, sample_user_profile):
        """Test that internships are ranked by match score"""
        # Create internships with different skill requirements
        internship1 = InternshipListing(
            id="int-1",
            title="Python Developer",
            company="Company A",
            location="Remote",
            internship_type=InternshipType.SUMMER,
            duration="3 months",
            stipend="₹20,000",
            required_skills=["Python", "JavaScript"],  # 2/2 match
            preferred_skills=[],
            responsibilities=["Develop"],
            verification_status=VerificationStatus.VERIFIED,
            trust_score=85,
            red_flags=[],
            posted_date=datetime.now().date(),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        internship2 = InternshipListing(
            id="int-2",
            title="Full Stack Developer",
            company="Company B",
            location="Remote",
            internship_type=InternshipType.SUMMER,
            duration="3 months",
            stipend="₹25,000",
            required_skills=["Python", "Django", "PostgreSQL"],  # 1/3 match
            preferred_skills=[],
            responsibilities=["Develop"],
            verification_status=VerificationStatus.VERIFIED,
            trust_score=85,
            red_flags=[],
            posted_date=datetime.now().date(),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        internship3 = InternshipListing(
            id="int-3",
            title="React Developer",
            company="Company C",
            location="Remote",
            internship_type=InternshipType.SUMMER,
            duration="3 months",
            stipend="₹22,000",
            required_skills=["React", "JavaScript"],  # 2/2 match
            preferred_skills=[],
            responsibilities=["Develop"],
            verification_status=VerificationStatus.VERIFIED,
            trust_score=85,
            red_flags=[],
            posted_date=datetime.now().date(),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        internships = [internship2, internship1, internship3]  # Intentionally unordered
        
        ranked = await matching_service.rank_internships(sample_user_profile, internships)
        
        # Should be sorted by match percentage (descending)
        assert len(ranked) == 3
        assert ranked[0]["match_percentage"] >= ranked[1]["match_percentage"]
        assert ranked[1]["match_percentage"] >= ranked[2]["match_percentage"]
        
        # internship1 and internship3 should be ranked higher than internship2
        assert ranked[0]["internship"].id in ["int-1", "int-3"]
        assert ranked[2]["internship"].id == "int-2"
    
    @pytest.mark.asyncio
    async def test_rank_empty_internships_list(self, matching_service, sample_user_profile):
        """Test ranking with empty internships list"""
        internships = []
        
        ranked = await matching_service.rank_internships(sample_user_profile, internships)
        
        assert len(ranked) == 0
    
    @pytest.mark.asyncio
    async def test_ranked_internships_include_match_details(self, matching_service, sample_user_profile):
        """Test that ranked internships include match details"""
        internship = InternshipListing(
            id="int-1",
            title="Python Developer",
            company="Company A",
            location="Remote",
            internship_type=InternshipType.SUMMER,
            duration="3 months",
            stipend="₹20,000",
            required_skills=["Python", "Django"],
            preferred_skills=["React"],
            responsibilities=["Develop"],
            verification_status=VerificationStatus.VERIFIED,
            trust_score=85,
            red_flags=[],
            posted_date=datetime.now().date(),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        ranked = await matching_service.rank_internships(sample_user_profile, [internship])
        
        assert len(ranked) == 1
        assert "internship" in ranked[0]
        assert "match_percentage" in ranked[0]
        assert "matching_skills" in ranked[0]
        assert "missing_skills" in ranked[0]
        assert isinstance(ranked[0]["match_percentage"], int)
        assert isinstance(ranked[0]["matching_skills"], list)
        assert isinstance(ranked[0]["missing_skills"], list)


class TestCreateSkillMatch:
    """Tests for create_skill_match method"""
    
    @pytest.mark.asyncio
    async def test_create_skill_match_complete(self, matching_service):
        """Test creating a complete skill match record"""
        user_id = "user-123"
        internship_id = "int-123"
        user_skills = ["Python", "JavaScript"]
        required_skills = ["Python", "Django", "REST API"]
        
        skill_match = await matching_service.create_skill_match(
            user_id=user_id,
            internship_id=internship_id,
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        assert isinstance(skill_match, SkillMatch)
        assert skill_match.user_id == user_id
        assert skill_match.internship_id == internship_id
        assert skill_match.match_percentage >= 0
        assert skill_match.match_percentage <= 100
        assert len(skill_match.matching_skills) > 0
        assert len(skill_match.missing_skills) > 0
        assert len(skill_match.learning_path) > 0
    
    @pytest.mark.asyncio
    async def test_skill_match_includes_learning_path(self, matching_service):
        """Test that skill match includes learning path for missing skills"""
        user_id = "user-123"
        internship_id = "int-123"
        user_skills = ["Python"]
        required_skills = ["Python", "Django", "REST API"]
        
        skill_match = await matching_service.create_skill_match(
            user_id=user_id,
            internship_id=internship_id,
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # Should have learning path for Django and REST API
        assert len(skill_match.learning_path) == 2
        learning_skills = [item.skill for item in skill_match.learning_path]
        assert "Django" in learning_skills
        assert "REST API" in learning_skills


class TestSkillNormalization:
    """Tests for skill normalization"""
    
    @pytest.mark.asyncio
    async def test_normalize_skill(self, matching_service):
        """Test skill normalization"""
        assert matching_service._normalize_skill("Python") == "python"
        assert matching_service._normalize_skill("  JavaScript  ") == "javascript"
        assert matching_service._normalize_skill("REST API") == "rest api"
    
    def test_get_skill_difficulty(self, matching_service):
        """Test skill difficulty determination"""
        assert matching_service._get_skill_difficulty("Git") == "easy"
        assert matching_service._get_skill_difficulty("Python") == "medium"
        assert matching_service._get_skill_difficulty("Machine Learning") == "hard"
        assert matching_service._get_skill_difficulty("UnknownSkill") == "medium"  # Default
    
    def test_get_learning_resources(self, matching_service):
        """Test getting learning resources for skills"""
        python_resources = matching_service._get_learning_resources("Python")
        assert len(python_resources) > 0
        assert any("Python" in resource for resource in python_resources)
        
        # Unknown skill should get default resources
        unknown_resources = matching_service._get_learning_resources("XYZ_UnknownTech_9999")
        assert len(unknown_resources) > 0
        # Check if any default resource keywords are present
        default_keywords = ["Coursera", "Udemy", "YouTube", "Official documentation"]
        assert any(keyword in resource for resource in unknown_resources for keyword in default_keywords)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    @pytest.mark.asyncio
    async def test_match_percentage_bounds(self, matching_service):
        """Test that match percentage is always between 0 and 100"""
        # Test various scenarios
        test_cases = [
            (["Python"], ["Python"], 100),
            ([], ["Python"], 0),
            (["Python"], [], 100),
            (["Python", "Java"], ["Python"], 100),
            (["Python"], ["Python", "Java"], 50),
        ]
        
        for user_skills, required_skills, expected_min in test_cases:
            result = await matching_service.calculate_skill_match(
                user_skills=user_skills,
                required_skills=required_skills
            )
            assert 0 <= result["match_percentage"] <= 100
    
    @pytest.mark.asyncio
    async def test_duplicate_skills_in_input(self, matching_service):
        """Test handling of duplicate skills in input"""
        user_skills = ["Python", "Python", "JavaScript"]
        required_skills = ["Python", "JavaScript", "JavaScript"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # Should handle duplicates correctly
        assert result["match_percentage"] == 100
    
    @pytest.mark.asyncio
    async def test_special_characters_in_skills(self, matching_service):
        """Test handling of special characters in skill names"""
        user_skills = ["C++", "C#", ".NET"]
        required_skills = ["C++", "C#", ".NET"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        assert result["match_percentage"] == 100
        assert len(result["matching_skills"]) == 3


class TestMatchingEdgeCases:
    """
    Unit tests for matching edge cases (Task 5.7)
    
    Tests cover:
    - 100% skill match
    - 0% skill match
    - Empty skill lists
    - Partial overlap
    
    Requirements: US-4 (4.1-4.7)
    """
    
    @pytest.mark.asyncio
    async def test_100_percent_skill_match(self, matching_service):
        """
        Test 100% skill match when user has all required skills
        
        Edge case: Perfect match scenario
        Expected: match_percentage = 100, all skills matching, no missing skills
        """
        user_skills = ["Python", "Django", "REST API", "PostgreSQL"]
        required_skills = ["Python", "Django", "REST API", "PostgreSQL"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # Verify 100% match
        assert result["match_percentage"] == 100, \
            f"Expected 100% match, got {result['match_percentage']}%"
        
        # Verify all skills are matching
        assert len(result["matching_skills"]) == 4, \
            f"Expected 4 matching skills, got {len(result['matching_skills'])}"
        
        # Verify no missing skills
        assert len(result["missing_skills"]) == 0, \
            f"Expected 0 missing skills, got {len(result['missing_skills'])}"
        
        # Verify matching skills contain all required skills (case-insensitive)
        matching_normalized = set(s.lower() for s in result["matching_skills"])
        required_normalized = set(s.lower() for s in required_skills)
        assert matching_normalized == required_normalized, \
            f"Matching skills {matching_normalized} should equal required skills {required_normalized}"
    
    @pytest.mark.asyncio
    async def test_100_percent_match_with_extra_user_skills(self, matching_service):
        """
        Test 100% match when user has all required skills plus additional skills
        
        Edge case: User is overqualified
        Expected: match_percentage = 100, extra skills don't reduce match
        """
        user_skills = ["Python", "Django", "REST API", "PostgreSQL", "React", "JavaScript", "Docker"]
        required_skills = ["Python", "Django", "REST API"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # Should still be 100% match
        assert result["match_percentage"] == 100, \
            f"Expected 100% match when user has extra skills, got {result['match_percentage']}%"
        
        # Verify all required skills are matching
        assert len(result["matching_skills"]) == 3, \
            f"Expected 3 matching skills, got {len(result['matching_skills'])}"
        
        # Verify no missing skills
        assert len(result["missing_skills"]) == 0, \
            f"Expected 0 missing skills, got {len(result['missing_skills'])}"
    
    @pytest.mark.asyncio
    async def test_0_percent_skill_match(self, matching_service):
        """
        Test 0% skill match when user has no required skills
        
        Edge case: Complete mismatch scenario
        Expected: match_percentage = 0, no matching skills, all skills missing
        """
        user_skills = ["Java", "Spring Boot", "Hibernate", "Maven"]
        required_skills = ["Python", "Django", "REST API", "PostgreSQL"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # Verify 0% match
        assert result["match_percentage"] == 0, \
            f"Expected 0% match, got {result['match_percentage']}%"
        
        # Verify no matching skills
        assert len(result["matching_skills"]) == 0, \
            f"Expected 0 matching skills, got {len(result['matching_skills'])}"
        
        # Verify all skills are missing
        assert len(result["missing_skills"]) == 4, \
            f"Expected 4 missing skills, got {len(result['missing_skills'])}"
        
        # Verify missing skills contain all required skills (case-insensitive)
        missing_normalized = set(s.lower() for s in result["missing_skills"])
        required_normalized = set(s.lower() for s in required_skills)
        assert missing_normalized == required_normalized, \
            f"Missing skills {missing_normalized} should equal required skills {required_normalized}"
    
    @pytest.mark.asyncio
    async def test_empty_user_skills_list(self, matching_service):
        """
        Test with empty user skills list
        
        Edge case: User has no skills
        Expected: match_percentage = 0, no matching skills, all required skills missing
        """
        user_skills = []
        required_skills = ["Python", "Django", "REST API"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # Verify 0% match
        assert result["match_percentage"] == 0, \
            f"Expected 0% match with empty user skills, got {result['match_percentage']}%"
        
        # Verify no matching skills
        assert len(result["matching_skills"]) == 0, \
            f"Expected 0 matching skills, got {len(result['matching_skills'])}"
        
        # Verify all required skills are missing
        assert len(result["missing_skills"]) == len(required_skills), \
            f"Expected {len(required_skills)} missing skills, got {len(result['missing_skills'])}"
        
        # Verify missing skills equal required skills
        assert set(s.lower() for s in result["missing_skills"]) == set(s.lower() for s in required_skills), \
            "All required skills should be in missing skills when user has no skills"
    
    @pytest.mark.asyncio
    async def test_empty_required_skills_list(self, matching_service):
        """
        Test with empty required skills list
        
        Edge case: Internship has no skill requirements
        Expected: match_percentage = 100, no matching or missing skills
        """
        user_skills = ["Python", "Django", "REST API"]
        required_skills = []
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # Verify 100% match (no requirements to fail)
        assert result["match_percentage"] == 100, \
            f"Expected 100% match with empty required skills, got {result['match_percentage']}%"
        
        # Verify no matching skills (nothing to match against)
        assert len(result["matching_skills"]) == 0, \
            f"Expected 0 matching skills, got {len(result['matching_skills'])}"
        
        # Verify no missing skills (no requirements)
        assert len(result["missing_skills"]) == 0, \
            f"Expected 0 missing skills, got {len(result['missing_skills'])}"
    
    @pytest.mark.asyncio
    async def test_both_empty_skill_lists(self, matching_service):
        """
        Test with both empty user and required skills lists
        
        Edge case: No skills on either side
        Expected: match_percentage = 100, no matching or missing skills
        """
        user_skills = []
        required_skills = []
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # Verify 100% match (vacuous truth - no requirements to fail)
        assert result["match_percentage"] == 100, \
            f"Expected 100% match with both empty lists, got {result['match_percentage']}%"
        
        # Verify no matching skills
        assert len(result["matching_skills"]) == 0, \
            f"Expected 0 matching skills, got {len(result['matching_skills'])}"
        
        # Verify no missing skills
        assert len(result["missing_skills"]) == 0, \
            f"Expected 0 missing skills, got {len(result['missing_skills'])}"
    
    @pytest.mark.asyncio
    async def test_partial_overlap_one_third(self, matching_service):
        """
        Test partial skill overlap (1 out of 3 required skills)
        
        Edge case: Low match scenario
        Expected: match_percentage = 33, one matching skill, two missing skills
        """
        user_skills = ["Python", "JavaScript", "React"]
        required_skills = ["Python", "Django", "PostgreSQL"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # Verify 33% match (1 out of 3)
        assert result["match_percentage"] == 33, \
            f"Expected 33% match (1/3), got {result['match_percentage']}%"
        
        # Verify one matching skill
        assert len(result["matching_skills"]) == 1, \
            f"Expected 1 matching skill, got {len(result['matching_skills'])}"
        
        # Verify Python is the matching skill
        assert "Python" in result["matching_skills"] or "python" in [s.lower() for s in result["matching_skills"]], \
            f"Expected Python in matching skills, got {result['matching_skills']}"
        
        # Verify two missing skills
        assert len(result["missing_skills"]) == 2, \
            f"Expected 2 missing skills, got {len(result['missing_skills'])}"
        
        # Verify Django and PostgreSQL are missing
        missing_normalized = set(s.lower() for s in result["missing_skills"])
        assert "django" in missing_normalized and "postgresql" in missing_normalized, \
            f"Expected Django and PostgreSQL in missing skills, got {result['missing_skills']}"
    
    @pytest.mark.asyncio
    async def test_partial_overlap_two_thirds(self, matching_service):
        """
        Test partial skill overlap (2 out of 3 required skills)
        
        Edge case: High but not perfect match
        Expected: match_percentage = 66, two matching skills, one missing skill
        """
        user_skills = ["Python", "Django", "React", "JavaScript"]
        required_skills = ["Python", "Django", "PostgreSQL"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # Verify 66% match (2 out of 3)
        assert result["match_percentage"] == 66, \
            f"Expected 66% match (2/3), got {result['match_percentage']}%"
        
        # Verify two matching skills
        assert len(result["matching_skills"]) == 2, \
            f"Expected 2 matching skills, got {len(result['matching_skills'])}"
        
        # Verify Python and Django are matching
        matching_normalized = set(s.lower() for s in result["matching_skills"])
        assert "python" in matching_normalized and "django" in matching_normalized, \
            f"Expected Python and Django in matching skills, got {result['matching_skills']}"
        
        # Verify one missing skill
        assert len(result["missing_skills"]) == 1, \
            f"Expected 1 missing skill, got {len(result['missing_skills'])}"
        
        # Verify PostgreSQL is missing
        assert "PostgreSQL" in result["missing_skills"] or "postgresql" in [s.lower() for s in result["missing_skills"]], \
            f"Expected PostgreSQL in missing skills, got {result['missing_skills']}"
    
    @pytest.mark.asyncio
    async def test_partial_overlap_with_preferred_skills(self, matching_service):
        """
        Test partial overlap with both required and preferred skills
        
        Edge case: Weighted matching with preferred skills
        Expected: Weighted calculation (70% required + 30% preferred)
        """
        user_skills = ["Python", "React", "JavaScript"]
        required_skills = ["Python", "Django"]  # 50% match (1/2)
        preferred_skills = ["React", "JavaScript"]  # 100% match (2/2)
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills
        )
        
        # Calculate expected: (50% * 0.7) + (100% * 0.3) = 35 + 30 = 65%
        expected_percentage = 65
        assert result["match_percentage"] == expected_percentage, \
            f"Expected {expected_percentage}% match with weighted calculation, got {result['match_percentage']}%"
        
        # Verify matching skills include Python, React, and JavaScript
        assert len(result["matching_skills"]) == 3, \
            f"Expected 3 matching skills, got {len(result['matching_skills'])}"
        
        # Verify Django is missing
        assert len(result["missing_skills"]) == 1, \
            f"Expected 1 missing skill, got {len(result['missing_skills'])}"
        assert "Django" in result["missing_skills"] or "django" in [s.lower() for s in result["missing_skills"]], \
            f"Expected Django in missing skills, got {result['missing_skills']}"
    
    @pytest.mark.asyncio
    async def test_partial_overlap_case_insensitive(self, matching_service):
        """
        Test partial overlap with case variations
        
        Edge case: Case-insensitive matching with partial overlap
        Expected: Case should not affect matching
        """
        user_skills = ["PYTHON", "javascript", "ReAcT"]
        required_skills = ["Python", "Django", "JavaScript"]
        
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills
        )
        
        # Verify 66% match (2 out of 3, case-insensitive)
        assert result["match_percentage"] == 66, \
            f"Expected 66% match with case variations, got {result['match_percentage']}%"
        
        # Verify two matching skills
        assert len(result["matching_skills"]) == 2, \
            f"Expected 2 matching skills, got {len(result['matching_skills'])}"
        
        # Verify one missing skill
        assert len(result["missing_skills"]) == 1, \
            f"Expected 1 missing skill, got {len(result['missing_skills'])}"



# ============================================================================
# Property-Based Tests
# ============================================================================

class TestPropertyBasedMatching:
    """Property-based tests for matching service using Hypothesis"""
    
    # Feature: internship-discovery, Property 9: Skill Match Percentage Bounds
    @given(
        user_skills=st.lists(
            st.text(min_size=1, max_size=30, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters=' +-#.'
            )),
            min_size=0,
            max_size=20
        ),
        required_skills=st.lists(
            st.text(min_size=1, max_size=30, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters=' +-#.'
            )),
            min_size=0,
            max_size=20
        ),
        preferred_skills=st.lists(
            st.text(min_size=1, max_size=30, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters=' +-#.'
            )),
            min_size=0,
            max_size=20
        )
    )
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_property_skill_match_percentage_bounds(
        self,
        user_skills,
        required_skills,
        preferred_skills
    ):
        """
        **Validates: Requirements 4.4**
        
        Property 9: Skill Match Percentage Bounds
        
        For any skill matching calculation between user skills and internship 
        requirements, the resulting match percentage must be an integer between 
        0 and 100 (inclusive).
        
        This property ensures that regardless of the input skills (empty lists,
        duplicates, special characters, case variations, etc.), the match 
        percentage is always a valid percentage value.
        """
        matching_service = MatchingService()
        
        # Calculate skill match with arbitrary inputs
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills if preferred_skills else None
        )
        
        # Property: Match percentage must be an integer between 0 and 100
        assert isinstance(result["match_percentage"], int), \
            f"Match percentage must be an integer, got {type(result['match_percentage'])}"
        
        assert 0 <= result["match_percentage"] <= 100, \
            f"Match percentage must be between 0 and 100, got {result['match_percentage']}"
        
        # Additional invariants that should always hold
        assert isinstance(result["matching_skills"], list), \
            "Matching skills must be a list"
        
        assert isinstance(result["missing_skills"], list), \
            "Missing skills must be a list"
        
        # Matching skills should be a subset of required + preferred skills
        all_required_and_preferred = set(
            s.lower().strip() for s in (required_skills + preferred_skills)
        )
        matching_normalized = set(s.lower().strip() for s in result["matching_skills"])
        assert matching_normalized.issubset(all_required_and_preferred), \
            "Matching skills should be a subset of required and preferred skills"
        
        # Missing skills should be a subset of required skills
        required_normalized = set(s.lower().strip() for s in required_skills)
        missing_normalized = set(s.lower().strip() for s in result["missing_skills"])
        assert missing_normalized.issubset(required_normalized), \
            "Missing skills should be a subset of required skills"
    
    # Feature: internship-discovery, Property 10: Skill Match Calculation
    @given(
        user_skills=st.lists(
            st.text(min_size=1, max_size=30, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters=' +-#.'
            )),
            min_size=0,
            max_size=20,
            unique=True
        ),
        required_skills=st.lists(
            st.text(min_size=1, max_size=30, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters=' +-#.'
            )),
            min_size=1,
            max_size=20,
            unique=True
        )
    )
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_property_skill_match_calculation(
        self,
        user_skills,
        required_skills
    ):
        """
        **Validates: Requirements 4.1, 4.2, 4.3, 4.5**
        
        Property 10: Skill Match Calculation
        
        For any set of user skills (from resume or manual input) and any 
        internship with required skills, the system should calculate a match 
        percentage, identify matching skills (intersection), and identify 
        missing skills (difference).
        
        This property ensures that:
        1. Match percentage is calculated correctly
        2. Matching skills = intersection of user skills and required skills
        3. Missing skills = required skills - user skills
        4. The calculation works for skills from any source (resume or manual)
        """
        matching_service = MatchingService()
        
        # Calculate skill match
        result = await matching_service.calculate_skill_match(
            user_skills=user_skills,
            required_skills=required_skills,
            preferred_skills=None
        )
        
        # Normalize skills for comparison
        user_skills_normalized = set(s.lower().strip() for s in user_skills)
        required_skills_normalized = set(s.lower().strip() for s in required_skills)
        
        # Calculate expected intersection and difference
        expected_matching = user_skills_normalized.intersection(required_skills_normalized)
        expected_missing = required_skills_normalized.difference(user_skills_normalized)
        
        # Get actual results (normalized)
        actual_matching = set(s.lower().strip() for s in result["matching_skills"])
        actual_missing = set(s.lower().strip() for s in result["missing_skills"])
        
        # Property 1: Matching skills should be the intersection
        assert actual_matching == expected_matching, \
            f"Matching skills should be intersection. Expected: {expected_matching}, Got: {actual_matching}"
        
        # Property 2: Missing skills should be the difference (required - user)
        assert actual_missing == expected_missing, \
            f"Missing skills should be difference. Expected: {expected_missing}, Got: {actual_missing}"
        
        # Property 3: Match percentage should be calculated correctly
        # For required-only skills: match_pct = (matching / required) * 100
        if required_skills_normalized:
            expected_percentage = int((len(expected_matching) / len(required_skills_normalized)) * 100)
            assert result["match_percentage"] == expected_percentage, \
                f"Match percentage incorrect. Expected: {expected_percentage}%, Got: {result['match_percentage']}%"
        
        # Property 4: Matching + Missing should equal Required (no overlap, no gaps)
        assert actual_matching.union(actual_missing) == required_skills_normalized, \
            "Matching and missing skills should partition the required skills"
        
        assert actual_matching.intersection(actual_missing) == set(), \
            "Matching and missing skills should not overlap"
        
        # Property 5: All matching skills must be in both user and required
        for skill in actual_matching:
            assert skill in user_skills_normalized, \
                f"Matching skill '{skill}' not in user skills"
            assert skill in required_skills_normalized, \
                f"Matching skill '{skill}' not in required skills"
        
        # Property 6: All missing skills must be in required but not in user
        for skill in actual_missing:
            assert skill in required_skills_normalized, \
                f"Missing skill '{skill}' not in required skills"
            assert skill not in user_skills_normalized, \
                f"Missing skill '{skill}' should not be in user skills"
        
        # Property 7: Match percentage should reflect the proportion of matched skills
        # 0% when no matching skills, 100% when all required skills are matched
        if len(expected_matching) == 0:
            assert result["match_percentage"] == 0, \
                "Match percentage should be 0 when no skills match"
        elif len(expected_matching) == len(required_skills_normalized):
            assert result["match_percentage"] == 100, \
                "Match percentage should be 100 when all required skills match"
    
    # Feature: internship-discovery, Property 11: Learning Path Generation
    @given(
        missing_skills=st.lists(
            st.text(min_size=1, max_size=30, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters=' +-#.'
            )),
            min_size=1,  # At least one missing skill
            max_size=15,
            unique=True
        ),
        required_skills=st.lists(
            st.text(min_size=1, max_size=30, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters=' +-#.'
            )),
            min_size=0,
            max_size=15,
            unique=True
        )
    )
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_property_learning_path_generation(
        self,
        missing_skills,
        required_skills
    ):
        """
        **Validates: Requirements 4.6**
        
        Property 11: Learning Path Generation
        
        For any non-empty set of missing skills, the system should generate a 
        learning path with at least one recommendation per skill, including 
        estimated time and resources.
        
        This property ensures that:
        1. Every missing skill gets a learning path item
        2. Each item has all required fields (skill, estimated_time, difficulty, resources, priority)
        3. Resources list is non-empty for each skill
        4. Estimated time is a valid time string
        5. Difficulty is one of: Easy, Medium, Hard
        6. Priority is one of: High, Medium, Low
        7. Required skills get higher priority than non-required skills
        """
        matching_service = MatchingService()
        
        # Generate learning path
        learning_path = await matching_service.generate_learning_path(
            missing_skills=missing_skills,
            required_skills=required_skills
        )
        
        # Property 1: Learning path should have exactly one item per missing skill
        assert len(learning_path) == len(missing_skills), \
            f"Learning path should have {len(missing_skills)} items, got {len(learning_path)}"
        
        # Property 2: All learning path items should be LearningPathItem instances
        assert all(isinstance(item, LearningPathItem) for item in learning_path), \
            "All learning path items should be LearningPathItem instances"
        
        # Normalize missing skills for comparison
        missing_skills_normalized = set(s.lower().strip() for s in missing_skills)
        learning_path_skills_normalized = set(item.skill.lower().strip() for item in learning_path)
        
        # Property 3: Every missing skill should have a learning path item
        assert learning_path_skills_normalized == missing_skills_normalized, \
            f"Learning path skills should match missing skills. Missing: {missing_skills_normalized - learning_path_skills_normalized}"
        
        # Property 4: Each learning path item should have all required fields
        for item in learning_path:
            # Check skill field
            assert item.skill is not None and len(item.skill.strip()) > 0, \
                "Each learning path item must have a non-empty skill name"
            
            # Check estimated_time field
            assert item.estimated_time is not None and len(item.estimated_time.strip()) > 0, \
                f"Learning path item for '{item.skill}' must have estimated_time"
            
            # Check difficulty field
            assert item.difficulty in ["Easy", "Medium", "Hard"], \
                f"Learning path item for '{item.skill}' has invalid difficulty: {item.difficulty}"
            
            # Check resources field
            assert item.resources is not None, \
                f"Learning path item for '{item.skill}' must have resources"
            assert isinstance(item.resources, list), \
                f"Resources for '{item.skill}' must be a list"
            assert len(item.resources) > 0, \
                f"Learning path item for '{item.skill}' must have at least one resource"
            
            # Check that all resources are non-empty strings
            for resource in item.resources:
                assert isinstance(resource, str) and len(resource.strip()) > 0, \
                    f"All resources for '{item.skill}' must be non-empty strings"
            
            # Check priority field
            assert item.priority in ["High", "Medium", "Low"], \
                f"Learning path item for '{item.skill}' has invalid priority: {item.priority}"
        
        # Property 5: Required skills should have High priority
        if required_skills:
            required_skills_normalized = set(s.lower().strip() for s in required_skills)
            
            for item in learning_path:
                item_skill_normalized = item.skill.lower().strip()
                
                if item_skill_normalized in required_skills_normalized:
                    assert item.priority == "High", \
                        f"Required skill '{item.skill}' should have High priority, got {item.priority}"
        
        # Property 6: Non-required skills should have Medium or Low priority (not High)
        if required_skills:
            required_skills_normalized = set(s.lower().strip() for s in required_skills)
            
            for item in learning_path:
                item_skill_normalized = item.skill.lower().strip()
                
                if item_skill_normalized not in required_skills_normalized:
                    assert item.priority in ["Medium", "Low"], \
                        f"Non-required skill '{item.skill}' should have Medium or Low priority, got {item.priority}"
        
        # Property 7: Learning path should be sorted by priority (High first)
        # High priority items should come before Medium and Low priority items
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        priorities = [priority_order[item.priority] for item in learning_path]
        
        # Check if the list is sorted (each element <= next element)
        for i in range(len(priorities) - 1):
            assert priorities[i] <= priorities[i + 1], \
                f"Learning path should be sorted by priority. Found {learning_path[i].priority} before {learning_path[i+1].priority}"
        
        # Property 8: Estimated time should follow valid format patterns
        valid_time_patterns = ["week", "month", "day", "hour"]
        for item in learning_path:
            time_lower = item.estimated_time.lower()
            assert any(pattern in time_lower for pattern in valid_time_patterns), \
                f"Estimated time '{item.estimated_time}' for '{item.skill}' should contain a valid time unit"
    
    # Feature: internship-discovery, Property 12: Internship Ranking by Match Score
    @given(
        # Generate a list of internships with random skill requirements
        num_internships=st.integers(min_value=1, max_value=10),
        user_skills=st.lists(
            st.text(min_size=1, max_size=20, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters=' +-#.'
            )),
            min_size=1,
            max_size=15,
            unique=True
        )
    )
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_property_internship_ranking_by_match_score(
        self,
        num_internships,
        user_skills
    ):
        """
        **Validates: Requirements 4.7**
        
        Property 12: Internship Ranking by Match Score
        
        For any list of internships with calculated match scores, when sorted 
        by relevance, the internships should be ordered by match percentage in 
        descending order (highest match first).
        
        This property ensures that:
        1. Internships are sorted in descending order by match percentage
        2. Each ranked entry includes the internship and its match details
        3. The ranking is stable and deterministic for the same inputs
        4. All internships in the input list appear in the output
        5. Match percentages are correctly calculated for each internship
        """
        matching_service = MatchingService()
        
        # Create a user profile with the generated skills
        user_profile = StudentProfile(
            id=f"profile-{uuid.uuid4()}",
            user_id=f"user-{uuid.uuid4()}",
            graduation_year=2026,
            current_semester=4,
            degree="B.Tech",
            branch="Computer Science",
            skills=user_skills,
            preferred_roles=["Software Engineer"],
            internship_type=LocationPreference.REMOTE,
            compensation_preference=CompensationPreference.PAID,
            target_companies=[],
            resume_url=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Generate random internships with different skill requirements
        internships = []
        skill_pool = [
            "Python", "JavaScript", "Java", "C++", "React", "Angular", "Vue",
            "Django", "Flask", "Node.js", "SQL", "MongoDB", "PostgreSQL",
            "AWS", "Docker", "Kubernetes", "Git", "REST API", "GraphQL",
            "Machine Learning", "Data Analysis", "HTML", "CSS"
        ]
        
        for i in range(num_internships):
            # Randomly select 1-5 required skills from the pool
            import random
            num_required = random.randint(1, min(5, len(skill_pool)))
            required_skills = random.sample(skill_pool, num_required)
            
            # Optionally add 0-3 preferred skills
            num_preferred = random.randint(0, min(3, len(skill_pool)))
            preferred_skills = random.sample(skill_pool, num_preferred) if num_preferred > 0 else []
            
            internship = InternshipListing(
                id=f"int-{i}",
                title=f"Internship {i}",
                company=f"Company {i}",
                location="Remote",
                internship_type=InternshipType.SUMMER,
                duration="3 months",
                stipend="₹20,000",
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                responsibilities=["Develop", "Test"],
                verification_status=VerificationStatus.VERIFIED,
                trust_score=85,
                red_flags=[],
                posted_date=datetime.now().date(),
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            internships.append(internship)
        
        # Rank the internships
        ranked = await matching_service.rank_internships(user_profile, internships)
        
        # Property 1: All internships should be in the ranked list
        assert len(ranked) == len(internships), \
            f"Ranked list should have {len(internships)} internships, got {len(ranked)}"
        
        # Property 2: Each ranked entry should have required fields
        for entry in ranked:
            assert "internship" in entry, \
                "Each ranked entry must have 'internship' field"
            assert "match_percentage" in entry, \
                "Each ranked entry must have 'match_percentage' field"
            assert "matching_skills" in entry, \
                "Each ranked entry must have 'matching_skills' field"
            assert "missing_skills" in entry, \
                "Each ranked entry must have 'missing_skills' field"
            
            # Verify types
            assert isinstance(entry["internship"], InternshipListing), \
                "internship field must be an InternshipListing"
            assert isinstance(entry["match_percentage"], int), \
                "match_percentage must be an integer"
            assert isinstance(entry["matching_skills"], list), \
                "matching_skills must be a list"
            assert isinstance(entry["missing_skills"], list), \
                "missing_skills must be a list"
            
            # Verify match percentage bounds
            assert 0 <= entry["match_percentage"] <= 100, \
                f"match_percentage must be between 0 and 100, got {entry['match_percentage']}"
        
        # Property 3: Internships should be sorted by match percentage in descending order
        match_percentages = [entry["match_percentage"] for entry in ranked]
        
        for i in range(len(match_percentages) - 1):
            assert match_percentages[i] >= match_percentages[i + 1], \
                f"Internships should be sorted by match percentage (descending). " \
                f"Found {match_percentages[i]}% at position {i} followed by " \
                f"{match_percentages[i + 1]}% at position {i + 1}"
        
        # Property 4: All original internships should be present in ranked list
        original_ids = set(internship.id for internship in internships)
        ranked_ids = set(entry["internship"].id for entry in ranked)
        
        assert original_ids == ranked_ids, \
            f"All original internships should be in ranked list. " \
            f"Missing: {original_ids - ranked_ids}, Extra: {ranked_ids - original_ids}"
        
        # Property 5: Match percentages should be correctly calculated
        # Verify by recalculating match for each internship
        for entry in ranked:
            internship = entry["internship"]
            
            # Recalculate match
            recalculated = await matching_service.calculate_skill_match(
                user_skills=user_profile.skills,
                required_skills=internship.required_skills,
                preferred_skills=internship.preferred_skills
            )
            
            # Match percentage should be the same
            assert entry["match_percentage"] == recalculated["match_percentage"], \
                f"Match percentage mismatch for {internship.id}. " \
                f"Ranked: {entry['match_percentage']}%, Recalculated: {recalculated['match_percentage']}%"
        
        # Property 6: Ranking should be deterministic (same input = same output)
        # Rank again and verify the order is the same
        ranked_again = await matching_service.rank_internships(user_profile, internships)
        
        for i in range(len(ranked)):
            assert ranked[i]["internship"].id == ranked_again[i]["internship"].id, \
                f"Ranking should be deterministic. Position {i} differs between runs"
            assert ranked[i]["match_percentage"] == ranked_again[i]["match_percentage"], \
                f"Match percentages should be deterministic. Position {i} differs between runs"
        
        # Property 7: Higher match percentage means better ranking (lower index)
        # If two internships have different match percentages, the one with higher
        # percentage should appear earlier in the list
        for i in range(len(ranked)):
            for j in range(i + 1, len(ranked)):
                if ranked[i]["match_percentage"] > ranked[j]["match_percentage"]:
                    # This is correct - higher match comes first
                    pass
                elif ranked[i]["match_percentage"] == ranked[j]["match_percentage"]:
                    # Equal match percentages - order doesn't matter
                    pass
                else:
                    # This should never happen - lower match percentage before higher
                    pytest.fail(
                        f"Ranking violation: Internship at position {i} has "
                        f"{ranked[i]['match_percentage']}% match, but internship at "
                        f"position {j} has {ranked[j]['match_percentage']}% match"
                    )
