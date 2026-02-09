# Quick Start: Context-Aware Resume Analysis

## 🚀 For Developers

### Start the Backend
```bash
cd backend
source venv_py312/bin/activate  # or venv_py312\Scripts\activate on Windows
python -m uvicorn main:app --reload --port 8001
```

### Test the Feature
```bash
cd backend
python test_context_aware_resume.py
```

### View API Docs
Open: http://localhost:8001/docs
Look for: **"AI - Context-Aware Resume"** tag

## 📝 API Quick Reference

### 1. Submit Career Intent
```bash
curl -X POST "http://localhost:8001/api/ai/career-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "desired_role": "Data Analyst",
    "experience_level": "0-2 years",
    "target_companies": ["Product-based companies"]
  }'
```

**Response**: `{ "intent_id": "...", "message": "..." }`

### 2. Analyze Resume
```bash
curl -X POST "http://localhost:8001/api/ai/context-aware-analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Your resume text here...",
    "intent_id": "your-intent-id-here"
  }'
```

**Response**: Full analysis with certifications, projects, skill gaps

## 🎨 For Frontend Developers

### Step 1: Career Intent Form
```javascript
const submitIntent = async (formData) => {
  const response = await fetch('/api/ai/career-intent', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      desired_role: formData.role,
      experience_level: formData.experience,
      target_companies: formData.companies
    })
  });
  const { intent_id } = await response.json();
  return intent_id;
};
```

### Step 2: Upload Resume
```javascript
const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/ai/resume/upload', {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  return data.data.full_text;
};
```

### Step 3: Get Analysis
```javascript
const analyzeResume = async (resumeText, intentId) => {
  const response = await fetch('/api/ai/context-aware-analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_text: resumeText,
      intent_id: intentId
    })
  });
  const result = await response.json();
  return result.data;
};
```

### Step 4: Display Results
```javascript
// Role Fit Score
<div className="score-card">
  <h3>Role Fit Score</h3>
  <div className="progress-bar">
    <div style={{ width: `${analysis.role_fit_score}%` }}>
      {analysis.role_fit_score}%
    </div>
  </div>
</div>

// Certifications with Links
{analysis.certifications.map(cert => (
  <div className="cert-card" key={cert.name}>
    <h4>{cert.name}</h4>
    <p>{cert.description}</p>
    <a href={cert.link} target="_blank">
      View Certification →
    </a>
    <span className={`priority-${cert.priority.toLowerCase()}`}>
      {cert.priority} Priority
    </span>
  </div>
))}

// Project Ideas with Resume Bullets
{analysis.projects.map(project => (
  <div className="project-card" key={project.title}>
    <h4>{project.title}</h4>
    <p>{project.project_idea}</p>
    <div className="resume-bullets">
      <h5>Ready-to-use Resume Bullets:</h5>
      {project.resume_bullets.map((bullet, i) => (
        <div key={i} className="bullet-item">
          <span>{bullet}</span>
          <button onClick={() => copyToClipboard(bullet)}>
            Copy
          </button>
        </div>
      ))}
    </div>
  </div>
))}
```

## 📊 Response Structure

```javascript
{
  role_fit_score: 70,                    // 0-100
  existing_skills: [...],                // Array of strings
  missing_skills: [...],                 // Array of strings
  
  technical_skills_required: [
    {
      skill: "Python",
      importance: "High",
      why: "...",
      current_level: "Basic",
      target_level: "Intermediate",
      estimated_learning_time: "8-10 weeks"
    }
  ],
  
  certifications: [
    {
      name: "Google Data Analytics",
      provider: "Coursera",
      link: "https://...",              // Real, clickable link
      priority: "High",
      why_recommended: "..."
    }
  ],
  
  projects: [
    {
      title: "...",
      skills_covered: [...],
      project_idea: "...",
      resume_bullets: [                 // Copy-paste ready!
        "Built dashboard analyzing 50k+ records",
        "Improved efficiency by 30%"
      ],
      resources: {
        dataset: "https://kaggle.com/...",
        reference_repo: "https://github.com/..."
      }
    }
  ],
  
  skill_matching: {
    fully_matching: [...],
    partially_matching: [...],
    completely_missing: [...]
  },
  
  ats_optimization: {
    score: 65,
    missing_keywords: [...],
    suggestions: [...]
  },
  
  company_specific_advice: [...]
}
```

## 🎯 UI Components Needed

1. **Career Intent Form**
   - Role input (text)
   - Experience dropdown (0-2, 3-5, 5+ years)
   - Company type checkboxes
   - Industry multi-select (optional)

2. **Resume Upload**
   - File input (PDF/DOCX/TXT)
   - Upload progress
   - Text preview

3. **Results Dashboard**
   - Role fit score (circular progress or bar)
   - Skill cards (existing vs missing)
   - Certification cards with links
   - Project cards with copy buttons
   - ATS tips section
   - Company advice section

## 🎨 Design Suggestions

### Color Coding
- **High Priority**: Red/Orange (#e53e3e)
- **Medium Priority**: Yellow/Amber (#ed8936)
- **Low Priority**: Blue (#4299e1)
- **Existing Skills**: Green (#48bb78)
- **Missing Skills**: Red (#e53e3e)

### Layout
```
┌─────────────────────────────────────┐
│  Role Fit Score: 70%  [Progress]   │
├─────────────────────────────────────┤
│  ✅ Existing Skills (7)             │
│  [Skill] [Skill] [Skill]            │
├─────────────────────────────────────┤
│  ❌ Missing Skills (7)              │
│  [Skill] [Skill] [Skill]            │
├─────────────────────────────────────┤
│  🎓 Certifications (2)              │
│  ┌─────────────────────────────┐   │
│  │ Google Data Analytics       │   │
│  │ [View Certification →]      │   │
│  │ Priority: HIGH              │   │
│  └─────────────────────────────┘   │
├─────────────────────────────────────┤
│  💡 Project Ideas (2)               │
│  ┌─────────────────────────────┐   │
│  │ E-commerce Dashboard        │   │
│  │ Resume Bullets:             │   │
│  │ • Built dashboard... [Copy] │   │
│  │ • Improved by 30%... [Copy] │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

## 🔧 Environment Setup

### Required
```env
GEMINI_API_KEY=your_key_here
```

### Optional
```env
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
```

## 📚 Documentation

- **Full API Docs**: `backend/CONTEXT_AWARE_RESUME_API.md`
- **Implementation Details**: `CONTEXT_AWARE_FEATURE_COMPLETE.md`
- **Test Script**: `backend/test_context_aware_resume.py`

## ✅ Checklist for Frontend

- [ ] Create career intent form (multi-step or single page)
- [ ] Add resume upload with intent_id
- [ ] Design results page with all sections
- [ ] Add copy-to-clipboard for resume bullets
- [ ] Make certification links clickable
- [ ] Add skill progress visualizations
- [ ] Implement responsive design
- [ ] Add loading states
- [ ] Handle errors gracefully
- [ ] Test with real resumes

## 🚀 Ready to Go!

The backend is fully implemented and tested. All endpoints are working. Just build the frontend UI and connect to these endpoints!

**API Base URL**: `http://localhost:8001/api/ai`
**Docs**: `http://localhost:8001/docs`
