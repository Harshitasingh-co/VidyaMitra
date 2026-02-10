"""
Calendar Service - Internship calendar and timeline logic

This service handles semester-to-calendar mapping, application window calculations,
deadline tracking, and preparation window recommendations.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)


class CalendarService:
    """Internship calendar and timeline logic"""
    
    # Semester mapping with application windows and internship periods
    SEMESTER_MAPPING = {
        1: {
            "focus": "Skill Building",
            "description": "Focus on building foundational skills and academic performance",
            "internships": [],
            "recommendation": "Too early for internships. Focus on coursework and skill development."
        },
        2: {
            "focus": "Skill Building",
            "description": "Continue skill development and explore areas of interest",
            "internships": [],
            "recommendation": "Too early for internships. Build projects and learn new technologies."
        },
        3: {
            "focus": "Summer Internships",
            "description": "Apply for summer internships to gain industry experience",
            "apply_window": "Jan-Mar",
            "internship_period": "May-Jul",
            "apply_months": [1, 2, 3],
            "internship_months": [5, 6, 7],
            "recommendation": "Apply for Summer Internships between January and March for May-July positions."
        },
        4: {
            "focus": "Summer Internships",
            "description": "Prime time for summer internship applications",
            "apply_window": "Jan-Mar",
            "internship_period": "May-Jul",
            "apply_months": [1, 2, 3],
            "internship_months": [5, 6, 7],
            "recommendation": "Apply for Summer Internships between January and March for May-July positions."
        },
        5: {
            "focus": "Winter/Summer Internships",
            "description": "Apply for winter internships or prepare for next summer",
            "apply_window": "Aug-Oct",
            "internship_period": "Dec-Jan",
            "apply_months": [8, 9, 10],
            "internship_months": [12, 1],
            "recommendation": "Apply for Winter Internships between August and October for December-January positions."
        },
        6: {
            "focus": "Winter/Summer Internships",
            "description": "Continue applying for winter internships or summer opportunities",
            "apply_window": "Aug-Oct",
            "internship_period": "Dec-Jan",
            "apply_months": [8, 9, 10],
            "internship_months": [12, 1],
            "recommendation": "Apply for Winter Internships between August and October for December-January positions."
        },
        7: {
            "focus": "Final Year Internships",
            "description": "Apply for final year internships and pre-placement opportunities",
            "apply_window": "Jul-Sep",
            "internship_period": "Jan-Apr",
            "apply_months": [7, 8, 9],
            "internship_months": [1, 2, 3, 4],
            "recommendation": "Apply for Final Year Internships between July and September for January-April positions."
        },
        8: {
            "focus": "Pre-Placement",
            "description": "Focus on placement preparation and final projects",
            "apply_window": "Ongoing",
            "internship_period": "Flexible",
            "apply_months": list(range(1, 13)),
            "internship_months": list(range(1, 13)),
            "recommendation": "Focus on placement preparation. Apply for short-term or flexible internships as needed."
        }
    }
    
    def __init__(self):
        """Initialize the calendar service"""
        logger.info("CalendarService initialized")
    
    def get_calendar_for_semester(self, semester: int, current_month: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate personalized internship calendar based on semester
        
        Args:
            semester: Current semester (1-8)
            current_month: Current month (1-12), defaults to current date
            
        Returns:
            Dictionary containing calendar information with:
            - semester: The input semester
            - focus: Main focus area for this semester
            - description: Detailed description
            - apply_window: Application window (if applicable)
            - internship_period: Internship period (if applicable)
            - recommendation: Personalized recommendation
            - current_status: Status based on current month
            - upcoming_deadlines: List of upcoming deadlines
            
        Raises:
            ValueError: If semester is not between 1 and 8
        """
        if not (1 <= semester <= 8):
            logger.error(f"Invalid semester value: {semester}")
            raise ValueError(f"Semester must be between 1 and 8, got {semester}")
        
        if current_month is None:
            current_month = datetime.now().month
        
        if not (1 <= current_month <= 12):
            logger.error(f"Invalid month value: {current_month}")
            raise ValueError(f"Month must be between 1 and 12, got {current_month}")
        
        logger.info(f"Generating calendar for semester {semester}, current month {current_month}")
        
        # Get base calendar info from mapping
        calendar_info = self.SEMESTER_MAPPING[semester].copy()
        calendar_info['semester'] = semester
        
        # Determine current status based on month
        if semester in [1, 2]:
            # Skill building semesters - no application windows
            calendar_info['current_status'] = "Focus on skill development"
        else:
            apply_months = calendar_info.get('apply_months', [])
            internship_months = calendar_info.get('internship_months', [])
            
            if current_month in apply_months:
                calendar_info['current_status'] = "Application window is OPEN - Apply now!"
            elif current_month in internship_months:
                calendar_info['current_status'] = "Internship period - Focus on current internship or prepare for next cycle"
            else:
                # Calculate months until next application window
                months_until_window = self._calculate_months_until_window(current_month, apply_months)
                if months_until_window <= 2:
                    calendar_info['current_status'] = f"Application window opens in {months_until_window} month(s) - Start preparing!"
                else:
                    calendar_info['current_status'] = f"Preparation phase - {months_until_window} month(s) until application window"
        
        # Get upcoming deadlines
        calendar_info['upcoming_deadlines'] = self.get_upcoming_deadlines(semester, current_month)
        
        logger.debug(f"Calendar generated for semester {semester}: {calendar_info['focus']}")
        return calendar_info
    
    def _calculate_months_until_window(self, current_month: int, apply_months: List[int]) -> int:
        """
        Calculate months until next application window
        
        Args:
            current_month: Current month (1-12)
            apply_months: List of application months
            
        Returns:
            Number of months until next application window
        """
        if not apply_months:
            return 0
        
        # Find the next application month
        future_months = [m for m in apply_months if m > current_month]
        
        if future_months:
            # Next window is in the same year
            return min(future_months) - current_month
        else:
            # Next window is in the next year
            return (12 - current_month) + min(apply_months)
    
    def get_upcoming_deadlines(self, semester: int, current_month: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get upcoming application deadlines based on semester
        
        Args:
            semester: Current semester (1-8)
            current_month: Current month (1-12), defaults to current date
            
        Returns:
            List of deadline dictionaries with:
            - type: Type of deadline (e.g., "Application Window Opens")
            - month: Month name
            - description: Description of the deadline
            
        Raises:
            ValueError: If semester is not between 1 and 8
        """
        if not (1 <= semester <= 8):
            logger.error(f"Invalid semester value: {semester}")
            raise ValueError(f"Semester must be between 1 and 8, got {semester}")
        
        if current_month is None:
            current_month = datetime.now().month
        
        logger.info(f"Getting upcoming deadlines for semester {semester}, current month {current_month}")
        
        deadlines = []
        
        # For skill-building semesters, no deadlines
        if semester in [1, 2]:
            return deadlines
        
        calendar_info = self.SEMESTER_MAPPING[semester]
        apply_months = calendar_info.get('apply_months', [])
        internship_months = calendar_info.get('internship_months', [])
        
        # Month names for display
        month_names = [
            "", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        # Add application window deadlines
        if apply_months:
            first_apply_month = min(apply_months)
            last_apply_month = max(apply_months)
            
            # Application window opens
            if first_apply_month >= current_month or first_apply_month < current_month:
                deadlines.append({
                    "type": "Application Window Opens",
                    "month": month_names[first_apply_month],
                    "month_number": first_apply_month,
                    "description": f"Start applying for {calendar_info['focus'].lower()}"
                })
            
            # Application window closes
            if last_apply_month >= current_month or last_apply_month < current_month:
                deadlines.append({
                    "type": "Application Window Closes",
                    "month": month_names[last_apply_month],
                    "month_number": last_apply_month,
                    "description": f"Last month to apply for {calendar_info['focus'].lower()}"
                })
        
        # Add internship period deadlines
        if internship_months:
            first_internship_month = min(internship_months)
            
            deadlines.append({
                "type": "Internship Starts",
                "month": month_names[first_internship_month],
                "month_number": first_internship_month,
                "description": f"Expected start date for {calendar_info['focus'].lower()}"
            })
        
        # Sort deadlines by month (considering year wrap-around)
        deadlines.sort(key=lambda x: x['month_number'] if x['month_number'] >= current_month else x['month_number'] + 12)
        
        logger.debug(f"Found {len(deadlines)} upcoming deadlines for semester {semester}")
        return deadlines
    
    def calculate_preparation_window(self, semester: int, target_month: Optional[int] = None) -> Dict[str, Any]:
        """
        Calculate how much time to prepare for internship applications
        
        Args:
            semester: Current semester (1-8)
            target_month: Target application month, defaults to first month of application window
            
        Returns:
            Dictionary containing:
            - semester: Input semester
            - current_month: Current month
            - target_month: Target application month
            - months_to_prepare: Number of months until target
            - weeks_to_prepare: Number of weeks until target
            - preparation_status: Status message
            - recommended_actions: List of recommended preparation actions
            
        Raises:
            ValueError: If semester is not between 1 and 8
        """
        if not (1 <= semester <= 8):
            logger.error(f"Invalid semester value: {semester}")
            raise ValueError(f"Semester must be between 1 and 8, got {semester}")
        
        current_date = datetime.now()
        current_month = current_date.month
        
        logger.info(f"Calculating preparation window for semester {semester}")
        
        # For skill-building semesters
        if semester in [1, 2]:
            return {
                "semester": semester,
                "current_month": current_month,
                "target_month": None,
                "months_to_prepare": None,
                "weeks_to_prepare": None,
                "preparation_status": "Focus on skill building - no immediate internship applications",
                "recommended_actions": [
                    "Build strong foundation in core subjects",
                    "Learn programming languages and tools",
                    "Work on small projects to practice",
                    "Maintain good academic performance"
                ]
            }
        
        calendar_info = self.SEMESTER_MAPPING[semester]
        apply_months = calendar_info.get('apply_months', [])
        
        # Determine target month
        if target_month is None:
            target_month = min(apply_months) if apply_months else current_month
        
        # Calculate months and weeks to prepare
        if target_month >= current_month:
            months_to_prepare = target_month - current_month
            target_date = datetime(current_date.year, target_month, 1)
        else:
            # Target is in next year
            months_to_prepare = (12 - current_month) + target_month
            target_date = datetime(current_date.year + 1, target_month, 1)
        
        weeks_to_prepare = (target_date - current_date).days // 7
        
        # Determine preparation status
        if months_to_prepare == 0:
            preparation_status = "Application window is NOW - Apply immediately!"
        elif months_to_prepare == 1:
            preparation_status = "Application window opens next month - Final preparations!"
        elif months_to_prepare <= 2:
            preparation_status = f"Application window opens in {months_to_prepare} months - Intensive preparation phase"
        else:
            preparation_status = f"You have {months_to_prepare} months to prepare - Good time to build skills"
        
        # Recommended actions based on time available
        if months_to_prepare <= 1:
            recommended_actions = [
                "Polish your resume immediately",
                "Prepare for technical interviews",
                "Research target companies",
                "Practice coding problems daily",
                "Update LinkedIn profile"
            ]
        elif months_to_prepare <= 3:
            recommended_actions = [
                "Complete relevant online courses/certifications",
                "Build 2-3 strong projects for your portfolio",
                "Start practicing coding problems",
                "Update resume with recent projects",
                "Network with professionals in your field"
            ]
        else:
            recommended_actions = [
                "Learn new technologies relevant to your field",
                "Build comprehensive projects",
                "Contribute to open source",
                "Develop strong problem-solving skills",
                "Build a professional online presence"
            ]
        
        result = {
            "semester": semester,
            "current_month": current_month,
            "target_month": target_month,
            "months_to_prepare": months_to_prepare,
            "weeks_to_prepare": weeks_to_prepare,
            "preparation_status": preparation_status,
            "recommended_actions": recommended_actions
        }
        
        logger.debug(f"Preparation window calculated: {months_to_prepare} months, {weeks_to_prepare} weeks")
        return result
