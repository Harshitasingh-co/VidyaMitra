# VidyaMitra - Quick Reference Card

## 🚀 Quick Start

```bash
# Backend
cd backend && venv_py312/bin/python -m uvicorn main:app --reload --port 8001

# Frontend
cd frontend && npm run dev

# Access
Frontend: http://localhost:5173
API Docs: http://localhost:8001/docs
```

## 🔑 Environment

```env
# backend/.env
GEMINI_API_KEY=AIzaSyCkaA3xSnzQIf0-U4s7CDt84oqwxxiX_B4

# frontend/.env
VITE_API_URL=http://localhost:8001/api
```

## 📍 Main Routes

| Route | Feature | Status |
|-------|---------|--------|
| `/` | Dashboard | ✅ |
| `/resume` | Context-Aware Resume | ✅ |
| `/interview` | Basic Interview | ✅ |
| `/career` | Career Planning | ✅ |
| `/ai-mentor` | Coming Soon | 🚧 |

## 🎯 Key Features

### 1. Context-Aware Resume (✅ COMPLETE)
```
Step 1: Career Goals → Step 2: Upload → Step 3: Results
- Role fit score
- Certifications with links
- Project ideas with resume bullets
- Technical skills gap
- Company advice
```

### 2. Advanced Interview (✅ BACKEND ONLY)
```
Types: Technical | Aptitude | Soft Skills | Full
- Pre-interview intelligence
- Adaptive difficulty
- Anti-cheating (tab/paste detection)
- Comprehensive reports
```

### 3. Career Planning (✅ COMPLETE)
```
Input: Current role → Target role → Skills
Output: Roadmap, certifications, milestones
```

## 📡 API Endpoints

### Context-Aware Resume
```bash
POST /api/ai/career-intent
POST /api/ai/context-aware-analyze
POST /api/ai/upload-with-intent
```

### Advanced Interview
```bash
POST /api/ai/advanced-interview/start
POST /api/ai/advanced-interview/technical/question
POST /api/ai/advanced-interview/technical/submit
POST /api/ai/advanced-interview/aptitude/question
POST /api/ai/advanced-interview/aptitude/submit
POST /api/ai/advanced-interview/soft-skills/question
POST /api/ai/advanced-interview/soft-skills/submit
GET  /api/ai/advanced-interview/report/{session_id}
```

### Career Planning
```bash
POST /api/ai/career/roadmap
POST /api/ai/career/skill-gap
```

## 🧪 Testing

```bash
# Test context-aware resume
cd backend && venv_py312/bin/python test_context_aware_resume.py

# Test advanced interview
cd backend && venv_py312/bin/python test_advanced_interview.py
```

## 📊 Project Stats

- **Total Endpoints**: 30+
- **Backend Files**: 25+
- **Frontend Pages**: 7
- **AI Models**: Gemini 2.5 Flash
- **Temperature**: 0.3
- **Lines of Code**: 10,000+

## 🎨 Tech Stack

**Backend**: FastAPI + Python 3.12 + Gemini AI
**Frontend**: React + Vite + Axios
**Database**: In-memory (Supabase-ready)
**Auth**: JWT (optional)

## 📝 Documentation

1. `IMPLEMENTATION_SUMMARY.md` - Complete overview
2. `CONTEXT_AWARE_RESUME_API.md` - Resume API docs
3. `ADVANCED_INTERVIEW_API.md` - Interview API docs
4. `QUICK_START_CONTEXT_AWARE.md` - Quick start guide

## 🔧 Common Commands

```bash
# Check backend health
curl http://localhost:8001/health

# View API docs
open http://localhost:8001/docs

# Check frontend
open http://localhost:5173

# Run tests
cd backend && venv_py312/bin/python test_*.py
```

## ⚠️ Known Issues

1. **Gemini API Quota**: Free tier = 20 requests/day
2. **Frontend**: Advanced interview UI not built yet
3. **Database**: Using in-memory storage (temporary)

## 🎯 Next Steps

1. Build advanced interview frontend
2. Connect to Supabase for persistence
3. Add job matching frontend
4. Add project generator frontend

## 📞 Quick Help

**API not working?**
- Check if backend is running on port 8001
- Verify GEMINI_API_KEY in backend/.env
- Check API quota: https://ai.dev/rate-limit

**Frontend not loading?**
- Check if frontend is running on port 5173
- Verify VITE_API_URL in frontend/.env
- Clear browser cache

**Tests failing?**
- Ensure backend is running
- Check Gemini API quota
- Wait 30s between test runs

---

**Quick Access**: http://localhost:5173
**API Docs**: http://localhost:8001/docs
**GitHub**: https://github.com/Harshitasingh-co/VidyaMitra
