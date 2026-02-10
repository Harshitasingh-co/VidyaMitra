# Implementation Plan: Internship Discovery & Verification Module

## Overview

This implementation plan breaks down the Internship Discovery & Verification Module into discrete, incremental coding tasks. Each task builds on previous work, with testing integrated throughout to validate functionality early. The plan follows the existing VidyaMitra architecture patterns using FastAPI, Google Gemini AI, and React.

## Tasks

- [x] 1. Set up database schema and core data models
  - Create Supabase migration file with all 7 tables (student_profiles, internship_listings, verification_results, skill_matches, readiness_scores, user_alerts, scam_reports)
  - Add indexes and triggers for updated_at columns
  - Create Pydantic models in `backend/app/models/internship.py` for all data structures
  - _Requirements: US-1 (1.1-1.9), US-2 (2.1-2.8), US-3 (3.1-3.6), US-4 (4.1-4.7), US-5 (5.1-5.6), US-6 (6.1-6.5), US-7 (7.1-7.4), US-8 (8.1-8.5)_

- [x] 1.1 Write property test for profile data round-trip
  - **Property 1: Profile Data Round-Trip**
  - **Validates: Requirements 1.1, 1.3, 1.4, 1.6, 1.7, 1.8, 1.9**

- [x] 1.2 Write property test for semester validation
  - **Property 2: Semester Validation**
  - **Validates: Requirements 1.2**

- [ ] 2. Implement profile service and API endpoints
  - [x] 2.1 Create `backend/app/services/internship_service.py` with profile management methods
    - Implement `create_profile()` and `update_profile()` with validation
    - Implement `get_profile()` for retrieving user profile
    - Add Supabase database integration for CRUD operations
    - _Requirements: US-1 (1.1-1.9)_
  
  - [x] 2.2 Create profile API endpoints in `backend/app/routers/internship.py`
    - Implement `POST /api/internships/profile` for create/update
    - Implement `GET /api/internships/profile` for retrieval
    - Add authentication middleware integration
    - Add request/response validation
    - _Requirements: US-1 (1.1-1.9)_
  
  - [x] 2.3 Write unit tests for profile service
    - Test profile creation with valid data
    - Test profile update
    - Test validation errors (invalid semester, graduation year)
    - Test missing required fields
    - _Requirements: US-1 (1.1-1.9)_

- [ ] 3. Implement verification service with fraud detection
  - [x] 3.1 Create `backend/app/services/verification_service.py`
    - Implement `verify_internship()` method with trust score calculation
    - Implement `check_domain_authenticity()` for domain verification
    - Implement `check_platform_legitimacy()` for known platform detection
    - Implement `detect_red_flags()` with all red flag rules (registration fees, WhatsApp-only, non-official email, unrealistic stipend, vague descriptions)
    - Implement `calculate_trust_score()` based on signals and red flags
    - _Requirements: US-3 (3.1-3.6)_
  
  - [x] 3.2 Create verification API endpoint
    - Implement `GET /api/internships/{internship_id}/verify`
    - Cache verification results in database
    - Return verification status, trust score, signals, and red flags
    - _Requirements: US-3 (3.1-3.6)_
  
  - [x] 3.3 Write property tests for verification
    - **Property 5: Verification Status Assignment**
    - **Validates: Requirements 3.1**
  
  - [x] 3.4 Write property test for domain verification
    - **Property 6: Domain Verification**
    - **Validates: Requirements 3.2**
  
  - [x] 3.5 Write property test for platform recognition
    - **Property 7: Platform Recognition**
    - **Validates: Requirements 3.3**
  
  - [x] 3.6 Write property test for red flag detection
    - **Property 8: Red Flag Detection**
    - **Validates: Requirements 3.4, 3.5**
  
  - [x] 3.7 Write unit tests for verification edge cases
    - Test internship with no domain
    - Test internship with unknown platform
    - Test internship with multiple red flags
    - Test trust score boundary conditions (50, 79, 80)
    - _Requirements: US-3 (3.1-3.6)_

- [x] 4. Checkpoint - Ensure profile and verification tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement skill matching service
  - [x] 5.1 Create `backend/app/services/matching_service.py`
    - Implement `calculate_skill_match()` with percentage calculation
    - Implement skill intersection (matching skills) and difference (missing skills)
    - Implement `generate_learning_path()` for missing skills
    - Implement `rank_internships()` by match score
    - _Requirements: US-4 (4.1-4.7)_
  
  - [x] 5.2 Create skill matching API endpoint
    - Implement `POST /api/internships/{internship_id}/match`
    - Retrieve user profile and internship details
    - Calculate and cache skill match results
    - Return match percentage, matching skills, missing skills, and learning path
    - _Requirements: US-4 (4.1-4.7)_
  
  - [x] 5.3 Write property test for match percentage bounds
    - **Property 9: Skill Match Percentage Bounds**
    - **Validates: Requirements 4.4**
  
  - [x] 5.4 Write property test for skill match calculation
    - **Property 10: Skill Match Calculation**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.5**
  
  - [x] 5.5 Write property test for learning path generation
    - **Property 11: Learning Path Generation**
    - **Validates: Requirements 4.6**
  
  - [x] 5.6 Write property test for internship ranking
    - **Property 12: Internship Ranking by Match Score**
    - **Validates: Requirements 4.7**
  
  - [x] 5.7 Write unit tests for matching edge cases
    - Test 100% skill match
    - Test 0% skill match
    - Test empty skill lists
    - Test partial overlap
    - _Requirements: US-4 (4.1-4.7)_

- [ ] 6. Implement calendar service
  - [x] 6.1 Create `backend/app/services/calendar_service.py`
    - Implement semester-to-calendar mapping with SEMESTER_MAPPING constant
    - Implement `get_calendar_for_semester()` method
    - Implement `get_upcoming_deadlines()` method
    - Implement `calculate_preparation_window()` method
    - _Requirements: US-2 (2.1-2.8)_
  
  - [x] 6.2 Create calendar API endpoint
    - Implement `GET /api/internships/calendar`
    - Retrieve user's semester from profile
    - Return personalized calendar with application windows and deadlines
    - _Requirements: US-2 (2.1-2.8)_
  
  - [x] 6.3 Write property test for semester-to-calendar mapping
    - **Property 3: Semester-to-Calendar Mapping**
    - **Validates: Requirements 2.1, 2.7**
  
  - [x] 6.4 Write property test for internship date display
    - **Property 4: Internship Date Display**
    - **Validates: Requirements 2.5, 2.6**
  
  - [x] 6.5 Write unit tests for calendar service
    - Test calendar for semester 1 (skill building)
    - Test calendar for semester 4 (summer internships)
    - Test calendar for semester 7 (final year)
    - Test preparation window calculation
    - _Requirements: US-2 (2.1-2.8)_

- [ ] 7. Implement AI services for skill extraction and career guidance
  - [x] 7.1 Create `backend/ai/internship_ai.py`
    - Implement `extract_skills_from_resume()` using Gemini API
    - Implement `generate_career_guidance()` with all components (why good fit, skills to improve, certifications, projects)
    - Implement `generate_learning_recommendations()` for missing skills
    - Add error handling and retry logic for AI calls
    - _Requirements: US-1 (1.5), US-5 (5.1-5.6)_
  
  - [x] 7.2 Create career guidance API endpoint
    - Implement `GET /api/internships/{internship_id}/guidance`
    - Retrieve user profile, internship details, and skill match
    - Generate and return AI-powered guidance
    - _Requirements: US-5 (5.1-5.6)_
  
  - [ ] 7.3 Write property test for career guidance completeness
    - **Property 13: Career Guidance Completeness**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
  
  - [~] 7.4 Write property test for guidance personalization
    - **Property 14: Guidance Personalization**
    - **Validates: Requirements 5.6**
  
  - [~] 7.5 Write unit tests for AI services
    - Test skill extraction from sample resume
    - Test guidance generation for specific internship
    - Test AI service timeout handling
    - Test malformed AI response handling
    - _Requirements: US-1 (1.5), US-5 (5.1-5.6)_

- [~] 8. Checkpoint - Ensure matching, calendar, and AI tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement readiness score calculation
  - [ ] 9.1 Create readiness calculation in `backend/app/services/internship_service.py`
    - Implement `calculate_readiness_score()` with weighted formula (resume 30%, skills 40%, semester 30%)
    - Implement `calculate_resume_strength()` helper method
    - Implement `calculate_semester_readiness()` helper method
    - Implement recommendation logic (≥70 = "Apply Now", <70 = "Prepare for X days")
    - Implement `generate_improvement_actions()` based on weakest component
    - _Requirements: US-6 (6.1-6.5)_
  
  - [~] 9.2 Create readiness score API endpoint
    - Implement `GET /api/internships/{internship_id}/readiness`
    - Calculate and cache readiness score
    - Return overall score, component breakdown, recommendation, and improvement actions
    - _Requirements: US-6 (6.1-6.5)_
  
  - [~] 9.3 Write property test for readiness score calculation
    - **Property 15: Readiness Score Calculation**
    - **Validates: Requirements 6.1, 6.4**
  
  - [~] 9.4 Write property test for readiness recommendation logic
    - **Property 16: Readiness Recommendation Logic**
    - **Validates: Requirements 6.2, 6.3**
  
  - [~] 9.5 Write property test for improvement actions generation
    - **Property 17: Improvement Actions Generation**
    - **Validates: Requirements 6.5**
  
  - [~] 9.6 Write unit tests for readiness edge cases
    - Test readiness with score exactly 70 (boundary)
    - Test readiness with score 69 (boundary)
    - Test readiness with all components at 100
    - Test readiness with all components at 0
    - _Requirements: US-6 (6.1-6.5)_

- [ ] 10. Implement search and filtering functionality
  - [ ] 10.1 Implement search in `backend/app/services/internship_service.py`
    - Implement `search_internships()` with filters (skills, roles, type, compensation, location)
    - Add skill matching for each result
    - Add ranking by match score
    - Add pagination support
    - _Requirements: US-4 (4.1-4.7)_
  
  - [~] 10.2 Create search API endpoint
    - Implement `POST /api/internships/search`
    - Accept search filters in request body
    - Return ranked internships with match scores
    - _Requirements: US-4 (4.1-4.7)_
  
  - [~] 10.3 Create internship details endpoint
    - Implement `GET /api/internships/{internship_id}`
    - Return complete internship information
    - Include verification status and trust score
    - _Requirements: US-3 (3.1-3.6), US-4 (4.1-4.7)_
  
  - [~] 10.4 Write unit tests for search functionality
    - Test search with skill filter
    - Test search with role filter
    - Test search with multiple filters
    - Test search with no results
    - Test pagination
    - _Requirements: US-4 (4.1-4.7)_

- [ ] 11. Implement alert and notification system
  - [ ] 11.1 Create `backend/app/services/alert_service.py`
    - Implement `create_alert()` method
    - Implement `create_new_match_alert()` for new matching internships
    - Implement `create_deadline_alert()` for approaching deadlines (7, 3, 1 days)
    - Implement `create_readiness_improvement_alert()` for score increases
    - Implement `create_season_preparation_alert()` for upcoming seasons
    - _Requirements: US-8 (8.1-8.5)_
  
  - [~] 11.2 Create alert API endpoints
    - Implement `GET /api/internships/alerts` with pagination
    - Implement `PATCH /api/internships/alerts/{alert_id}/read` to mark as read
    - Filter alerts by user_id
    - _Requirements: US-8 (8.1-8.5)_
  
  - [~] 11.3 Write property test for new match alert creation
    - **Property 19: New Match Alert Creation**
    - **Validates: Requirements 8.1**
  
  - [~] 11.4 Write property test for deadline alert creation
    - **Property 20: Deadline Alert Creation**
    - **Validates: Requirements 8.2**
  
  - [~] 11.5 Write property test for readiness improvement alert
    - **Property 21: Readiness Improvement Alert**
    - **Validates: Requirements 8.3**
  
  - [~] 11.6 Write property test for season preparation alert
    - **Property 22: Season Preparation Alert**
    - **Validates: Requirements 8.4**
  
  - [~] 11.7 Write unit tests for alert service
    - Test alert creation
    - Test marking alert as read
    - Test alert filtering by user
    - Test alert pagination
    - _Requirements: US-8 (8.1-8.5)_

- [ ] 12. Implement scam reporting functionality
  - [ ] 12.1 Add scam reporting to `backend/app/services/internship_service.py`
    - Implement `report_scam()` method
    - Create scam report record with "Pending" status
    - _Requirements: US-7 (7.3)_
  
  - [~] 12.2 Create scam report API endpoint
    - Implement `POST /api/internships/report-scam`
    - Accept internship_id, reason, and optional details
    - Return confirmation
    - _Requirements: US-7 (7.3)_
  
  - [~] 12.3 Write property test for scam report submission
    - **Property 18: Scam Report Submission**
    - **Validates: Requirements 7.3**
  
  - [~] 12.4 Write unit tests for scam reporting
    - Test report creation
    - Test report with missing details
    - Test duplicate reports
    - _Requirements: US-7 (7.3)_

- [x] 13. Register router and update main.py
  - Add internship router to `backend/main.py`
  - Configure CORS for new endpoints
  - Update API documentation
  - _Requirements: All user stories_

- [~] 14. Checkpoint - Ensure all backend tests pass
  - Run full test suite
  - Verify all API endpoints work
  - Check authentication on protected routes
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Create frontend service layer
  - [x] 15.1 Create `frontend/src/services/internshipApi.js`
    - Implement API client methods for all endpoints
    - Add error handling and response formatting
    - Add authentication token handling
    - _Requirements: All user stories_

- [ ] 16. Build profile management UI
  - [x] 16.1 Create `frontend/src/pages/InternshipProfile.jsx`
    - Build profile form with all fields (graduation year, semester, degree, branch, skills, roles, preferences)
    - Add skill input with autocomplete
    - Add resume upload functionality
    - Integrate with profile API endpoints
    - Add form validation
    - _Requirements: US-1 (1.1-1.9)_
  
  - [ ] 16.2 Create `frontend/src/components/SkillInput.jsx`
    - Build reusable skill input component with tag display
    - Add skill addition and removal
    - _Requirements: US-1 (1.4)_

- [ ] 17. Build internship discovery dashboard
  - [ ] 17.1 Create `frontend/src/pages/InternshipDiscovery.jsx`
    - Build main dashboard layout
    - Add search and filter interface
    - Display internship list with match scores
    - Add pagination
    - Integrate with search API
    - _Requirements: US-4 (4.1-4.7)_
  
  - [ ] 17.2 Create `frontend/src/components/InternshipCard.jsx`
    - Build internship card component
    - Display title, company, location, stipend
    - Show verification badge
    - Show skill match percentage
    - Add "View Details" button
    - _Requirements: US-3 (3.1-3.6), US-4 (4.1-4.7)_
  
  - [ ] 17.3 Create `frontend/src/components/VerificationBadge.jsx`
    - Build verification status indicator
    - Show trust score
    - Display appropriate icon and color for status
    - _Requirements: US-3 (3.1-3.6)_

- [ ] 18. Build internship details page
  - [ ] 18.1 Create `frontend/src/pages/InternshipDetails.jsx`
    - Build detailed internship view
    - Display all internship information
    - Show verification details with red flags
    - Display skill match breakdown
    - Show readiness score
    - Display AI career guidance
    - Add "Report Scam" button
    - _Requirements: US-3 (3.1-3.6), US-4 (4.1-4.7), US-5 (5.1-5.6), US-6 (6.1-6.5), US-7 (7.3)_
  
  - [ ] 18.2 Create `frontend/src/components/SkillMatchCard.jsx`
    - Build skill match visualization
    - Show matching skills (green)
    - Show missing skills (red)
    - Display learning path
    - _Requirements: US-4 (4.1-4.7)_
  
  - [ ] 18.3 Create `frontend/src/components/ReadinessScore.jsx`
    - Build readiness score display
    - Show overall score with progress bar
    - Display component breakdown (resume, skills, semester)
    - Show recommendation
    - Display improvement actions
    - _Requirements: US-6 (6.1-6.5)_
  
  - [ ] 18.4 Create `frontend/src/components/RedFlagAlert.jsx`
    - Build warning banner for red flags
    - Display red flag list with severity indicators
    - Show educational tips
    - _Requirements: US-3 (3.4-3.5)_
  
  - [ ] 18.5 Create `frontend/src/components/CareerGuidance.jsx`
    - Build AI guidance display
    - Show why it's a good fit
    - Display skills to improve
    - List recommended certifications
    - Show project ideas
    - _Requirements: US-5 (5.1-5.6)_

- [ ] 19. Build calendar and timeline UI
  - [ ] 19.1 Create `frontend/src/components/InternshipCalendar.jsx`
    - Build calendar visualization
    - Display application windows
    - Show deadlines
    - Highlight current period
    - Display preparation recommendations
    - _Requirements: US-2 (2.1-2.8)_
  
  - [~] 19.2 Integrate calendar into dashboard
    - Add calendar section to InternshipDiscovery page
    - Fetch calendar data based on user's semester
    - _Requirements: US-2 (2.1-2.8)_

- [ ] 20. Build alerts and notifications UI
  - [ ] 20.1 Create `frontend/src/components/AlertCenter.jsx`
    - Build alert list component
    - Display unread alerts with badge
    - Add mark as read functionality
    - Group alerts by type
    - _Requirements: US-8 (8.1-8.5)_
  
  - [~] 20.2 Add alert notifications to dashboard
    - Add alert bell icon to navigation
    - Show unread count
    - Display recent alerts in dropdown
    - _Requirements: US-8 (8.1-8.5)_

- [ ] 21. Build scam education and reporting UI
  - [ ] 21.1 Create `frontend/src/components/ScamEducation.jsx`
    - Build educational content display
    - Show interactive checklist
    - Display fraud detection tips
    - Show examples of verified vs fraudulent listings
    - _Requirements: US-7 (7.1-7.4)_
  
  - [~] 21.2 Create scam report modal
    - Build report form modal
    - Add reason selection
    - Add details text area
    - Integrate with report API
    - _Requirements: US-7 (7.3)_

- [~] 22. Add navigation and routing
  - Update `frontend/src/App.jsx` with new routes
  - Add navigation links to dashboard
  - Add protected route guards
  - _Requirements: All user stories_

- [~] 23. Final checkpoint - End-to-end testing
  - Test complete user journey: Profile setup → Search → View details → Check readiness
  - Test verification flow with different internship types
  - Test alert creation and display
  - Test scam reporting
  - Verify responsive design
  - Check accessibility
  - Ensure all tests pass, ask the user if questions arise.

- [~] 24. Documentation and deployment preparation
  - Update API documentation
  - Add inline code comments
  - Create user guide for new features
  - Update README with setup instructions
  - _Requirements: All user stories_

## Notes

- All tasks are required for comprehensive implementation with full test coverage
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Integration tests verify end-to-end flows
- Frontend tasks build on completed backend functionality
- All API endpoints require authentication except health checks
