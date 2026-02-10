# Internship Discovery & Verification Module - Requirements

## Overview

A comprehensive internship discovery system that helps students find genuine, skill-aligned, semester-appropriate internships while protecting them from fraudulent listings.

## User Stories

### US-1: Student Profile Setup
**As a** student  
**I want to** provide my academic and skill information  
**So that** I can receive personalized internship recommendations

**Acceptance Criteria**:
- 1.1 Student can input graduation year
- 1.2 Student can select current semester (1-8)
- 1.3 Student can specify degree (B.Tech, M.Tech, BCA, MCA, etc.) and branch
- 1.4 Student can manually add skills
- 1.5 System can extract skills from uploaded resume
- 1.6 Student can select preferred role(s) (e.g., Software Engineer, Data Analyst)
- 1.7 Student can choose internship type (Remote/On-site/Hybrid)
- 1.8 Student can filter by compensation (Paid/Unpaid)
- 1.9 Student can optionally specify target companies

### US-2: Internship Calendar Engine
**As a** student  
**I want to** see when I should apply for internships based on my semester  
**So that** I don't miss application deadlines

**Acceptance Criteria**:
- 2.1 System maps semester to ideal internship application window
- 2.2 System displays Summer Internship timeline (typically Jan-March applications)
- 2.3 System displays Winter Internship timeline (typically Aug-Oct applications)
- 2.4 System shows Research/Off-cycle internship opportunities
- 2.5 System displays application deadlines
- 2.6 System shows expected internship start month
- 2.7 System provides preparation window recommendations
- 2.8 Example output: "Based on Semester 4, you should apply for Summer Internships between Jan–March"

### US-3: Internship Verification System
**As a** student  
**I want to** know if an internship listing is genuine  
**So that** I can avoid scams and fraudulent opportunities

**Acceptance Criteria**:
- 3.1 System classifies internships as: ✅ Verified, ⚠️ Use Caution, ❌ Potential Scam
- 3.2 System verifies official company domain
- 3.3 System validates known platforms (Internshala, LinkedIn, Wellfound, AICTE, NSDC, Company career pages)
- 3.4 System detects red flags:
  - Registration fees required
  - WhatsApp-only contact
  - Gmail/Yahoo emails for official communication
  - Unrealistic stipend promises (e.g., ₹50k+ for freshers)
  - No official offer letter
  - Vague job descriptions
- 3.5 System displays clear warning banners for risky listings
- 3.6 System provides fraud education tips

### US-4: Skill-Based Internship Matching
**As a** student  
**I want to** see how well my skills match an internship  
**So that** I can apply to relevant opportunities

**Acceptance Criteria**:
- 4.1 System matches internships using resume skills
- 4.2 System matches internships using user-selected skills
- 4.3 System matches internships based on desired role
- 4.4 System calculates and displays skill match percentage (0-100%)
- 4.5 System identifies missing skills required for internship
- 4.6 System suggests learning path for missing skills
- 4.7 System prioritizes internships with higher match scores

### US-5: AI Career Guidance
**As a** student  
**I want to** understand why an internship is recommended  
**So that** I can make informed decisions

**Acceptance Criteria**:
- 5.1 System explains why internship fits the user's profile
- 5.2 System describes what skills the internship will improve
- 5.3 System suggests certifications to complete before applying
- 5.4 System recommends mini-projects to strengthen resume
- 5.5 Explanations are conversational, not static text
- 5.6 Guidance is personalized based on user's current skill level

### US-6: Internship Readiness Score
**As a** student  
**I want to** know if I'm ready to apply for an internship  
**So that** I can improve my chances of selection

**Acceptance Criteria**:
- 6.1 System calculates readiness score (0-100) based on:
  - Resume strength (30%)
  - Skill match (40%)
  - Semester readiness (30%)
- 6.2 System provides "Apply Now" recommendation if score ≥ 70
- 6.3 System provides "Prepare for X days" recommendation if score < 70
- 6.4 System shows breakdown of readiness score components
- 6.5 System provides actionable steps to improve readiness

### US-7: Internship Scam Education
**As a** student  
**I want to** learn how to identify scam internships  
**So that** I can protect myself from fraud

**Acceptance Criteria**:
- 7.1 System provides interactive checklist:
  - "Does this internship ask for money?"
  - "Is there an official offer letter?"
  - "Is the contact email from official domain?"
  - "Are the responsibilities clearly defined?"
  - "Is the stipend realistic?"
- 7.2 System provides educational content about common scams
- 7.3 System allows users to report suspicious listings
- 7.4 System shows examples of verified vs fraudulent listings

### US-8: Smart Alerts & Notifications
**As a** student  
**I want to** be notified about relevant internships  
**So that** I don't miss opportunities

**Acceptance Criteria**:
- 8.1 System notifies when matching internship opens
- 8.2 System alerts when application deadline is approaching (7 days, 3 days, 1 day)
- 8.3 System notifies when user's readiness score improves
- 8.4 System suggests when to start preparing for upcoming internship season
- 8.5 Notifications are personalized and actionable

## Data Models

### Student Profile
```json
{
  "user_id": "string",
  "graduation_year": 2026,
  "current_semester": 4,
  "degree": "B.Tech",
  "branch": "Computer Science",
  "skills": ["Python", "SQL", "React"],
  "preferred_roles": ["Software Engineer", "Data Analyst"],
  "internship_type": "Remote",
  "compensation_preference": "Paid",
  "target_companies": ["Google", "Microsoft"],
  "resume_url": "string"
}
```

### Internship Listing
```json
{
  "internship_id": "string",
  "title": "Software Engineering Intern",
  "company": "TechCorp",
  "company_domain": "techcorp.com",
  "platform": "Internshala",
  "location": "Remote",
  "type": "Summer",
  "duration": "2-3 months",
  "stipend": "₹15,000/month",
  "required_skills": ["Python", "Django", "REST API"],
  "responsibilities": ["Build APIs", "Write tests"],
  "application_deadline": "2026-03-15",
  "start_date": "2026-05-01",
  "verification_status": "Verified",
  "red_flags": [],
  "posted_date": "2026-01-15"
}
```

### Verification Result
```json
{
  "internship_id": "string",
  "status": "Verified | Use Caution | Potential Scam",
  "trust_score": 85,
  "verification_signals": {
    "official_domain": true,
    "known_platform": true,
    "company_verified": true
  },
  "red_flags": [
    {
      "type": "registration_fee",
      "severity": "high",
      "description": "Asks for registration fee"
    }
  ],
  "last_verified": "2026-01-20"
}
```

### Skill Match Result
```json
{
  "internship_id": "string",
  "user_id": "string",
  "match_percentage": 75,
  "matching_skills": ["Python", "SQL"],
  "missing_skills": ["Django", "REST API"],
  "learning_path": [
    {
      "skill": "Django",
      "estimated_time": "2 weeks",
      "resources": ["Django Official Tutorial", "Coursera Django Course"]
    }
  ]
}
```

### Readiness Score
```json
{
  "user_id": "string",
  "internship_id": "string",
  "overall_score": 72,
  "components": {
    "resume_strength": 65,
    "skill_match": 75,
    "semester_readiness": 80
  },
  "recommendation": "Apply Now | Prepare for 30 days",
  "improvement_actions": [
    "Add Django project to resume",
    "Complete REST API certification"
  ]
}
```

## Technical Requirements

### Backend APIs Required
1. `POST /api/internships/profile` - Create/update student profile
2. `GET /api/internships/calendar` - Get internship calendar based on semester
3. `POST /api/internships/search` - Search internships with filters
4. `GET /api/internships/{id}/verify` - Get verification status
5. `POST /api/internships/match` - Calculate skill match
6. `GET /api/internships/{id}/guidance` - Get AI career guidance
7. `GET /api/internships/{id}/readiness` - Calculate readiness score
8. `POST /api/internships/report-scam` - Report suspicious listing
9. `GET /api/internships/alerts` - Get personalized alerts

### AI/ML Components
1. **Skill Extraction**: Extract skills from resume using NLP
2. **Fraud Detection**: ML model to detect scam patterns
3. **Recommendation Engine**: Hybrid rule-based + AI matching
4. **Career Guidance**: GenAI for personalized explanations

### Verification Rules
1. **Verified** (Trust Score ≥ 80):
   - Official company domain
   - Listed on known platforms
   - No red flags
   - Company verified on LinkedIn/Crunchbase

2. **Use Caution** (Trust Score 50-79):
   - 1-2 minor red flags
   - Unknown platform but official domain
   - Limited company information

3. **Potential Scam** (Trust Score < 50):
   - 3+ red flags
   - Registration fee required
   - Non-official email domain
   - Unrealistic promises

### Internship Calendar Logic

**Semester Mapping**:
- Semester 1-2: Focus on skill building, no internships yet
- Semester 3-4: Summer internships (Apply: Jan-Mar, Start: May-Jul)
- Semester 5-6: Winter internships (Apply: Aug-Oct, Start: Dec-Jan) or Summer
- Semester 7-8: Final year internships/Pre-placement (Apply: Jul-Sep)

**Timeline Windows**:
- Summer: Application (Jan-Mar) → Selection (Mar-Apr) → Internship (May-Jul)
- Winter: Application (Aug-Oct) → Selection (Oct-Nov) → Internship (Dec-Jan)
- Research: Year-round, 3-6 months duration

## Non-Functional Requirements

### Performance
- API response time < 2 seconds
- Skill matching calculation < 1 second
- Support 1000+ concurrent users

### Security
- Secure storage of student data
- API rate limiting
- Input validation and sanitization
- HTTPS only

### Scalability
- Support 100,000+ internship listings
- Handle 10,000+ student profiles
- Efficient search and filtering

## Success Metrics

1. **User Engagement**:
   - 70%+ students complete profile setup
   - 50%+ students check readiness score
   - 30%+ students use AI guidance

2. **Safety**:
   - 95%+ accuracy in fraud detection
   - < 1% false positives for verified internships
   - 80%+ students report feeling safer

3. **Effectiveness**:
   - 60%+ skill match accuracy
   - 40%+ students apply to recommended internships
   - 25%+ students get selected

## Future Enhancements

1. Interview preparation for specific companies
2. Peer reviews of internship experiences
3. Salary negotiation guidance
4. Internship-to-PPO conversion tips
5. Alumni mentorship matching
6. Company culture insights
7. Integration with college placement cells

## Dependencies

- Resume parsing AI (existing in VidyaMitra)
- Gemini AI for guidance generation
- Internship data sources (APIs or web scraping)
- Email/SMS notification service
- Database for storing listings and user data

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Inaccurate fraud detection | High | Manual review queue, user reporting |
| Outdated internship listings | Medium | Daily data refresh, expiry dates |
| Poor skill matching | Medium | Continuous ML model improvement |
| API quota limits | Low | Caching, rate limiting |
| Data privacy concerns | High | Encryption, compliance with data laws |

---

**Status**: Requirements Defined
**Next Step**: Design Document
**Priority**: High
**Estimated Effort**: 3-4 weeks
