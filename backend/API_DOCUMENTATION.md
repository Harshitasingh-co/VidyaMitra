# VidyaMitra API Documentation

## Overview

VidyaMitra API provides AI-powered educational services including resume analysis, mock interviews, and career path planning using OpenAI GPT-4 and LangChain.

## Base URL

```
http://localhost:8000
```

## Authentication

All AI endpoints require JWT authentication.

### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Get Profile
```http
GET /api/auth/me
Authorization: Bearer <token>
```

---

## AI Endpoints

### 1. Resume Analysis

#### Upload Resume
```http
POST /api/ai/resume/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <resume.pdf>
```

Response:
```json
{
  "success": true,
  "data": {
    "filename": "resume.pdf",
    "text_length": 2500,
    "full_text": "..."
  }
}
```

#### Analyze Resume
```http
POST /api/ai/resume/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "resume_text": "Full resume text here...",
  "target_role": "Software Engineer"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "ats_score": 85,
    "summary": "Strong technical background with 5 years experience...",
    "strengths": [
      "Solid programming skills",
      "Good project experience"
    ],
    "weaknesses": [
      "Limited cloud experience",
      "No certifications mentioned"
    ],
    "skills_identified": ["Python", "JavaScript", "SQL"],
    "missing_skills": ["AWS", "Docker", "Kubernetes"],
    "recommendations": [
      {
        "category": "Technical Skills",
        "suggestion": "Add cloud computing experience",
        "priority": "high"
      }
    ],
    "learning_resources": [
      {
        "skill": "AWS",
        "resource_type": "certification",
        "suggested_keywords": "AWS Solutions Architect"
      }
    ],
    "external_resources": [
      {
        "skill": "AWS",
        "videos": [...]
      }
    ]
  }
}
```

#### Extract Skills
```http
POST /api/ai/resume/extract-skills
Authorization: Bearer <token>
Content-Type: application/json

{
  "resume_text": "Resume text...",
  "target_role": "Data Scientist"
}
```

#### Match Job Description
```http
POST /api/ai/resume/match-job
Authorization: Bearer <token>
Content-Type: application/json

{
  "resume_text": "Resume text...",
  "job_description": "Job posting text..."
}
```

Response:
```json
{
  "success": true,
  "data": {
    "match_percentage": 78,
    "matching_keywords": ["Python", "Machine Learning"],
    "missing_keywords": ["TensorFlow", "PyTorch"],
    "recommendations": [
      "Add TensorFlow projects to resume",
      "Highlight ML model deployment experience"
    ]
  }
}
```

---

### 2. Mock Interview

#### Start Interview
```http
POST /api/ai/interview/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "role": "Software Engineer",
  "experience_level": "mid",
  "industry": "Technology",
  "num_questions": 5
}
```

Response:
```json
{
  "success": true,
  "data": {
    "session_id": "interview_user@example.com_Software Engineer",
    "role": "Software Engineer",
    "questions": [
      {
        "id": "q1",
        "question": "Explain the difference between REST and GraphQL",
        "category": "technical",
        "difficulty": "medium",
        "expected_topics": ["API design", "data fetching"]
      }
    ],
    "total_questions": 5
  }
}
```

#### Evaluate Answer
```http
POST /api/ai/interview/answer
Authorization: Bearer <token>
Content-Type: application/json

{
  "question": "Explain the difference between REST and GraphQL",
  "category": "technical",
  "answer": "REST is an architectural style that uses standard HTTP methods..."
}
```

Response:
```json
{
  "success": true,
  "data": {
    "overall_score": 82,
    "confidence_level": "high",
    "clarity_score": 85,
    "technical_accuracy": 80,
    "communication_score": 88,
    "tone_analysis": "professional",
    "strengths": [
      "Clear explanation of concepts",
      "Good use of examples"
    ],
    "improvements": [
      "Could mention more about GraphQL subscriptions",
      "Add comparison of performance characteristics"
    ],
    "detailed_feedback": "Your answer demonstrates solid understanding...",
    "suggested_answer_points": [
      "Mention over-fetching/under-fetching",
      "Discuss type safety"
    ]
  }
}
```

#### Generate Follow-up
```http
POST /api/ai/interview/followup?question=...&answer=...
Authorization: Bearer <token>
```

#### Overall Feedback
```http
POST /api/ai/interview/feedback
Authorization: Bearer <token>
Content-Type: application/json

{
  "evaluations": [
    {
      "overall_score": 82,
      "clarity_score": 85,
      "technical_accuracy": 80
    }
  ],
  "role": "Software Engineer"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "overall_performance": "good",
    "key_strengths": [
      "Strong technical knowledge",
      "Clear communication"
    ],
    "key_weaknesses": [
      "Could provide more specific examples"
    ],
    "improvement_plan": [
      "Practice STAR method for behavioral questions",
      "Study system design patterns"
    ],
    "readiness_level": "ready",
    "final_advice": "You're well-prepared for mid-level interviews...",
    "average_scores": {
      "overall": 82.0,
      "clarity": 85.0,
      "technical": 80.0
    }
  }
}
```

---

### 3. Career Path Planning

#### Generate Career Roadmap
```http
POST /api/ai/career/roadmap
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_role": "Frontend Developer",
  "target_role": "Full Stack Developer",
  "current_skills": ["React", "JavaScript", "CSS", "HTML"],
  "experience_years": 3
}
```

Response:
```json
{
  "success": true,
  "data": {
    "transition_feasibility": "high",
    "estimated_timeline": "4-6 months",
    "transferable_skills": ["JavaScript", "React", "Problem Solving"],
    "skills_to_acquire": [
      {
        "skill": "Node.js",
        "priority": "critical",
        "estimated_learning_time": "6 weeks"
      },
      {
        "skill": "SQL/Databases",
        "priority": "critical",
        "estimated_learning_time": "4 weeks"
      }
    ],
    "learning_path": [
      {
        "phase": 1,
        "title": "Backend Fundamentals",
        "duration": "6 weeks",
        "focus_areas": ["Node.js", "Express", "REST APIs"],
        "activities": [
          "Complete Node.js course",
          "Build 3 REST APIs"
        ],
        "resources_needed": ["Online course", "Practice projects"]
      }
    ],
    "certifications": [
      {
        "name": "AWS Certified Developer",
        "provider": "Amazon",
        "priority": "medium",
        "estimated_cost": "$150"
      }
    ],
    "milestones": [
      {
        "month": 1,
        "goal": "Complete Node.js fundamentals",
        "success_criteria": "Build and deploy a REST API"
      }
    ],
    "job_search_tips": [
      "Highlight full-stack projects in portfolio",
      "Contribute to open-source backend projects"
    ],
    "learning_resources": [
      {
        "skill": "Node.js",
        "videos": [...],
        "courses": [...]
      }
    ]
  }
}
```

#### Analyze Skill Gap
```http
POST /api/ai/career/skill-gap
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_skills": ["Python", "Django", "SQL"],
  "target_role": "Machine Learning Engineer"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "matching_skills": ["Python", "SQL"],
    "missing_critical_skills": ["TensorFlow", "PyTorch", "Statistics"],
    "missing_optional_skills": ["MLOps", "Docker"],
    "skill_match_percentage": 40,
    "learning_priority": [
      {
        "skill": "Machine Learning Fundamentals",
        "reason": "Core requirement for ML Engineer role",
        "difficulty": "medium"
      }
    ]
  }
}
```

#### Get Role Requirements
```http
GET /api/ai/career/role-requirements/Data%20Scientist
Authorization: Bearer <token>
```

#### Get Learning Resources
```http
POST /api/ai/career/learning-resources?learning_style=mixed
Authorization: Bearer <token>
Content-Type: application/json

["Python", "Machine Learning", "Docker"]
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "2024-01-15T10:30:00",
  "error_code": "OPTIONAL_CODE",
  "details": {}
}
```

Common HTTP Status Codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing/invalid token)
- `500` - Internal Server Error

---

## Rate Limiting

Consider implementing rate limiting for production:
- Resume analysis: 10 requests/hour
- Interview sessions: 5 sessions/day
- Career roadmaps: 5 requests/day

---

## Testing

Use the interactive API documentation at:
```
http://localhost:8000/docs
```

Or test with curl:
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password"

# Use token
curl -X POST http://localhost:8000/api/ai/resume/analyze \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "...", "target_role": "Developer"}'
```
