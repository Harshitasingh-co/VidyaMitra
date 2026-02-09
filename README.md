# VidyaMitra - AI-Powered Career Development Platform

VidyaMitra is a comprehensive AI-powered platform designed to help students and professionals with career development, skill assessment, and interview preparation.

## 🌟 Features

### 1. AI Resume Analyzer
- Upload and analyze resumes in PDF format
- ATS (Applicant Tracking System) scoring
- Skill extraction and gap analysis
- Personalized recommendations for improvement
- Identifies strengths and weaknesses

### 2. AI Interview Simulator
- Generate role-specific interview questions
- Real-time answer evaluation with AI feedback
- Adaptive follow-up questions based on responses
- Detailed performance scoring
- Practice for entry, mid, and senior level positions

### 3. AI Career Roadmap
- Personalized career transition planning
- Skill gap analysis
- 3-6 month learning paths with milestones
- Certification recommendations
- Transferable skills identification
- Job search tips

### 4. AI Mentor (Coming Soon)
- Interactive AI chat for career guidance
- Personalized learning recommendations
- Real-time career advice

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: Google Gemini AI (gemini-2.5-flash)
- **PDF Processing**: PyPDF2
- **Authentication**: JWT tokens (optional)
- **Database**: Supabase (optional)

### Frontend
- **Framework**: React.js with Vite
- **Styling**: Custom CSS with modern design
- **Icons**: Lucide React
- **Routing**: React Router v6
- **HTTP Client**: Axios

## 📋 Prerequisites

- Python 3.12+ (backend)
- Node.js 16+ (frontend)
- Google Gemini API key

## 🚀 Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3.12 -m venv venv_py312
source venv_py312/bin/activate  # On Windows: venv_py312\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
```

5. Add your API keys to `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

6. Start the backend server:
```bash
python -m uvicorn main:app --reload --port 8001
```

The backend will be available at `http://localhost:8001`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Update `.env` with backend URL:
```env
VITE_API_URL=http://localhost:8001/api
```

5. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📁 Project Structure

```
VidyaMitra/
├── backend/
│   ├── ai/                    # AI services (Gemini integration)
│   ├── app/
│   │   ├── models/           # Data models
│   │   ├── routers/          # API endpoints
│   │   └── services/         # Business logic
│   ├── core/                 # Configuration and security
│   ├── services/             # External API services
│   ├── utils/                # Utility functions
│   ├── main.py               # FastAPI application
│   └── requirements.txt      # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── pages/            # React page components
    │   ├── services/         # API client
    │   ├── App.jsx           # Main app component
    │   └── main.jsx          # Entry point
    ├── package.json          # Node dependencies
    └── vite.config.js        # Vite configuration
```

## 🔑 API Endpoints

### Resume Analysis
- `POST /api/ai/resume/upload` - Upload resume PDF
- `POST /api/ai/resume/analyze` - Analyze resume content

### Mock Interview
- `POST /api/ai/interview/start` - Start interview session
- `POST /api/ai/interview/answer` - Submit answer for evaluation
- `POST /api/ai/interview/followup` - Get follow-up question
- `POST /api/ai/interview/feedback` - Get final feedback

### Career Planning
- `POST /api/ai/career/roadmap` - Generate career roadmap
- `POST /api/ai/career/skill-gap` - Analyze skill gaps

## 🎨 Features in Detail

### Resume Analysis
The AI analyzes resumes for:
- ATS compatibility score
- Keyword optimization
- Skills extraction
- Experience relevance
- Formatting and structure
- Missing critical skills
- Actionable recommendations

### Mock Interview
- Customizable by role and experience level
- Generates 2-5 questions per session
- Evaluates answers on:
  - Relevance
  - Depth of knowledge
  - Communication clarity
  - Technical accuracy
- Provides improvement suggestions

### Career Roadmap
- Analyzes current skills vs target role requirements
- Creates phased learning plans
- Suggests certifications and courses
- Provides realistic timelines
- Identifies transferable skills

## 🔒 Security

- Environment variables for sensitive data
- Optional JWT authentication
- CORS configuration for frontend-backend communication
- Input validation on all endpoints

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👥 Authors

- Harshita Singh

## 🙏 Acknowledgments

- Google Gemini AI for powering the AI features
- FastAPI for the robust backend framework
- React and Vite for the modern frontend experience

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Note**: This is a demo application. For production use, ensure proper security measures, database setup, and API key management.
