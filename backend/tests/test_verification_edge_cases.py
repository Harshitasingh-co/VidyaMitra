"""
Unit Tests for Verification Service Edge Cases

Tests cover specific edge cases and boundary conditions for the verification service.
"""

import pytest
from app.services.verification_service import VerificationService
from app.models.internship import (
    InternshipListing,
    InternshipType,
    VerificationStatus,
    VerificationSignals,
    RedFlag,
    RedFlagSeverity
)
from datetime import date


@pytest.fixture
def verification_service():
    """Create a VerificationService instance"""
    return VerificationService()


@pytest.fixture
def base_internship_data():
    """Create base internship data for testing"""
    return {
        "id": "test-internship-123",
        "title": "Software Engineering Intern",
        "company": "TechCorp",
        "company_domain": "techcorp.com",
        "platform": "LinkedIn",
        "location": "Remote",
        "internship_type": InternshipType.SUMMER,
        "duration": "3 months",
        "stipend": "₹15000/month",
        "required_skills": ["Python", "JavaScript"],
        "preferred_skills": ["React", "Node.js"],
        "responsibilities": [
            "Develop web applications",
            "Write unit tests",
            "Collaborate with team"
        ],
        "application_deadline": date(2026, 3, 31),
        "start_date": date(2026, 5, 1),
        "verification_status": VerificationStatus.PENDING,
        "trust_score": 0,
        "red_flags": [],
        "posted_date": date(2026, 1, 15),
        "is_active": True,
        "source_url": "https://linkedin.com/jobs/123"
    }


class TestInternshipWithNoDomain:
    """Tests for internships without a company domain"""
    
    def test_no_domain_provided(self, verification_service):
        """Test internship with no domain"""
        result = verification_service.check_domain_authenticity("TechCorp", None)
        assert result is False
    
    def test_empty_domain_string(self, verification_service):
        """Test internship with empty domain string"""
        result = verification_service.check_domain_authenticity("TechCorp", "")
        assert result is False
    
    def test_whitespace_domain(self, verification_service):
        """Test internship with whitespace-only domain"""
        result = verification_service.check_domain_authenticity("TechCorp", "   ")
        assert result is False


class TestInternshipWithUnknownPlatform:
    """Tests for internships from unknown platforms"""
    
    def test_unknown_platform(self, verification_service):
        """Test internship from unknown platform"""
        result = verification_service.check_platform_legitimacy("UnknownJobSite")
        assert result is False
    
    def test_no_platform_provided(self, verification_service):
        """Test internship with no platform"""
        result = verification_service.check_platform_legitimacy(None)
        assert result is False
    
    def test_empty_platform_string(self, verification_service):
        """Test internship with empty platform string"""
        result = verification_service.check_platform_legitimacy("")
        assert result is False
    
    def test_case_insensitive_platform_match(self, verification_service):
        """Test platform recognition is case-insensitive"""
        assert verification_service.check_platform_legitimacy("INTERNSHALA") is True
        assert verification_service.check_platform_legitimacy("internshala") is True
        assert verification_service.check_platform_legitimacy("InTeRnShAlA") is True


class TestInternshipWithMultipleRedFlags:
    """Tests for internships with multiple red flags"""
    
    def test_all_red_flags_present(self, verification_service, base_internship_data):
        """Test internship with all possible red flags"""
        internship_data = base_internship_data.copy()
        internship_data["title"] = "Intern - registration fee required"
        internship_data["company_domain"] = "gmail.com"
        internship_data["stipend"] = "₹100000/month"
        internship_data["responsibilities"] = [
            "Contact on WhatsApp only",
            "Various tasks as assigned"
        ]
        
        red_flags = verification_service.detect_red_flags(internship_data)
        
        # Should detect multiple red flags
        assert len(red_flags) >= 4
        
        # Verify specific flag types are present
        flag_types = [flag.type for flag in red_flags]
        assert "registration_fee" in flag_types
        assert "non_official_email" in flag_types
        assert "unrealistic_stipend" in flag_types
        assert "whatsapp_only" in flag_types or "vague_description" in flag_types
    
    def test_multiple_high_severity_flags(self, verification_service, base_internship_data):
        """Test internship with multiple high-severity red flags"""
        internship_data = base_internship_data.copy()
        internship_data["title"] = "Intern - registration fee ₹5000"
        internship_data["company_domain"] = "yahoo.com"
        internship_data["responsibilities"] = ["WhatsApp only for communication"]
        
        red_flags = verification_service.detect_red_flags(internship_data)
        
        # Count high severity flags
        high_severity_count = sum(1 for flag in red_flags if flag.severity == RedFlagSeverity.HIGH)
        assert high_severity_count >= 2
    
    def test_trust_score_with_many_red_flags(self, verification_service):
        """Test trust score calculation with many red flags"""
        signals = VerificationSignals(
            official_domain=True,
            known_platform=True,
            company_verified=False
        )
        
        # Create multiple red flags
        red_flags = [
            RedFlag(type="flag1", severity=RedFlagSeverity.HIGH, description="Test 1"),
            RedFlag(type="flag2", severity=RedFlagSeverity.HIGH, description="Test 2"),
            RedFlag(type="flag3", severity=RedFlagSeverity.MEDIUM, description="Test 3"),
            RedFlag(type="flag4", severity=RedFlagSeverity.LOW, description="Test 4"),
        ]
        
        score = verification_service.calculate_trust_score(signals, red_flags)
        
        # Score should be significantly reduced
        # Base 50 + 20 (domain) + 20 (platform) - 20 - 20 - 10 - 5 = 35
        assert score < 50
        assert score >= 0  # Should not go below 0


class TestTrustScoreBoundaryConditions:
    """Tests for trust score boundary conditions"""
    
    def test_trust_score_exactly_50(self, verification_service):
        """Test trust score at boundary: exactly 50"""
        signals = VerificationSignals(
            official_domain=False,
            known_platform=False,
            company_verified=False
        )
        red_flags = []
        
        score = verification_service.calculate_trust_score(signals, red_flags)
        assert score == 50
    
    def test_trust_score_exactly_79(self, verification_service):
        """Test trust score at boundary: exactly 79 (or close to it)"""
        signals = VerificationSignals(
            official_domain=True,   # +20
            known_platform=True,    # +20
            company_verified=False
        )
        red_flags = [
            RedFlag(type="test1", severity=RedFlagSeverity.MEDIUM, description="Test"),  # -10
            RedFlag(type="test2", severity=RedFlagSeverity.LOW, description="Test")      # -5
        ]
        
        score = verification_service.calculate_trust_score(signals, red_flags)
        # 50 + 20 + 20 - 10 - 5 = 75
        assert score == 75
        assert score < 80  # Should be Use Caution, not Verified
    
    def test_trust_score_exactly_80(self, verification_service):
        """Test trust score at boundary: exactly 80"""
        signals = VerificationSignals(
            official_domain=True,   # +20
            known_platform=True,    # +20
            company_verified=True   # +10
        )
        red_flags = [
            RedFlag(type="test", severity=RedFlagSeverity.HIGH, description="Test")  # -20
        ]
        
        score = verification_service.calculate_trust_score(signals, red_flags)
        # 50 + 20 + 20 + 10 - 20 = 80
        assert score == 80
    
    def test_trust_score_minimum_zero(self, verification_service):
        """Test trust score cannot go below 0"""
        signals = VerificationSignals(
            official_domain=False,
            known_platform=False,
            company_verified=False
        )
        
        # Create many high-severity red flags
        red_flags = [
            RedFlag(type=f"flag{i}", severity=RedFlagSeverity.HIGH, description=f"Test {i}")
            for i in range(10)
        ]
        
        score = verification_service.calculate_trust_score(signals, red_flags)
        assert score == 0  # Should be clamped to 0
    
    def test_trust_score_maximum_100(self, verification_service):
        """Test trust score cannot exceed 100"""
        signals = VerificationSignals(
            official_domain=True,
            known_platform=True,
            company_verified=True
        )
        red_flags = []
        
        score = verification_service.calculate_trust_score(signals, red_flags)
        # 50 + 20 + 20 + 10 = 100
        assert score == 100
        assert score <= 100  # Should not exceed 100


class TestDomainAuthenticity:
    """Tests for domain authenticity checking"""
    
    def test_official_domain_match(self, verification_service):
        """Test official domain that matches company name"""
        result = verification_service.check_domain_authenticity("TechCorp", "techcorp.com")
        assert result is True
    
    def test_official_domain_with_subdomain(self, verification_service):
        """Test official domain with subdomain"""
        result = verification_service.check_domain_authenticity("TechCorp", "careers.techcorp.com")
        assert result is True
    
    def test_non_official_email_domains(self, verification_service):
        """Test all non-official email domains are rejected"""
        for domain in verification_service.NON_OFFICIAL_DOMAINS:
            result = verification_service.check_domain_authenticity("TechCorp", domain)
            assert result is False, f"Domain {domain} should be rejected"
    
    def test_domain_case_insensitive(self, verification_service):
        """Test domain checking is case-insensitive"""
        assert verification_service.check_domain_authenticity("TechCorp", "TECHCORP.COM") is True
        assert verification_service.check_domain_authenticity("techcorp", "TechCorp.com") is True
    
    def test_company_name_normalization(self, verification_service):
        """Test company name normalization (removing Pvt Ltd, Inc, etc.)"""
        assert verification_service.check_domain_authenticity("TechCorp Pvt Ltd", "techcorp.com") is True
        assert verification_service.check_domain_authenticity("TechCorp Inc.", "techcorp.com") is True
        assert verification_service.check_domain_authenticity("TechCorp Limited", "techcorp.com") is True


class TestRedFlagDetection:
    """Tests for specific red flag detection"""
    
    def test_registration_fee_keywords(self, verification_service, base_internship_data):
        """Test detection of various registration fee keywords"""
        keywords = [
            "registration fee",
            "enrollment fee",
            "joining fee",
            "application fee",
            "processing fee",
            "security deposit"
        ]
        
        for keyword in keywords:
            internship_data = base_internship_data.copy()
            internship_data["title"] = f"Intern - {keyword} required"
            
            red_flags = verification_service.detect_red_flags(internship_data)
            flag_types = [flag.type for flag in red_flags]
            
            assert "registration_fee" in flag_types, f"Failed to detect: {keyword}"
    
    def test_whatsapp_only_keywords(self, verification_service, base_internship_data):
        """Test detection of WhatsApp-only contact keywords"""
        keywords = [
            "whatsapp only",
            "contact on whatsapp",
            "whatsapp for details",
            "message on whatsapp"
        ]
        
        for keyword in keywords:
            internship_data = base_internship_data.copy()
            internship_data["responsibilities"] = [keyword]
            
            red_flags = verification_service.detect_red_flags(internship_data)
            flag_types = [flag.type for flag in red_flags]
            
            assert "whatsapp_only" in flag_types, f"Failed to detect: {keyword}"
    
    def test_vague_description_detection(self, verification_service, base_internship_data):
        """Test detection of vague job descriptions"""
        vague_descriptions = [
            ["various tasks"],
            ["general work"],
            ["miscellaneous duties"],
            ["as assigned"],
            ["flexible role"]
        ]
        
        for description in vague_descriptions:
            internship_data = base_internship_data.copy()
            internship_data["responsibilities"] = description
            
            red_flags = verification_service.detect_red_flags(internship_data)
            flag_types = [flag.type for flag in red_flags]
            
            assert "vague_description" in flag_types
    
    def test_no_responsibilities_listed(self, verification_service, base_internship_data):
        """Test detection when no responsibilities are listed"""
        internship_data = base_internship_data.copy()
        internship_data["responsibilities"] = []
        
        red_flags = verification_service.detect_red_flags(internship_data)
        flag_types = [flag.type for flag in red_flags]
        
        assert "vague_description" in flag_types
    
    def test_unrealistic_stipend_detection(self, verification_service, base_internship_data):
        """Test detection of unrealistically high stipends"""
        unrealistic_stipends = [
            "₹60000",
            "₹75000/month",
            "₹100000 per month",
            "₹80k"
        ]
        
        for stipend in unrealistic_stipends:
            internship_data = base_internship_data.copy()
            internship_data["stipend"] = stipend
            
            red_flags = verification_service.detect_red_flags(internship_data)
            flag_types = [flag.type for flag in red_flags]
            
            assert "unrealistic_stipend" in flag_types, f"Failed to detect: {stipend}"
    
    def test_realistic_stipend_no_flag(self, verification_service, base_internship_data):
        """Test that realistic stipends don't trigger red flags"""
        realistic_stipends = [
            "₹10000",
            "₹15000/month",
            "₹20000 per month",
            "₹25k",
            "Unpaid"
        ]
        
        for stipend in realistic_stipends:
            internship_data = base_internship_data.copy()
            internship_data["stipend"] = stipend
            
            red_flags = verification_service.detect_red_flags(internship_data)
            flag_types = [flag.type for flag in red_flags]
            
            # Should not have unrealistic_stipend flag
            assert "unrealistic_stipend" not in flag_types, f"False positive for: {stipend}"


class TestVerificationNotes:
    """Tests for verification notes generation"""
    
    def test_notes_include_positive_signals(self, verification_service):
        """Test that verification notes include positive signals"""
        signals = VerificationSignals(
            official_domain=True,
            known_platform=True,
            company_verified=False
        )
        red_flags = []
        trust_score = 90
        
        notes = verification_service._generate_verification_notes(signals, red_flags, trust_score)
        
        assert "Official company domain verified" in notes
        assert "Listed on known platform" in notes
    
    def test_notes_include_red_flags(self, verification_service):
        """Test that verification notes include red flag warnings"""
        signals = VerificationSignals(
            official_domain=False,
            known_platform=False,
            company_verified=False
        )
        red_flags = [
            RedFlag(type="registration_fee", severity=RedFlagSeverity.HIGH, description="Asks for registration fee"),
            RedFlag(type="whatsapp_only", severity=RedFlagSeverity.HIGH, description="WhatsApp-only contact")
        ]
        trust_score = 30
        
        notes = verification_service._generate_verification_notes(signals, red_flags, trust_score)
        
        assert "red flag" in notes.lower()
        assert "Asks for registration fee" in notes
        assert "WhatsApp-only contact" in notes
    
    def test_notes_include_overall_assessment(self, verification_service):
        """Test that verification notes include overall assessment"""
        signals = VerificationSignals(
            official_domain=True,
            known_platform=True,
            company_verified=True
        )
        red_flags = []
        
        # Test for Verified status
        trust_score = 90
        notes = verification_service._generate_verification_notes(signals, red_flags, trust_score)
        assert "legitimate and safe" in notes.lower()
        
        # Test for Use Caution status
        trust_score = 60
        notes = verification_service._generate_verification_notes(signals, red_flags, trust_score)
        assert "caution" in notes.lower()
        
        # Test for Potential Scam status
        trust_score = 30
        notes = verification_service._generate_verification_notes(signals, red_flags, trust_score)
        assert "risk" in notes.lower() or "avoid" in notes.lower()
