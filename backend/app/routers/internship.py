"""
API endpoints for Internship Discovery & Verification Module

This router provides endpoints for:
- Student profile management (create, read, update)
- Internship search and filtering
- Verification and fraud detection
- Skill matching and career guidance
- Readiness scoring
- Alerts and notifications
- Scam reporting
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from pydantic import BaseModel
import logging

from app.models.internship import (
    StudentProfileCreate,
    StudentProfile,
    StudentProfileUpdate,
    InternshipSearchRequest,
    InternshipCalendarResponse,
    ScamReportCreate,
)
from app.services.internship_service_mongo import (
    InternshipServiceMongo,
    ProfileValidationError,
    ProfileNotFoundError,
    DatabaseOperationError,
)
from core.security import get_current_user
from core.config import get_settings
from utils.response_formatter import get_response_formatter
from core.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Fallback in-memory storage if MongoDB not available
in_memory_profiles = {}


def get_internship_service() -> Optional[InternshipServiceMongo]:
    """
    Dependency to get InternshipServiceMongo instance
    
    Returns:
        InternshipServiceMongo instance or None for in-memory mode
    """
    db = get_database()
    if db is None:
        logger.info("Using in-memory storage mode for internship profiles")
        return None  # Signal to use in-memory storage
    return InternshipServiceMongo()


# ============================================================================
# Profile Management Endpoints
# ============================================================================

@router.post("/profile", status_code=status.HTTP_201_CREATED)
async def create_or_update_profile(
    profile: StudentProfileCreate,
    current_user: dict = Depends(get_current_user),
    service: Optional[InternshipServiceMongo] = Depends(get_internship_service)
):
    """
    Create or update student profile
    
    This endpoint allows students to create a new profile or update an existing one
    with their academic information, skills, preferences, and career goals.
    
    **Requirements**: US-1 (1.1-1.9)
    
    **Request Body**:
    - graduation_year: Year of graduation (2024-2035)
    - current_semester: Current semester (1-8)
    - degree: Degree program (e.g., B.Tech, M.Tech, BCA, MCA)
    - branch: Branch/specialization (e.g., Computer Science, Electronics)
    - skills: List of skills (manual or from resume)
    - preferred_roles: List of preferred job roles
    - internship_type: Location preference (Remote/On-site/Hybrid)
    - compensation_preference: Compensation preference (Paid/Unpaid/Any)
    - target_companies: Optional list of target companies
    - resume_url: Optional URL to uploaded resume
    
    **Returns**:
    - Created or updated student profile with all fields
    
    **Errors**:
    - 400: Validation error (invalid semester, graduation year, etc.)
    - 401: Unauthorized (missing or invalid token)
    """
    try:
        user_id = current_user.get("email") or current_user.get("sub")
        logger.info(f"Creating/updating profile for user: {user_id}")
        
        # Use in-memory storage if service is None
        if service is None:
            logger.info("Using in-memory storage for profile")
            profile_data = profile.model_dump()
            profile_data["user_id"] = user_id
            profile_data["id"] = user_id  # Use user_id as profile ID
            in_memory_profiles[user_id] = profile_data
            
            formatter = get_response_formatter()
            return formatter.success(
                profile_data,
                "Profile saved successfully (in-memory mode)"
            )
        
        # Create or update profile using service
        result = await service.create_profile(user_id, profile)
        
        formatter = get_response_formatter()
        return formatter.success(
            result.model_dump(),
            "Profile created/updated successfully"
        )
        
    except ProfileValidationError as e:
        logger.warning(f"Profile validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": str(e),
                "details": {}
            }
        )
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to create/update profile",
                "details": {"error": str(e)}
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_or_update_profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {}
            }
        )


@router.get("/profile")
async def get_profile(
    current_user: dict = Depends(get_current_user),
    service: Optional[InternshipServiceMongo] = Depends(get_internship_service)
):
    """
    Get current user's student profile
    
    Retrieves the complete student profile for the authenticated user,
    including all academic information, skills, preferences, and career goals.
    
    **Requirements**: US-1 (1.1-1.9)
    
    **Returns**:
    - Complete student profile with all fields
    
    **Errors**:
    - 401: Unauthorized (missing or invalid token)
    - 404: Profile not found (user hasn't created a profile yet)
    """
    try:
        user_id = current_user.get("email") or current_user.get("sub")
        logger.info(f"Retrieving profile for user: {user_id}")
        
        # Use in-memory storage if service is None
        if service is None:
            logger.info("Using in-memory storage for profile retrieval")
            profile_data = in_memory_profiles.get(user_id)
            
            if not profile_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "PROFILE_NOT_FOUND",
                        "message": "Student profile not found",
                        "details": {
                            "action": "Create a profile at POST /api/internships/profile"
                        }
                    }
                )
            
            formatter = get_response_formatter()
            return formatter.success(
                profile_data,
                "Profile retrieved successfully (in-memory mode)"
            )
        
        # Get profile using service
        result = await service.get_profile(user_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "PROFILE_NOT_FOUND",
                    "message": "Student profile not found",
                    "details": {
                        "action": "Create a profile at POST /api/internships/profile"
                    }
                }
            )
        
        formatter = get_response_formatter()
        return formatter.success(
            result.model_dump(),
            "Profile retrieved successfully"
        )
        
    except HTTPException:
        raise
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to retrieve profile",
                "details": {"error": str(e)}
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {}
            }
        )


@router.patch("/profile", response_model=StudentProfile)
async def update_profile(
    profile_update: StudentProfileUpdate,
    current_user: dict = Depends(get_current_user),
    service: Optional[InternshipServiceMongo] = Depends(get_internship_service)
):
    """
    Update existing student profile (partial update)
    
    Allows updating specific fields of an existing profile without providing all fields.
    Only the fields provided in the request will be updated.
    
    **Requirements**: US-1 (1.1-1.9)
    
    **Request Body** (all fields optional):
    - graduation_year: Year of graduation (2024-2035)
    - current_semester: Current semester (1-8)
    - degree: Degree program
    - branch: Branch/specialization
    - skills: List of skills
    - preferred_roles: List of preferred job roles
    - internship_type: Location preference
    - compensation_preference: Compensation preference
    - target_companies: List of target companies
    - resume_url: URL to uploaded resume
    
    **Returns**:
    - Updated student profile with all fields
    
    **Errors**:
    - 400: Validation error (invalid values)
    - 401: Unauthorized (missing or invalid token)
    - 404: Profile not found (user hasn't created a profile yet)
    - 503: Service unavailable (database not configured)
    """
    try:
        user_id = current_user.get("email") or current_user.get("sub")
        logger.info(f"Updating profile for user: {user_id}")
        
        # Update profile using service
        result = await service.update_profile(user_id, profile_update)
        
        formatter = get_response_formatter()
        return formatter.success(
            result.model_dump(),
            "Profile updated successfully"
        )
        
    except ProfileNotFoundError as e:
        logger.warning(f"Profile not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PROFILE_NOT_FOUND",
                "message": str(e),
                "details": {
                    "action": "Create a profile at POST /api/internships/profile"
                }
            }
        )
    except ProfileValidationError as e:
        logger.warning(f"Profile validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": str(e),
                "details": {}
            }
        )
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to update profile",
                "details": {"error": str(e)}
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in update_profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {}
            }
        )


# ============================================================================
# Placeholder endpoints for future implementation
# ============================================================================

@router.get("/calendar", response_model=InternshipCalendarResponse)
async def get_internship_calendar(
    current_user: dict = Depends(get_current_user),
    service: Optional[InternshipServiceMongo] = Depends(get_internship_service)
):
    """
    Get personalized internship calendar based on semester
    
    This endpoint retrieves the user's semester from their profile and returns
    a personalized calendar with application windows, deadlines, and recommendations.
    
    **Requirements**: US-2 (2.1-2.8)
    
    **Returns**:
    - semester: User's current semester
    - focus: Main focus area (e.g., "Summer Internships", "Skill Building")
    - description: Detailed description of the focus area
    - apply_window: Application window (e.g., "Jan-Mar") if applicable
    - internship_period: Internship period (e.g., "May-Jul") if applicable
    - recommendation: Personalized recommendation message
    - current_status: Status based on current month
    - upcoming_deadlines: List of upcoming deadlines with type, month, and description
    
    **Errors**:
    - 401: Unauthorized (missing or invalid token)
    - 404: Profile not found (user hasn't created a profile yet)
    - 503: Service unavailable (database not configured)
    """
    try:
        user_id = current_user.get("email") or current_user.get("sub")
        logger.info(f"Retrieving calendar for user: {user_id}")
        
        # Get user profile to retrieve semester
        profile = await service.get_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "PROFILE_NOT_FOUND",
                    "message": "Student profile not found. Please create a profile first.",
                    "details": {
                        "action": "Create a profile at POST /api/internships/profile"
                    }
                }
            )
        
        # Initialize calendar service
        from app.services.calendar_service import CalendarService
        calendar_service = CalendarService()
        
        # Get calendar for user's semester
        calendar_data = calendar_service.get_calendar_for_semester(
            semester=profile.current_semester
        )
        
        logger.info(f"Calendar generated for user {user_id}, semester {profile.current_semester}")
        
        # Format response
        formatter = get_response_formatter()
        return formatter.success(
            calendar_data,
            f"Calendar retrieved for semester {profile.current_semester}"
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        # Handle invalid semester from calendar service
        logger.error(f"Invalid semester value: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_SEMESTER",
                "message": str(e),
                "details": {}
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_internship_calendar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while retrieving calendar",
                "details": {"error": str(e)}
            }
        )


@router.post("/search")
async def search_internships(
    request: InternshipSearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Search internships with filters and skill matching
    
    **Requirements**: US-4 (4.1-4.7)
    
    **Status**: Not yet implemented
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Search endpoint not yet implemented"
    )


@router.get("/{internship_id}")
async def get_internship_details(
    internship_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed internship information
    
    **Requirements**: US-3 (3.1-3.6), US-4 (4.1-4.7)
    
    **Status**: Not yet implemented
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Internship details endpoint not yet implemented"
    )


@router.get("/{internship_id}/verify")
async def verify_internship(
    internship_id: str,
    current_user: dict = Depends(get_current_user),
    service: Optional[InternshipServiceMongo] = Depends(get_internship_service)
):
    """
    Get verification status and fraud analysis
    
    This endpoint performs comprehensive fraud detection and verification on an internship listing,
    checking for red flags, domain authenticity, platform legitimacy, and calculating a trust score.
    
    **Requirements**: US-3 (3.1-3.6)
    
    **Verification Process**:
    1. Retrieve internship details from database
    2. Check domain authenticity (official vs free email)
    3. Verify platform legitimacy (known platforms)
    4. Detect red flags (registration fees, WhatsApp-only, vague descriptions, etc.)
    5. Calculate trust score (0-100) based on signals and red flags
    6. Assign verification status (Verified/Use Caution/Potential Scam)
    7. Cache verification result in database
    
    **Trust Score Thresholds**:
    - ≥80: Verified (safe to apply)
    - 50-79: Use Caution (verify details before applying)
    - <50: Potential Scam (avoid this internship)
    
    **Returns**:
    - status: VerificationStatus (Verified/Use Caution/Potential Scam)
    - trust_score: int (0-100)
    - verification_signals: Object with official_domain, known_platform, company_verified flags
    - red_flags: List of detected red flags with type, severity, and description
    - verification_notes: Human-readable summary of verification
    - last_verified: Timestamp of verification
    
    **Errors**:
    - 401: Unauthorized (missing or invalid token)
    - 404: Internship not found
    - 503: Service unavailable (database not configured)
    """
    try:
        user_id = current_user.get("email") or current_user.get("sub")
        logger.info(f"Verifying internship {internship_id} for user {user_id}")
        
        # Get internship details
        try:
            internship_result = supabase.table('internship_listings').select('*').eq('id', internship_id).execute()
            if not internship_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "INTERNSHIP_NOT_FOUND",
                        "message": f"Internship with ID {internship_id} not found",
                        "details": {}
                    }
                )
            internship_data = internship_result.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve internship {internship_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "DATABASE_ERROR",
                    "message": "Failed to retrieve internship details",
                    "details": {"error": str(e)}
                }
            )
        
        # Convert to InternshipListing model
        from app.models.internship import InternshipListing
        internship = InternshipListing(**internship_data)
        
        # Initialize verification service
        from app.services.verification_service import VerificationService
        verification_service = VerificationService(supabase)
        
        # Perform verification
        verification_result = await verification_service.verify_internship(internship)
        
        # Cache verification result in database
        try:
            # Check if verification already exists
            existing_verification = supabase.table('verification_results').select('*').eq('internship_id', internship_id).execute()
            
            verification_dict = {
                'internship_id': internship_id,
                'status': verification_result.status.value,
                'trust_score': verification_result.trust_score,
                'verification_signals': verification_result.verification_signals.model_dump(),
                'red_flags': [flag.model_dump() for flag in verification_result.red_flags],
                'verification_notes': verification_result.verification_notes,
                'last_verified': verification_result.last_verified.isoformat()
            }
            
            if existing_verification.data:
                # Update existing verification
                logger.info(f"Updating existing verification for internship {internship_id}")
                supabase.table('verification_results').update(verification_dict).eq('internship_id', internship_id).execute()
            else:
                # Insert new verification
                logger.info(f"Creating new verification for internship {internship_id}")
                supabase.table('verification_results').insert(verification_dict).execute()
            
            # Also update the internship listing with verification status and trust score
            supabase.table('internship_listings').update({
                'verification_status': verification_result.status.value,
                'trust_score': verification_result.trust_score,
                'red_flags': [flag.model_dump() for flag in verification_result.red_flags]
            }).eq('id', internship_id).execute()
            
        except Exception as e:
            # Log error but don't fail the request - caching is optional
            logger.warning(f"Failed to cache verification result: {e}")
        
        # Return verification result
        formatter = get_response_formatter()
        return formatter.success(
            {
                "internship_id": internship_id,
                "status": verification_result.status.value,
                "trust_score": verification_result.trust_score,
                "verification_signals": verification_result.verification_signals.model_dump(),
                "red_flags": [flag.model_dump() for flag in verification_result.red_flags],
                "verification_notes": verification_result.verification_notes,
                "last_verified": verification_result.last_verified.isoformat()
            },
            f"Verification complete: {verification_result.status.value} (trust score: {verification_result.trust_score})"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in verify_internship: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during verification",
                "details": {"error": str(e)}
            }
        )


@router.post("/{internship_id}/match")
async def calculate_skill_match(
    internship_id: str,
    current_user: dict = Depends(get_current_user),
    service: Optional[InternshipServiceMongo] = Depends(get_internship_service)
):
    """
    Calculate skill match percentage and identify gaps
    
    This endpoint calculates how well a user's skills match an internship's requirements,
    identifies missing skills, and generates a personalized learning path.
    
    **Requirements**: US-4 (4.1-4.7)
    
    **Algorithm**:
    1. Retrieve user profile and internship details
    2. Calculate skill match percentage (required: 70% weight, preferred: 30% weight)
    3. Identify matching skills (intersection)
    4. Identify missing skills (difference)
    5. Generate learning path for missing skills
    6. Cache results in database
    
    **Returns**:
    - match_percentage: int (0-100)
    - matching_skills: List[str]
    - missing_skills: List[str]
    - learning_path: List[LearningPathItem]
    
    **Errors**:
    - 401: Unauthorized (missing or invalid token)
    - 404: Profile or internship not found
    - 422: Cannot calculate match without profile
    - 503: Service unavailable (database not configured)
    """
    try:
        user_id = current_user.get("email") or current_user.get("sub")
        logger.info(f"Calculating skill match for user {user_id} and internship {internship_id}")
        
        # Get user profile
        profile = await service.get_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "PROFILE_NOT_FOUND",
                    "message": "Student profile not found",
                    "details": {
                        "action": "Create a profile at POST /api/internships/profile"
                    }
                }
            )
        
        # Get internship details
        try:
            internship_result = supabase.table('internship_listings').select('*').eq('id', internship_id).execute()
            if not internship_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "INTERNSHIP_NOT_FOUND",
                        "message": f"Internship with ID {internship_id} not found",
                        "details": {}
                    }
                )
            internship_data = internship_result.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve internship {internship_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "DATABASE_ERROR",
                    "message": "Failed to retrieve internship details",
                    "details": {"error": str(e)}
                }
            )
        
        # Initialize matching service
        from app.services.matching_service import MatchingService
        matching_service = MatchingService(supabase)
        
        # Create skill match with learning path
        skill_match = await matching_service.create_skill_match(
            user_id=user_id,
            internship_id=internship_id,
            user_skills=profile.skills,
            required_skills=internship_data.get('required_skills', []),
            preferred_skills=internship_data.get('preferred_skills', [])
        )
        
        # Cache the result in database
        try:
            # Check if match already exists
            existing_match = supabase.table('skill_matches').select('*').eq('user_id', user_id).eq('internship_id', internship_id).execute()
            
            match_dict = {
                'user_id': user_id,
                'internship_id': internship_id,
                'match_percentage': skill_match.match_percentage,
                'matching_skills': skill_match.matching_skills,
                'missing_skills': skill_match.missing_skills,
                'learning_path': [item.model_dump() for item in skill_match.learning_path]
            }
            
            if existing_match.data:
                # Update existing match
                logger.info(f"Updating existing skill match for user {user_id} and internship {internship_id}")
                supabase.table('skill_matches').update(match_dict).eq('user_id', user_id).eq('internship_id', internship_id).execute()
            else:
                # Insert new match
                logger.info(f"Creating new skill match for user {user_id} and internship {internship_id}")
                supabase.table('skill_matches').insert(match_dict).execute()
        except Exception as e:
            # Log error but don't fail the request - caching is optional
            logger.warning(f"Failed to cache skill match: {e}")
        
        # Return the skill match result
        formatter = get_response_formatter()
        return formatter.success(
            {
                "match_percentage": skill_match.match_percentage,
                "matching_skills": skill_match.matching_skills,
                "missing_skills": skill_match.missing_skills,
                "learning_path": [item.model_dump() for item in skill_match.learning_path]
            },
            f"Skill match calculated: {skill_match.match_percentage}% match"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in calculate_skill_match: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)}
            }
        )


@router.get("/{internship_id}/guidance")
async def get_career_guidance(
    internship_id: str,
    current_user: dict = Depends(get_current_user),
    service: Optional[InternshipServiceMongo] = Depends(get_internship_service)
):
    """
    Get AI-powered career guidance for internship
    
    This endpoint generates personalized career guidance using AI, explaining why
    an internship is a good fit, what skills to improve, recommended certifications,
    and project ideas to strengthen the application.
    
    **Requirements**: US-5 (5.1-5.6)
    
    **Process**:
    1. Retrieve user profile
    2. Retrieve internship details
    3. Calculate or retrieve skill match
    4. Generate AI-powered guidance with:
       - Why this internship is a good fit
       - Skills to improve
       - Recommended certifications
       - Project ideas to strengthen resume
    
    **Returns**:
    - why_good_fit: Personalized explanation of fit (2-3 sentences)
    - skills_to_improve: List of skills to focus on
    - certifications: List of recommended certifications
    - projects: List of project ideas
    
    **Errors**:
    - 401: Unauthorized (missing or invalid token)
    - 404: Profile or internship not found
    - 422: Cannot generate guidance without profile
    - 503: AI service unavailable
    """
    try:
        user_id = current_user.get("email") or current_user.get("sub")
        logger.info(f"Generating career guidance for user {user_id} and internship {internship_id}")
        
        # Get user profile
        profile = await service.get_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "PROFILE_NOT_FOUND",
                    "message": "Student profile not found. Please create a profile first.",
                    "details": {
                        "action": "Create a profile at POST /api/internships/profile"
                    }
                }
            )
        
        # Get internship details
        try:
            internship_result = supabase.table('internship_listings').select('*').eq('id', internship_id).execute()
            if not internship_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "INTERNSHIP_NOT_FOUND",
                        "message": f"Internship with ID {internship_id} not found",
                        "details": {}
                    }
                )
            internship_data = internship_result.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve internship {internship_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "DATABASE_ERROR",
                    "message": "Failed to retrieve internship details",
                    "details": {"error": str(e)}
                }
            )
        
        # Get or calculate skill match
        skill_match_data = None
        try:
            # Try to get cached skill match
            skill_match_result = supabase.table('skill_matches').select('*').eq('user_id', user_id).eq('internship_id', internship_id).execute()
            
            if skill_match_result.data:
                skill_match_data = skill_match_result.data[0]
                logger.info(f"Using cached skill match for user {user_id} and internship {internship_id}")
            else:
                # Calculate skill match if not cached
                logger.info(f"Calculating skill match for user {user_id} and internship {internship_id}")
                from app.services.matching_service import MatchingService
                matching_service = MatchingService(supabase)
                
                skill_match = await matching_service.create_skill_match(
                    user_id=user_id,
                    internship_id=internship_id,
                    user_skills=profile.skills,
                    required_skills=internship_data.get('required_skills', []),
                    preferred_skills=internship_data.get('preferred_skills', [])
                )
                
                skill_match_data = {
                    'match_percentage': skill_match.match_percentage,
                    'matching_skills': skill_match.matching_skills,
                    'missing_skills': skill_match.missing_skills,
                    'learning_path': [item.model_dump() for item in skill_match.learning_path]
                }
                
                # Cache the skill match
                try:
                    supabase.table('skill_matches').insert({
                        'user_id': user_id,
                        'internship_id': internship_id,
                        **skill_match_data
                    }).execute()
                except Exception as e:
                    logger.warning(f"Failed to cache skill match: {e}")
        
        except Exception as e:
            logger.error(f"Failed to get/calculate skill match: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "SKILL_MATCH_ERROR",
                    "message": "Failed to calculate skill match",
                    "details": {"error": str(e)}
                }
            )
        
        # Generate AI-powered career guidance
        try:
            from ai.internship_ai import get_internship_ai
            ai_service = get_internship_ai()
            
            # Prepare data for AI
            user_profile_dict = {
                'user_id': user_id,
                'graduation_year': profile.graduation_year,
                'current_semester': profile.current_semester,
                'degree': profile.degree,
                'branch': profile.branch,
                'skills': profile.skills,
                'preferred_roles': profile.preferred_roles
            }
            
            internship_dict = {
                'id': internship_id,
                'title': internship_data.get('title', ''),
                'company': internship_data.get('company', ''),
                'required_skills': internship_data.get('required_skills', []),
                'preferred_skills': internship_data.get('preferred_skills', []),
                'responsibilities': internship_data.get('responsibilities', [])
            }
            
            # Generate guidance
            guidance = await ai_service.generate_career_guidance(
                user_profile=user_profile_dict,
                internship=internship_dict,
                skill_match=skill_match_data
            )
            
            logger.info(f"Career guidance generated successfully for user {user_id} and internship {internship_id}")
            
            # Return guidance
            formatter = get_response_formatter()
            return formatter.success(
                guidance,
                "Career guidance generated successfully"
            )
            
        except ValueError as e:
            logger.error(f"AI service error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "AI_SERVICE_ERROR",
                    "message": "Career guidance generation temporarily unavailable",
                    "details": {
                        "error": str(e),
                        "retry_after": 60
                    }
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error generating career guidance: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred while generating guidance",
                    "details": {"error": str(e)}
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_career_guidance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)}
            }
        )


@router.get("/{internship_id}/readiness")
async def calculate_readiness_score(
    internship_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate readiness score and recommendations
    
    **Requirements**: US-6 (6.1-6.5)
    
    **Status**: Not yet implemented
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Readiness score endpoint not yet implemented"
    )


@router.post("/report-scam")
async def report_scam(
    report: ScamReportCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Report suspicious internship listing
    
    **Requirements**: US-7 (7.3)
    
    **Status**: Not yet implemented
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Scam report endpoint not yet implemented"
    )


@router.get("/alerts")
async def get_user_alerts(
    limit: int = Query(20, le=100, description="Maximum number of alerts to return"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get personalized alerts and notifications
    
    **Requirements**: US-8 (8.1-8.5)
    
    **Status**: Not yet implemented
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Alerts endpoint not yet implemented"
    )


@router.patch("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark alert as read
    
    **Requirements**: US-8 (8.1-8.5)
    
    **Status**: Not yet implemented
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Mark alert read endpoint not yet implemented"
    )
