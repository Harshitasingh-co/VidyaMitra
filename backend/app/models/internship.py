"""
Pydantic models for the Internship Discovery & Verification Module

These models define the data structures for student profiles, internship listings,
verification results, skill matches, readiness scores, alerts, and scam reports.
"""

from pydantic import BaseModel, Field, validator, field_validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class InternshipType(str, Enum):
    """Types of internships available"""
    SUMMER = "Summer"
    WINTER = "Winter"
    RESEARCH = "Research"
    OFF_CYCLE = "Off-cycle"


class VerificationStatus(str, Enum):
    """Verification status for internship listings"""
    VERIFIED = "Verified"
    USE_CAUTION = "Use Caution"
    POTENTIAL_SCAM = "Potential Scam"
    PENDING = "Pending"


class LocationPreference(str, Enum):
    """Student's location preference for internships"""
    REMOTE = "Remote"
    ON_SITE = "On-site"
    HYBRID = "Hybrid"


class CompensationPreference(str, Enum):
    """Student's compensation preference"""
    PAID = "Paid"
    UNPAID = "Unpaid"
    ANY = "Any"


class AlertType(str, Enum):
    """Types of alerts that can be sent to users"""
    NEW_MATCH = "new_match"
    DEADLINE_APPROACHING = "deadline_approaching"
    READINESS_IMPROVED = "readiness_improved"
    SEASON_STARTING = "season_starting"


class ScamReportStatus(str, Enum):
    """Status of scam reports"""
    PENDING = "Pending"
    REVIEWED = "Reviewed"
    CONFIRMED = "Confirmed"
    DISMISSED = "Dismissed"


class RedFlagSeverity(str, Enum):
    """Severity levels for red flags"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ============================================================================
# Student Profile Models
# ============================================================================

class StudentProfileBase(BaseModel):
    """Base model for student profile data"""
    graduation_year: int = Field(..., ge=2024, le=2035, description="Year of graduation")
    current_semester: int = Field(..., ge=1, le=8, description="Current semester (1-8)")
    degree: str = Field(..., min_length=1, max_length=50, description="Degree program (e.g., B.Tech, M.Tech)")
    branch: str = Field(..., min_length=1, max_length=100, description="Branch/specialization")
    skills: List[str] = Field(default_factory=list, description="List of skills")
    preferred_roles: List[str] = Field(default_factory=list, description="Preferred job roles")
    internship_type: Optional[LocationPreference] = Field(None, description="Location preference")
    compensation_preference: Optional[CompensationPreference] = Field(None, description="Compensation preference")
    target_companies: List[str] = Field(default_factory=list, description="Target companies")
    resume_url: Optional[str] = Field(None, description="URL to uploaded resume")


class StudentProfileCreate(StudentProfileBase):
    """Model for creating a new student profile"""
    pass


class StudentProfileUpdate(BaseModel):
    """Model for updating an existing student profile (all fields optional)"""
    graduation_year: Optional[int] = Field(None, ge=2024, le=2035)
    current_semester: Optional[int] = Field(None, ge=1, le=8)
    degree: Optional[str] = Field(None, min_length=1, max_length=50)
    branch: Optional[str] = Field(None, min_length=1, max_length=100)
    skills: Optional[List[str]] = None
    preferred_roles: Optional[List[str]] = None
    internship_type: Optional[LocationPreference] = None
    compensation_preference: Optional[CompensationPreference] = None
    target_companies: Optional[List[str]] = None
    resume_url: Optional[str] = None


class StudentProfile(StudentProfileBase):
    """Complete student profile with database fields"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Internship Listing Models
# ============================================================================

class RedFlag(BaseModel):
    """Model for a red flag in an internship listing"""
    type: str = Field(..., description="Type of red flag (e.g., 'registration_fee')")
    severity: RedFlagSeverity = Field(..., description="Severity level")
    description: str = Field(..., description="Human-readable description")


class InternshipListingBase(BaseModel):
    """Base model for internship listing data"""
    title: str = Field(..., min_length=1, max_length=200, description="Internship title")
    company: str = Field(..., min_length=1, max_length=200, description="Company name")
    company_domain: Optional[str] = Field(None, max_length=200, description="Company domain")
    platform: Optional[str] = Field(None, max_length=100, description="Platform where listed")
    location: str = Field(..., description="Location (city or 'Remote')")
    internship_type: InternshipType = Field(..., description="Type of internship")
    duration: str = Field(..., max_length=50, description="Duration (e.g., '2-3 months')")
    stipend: str = Field(..., max_length=100, description="Stipend amount")
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills")
    responsibilities: List[str] = Field(default_factory=list, description="Job responsibilities")
    application_deadline: Optional[date] = Field(None, description="Application deadline")
    start_date: Optional[date] = Field(None, description="Expected start date")
    source_url: Optional[str] = Field(None, description="Source URL")


class InternshipListingCreate(InternshipListingBase):
    """Model for creating a new internship listing"""
    pass


class InternshipListing(InternshipListingBase):
    """Complete internship listing with database fields"""
    id: str
    verification_status: VerificationStatus = VerificationStatus.PENDING
    trust_score: int = Field(0, ge=0, le=100)
    red_flags: List[RedFlag] = Field(default_factory=list)
    posted_date: date
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Verification Models
# ============================================================================

class VerificationSignals(BaseModel):
    """Signals used in verification process"""
    official_domain: bool = Field(False, description="Has official company domain")
    known_platform: bool = Field(False, description="Listed on known platform")
    company_verified: bool = Field(False, description="Company verified on external sources")


class VerificationResultBase(BaseModel):
    """Base model for verification result"""
    status: VerificationStatus = Field(..., description="Verification status")
    trust_score: int = Field(..., ge=0, le=100, description="Trust score (0-100)")
    verification_signals: VerificationSignals = Field(..., description="Verification signals")
    red_flags: List[RedFlag] = Field(default_factory=list, description="Detected red flags")
    verification_notes: Optional[str] = Field(None, description="Additional notes")


class VerificationResultCreate(VerificationResultBase):
    """Model for creating a verification result"""
    internship_id: str


class VerificationResult(VerificationResultBase):
    """Complete verification result with database fields"""
    id: str
    internship_id: str
    last_verified: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Skill Match Models
# ============================================================================

class LearningPathItem(BaseModel):
    """A single item in a learning path"""
    skill: str = Field(..., description="Skill to learn")
    estimated_time: str = Field(..., description="Estimated time to learn")
    difficulty: str = Field(..., description="Difficulty level (Easy/Medium/Hard)")
    resources: List[str] = Field(default_factory=list, description="Learning resources")
    priority: str = Field(..., description="Priority level (High/Medium/Low)")


class SkillMatchBase(BaseModel):
    """Base model for skill match data"""
    match_percentage: int = Field(..., ge=0, le=100, description="Match percentage (0-100)")
    matching_skills: List[str] = Field(default_factory=list, description="Skills that match")
    missing_skills: List[str] = Field(default_factory=list, description="Skills that are missing")
    learning_path: List[LearningPathItem] = Field(default_factory=list, description="Learning path for missing skills")


class SkillMatchCreate(SkillMatchBase):
    """Model for creating a skill match record"""
    user_id: str
    internship_id: str


class SkillMatch(SkillMatchBase):
    """Complete skill match with database fields"""
    id: str
    user_id: str
    internship_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Readiness Score Models
# ============================================================================

class ReadinessComponents(BaseModel):
    """Components of the readiness score"""
    resume_strength: int = Field(..., ge=0, le=100, description="Resume strength score")
    skill_match: int = Field(..., ge=0, le=100, description="Skill match score")
    semester_readiness: int = Field(..., ge=0, le=100, description="Semester readiness score")


class ReadinessScoreBase(BaseModel):
    """Base model for readiness score"""
    overall_score: int = Field(..., ge=0, le=100, description="Overall readiness score")
    resume_strength: int = Field(..., ge=0, le=100, description="Resume strength component")
    skill_match: int = Field(..., ge=0, le=100, description="Skill match component")
    semester_readiness: int = Field(..., ge=0, le=100, description="Semester readiness component")
    recommendation: str = Field(..., description="Recommendation (e.g., 'Apply Now')")
    improvement_actions: List[str] = Field(default_factory=list, description="Actions to improve readiness")


class ReadinessScoreCreate(ReadinessScoreBase):
    """Model for creating a readiness score"""
    user_id: str
    internship_id: str


class ReadinessScore(ReadinessScoreBase):
    """Complete readiness score with database fields"""
    id: str
    user_id: str
    internship_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Career Guidance Models
# ============================================================================

class CareerGuidance(BaseModel):
    """AI-generated career guidance for an internship"""
    internship_id: str
    why_good_fit: str = Field(..., description="Why this internship is a good fit")
    skills_to_improve: List[str] = Field(default_factory=list, description="Skills to improve")
    certifications: List[str] = Field(default_factory=list, description="Recommended certifications")
    project_ideas: List[str] = Field(default_factory=list, description="Project ideas to strengthen resume")
    timeline: str = Field(..., description="Recommended preparation timeline")


# ============================================================================
# Alert Models
# ============================================================================

class UserAlertBase(BaseModel):
    """Base model for user alert"""
    alert_type: AlertType = Field(..., description="Type of alert")
    title: str = Field(..., min_length=1, max_length=200, description="Alert title")
    message: str = Field(..., description="Alert message")
    internship_id: Optional[str] = Field(None, description="Related internship ID")


class UserAlertCreate(UserAlertBase):
    """Model for creating a user alert"""
    user_id: str


class UserAlert(UserAlertBase):
    """Complete user alert with database fields"""
    id: str
    user_id: str
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Scam Report Models
# ============================================================================

class ScamReportBase(BaseModel):
    """Base model for scam report"""
    reason: str = Field(..., min_length=1, description="Reason for reporting")
    details: Optional[str] = Field(None, description="Additional details")


class ScamReportCreate(ScamReportBase):
    """Model for creating a scam report"""
    internship_id: str


class ScamReport(ScamReportBase):
    """Complete scam report with database fields"""
    id: str
    internship_id: str
    reported_by: str
    status: ScamReportStatus = ScamReportStatus.PENDING
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Request/Response Models for API
# ============================================================================

class InternshipSearchRequest(BaseModel):
    """Request model for searching internships"""
    skills: Optional[List[str]] = Field(None, description="Filter by skills")
    roles: Optional[List[str]] = Field(None, description="Filter by roles")
    internship_type: Optional[InternshipType] = Field(None, description="Filter by type")
    compensation: Optional[CompensationPreference] = Field(None, description="Filter by compensation")
    location: Optional[str] = Field(None, description="Filter by location")
    min_match_percentage: Optional[int] = Field(0, ge=0, le=100, description="Minimum match percentage")


class InternshipCalendarResponse(BaseModel):
    """Response model for internship calendar"""
    semester: int
    focus: str
    apply_window: Optional[str] = None
    internship_period: Optional[str] = None
    preparation_days: Optional[int] = None
    upcoming_deadlines: List[Dict[str, Any]] = Field(default_factory=list)


class InternshipSearchResponse(BaseModel):
    """Response model for internship search"""
    internships: List[InternshipListing]
    total_count: int
    page: int
    page_size: int


class InternshipDetailsResponse(BaseModel):
    """Response model for detailed internship view"""
    internship: InternshipListing
    verification: Optional[VerificationResult] = None
    skill_match: Optional[SkillMatch] = None
    readiness_score: Optional[ReadinessScore] = None
    career_guidance: Optional[CareerGuidance] = None
