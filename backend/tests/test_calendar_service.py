"""
Property-based test for Semester-to-Calendar Mapping

This test validates Property 3: Semester-to-Calendar Mapping
For any valid semester (1-8), the calendar service should return a valid application
window with defined focus, apply window, and internship period (or skill-building
guidance for semesters 1-2).

Validates: Requirements 2.1, 2.7
"""
import pytest
from hypothesis import given, strategies as st, settings
from app.services.calendar_service import CalendarService


# ============================================================================
# Hypothesis Strategies for generating test data
# ============================================================================

# Strategy for valid semesters (1-8)
valid_semester_strategy = st.integers(min_value=1, max_value=8)

# Strategy for valid months (1-12)
valid_month_strategy = st.integers(min_value=1, max_value=12)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def calendar_service():
    """Create a CalendarService instance"""
    return CalendarService()


# ============================================================================
# Property 3: Semester-to-Calendar Mapping
# Feature: internship-discovery, Property 3: Semester-to-Calendar Mapping
# Validates: Requirements 2.1, 2.7
# ============================================================================

@pytest.mark.property
@pytest.mark.internship
@settings(max_examples=100)
@given(semester=valid_semester_strategy)
def test_semester_to_calendar_mapping_property(semester: int, calendar_service):
    """
    Property 3: Semester-to-Calendar Mapping
    
    For any valid semester (1-8), the calendar service should return a valid
    application window with defined focus, apply window, and internship period
    (or skill-building guidance for semesters 1-2).
    
    This validates that:
    - Every semester maps to a valid calendar (Requirement 2.1)
    - System provides preparation window recommendations (Requirement 2.7)
    
    Universal property: For all valid semesters, the calendar service returns
    a well-formed calendar response with all required fields.
    """
    # Get calendar for the semester
    calendar = calendar_service.get_calendar_for_semester(semester)
    
    # Verify calendar is returned (not None)
    assert calendar is not None, \
        f"Calendar should not be None for semester {semester}"
    
    # Verify required fields are present
    assert "semester" in calendar, \
        f"Calendar should contain 'semester' field for semester {semester}"
    assert "focus" in calendar, \
        f"Calendar should contain 'focus' field for semester {semester}"
    assert "description" in calendar, \
        f"Calendar should contain 'description' field for semester {semester}"
    assert "recommendation" in calendar, \
        f"Calendar should contain 'recommendation' field for semester {semester}"
    assert "current_status" in calendar, \
        f"Calendar should contain 'current_status' field for semester {semester}"
    assert "upcoming_deadlines" in calendar, \
        f"Calendar should contain 'upcoming_deadlines' field for semester {semester}"
    
    # Verify semester field matches input
    assert calendar["semester"] == semester, \
        f"Calendar semester {calendar['semester']} should match input semester {semester}"
    
    # Verify focus is a non-empty string
    assert isinstance(calendar["focus"], str), \
        f"Focus should be a string for semester {semester}"
    assert len(calendar["focus"]) > 0, \
        f"Focus should not be empty for semester {semester}"
    
    # Verify description is a non-empty string
    assert isinstance(calendar["description"], str), \
        f"Description should be a string for semester {semester}"
    assert len(calendar["description"]) > 0, \
        f"Description should not be empty for semester {semester}"
    
    # Verify recommendation is a non-empty string
    assert isinstance(calendar["recommendation"], str), \
        f"Recommendation should be a string for semester {semester}"
    assert len(calendar["recommendation"]) > 0, \
        f"Recommendation should not be empty for semester {semester}"
    
    # Verify current_status is a non-empty string
    assert isinstance(calendar["current_status"], str), \
        f"Current status should be a string for semester {semester}"
    assert len(calendar["current_status"]) > 0, \
        f"Current status should not be empty for semester {semester}"
    
    # Verify upcoming_deadlines is a list
    assert isinstance(calendar["upcoming_deadlines"], list), \
        f"Upcoming deadlines should be a list for semester {semester}"
    
    # Semester-specific validations
    if semester in [1, 2]:
        # Skill-building semesters should not have application windows
        assert "apply_window" not in calendar or calendar.get("internships") == [], \
            f"Semester {semester} should focus on skill building, not internships"
        
        # Should have skill-building focus
        assert "Skill Building" in calendar["focus"], \
            f"Semester {semester} should have 'Skill Building' focus"
        
        # Should have empty internships list or no internships field
        assert calendar.get("internships", []) == [], \
            f"Semester {semester} should have no internships"
    
    else:
        # Internship semesters (3-8) should have application windows
        assert "apply_window" in calendar, \
            f"Semester {semester} should have 'apply_window' field"
        assert "internship_period" in calendar, \
            f"Semester {semester} should have 'internship_period' field"
        
        # Verify apply_window is a non-empty string
        assert isinstance(calendar["apply_window"], str), \
            f"Apply window should be a string for semester {semester}"
        assert len(calendar["apply_window"]) > 0, \
            f"Apply window should not be empty for semester {semester}"
        
        # Verify internship_period is a non-empty string
        assert isinstance(calendar["internship_period"], str), \
            f"Internship period should be a string for semester {semester}"
        assert len(calendar["internship_period"]) > 0, \
            f"Internship period should not be empty for semester {semester}"
        
        # Verify apply_months exists and is a list
        assert "apply_months" in calendar, \
            f"Semester {semester} should have 'apply_months' field"
        assert isinstance(calendar["apply_months"], list), \
            f"Apply months should be a list for semester {semester}"
        assert len(calendar["apply_months"]) > 0, \
            f"Apply months should not be empty for semester {semester}"
        
        # Verify all apply_months are valid (1-12)
        for month in calendar["apply_months"]:
            assert 1 <= month <= 12, \
                f"Apply month {month} should be between 1 and 12 for semester {semester}"
        
        # Verify internship_months exists and is a list
        assert "internship_months" in calendar, \
            f"Semester {semester} should have 'internship_months' field"
        assert isinstance(calendar["internship_months"], list), \
            f"Internship months should be a list for semester {semester}"
        assert len(calendar["internship_months"]) > 0, \
            f"Internship months should not be empty for semester {semester}"
        
        # Verify all internship_months are valid (1-12)
        for month in calendar["internship_months"]:
            assert 1 <= month <= 12, \
                f"Internship month {month} should be between 1 and 12 for semester {semester}"


@pytest.mark.property
@pytest.mark.internship
@settings(max_examples=100)
@given(
    semester=valid_semester_strategy,
    current_month=valid_month_strategy
)
def test_semester_to_calendar_mapping_with_month_property(
    semester: int,
    current_month: int,
    calendar_service
):
    """
    Property 3 (Extended): Semester-to-Calendar Mapping with Current Month
    
    For any valid semester (1-8) and any valid month (1-12), the calendar service
    should return a valid application window with appropriate current_status based
    on the current month.
    
    This validates that:
    - Calendar generation works for any month of the year
    - Current status is appropriately set based on the month
    - Preparation window recommendations are provided (Requirement 2.7)
    """
    # Get calendar for the semester with specific month
    calendar = calendar_service.get_calendar_for_semester(semester, current_month)
    
    # Verify calendar is returned
    assert calendar is not None, \
        f"Calendar should not be None for semester {semester}, month {current_month}"
    
    # Verify all required fields are present
    assert "semester" in calendar
    assert "focus" in calendar
    assert "description" in calendar
    assert "recommendation" in calendar
    assert "current_status" in calendar
    assert "upcoming_deadlines" in calendar
    
    # Verify semester matches
    assert calendar["semester"] == semester
    
    # Verify current_status is set and non-empty
    assert isinstance(calendar["current_status"], str)
    assert len(calendar["current_status"]) > 0
    
    # For internship semesters, verify status is contextual
    if semester not in [1, 2]:
        # Status should mention one of: application, internship, preparation, or open
        status_lower = calendar["current_status"].lower()
        assert any(keyword in status_lower for keyword in [
            "application", "internship", "preparation", "open", "focus", "prepare"
        ]), f"Current status should be contextual for semester {semester}, month {current_month}"


# ============================================================================
# Additional Unit Tests for Calendar Service Edge Cases
# ============================================================================

@pytest.mark.unit
@pytest.mark.internship
def test_calendar_for_semester_1(calendar_service):
    """Test calendar for semester 1 (skill building)"""
    calendar = calendar_service.get_calendar_for_semester(1)
    
    assert calendar["semester"] == 1
    assert calendar["focus"] == "Skill Building"
    assert len(calendar["description"]) > 0
    assert calendar.get("internships", []) == []
    assert "apply_window" not in calendar or calendar.get("internships") == []


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_for_semester_2(calendar_service):
    """Test calendar for semester 2 (skill building)"""
    calendar = calendar_service.get_calendar_for_semester(2)
    
    assert calendar["semester"] == 2
    assert calendar["focus"] == "Skill Building"
    assert len(calendar["description"]) > 0
    assert calendar.get("internships", []) == []


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_for_semester_3(calendar_service):
    """Test calendar for semester 3 (summer internships)"""
    calendar = calendar_service.get_calendar_for_semester(3)
    
    assert calendar["semester"] == 3
    assert calendar["focus"] == "Summer Internships"
    assert calendar["apply_window"] == "Jan-Mar"
    assert calendar["internship_period"] == "May-Jul"
    assert calendar["apply_months"] == [1, 2, 3]
    assert calendar["internship_months"] == [5, 6, 7]


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_for_semester_4(calendar_service):
    """Test calendar for semester 4 (summer internships)"""
    calendar = calendar_service.get_calendar_for_semester(4)
    
    assert calendar["semester"] == 4
    assert calendar["focus"] == "Summer Internships"
    assert calendar["apply_window"] == "Jan-Mar"
    assert calendar["internship_period"] == "May-Jul"


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_for_semester_5(calendar_service):
    """Test calendar for semester 5 (winter internships)"""
    calendar = calendar_service.get_calendar_for_semester(5)
    
    assert calendar["semester"] == 5
    assert calendar["focus"] == "Winter/Summer Internships"
    assert calendar["apply_window"] == "Aug-Oct"
    assert calendar["internship_period"] == "Dec-Jan"
    assert calendar["apply_months"] == [8, 9, 10]
    assert calendar["internship_months"] == [12, 1]


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_for_semester_6(calendar_service):
    """Test calendar for semester 6 (winter internships)"""
    calendar = calendar_service.get_calendar_for_semester(6)
    
    assert calendar["semester"] == 6
    assert calendar["focus"] == "Winter/Summer Internships"
    assert calendar["apply_window"] == "Aug-Oct"
    assert calendar["internship_period"] == "Dec-Jan"


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_for_semester_7(calendar_service):
    """Test calendar for semester 7 (final year)"""
    calendar = calendar_service.get_calendar_for_semester(7)
    
    assert calendar["semester"] == 7
    assert calendar["focus"] == "Final Year Internships"
    assert calendar["apply_window"] == "Jul-Sep"
    assert calendar["internship_period"] == "Jan-Apr"
    assert calendar["apply_months"] == [7, 8, 9]
    assert calendar["internship_months"] == [1, 2, 3, 4]


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_for_semester_8(calendar_service):
    """Test calendar for semester 8 (pre-placement)"""
    calendar = calendar_service.get_calendar_for_semester(8)
    
    assert calendar["semester"] == 8
    assert calendar["focus"] == "Pre-Placement"
    assert calendar["apply_window"] == "Ongoing"
    assert calendar["internship_period"] == "Flexible"
    assert calendar["apply_months"] == list(range(1, 13))
    assert calendar["internship_months"] == list(range(1, 13))


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_invalid_semester_below_range(calendar_service):
    """Test calendar with semester below valid range"""
    with pytest.raises(ValueError, match="Semester must be between 1 and 8"):
        calendar_service.get_calendar_for_semester(0)


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_invalid_semester_above_range(calendar_service):
    """Test calendar with semester above valid range"""
    with pytest.raises(ValueError, match="Semester must be between 1 and 8"):
        calendar_service.get_calendar_for_semester(9)


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_invalid_semester_negative(calendar_service):
    """Test calendar with negative semester"""
    with pytest.raises(ValueError, match="Semester must be between 1 and 8"):
        calendar_service.get_calendar_for_semester(-1)


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_with_specific_month_in_application_window(calendar_service):
    """Test calendar during application window"""
    # Semester 4, January (application window for summer internships)
    calendar = calendar_service.get_calendar_for_semester(4, current_month=1)
    
    assert calendar["semester"] == 4
    assert "OPEN" in calendar["current_status"] or "Apply now" in calendar["current_status"]


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_with_specific_month_outside_window(calendar_service):
    """Test calendar outside application window"""
    # Semester 4, June (after application window, during internship period)
    calendar = calendar_service.get_calendar_for_semester(4, current_month=6)
    
    assert calendar["semester"] == 4
    # Should indicate internship period or preparation for next cycle
    assert "internship" in calendar["current_status"].lower() or \
           "prepare" in calendar["current_status"].lower() or \
           "preparation" in calendar["current_status"].lower()


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_upcoming_deadlines_structure(calendar_service):
    """Test that upcoming deadlines have proper structure"""
    calendar = calendar_service.get_calendar_for_semester(4)
    
    deadlines = calendar["upcoming_deadlines"]
    assert isinstance(deadlines, list)
    
    # For semester 4, should have deadlines
    if len(deadlines) > 0:
        for deadline in deadlines:
            assert "type" in deadline
            assert "month" in deadline
            assert "month_number" in deadline
            assert "description" in deadline
            assert isinstance(deadline["type"], str)
            assert isinstance(deadline["month"], str)
            assert isinstance(deadline["month_number"], int)
            assert isinstance(deadline["description"], str)
            assert 1 <= deadline["month_number"] <= 12


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_preparation_window_for_skill_building_semester(calendar_service):
    """Test preparation window for skill-building semesters"""
    prep_window = calendar_service.calculate_preparation_window(1)
    
    assert prep_window["semester"] == 1
    assert prep_window["target_month"] is None
    assert prep_window["months_to_prepare"] is None
    assert prep_window["weeks_to_prepare"] is None
    assert "skill building" in prep_window["preparation_status"].lower()
    assert len(prep_window["recommended_actions"]) > 0


@pytest.mark.unit
@pytest.mark.internship
def test_calendar_preparation_window_for_internship_semester(calendar_service):
    """Test preparation window for internship semesters"""
    prep_window = calendar_service.calculate_preparation_window(4)
    
    assert prep_window["semester"] == 4
    assert prep_window["target_month"] is not None
    assert prep_window["months_to_prepare"] is not None
    assert prep_window["weeks_to_prepare"] is not None
    assert isinstance(prep_window["preparation_status"], str)
    assert len(prep_window["recommended_actions"]) > 0
    
    # Verify target month is in the application window
    assert prep_window["target_month"] in [1, 2, 3]  # Jan-Mar for semester 4



# ============================================================================
# Property 4: Internship Date Display
# Feature: internship-discovery, Property 4: Internship Date Display
# Validates: Requirements 2.5, 2.6
# ============================================================================

@pytest.mark.property
@pytest.mark.internship
@settings(max_examples=100)
@given(
    has_deadline=st.booleans(),
    has_start_date=st.booleans()
)
def test_property_4_internship_date_display(has_deadline: bool, has_start_date: bool):
    """
    Property 4: Internship Date Display
    
    For any internship listing with an application deadline or start date,
    the system should include these dates in the displayed information.
    
    **Validates: Requirements 2.5, 2.6**
    
    Universal property: If an internship has a deadline or start date,
    those dates must be present in the internship data structure.
    """
    from datetime import date, timedelta
    from app.models.internship import InternshipListing, InternshipType
    
    # Create internship data with or without dates
    internship_data = {
        "id": "test-internship-123",
        "title": "Software Engineering Intern",
        "company": "TechCorp",
        "company_domain": "techcorp.com",
        "platform": "LinkedIn",
        "location": "Remote",
        "internship_type": InternshipType.SUMMER,
        "duration": "3 months",
        "stipend": "₹15000/month",
        "required_skills": ["Python"],
        "preferred_skills": [],
        "responsibilities": ["Develop applications"],
        "posted_date": date.today(),
        "is_active": True
    }
    
    # Add deadline if specified
    if has_deadline:
        internship_data["application_deadline"] = date.today() + timedelta(days=30)
    else:
        internship_data["application_deadline"] = None
    
    # Add start date if specified
    if has_start_date:
        internship_data["start_date"] = date.today() + timedelta(days=60)
    else:
        internship_data["start_date"] = None
    
    # Create InternshipListing model
    internship = InternshipListing(**internship_data)
    
    # Verify dates are present in the model
    if has_deadline:
        assert internship.application_deadline is not None, \
            "Application deadline should be present when specified"
        assert isinstance(internship.application_deadline, date), \
            "Application deadline should be a date object"
    else:
        assert internship.application_deadline is None, \
            "Application deadline should be None when not specified"
    
    if has_start_date:
        assert internship.start_date is not None, \
            "Start date should be present when specified"
        assert isinstance(internship.start_date, date), \
            "Start date should be a date object"
    else:
        assert internship.start_date is None, \
            "Start date should be None when not specified"
    
    # Verify dates can be serialized (for API responses)
    internship_dict = internship.model_dump()
    
    if has_deadline:
        assert "application_deadline" in internship_dict, \
            "Application deadline should be in serialized data"
        # Date should be serialized as string or date object
        assert internship_dict["application_deadline"] is not None
    
    if has_start_date:
        assert "start_date" in internship_dict, \
            "Start date should be in serialized data"
        # Date should be serialized as string or date object
        assert internship_dict["start_date"] is not None


@pytest.mark.unit
@pytest.mark.internship
def test_internship_with_both_dates():
    """Test internship with both application deadline and start date"""
    from datetime import date, timedelta
    from app.models.internship import InternshipListing, InternshipType
    
    deadline = date.today() + timedelta(days=30)
    start = date.today() + timedelta(days=60)
    
    internship = InternshipListing(
        id="test-123",
        title="Software Intern",
        company="TechCorp",
        location="Remote",
        internship_type=InternshipType.SUMMER,
        duration="3 months",
        stipend="₹15000",
        required_skills=["Python"],
        responsibilities=["Develop apps"],
        application_deadline=deadline,
        start_date=start,
        posted_date=date.today(),
        is_active=True
    )
    
    assert internship.application_deadline == deadline
    assert internship.start_date == start


@pytest.mark.unit
@pytest.mark.internship
def test_internship_with_only_deadline():
    """Test internship with only application deadline"""
    from datetime import date, timedelta
    from app.models.internship import InternshipListing, InternshipType
    
    deadline = date.today() + timedelta(days=30)
    
    internship = InternshipListing(
        id="test-123",
        title="Software Intern",
        company="TechCorp",
        location="Remote",
        internship_type=InternshipType.SUMMER,
        duration="3 months",
        stipend="₹15000",
        required_skills=["Python"],
        responsibilities=["Develop apps"],
        application_deadline=deadline,
        start_date=None,
        posted_date=date.today(),
        is_active=True
    )
    
    assert internship.application_deadline == deadline
    assert internship.start_date is None


@pytest.mark.unit
@pytest.mark.internship
def test_internship_with_only_start_date():
    """Test internship with only start date"""
    from datetime import date, timedelta
    from app.models.internship import InternshipListing, InternshipType
    
    start = date.today() + timedelta(days=60)
    
    internship = InternshipListing(
        id="test-123",
        title="Software Intern",
        company="TechCorp",
        location="Remote",
        internship_type=InternshipType.SUMMER,
        duration="3 months",
        stipend="₹15000",
        required_skills=["Python"],
        responsibilities=["Develop apps"],
        application_deadline=None,
        start_date=start,
        posted_date=date.today(),
        is_active=True
    )
    
    assert internship.application_deadline is None
    assert internship.start_date == start


@pytest.mark.unit
@pytest.mark.internship
def test_internship_with_no_dates():
    """Test internship with no dates specified"""
    from datetime import date
    from app.models.internship import InternshipListing, InternshipType
    
    internship = InternshipListing(
        id="test-123",
        title="Software Intern",
        company="TechCorp",
        location="Remote",
        internship_type=InternshipType.SUMMER,
        duration="3 months",
        stipend="₹15000",
        required_skills=["Python"],
        responsibilities=["Develop apps"],
        application_deadline=None,
        start_date=None,
        posted_date=date.today(),
        is_active=True
    )
    
    assert internship.application_deadline is None
    assert internship.start_date is None
