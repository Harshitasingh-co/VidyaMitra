"""
Pytest configuration and fixtures for VidyaMitra tests
"""
import pytest
from hypothesis import settings, Verbosity

# Configure Hypothesis for property-based testing
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("ci", max_examples=200, verbosity=Verbosity.verbose)
settings.register_profile("dev", max_examples=50, verbosity=Verbosity.normal)
settings.load_profile("default")


@pytest.fixture
def sample_student_profile_data():
    """Sample student profile data for testing"""
    return {
        "graduation_year": 2026,
        "current_semester": 4,
        "degree": "B.Tech",
        "branch": "Computer Science",
        "skills": ["Python", "SQL", "React"],
        "preferred_roles": ["Software Engineer", "Data Analyst"],
        "internship_type": "Remote",
        "compensation_preference": "Paid",
        "target_companies": ["Google", "Microsoft"],
        "resume_url": "https://example.com/resume.pdf"
    }


@pytest.fixture
def sample_internship_listing_data():
    """Sample internship listing data for testing"""
    return {
        "title": "Software Engineering Intern",
        "company": "TechCorp",
        "company_domain": "techcorp.com",
        "platform": "Internshala",
        "location": "Remote",
        "internship_type": "Summer",
        "duration": "2-3 months",
        "stipend": "₹15,000/month",
        "required_skills": ["Python", "Django", "REST API"],
        "preferred_skills": ["Docker", "AWS"],
        "responsibilities": ["Build APIs", "Write tests", "Code reviews"],
        "source_url": "https://internshala.com/internship/123"
    }


@pytest.fixture
def sample_verification_signals():
    """Sample verification signals for testing"""
    return {
        "official_domain": True,
        "known_platform": True,
        "company_verified": True
    }


@pytest.fixture
def sample_red_flags():
    """Sample red flags for testing"""
    return [
        {
            "type": "registration_fee",
            "severity": "high",
            "description": "Asks for registration fee"
        },
        {
            "type": "whatsapp_only",
            "severity": "medium",
            "description": "WhatsApp-only contact"
        }
    ]
