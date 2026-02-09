# VidyaMitra Quick Reference Guide

## 🚀 Getting Started (2 Minutes)

### 1. Start Backend
```bash
cd backend
./start.sh          # macOS/Linux
# OR
start.bat           # Windows
```

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🔑 Required API Keys

### Minimum (Required)
```env
OPENAI_API_KEY=sk-...
```
Get from: https://platform.openai.com

### Recommended
```env
SUPABASE_URL=https://...
SUPABASE_KEY=...
```
Get from: https://supabase.com

### Optional
```env
YOUTUBE_API_KEY=...
GOOGLE_API_KEY=...
GOOGLE_CSE_ID=...
PEXELS_API_KEY=...
```

---

## 📡 API Quick Reference

### Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123","full_name":"User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=user@example.com&password=pass123"
```

### Resume Analysis
```bash
# Analyze resume
curl -X POST http://localhost:8000/api/ai/resume/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"...","target_role":"Software Engineer"}'
```

### Mock Interview
```bash
# Start interview
curl -X POST http://localhost:8000/api/ai/interview/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"Developer","experience_level":"mid","num_questions":3}'
```

### Career Planning
```bash
# Generate roadmap
curl -X POST http://localhost:8000/api/ai/career/roadmap \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"current_role":"Frontend","target_role":"Full Stack","current_skills":["React"],"experience_years":3}'
```

---

## 🧪 Testing

### Quick Test
```bash
cd backend
python test_api.py
```

### Manual Test
1. Go to http://localhost:8000/docs
2. Click "Authorize"
3. Login to get token
4. Paste token in authorization
5. Test any endpoint

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check .env file
cat .env  # Verify OPENAI_API_KEY is set
```

### OpenAI API errors
- Check API key is valid
- Verify you have credits: https://platform.openai.com/usage
- Check rate limits

### Port already in use
```bash
# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Import errors
```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 📁 File Locations

### Configuration
- Backend config: `backend/.env`
- Frontend config: `frontend/.env`

### Logs
- Development: Terminal output
- Production: Check deployment platform logs

### Documentation
- API docs: http://localhost:8000/docs
- Full API reference: `backend/API_DOCUMENTATION.md`
- Deployment guide: `backend/DEPLOYMENT_GUIDE.md`

---

## 🔧 Common Commands

### Backend
```bash
# Start server
python -m uvicorn main:app --reload

# Run tests
python test_api.py

# Check health
curl http://localhost:8000/health

# Install dependencies
pip install -r requirements.txt
```

### Frontend
```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 📊 API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00"
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "2024-01-15T10:30:00",
  "error_code": "OPTIONAL_CODE"
}
```

---

## 💡 Tips

### Development
- Use `/docs` for interactive API testing
- Check logs for detailed error messages
- Enable debug mode in development
- Use `--reload` flag for auto-restart

### Production
- Set strong SECRET_KEY
- Enable HTTPS
- Set up monitoring
- Implement rate limiting
- Use environment-specific configs

### Cost Optimization
- Cache AI responses
- Set OpenAI usage limits
- Monitor token usage
- Use GPT-3.5 for less critical tasks

---

## 🎯 Three Main Scenarios

### 1. Resume Analysis
**Endpoint:** `POST /api/ai/resume/analyze`
**Use Case:** Upload resume, get AI feedback, identify skill gaps
**Output:** ATS score, strengths, weaknesses, recommendations

### 2. Mock Interview
**Endpoints:** 
- `POST /api/ai/interview/start` - Get questions
- `POST /api/ai/interview/answer` - Get feedback
**Use Case:** Practice interviews, get AI evaluation
**Output:** Scores, feedback, improvement tips

### 3. Career Planning
**Endpoint:** `POST /api/ai/career/roadmap`
**Use Case:** Plan career transition, get learning path
**Output:** Roadmap, skills to learn, certifications, timeline

---

## 📞 Support

### Check These First
1. Health endpoint: http://localhost:8000/health
2. API docs: http://localhost:8000/docs
3. Test script: `python test_api.py`
4. Logs in terminal

### Documentation
- `README.md` - Overview and setup
- `API_DOCUMENTATION.md` - Complete API reference
- `DEPLOYMENT_GUIDE.md` - Production deployment
- `IMPLEMENTATION_COMPLETE.md` - Technical details

---

## ✅ Verification Checklist

Before deploying:
- [ ] OpenAI API key configured
- [ ] Backend starts without errors
- [ ] Health check returns 200
- [ ] Test script passes
- [ ] Frontend connects to backend
- [ ] All three scenarios work
- [ ] Authentication works
- [ ] Error handling works

---

## 🚢 Deployment Quick Start

### Railway
```bash
railway login
railway init
railway up
```

### Render
1. Connect GitHub repo
2. Add environment variables
3. Deploy

### Docker
```bash
docker build -t vidyamitra-api backend/
docker run -p 8000:8000 --env-file backend/.env vidyamitra-api
```

---

**Need more help?** Check the full documentation in the respective MD files.
