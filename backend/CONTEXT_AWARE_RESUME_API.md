# Context-Aware Resume Analysis API Documentation

## Overview

The Context-Aware Resume Analysis feature provides intelligent, personalized resume analysis based on the user's specific career goals. Unlike generic resume analysis, this feature considers:

- **Desired Role**: Target job position
- **Experience Level**: Career stage (0-2 years, 3-5 years, 5+ years)
- **Target Companies**: Company types (Product-based, Startups, Enterprise, etc.)
- **Preferred Industries**: Industry preferences

## API Flow

```
1. User submits career intent → GET intent_id
2. User uploads resume → Extract text
3. System analyzes resume with context → Comprehensive analysis
```

## Endpoints

### 1. Submit Career Intent

**Endpoint**: `POST /api/ai/career-intent`

**Purpose**: Capture user's career goals before resume analysis

**Request Body**:
```json
{
  "desired_role": "Data Analyst",
  "experience_level": "0-2 years",
  "target_companies": ["Product-based companies", "Startups"],
  "preferred_industries": ["Tech", "E-commerce"],
  "location_preference": "Remote"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "intent_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Career intent captured successfully",
    "next_step": "Upload your resume for context-aware analysis"
  }
}
```

**Validation Rules**:
- `desired_role`: Required, min 2 characters
- `experience_level`: Required
- `target_companies`: Required, at least one company type
- `preferred_industries`: Optional
- `location_preference`: Optional

---

### 2. Get Career Intent

**Endpoint**: `GET /api/ai/career-intent/{intent_id}`

**Purpose**: Retrieve stored career intent

**Response**:
```json
{
  "success": true,
  "data": {
    "desired_role": "Data Analyst",
    "experience_level": "0-2 years",
    "target_companies": ["Product-based companies"],
    "preferred_industries": ["Tech"],
    "location_preference": "Remote"
  }
}
```

---

### 3. Context-Aware Resume Analysis

**Endpoint**: `POST /api/ai/context-aware-analyze`

**Purpose**: Analyze resume with career context

**Request Body** (Option 1 - Using intent_id):
```json
{
  "resume_text": "John Doe\nData Analyst with 1 year experience...",
  "intent_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Request Body** (Option 2 - Direct intent):
```json
{
  "resume_text": "John Doe\nData Analyst with 1 year experience...",
  "career_intent": {
    "desired_role": "Data Analyst",
    "experience_level": "0-2 years",
    "target_companies": ["Product-based companies"]
  }
}
```

**Response Structure**:
```json
{
  "success": true,
  "data": {
    "role_fit_score": 72,
    "existing_skills": ["SQL", "Excel", "Communication"],
    "missing_skills": ["Power BI", "Python", "Statistics"],
    
    "technical_skills_required": [
      {
        "skill": "Power BI",
        "importance": "High",
        "why": "Frequently required for Data Analyst roles in product companies",
        "current_level": "None",
        "target_level": "Intermediate",
        "estimated_learning_time": "4-6 weeks"
      }
    ],
    
    "certifications": [
      {
        "name": "Google Data Analytics Professional Certificate",
        "provider": "Google via Coursera",
        "description": "Covers SQL, data analysis, and business insights",
        "duration": "3-4 months",
        "level": "Beginner-Intermediate",
        "link": "https://www.coursera.org/professional-certificates/google-data-analytics",
        "why_recommended": "Addresses analytics fundamentals missing in resume",
        "priority": "High"
      }
    ],
    
    "projects": [
      {
        "title": "Customer Sales Insights Dashboard",
        "skills_covered": ["Power BI", "SQL"],
        "project_idea": "Build an interactive dashboard to analyze regional sales trends",
        "learning_outcomes": [
          "Dashboard design",
          "Business storytelling",
          "Data cleaning"
        ],
        "resources": {
          "dataset": "https://www.kaggle.com/datasets/kyanyoga/sample-sales-data",
          "reference_repo": "https://github.com/topics/data-analytics"
        },
        "resume_bullets": [
          "Built Power BI dashboards analyzing 50k+ sales records",
          "Generated insights that improved reporting efficiency by 30%"
        ],
        "estimated_time": "2-3 weeks",
        "difficulty": "Intermediate"
      }
    ],
    
    "skill_matching": {
      "fully_matching": [
        {
          "skill": "SQL",
          "evidence": "Mentioned in work experience section"
        }
      ],
      "partially_matching": [
        {
          "skill": "Data Visualization",
          "current_level": "Basic",
          "target_level": "Intermediate",
          "gap_description": "Need to learn advanced visualization tools like Power BI"
        }
      ],
      "completely_missing": [
        {
          "skill": "Python",
          "importance": "Critical",
          "learning_path": "Start with Python basics, then pandas and data analysis libraries"
        }
      ]
    },
    
    "resume_improvements": [
      {
        "section": "Work Experience",
        "current_issue": "Lacks quantifiable achievements",
        "suggestion": "Add metrics and impact numbers to each bullet point",
        "priority": "High"
      }
    ],
    
    "ats_optimization": {
      "score": 68,
      "missing_keywords": ["data visualization", "business intelligence", "KPI"],
      "formatting_issues": ["Inconsistent date formats", "Missing section headers"],
      "suggestions": [
        "Add a 'Technical Skills' section",
        "Use standard section headers"
      ]
    },
    
    "company_specific_advice": [
      {
        "company_type": "Product-based companies",
        "what_they_look_for": "Strong analytical skills, product sense, SQL proficiency",
        "how_to_stand_out": "Showcase projects with product metrics and user behavior analysis"
      }
    ],
    
    "career_intent": {
      "desired_role": "Data Analyst",
      "experience_level": "0-2 years",
      "target_companies": ["Product-based companies"]
    }
  },
  "message": "Context-aware resume analysis completed successfully"
}
```

---

### 4. Upload Resume with Intent

**Endpoint**: `POST /api/ai/upload-with-intent`

**Purpose**: Combined upload and analysis (convenience endpoint)

**Request**: Multipart form data
- `file`: Resume file (PDF/DOCX/TXT)
- `intent_id`: (Optional) Career intent ID

**Response** (with intent_id):
```json
{
  "success": true,
  "data": {
    "filename": "resume.pdf",
    "text_length": 2450,
    "full_text": "...",
    "analysis": { /* Full context-aware analysis */ },
    "message": "Resume uploaded and analyzed with career context"
  }
}
```

**Response** (without intent_id):
```json
{
  "success": true,
  "data": {
    "filename": "resume.pdf",
    "text_length": 2450,
    "text_preview": "...",
    "full_text": "...",
    "message": "Resume uploaded successfully. Submit for analysis next."
  }
}
```

---

### 5. Detailed Skill Gap Analysis

**Endpoint**: `POST /api/ai/skill-gap-details`

**Purpose**: Get detailed learning roadmap for skill gaps

**Request Body**:
```json
{
  "existing_skills": ["SQL", "Excel"],
  "required_skills": ["Python", "Power BI", "Statistics"],
  "desired_role": "Data Analyst"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "gap_summary": "You need to acquire 3 critical skills for Data Analyst role",
    "critical_gaps": [
      {
        "skill": "Python",
        "why_critical": "Essential for data manipulation and analysis",
        "learning_resources": [
          "Python for Data Analysis (Book)",
          "Coursera: Python for Data Science"
        ],
        "estimated_time": "8-10 weeks"
      }
    ],
    "nice_to_have_gaps": [
      {
        "skill": "R Programming",
        "benefit": "Alternative to Python for statistical analysis",
        "priority": "Medium"
      }
    ],
    "learning_roadmap": [
      {
        "week": 1,
        "focus": "Python Basics",
        "resources": ["Codecademy Python", "Python.org tutorial"]
      }
    ]
  }
}
```

---

## Key Features

### 1. Role-Specific Analysis
- Analysis tailored to desired role requirements
- Company-type specific recommendations
- Experience-level appropriate suggestions

### 2. Skill Gap Analysis
- **Fully Matching**: Skills that meet requirements
- **Partially Matching**: Skills that need improvement
- **Completely Missing**: Critical skills to acquire

### 3. Real Certifications
- Only widely-accepted certifications (Google, Microsoft, AWS, Coursera, edX)
- Official certification URLs
- Duration and difficulty levels
- Priority based on resume gaps

### 4. Project Ideas
- Practical projects to build missing skills
- Real dataset sources (Kaggle, UCI ML Repository)
- Ready-to-use resume bullet points
- Estimated completion time

### 5. ATS Optimization
- Keyword analysis
- Formatting suggestions
- Section recommendations

---

## Error Handling

### 400 Bad Request
```json
{
  "detail": "Desired role is required"
}
```

### 404 Not Found
```json
{
  "detail": "Career intent not found or expired"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Analysis failed: <error message>"
}
```

---

## Data Storage

- **Development**: In-memory storage (24-hour expiration)
- **Production**: Supabase integration (optional)
- Intent IDs are UUIDs
- Automatic cleanup of expired intents

---

## AI Model Configuration

- **Model**: Google Gemini 1.5 Flash
- **Temperature**: 0.3 (deterministic outputs)
- **Output Format**: Structured JSON
- **Validation**: Schema-based validation

---

## Best Practices

1. **Always collect career intent first** before resume analysis
2. **Store intent_id** on frontend for subsequent requests
3. **Handle expired intents** gracefully (24-hour TTL)
4. **Validate resume text length** (minimum 100 characters)
5. **Display certifications with clickable links**
6. **Show project ideas with actionable steps**

---

## Frontend Integration Example

```javascript
// Step 1: Submit career intent
const intentResponse = await fetch('/api/ai/career-intent', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    desired_role: 'Data Analyst',
    experience_level: '0-2 years',
    target_companies: ['Product-based companies']
  })
});
const { intent_id } = await intentResponse.json();

// Step 2: Upload resume
const formData = new FormData();
formData.append('file', resumeFile);
const uploadResponse = await fetch('/api/ai/resume/upload', {
  method: 'POST',
  body: formData
});
const { full_text } = await uploadResponse.json();

// Step 3: Get context-aware analysis
const analysisResponse = await fetch('/api/ai/context-aware-analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    resume_text: full_text,
    intent_id: intent_id
  })
});
const analysis = await analysisResponse.json();
```

---

## Testing

Test the endpoints using the FastAPI docs:
- Development: `http://localhost:8001/docs`
- Look for "AI - Context-Aware Resume" tag

---

## Notes

- Career intents expire after 24 hours
- Resume text must be at least 100 characters
- Certifications are real and verified
- Project ideas include actual dataset sources
- All responses are deterministic (temperature 0.3)
