"""
Internship Service - Core business logic for internship discovery

This service handles student profile management, internship search, verification,
skill matching, readiness scoring, and career guidance.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
from supabase import Client
from postgrest.exceptions import APIError

from app.models.internship import (
    StudentProfileCreate,
    StudentProfile,
    StudentProfileUpdate,
)

logger = logging.getLogger(__name__)


class ProfileValidationError(Exception):
    """Custom exception for profile validation errors"""
    pass


class ProfileNotFoundError(Exception):
    """Custom exception for profile not found errors"""
    pass


class DatabaseOperationError(Exception):
    """Custom exception for database operation errors"""
    pass


class InternshipService:
    """Core business logic for internship discovery"""
    
    def __init__(self, supabase_client: Client):
        """
        Initialize the internship service
        
        Args:
            supabase_client: Supabase client for database operations
        """
        self.db = supabase_client
        logger.info("InternshipService initialized")
    
    def _validate_profile_data(self, profile_data: StudentProfileCreate) -> None:
        """
        Validate profile data before database operations
        
        Args:
            profile_data: Student profile data to validate
            
        Raises:
            ProfileValidationError: If validation fails
        """
        # Validate graduation year
        current_year = datetime.now().year
        if profile_data.graduation_year < current_year:
            raise ProfileValidationError(
                f"Graduation year must be {current_year} or later"
            )
        
        if profile_data.graduation_year > current_year + 10:
            raise ProfileValidationError(
                f"Graduation year cannot be more than 10 years in the future"
            )
        
        # Validate semester
        if not (1 <= profile_data.current_semester <= 8):
            raise ProfileValidationError(
                "Current semester must be between 1 and 8"
            )
        
        # Validate degree and branch
        if not profile_data.degree or not profile_data.degree.strip():
            raise ProfileValidationError("Degree is required")
        
        if not profile_data.branch or not profile_data.branch.strip():
            raise ProfileValidationError("Branch is required")
        
        # Validate skills list
        if profile_data.skills:
            if len(profile_data.skills) > 50:
                raise ProfileValidationError(
                    "Maximum 50 skills allowed"
                )
            # Remove empty strings and duplicates
            profile_data.skills = list(set([s.strip() for s in profile_data.skills if s.strip()]))
        
        # Validate preferred roles
        if profile_data.preferred_roles:
            if len(profile_data.preferred_roles) > 20:
                raise ProfileValidationError(
                    "Maximum 20 preferred roles allowed"
                )
            profile_data.preferred_roles = list(set([r.strip() for r in profile_data.preferred_roles if r.strip()]))
        
        # Validate target companies
        if profile_data.target_companies:
            if len(profile_data.target_companies) > 30:
                raise ProfileValidationError(
                    "Maximum 30 target companies allowed"
                )
            profile_data.target_companies = list(set([c.strip() for c in profile_data.target_companies if c.strip()]))
        
        logger.debug(f"Profile data validation passed for semester {profile_data.current_semester}")
    
    async def create_profile(self, user_id: str, profile_data: StudentProfileCreate) -> StudentProfile:
        """
        Create or update student profile with comprehensive validation
        
        Args:
            user_id: User ID from authentication
            profile_data: Student profile data
            
        Returns:
            Created/updated student profile
            
        Raises:
            ProfileValidationError: If validation fails
            DatabaseOperationError: If database operation fails
        """
        try:
            logger.info(f"Creating/updating profile for user: {user_id}")
            
            # Validate profile data
            self._validate_profile_data(profile_data)
            
            # Convert Pydantic model to dict
            profile_dict = profile_data.model_dump()
            profile_dict['user_id'] = user_id
            
            # Convert enum values to strings if needed
            if profile_data.internship_type:
                profile_dict['internship_type'] = profile_data.internship_type.value
            if profile_data.compensation_preference:
                profile_dict['compensation_preference'] = profile_data.compensation_preference.value
            
            # Check if profile already exists
            existing = self.db.table('student_profiles').select('*').eq('user_id', user_id).execute()
            
            if existing.data:
                # Update existing profile
                logger.info(f"Updating existing profile for user: {user_id}")
                result = self.db.table('student_profiles').update(profile_dict).eq('user_id', user_id).execute()
            else:
                # Create new profile
                logger.info(f"Creating new profile for user: {user_id}")
                result = self.db.table('student_profiles').insert(profile_dict).execute()
            
            if not result.data:
                raise DatabaseOperationError("Failed to create/update profile - no data returned")
            
            logger.info(f"Profile successfully created/updated for user: {user_id}")
            return StudentProfile(**result.data[0])
            
        except ProfileValidationError:
            logger.warning(f"Profile validation failed for user: {user_id}")
            raise
        except APIError as e:
            logger.error(f"Supabase API error for user {user_id}: {e}")
            raise DatabaseOperationError(f"Database operation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating profile for user {user_id}: {e}")
            raise DatabaseOperationError(f"Failed to create/update profile: {str(e)}")
    
    async def get_profile(self, user_id: str) -> Optional[StudentProfile]:
        """
        Retrieve student profile with error handling
        
        Args:
            user_id: User ID from authentication
            
        Returns:
            Student profile if found, None otherwise
            
        Raises:
            DatabaseOperationError: If database operation fails
        """
        try:
            logger.info(f"Retrieving profile for user: {user_id}")
            
            result = self.db.table('student_profiles').select('*').eq('user_id', user_id).execute()
            
            if not result.data:
                logger.info(f"No profile found for user: {user_id}")
                return None
            
            logger.info(f"Profile retrieved successfully for user: {user_id}")
            return StudentProfile(**result.data[0])
            
        except APIError as e:
            logger.error(f"Supabase API error retrieving profile for user {user_id}: {e}")
            raise DatabaseOperationError(f"Failed to retrieve profile: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving profile for user {user_id}: {e}")
            raise DatabaseOperationError(f"Failed to retrieve profile: {str(e)}")
    
    async def update_profile(self, user_id: str, profile_data: StudentProfileUpdate) -> StudentProfile:
        """
        Update existing student profile with validation
        
        Args:
            user_id: User ID from authentication
            profile_data: Updated profile data (only provided fields will be updated)
            
        Returns:
            Updated student profile
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
            ProfileValidationError: If validation fails
            DatabaseOperationError: If database operation fails
        """
        try:
            logger.info(f"Updating profile for user: {user_id}")
            
            # Check if profile exists
            existing_profile = await self.get_profile(user_id)
            if not existing_profile:
                raise ProfileNotFoundError(f"Profile not found for user: {user_id}")
            
            # Only include fields that were actually provided
            update_dict = profile_data.model_dump(exclude_unset=True)
            
            if not update_dict:
                # No fields to update, just return existing profile
                logger.info(f"No fields to update for user: {user_id}")
                return existing_profile
            
            # Validate updated fields
            if 'graduation_year' in update_dict:
                current_year = datetime.now().year
                if update_dict['graduation_year'] < current_year:
                    raise ProfileValidationError(
                        f"Graduation year must be {current_year} or later"
                    )
                if update_dict['graduation_year'] > current_year + 10:
                    raise ProfileValidationError(
                        f"Graduation year cannot be more than 10 years in the future"
                    )
            
            if 'current_semester' in update_dict:
                if not (1 <= update_dict['current_semester'] <= 8):
                    raise ProfileValidationError(
                        "Current semester must be between 1 and 8"
                    )
            
            # Validate and clean skills
            if 'skills' in update_dict and update_dict['skills']:
                if len(update_dict['skills']) > 50:
                    raise ProfileValidationError("Maximum 50 skills allowed")
                update_dict['skills'] = list(set([s.strip() for s in update_dict['skills'] if s.strip()]))
            
            # Validate and clean preferred roles
            if 'preferred_roles' in update_dict and update_dict['preferred_roles']:
                if len(update_dict['preferred_roles']) > 20:
                    raise ProfileValidationError("Maximum 20 preferred roles allowed")
                update_dict['preferred_roles'] = list(set([r.strip() for r in update_dict['preferred_roles'] if r.strip()]))
            
            # Validate and clean target companies
            if 'target_companies' in update_dict and update_dict['target_companies']:
                if len(update_dict['target_companies']) > 30:
                    raise ProfileValidationError("Maximum 30 target companies allowed")
                update_dict['target_companies'] = list(set([c.strip() for c in update_dict['target_companies'] if c.strip()]))
            
            # Convert enum values to strings if needed
            if 'internship_type' in update_dict and update_dict['internship_type']:
                update_dict['internship_type'] = update_dict['internship_type'].value
            if 'compensation_preference' in update_dict and update_dict['compensation_preference']:
                update_dict['compensation_preference'] = update_dict['compensation_preference'].value
            
            result = self.db.table('student_profiles').update(update_dict).eq('user_id', user_id).execute()
            
            if not result.data:
                raise DatabaseOperationError("Failed to update profile - no data returned")
            
            logger.info(f"Profile successfully updated for user: {user_id}")
            return StudentProfile(**result.data[0])
            
        except (ProfileNotFoundError, ProfileValidationError):
            raise
        except APIError as e:
            logger.error(f"Supabase API error updating profile for user {user_id}: {e}")
            raise DatabaseOperationError(f"Failed to update profile: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating profile for user {user_id}: {e}")
            raise DatabaseOperationError(f"Failed to update profile: {str(e)}")
    
    async def delete_profile(self, user_id: str) -> bool:
        """
        Delete student profile with error handling
        
        Args:
            user_id: User ID from authentication
            
        Returns:
            True if deleted successfully
            
        Raises:
            DatabaseOperationError: If database operation fails
        """
        try:
            logger.info(f"Deleting profile for user: {user_id}")
            
            result = self.db.table('student_profiles').delete().eq('user_id', user_id).execute()
            
            logger.info(f"Profile successfully deleted for user: {user_id}")
            return True
            
        except APIError as e:
            logger.error(f"Supabase API error deleting profile for user {user_id}: {e}")
            raise DatabaseOperationError(f"Failed to delete profile: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting profile for user {user_id}: {e}")
            raise DatabaseOperationError(f"Failed to delete profile: {str(e)}")
