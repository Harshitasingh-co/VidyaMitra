# VidyaMitra Setup Guide

Complete step-by-step guide to set up and run the VidyaMitra platform.

## Prerequisites Installation

### 1. Python 3.10+
Download from: https://www.python.org/downloads/
```bash
python --version  # Verify installation
```

### 2. Node.js 18+ (includes npm)
Download from: https://nodejs.org/en/download
```bash
node --version
npm --version
```

### 3. VS Code
Download from: https://code.visualstudio.com/download

## Backend Setup

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Create Virtual Environment
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` file and add your API keys:
- Get Supabase credentials from: https://supabase.com
- Get OpenAI API key from: https://platform.openai.com
- Get Google API key from: https://console.cloud.google.com
- Get YouTube API key from: https://console.cloud.google.com
- Get Pexels API key from: https://www.pexels.com/api
- Get News API key from: https://newsapi.org

### Step 5: Start Backend Server
```bash
python -m uvicorn main:app --reload
```

Backend will run at: **http://localhost:8000**
API Documentation: **http://localhost:8000/docs**

## Frontend Setup

### Step 1: Open New Terminal (keep backend running)

### Step 2: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 3: Install Dependencies
```bash
npm install
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
```

The default configuration should work with local backend.

### Step 5: Start Frontend Server
```bash
npm run dev
```

Frontend will run at: **http://localhost:5173**

## Verification

Once both servers are running:

1. **Backend Health Check**: Visit http://localhost:8000/health
2. **API Documentation**: Visit http://localhost:8000/docs
3. **Frontend Application**: Visit http://localhost:5173

## Usage Flow

1. **Register**: Create a new account at http://localhost:5173/register
2. **Login**: Sign in with your credentials
3. **Dashboard**: Access all features from the main dashboard
4. **Resume Analysis**: Upload and analyze your resume
5. **Mock Interview**: Practice with AI-generated questions
6. **Career Path**: Get personalized career recommendations

## Troubleshooting

### Backend Issues
- Ensure virtual environment is activated
- Check all API keys are correctly set in `.env`
- Verify Python version is 3.10+

### Frontend Issues
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version is 18+

### CORS Issues
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`

## Development Tips

- Use two terminal windows: one for backend, one for frontend
- Backend auto-reloads on code changes (--reload flag)
- Frontend auto-reloads on code changes (Vite HMR)
- Check browser console for frontend errors
- Check terminal output for backend errors

## Next Steps

After successful setup:
1. Test all three scenarios (Resume, Interview, Career Path)
2. Customize UI styling in `frontend/src/index.css`
3. Add more AI features in backend services
4. Deploy to cloud (Vercel for frontend, Railway/Render for backend)

## Support

For issues or questions:
- Check API documentation at http://localhost:8000/docs
- Review error logs in terminal
- Verify all environment variables are set correctly
