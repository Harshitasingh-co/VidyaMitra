# VidyaMitra - New Features Usage Examples

## Quick Start with New Features

### Example 1: Complete Career Development Workflow

This example shows the full integrated workflow from resume to projects.

```bash
# Step 1: Login
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=user@example.com&password=password"

# Save the token
TOKEN="your-jwt-token-here"

# Step 2: Use Integrated Workflow (All-in-One)
curl -X POST http://localhost:8000/api/ai/projects/integrated-workflow \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Software Developer with 2 years experience in Python and SQL...",
    "target_role": "Data Analyst",
    "experience_years": 2,
    "experience_level": "entry"
  }'
```

**What you get:**
1. Skills extracted from resume
2. Job matches with fit scores
3. Missing skills identified
4. Project ideas to close gaps
5. Estimated improvement in fit score

---

### Example 2: Job Matching Only

Find which jobs you're qualified for right now.

```bash
curl -X POST http://localhost:8000/api/ai/job-match/match \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_skills": ["Python", "SQL", "Excel", "Data Cleaning"],
    "experience_years": 2,
    "target_domain": "Data Science"
  }'
```

**Response includes:**
- Multiple job matches sorted by fit score
- Matching skills for each role
- Missing critical skills
- Quick wins (easy skills with high impact)
- Specific recommendations

---

### Example 3: Detailed Skill Gap Analysis

Deep dive into what you need for a specific role.

```bash
curl -X POST http://localhost:8000/api/ai/job-match/skill-gap-analysis \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_skills": ["Python", "SQL", "Excel"],
    "target_role": "Data Scientist",
    "target_domain": "Data Science"
  }'
```

**Response includes:**
- Overall fit percentage
- Each missing skill with:
  - Importance level
  - Learning difficulty
  - Estimated time to learn
  - Why it's needed
- Prioritized learning order
- Timeline to readiness

---

### Example 4: Generate Resume Projects

Get project ideas that directly improve your resume.

```bash
curl -X POST http://localhost:8000/api/ai/projects/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_role": "Data Analyst",
    "missing_skills": ["Power BI", "Data Visualization", "Statistics"],
    "experience_level": "entry",
    "num_projects": 3
  }'
```

**Each project includes:**
- Compelling title
- Skills covered
- Tech stack
- Key features
- 3 resume bullet points (achievement-focused)
- Implementation steps with timeline
- Learning resources
- Impact on fit score
- Interview talking points

---

### Example 5: Skill-Specific Project

Need to master one specific skill? Get a focused project.

```bash
curl -X POST http://localhost:8000/api/ai/projects/skill-project \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "Machine Learning",
    "target_role": "Data Scientist",
    "experience_level": "mid"
  }'
```

**Response includes:**
- Detailed project focused on that skill
- Step-by-step implementation guide
- Success criteria
- Portfolio presentation tips
- GitHub README template

---

### Example 6: Enhance Existing Project

Already have a project? Make it better.

```bash
curl -X POST http://localhost:8000/api/ai/projects/enhance-project \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_description": "Built a todo list app with React and local storage",
    "missing_skills": ["TypeScript", "Testing", "CI/CD", "Backend"]
  }'
```

**Response includes:**
- Multiple enhancement suggestions
- Skills each enhancement covers
- Implementation effort (low/medium/high)
- Value added to resume
- Updated resume bullet points
- Prioritized recommendation

---

### Example 7: Portfolio Strategy

Get a complete portfolio improvement plan.

```bash
curl -X POST http://localhost:8000/api/ai/projects/portfolio-strategy \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_role": "Full Stack Developer",
    "current_projects": ["Todo App", "Weather Dashboard"],
    "missing_skills": ["Node.js", "Databases", "Authentication", "Docker"]
  }'
```

**Response includes:**
- Portfolio assessment (strengths and gaps)
- Recommended projects with priorities
- Portfolio presentation tips
- GitHub profile improvements
- Complete timeline

---

### Example 8: Browse Available Roles

See what roles are available in each domain.

```bash
# Get all domains
curl -X GET http://localhost:8000/api/ai/job-match/domains \
  -H "Authorization: Bearer $TOKEN"

# Get roles in a specific domain
curl -X GET http://localhost:8000/api/ai/job-match/roles/Data%20Science \
  -H "Authorization: Bearer $TOKEN"
```

---

## Real-World Use Cases

### Use Case 1: College Student Preparing for Job Market

**Goal:** Understand job readiness and build portfolio

```python
# 1. Match current skills to jobs
POST /api/ai/job-match/match
{
  "user_skills": ["Python", "Java", "HTML", "CSS"],
  "experience_years": 0,
  "target_domain": "Web Development"
}

# Result: 45% fit for Junior Frontend Developer
# Missing: React, JavaScript frameworks, Git

# 2. Generate projects to close gaps
POST /api/ai/projects/generate
{
  "target_role": "Junior Frontend Developer",
  "missing_skills": ["React", "JavaScript", "Git"],
  "experience_level": "entry",
  "num_projects": 3
}

# Result: 3 projects covering React, modern JS, and Git
# Estimated improvement: +30 fit score points
```

### Use Case 2: Professional Switching Careers

**Goal:** Transition from Business Analyst to Data Scientist

```python
# 1. Detailed gap analysis
POST /api/ai/job-match/skill-gap-analysis
{
  "user_skills": ["Excel", "SQL", "Tableau", "Business Analysis"],
  "target_role": "Data Scientist"
}

# Result: 40% fit, need ML, Python, Statistics
# Timeline: 6-8 months

# 2. Get portfolio strategy
POST /api/ai/projects/portfolio-strategy
{
  "target_role": "Data Scientist",
  "current_projects": [],
  "missing_skills": ["Machine Learning", "Python", "Statistics"]
}

# Result: Prioritized project roadmap
# 3 key projects to demonstrate ML skills
```

### Use Case 3: Improving Existing Portfolio

**Goal:** Make current projects more impressive

```python
# 1. Enhance existing project
POST /api/ai/projects/enhance-project
{
  "project_description": "E-commerce site with React frontend",
  "missing_skills": ["Backend", "Database", "Authentication", "Testing"]
}

# Result: 4 enhancement suggestions
# Priority: Add Node.js backend with MongoDB
# Impact: +20 fit score points for Full Stack roles
```

---

## Integration Patterns

### Pattern 1: Resume → Jobs → Projects

```
1. Upload Resume
   ↓
2. Extract Skills
   ↓
3. Match to Jobs (find gaps)
   ↓
4. Generate Projects (close gaps)
   ↓
5. Complete Projects
   ↓
6. Re-match (see improvement)
```

### Pattern 2: Target Role → Gap Analysis → Projects

```
1. Choose Target Role
   ↓
2. Analyze Skill Gap
   ↓
3. Prioritize Skills
   ↓
4. Generate Focused Projects
   ↓
5. Track Progress
```

### Pattern 3: Portfolio Improvement

```
1. List Current Projects
   ↓
2. Get Portfolio Strategy
   ↓
3. Enhance Existing Projects
   ↓
4. Add New Projects
   ↓
5. Optimize Presentation
```

---

## Tips for Best Results

### For Job Matching
- ✅ Be specific with skills (e.g., "React" not "frontend")
- ✅ Include both technical and soft skills
- ✅ Specify target domain for focused results
- ✅ Update experience years accurately

### For Project Generation
- ✅ List 3-5 missing skills for best project ideas
- ✅ Choose appropriate experience level
- ✅ Request 2-3 projects (not too many)
- ✅ Focus on skills with high impact on fit score

### For Portfolio Strategy
- ✅ List all current projects (even small ones)
- ✅ Be honest about skill gaps
- ✅ Consider time available for projects
- ✅ Follow prioritized recommendations

---

## Testing the Features

### Quick Test Script

```bash
# Set your token
export TOKEN="your-jwt-token"

# Test job matching
curl -X POST http://localhost:8000/api/ai/job-match/match \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_skills":["Python","SQL"],"experience_years":1}'

# Test project generation
curl -X POST http://localhost:8000/api/ai/projects/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target_role":"Data Analyst","missing_skills":["Power BI"],"experience_level":"entry"}'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"
TOKEN = "your-jwt-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Job matching
response = requests.post(
    f"{BASE_URL}/api/ai/job-match/match",
    json={
        "user_skills": ["Python", "SQL", "Excel"],
        "experience_years": 2,
        "target_domain": "Data Science"
    },
    headers=headers
)
print(response.json())

# Project generation
response = requests.post(
    f"{BASE_URL}/api/ai/projects/generate",
    json={
        "target_role": "Data Analyst",
        "missing_skills": ["Power BI", "Tableau"],
        "experience_level": "entry",
        "num_projects": 2
    },
    headers=headers
)
print(response.json())
```

---

## Next Steps

1. **Try the integrated workflow** for complete experience
2. **Explore interactive docs** at http://localhost:8000/docs
3. **Run automated tests**: `python test_api.py`
4. **Read full documentation**: `NEW_FEATURES_DOCUMENTATION.md`
5. **Customize job roles** in `job_match_ai.py` for your needs

---

## Support

- Interactive API testing: http://localhost:8000/docs
- Full documentation: `backend/NEW_FEATURES_DOCUMENTATION.md`
- Test script: `backend/test_api.py`
- Main README: `README.md`
