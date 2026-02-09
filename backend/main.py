from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, resume, interview, career, job_match, project_ideas, career_intent
from core.config import get_settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Educational Platform with GenAI Integration - Now with Job Matching & Project Generator",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(career_intent.router, prefix="/api/ai", tags=["AI - Context-Aware Resume"])
app.include_router(resume.router, prefix="/api/ai/resume", tags=["AI - Resume Analysis"])
app.include_router(interview.router, prefix="/api/ai/interview", tags=["AI - Mock Interview"])
app.include_router(career.router, prefix="/api/ai/career", tags=["AI - Career Planning"])
app.include_router(job_match.router, prefix="/api/ai/job-match", tags=["AI - Job Matching"])
app.include_router(project_ideas.router, prefix="/api/ai/projects", tags=["AI - Project Generator"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("VidyaMitra API starting up...")
    logger.info(f"Gemini API configured: {bool(settings.GEMINI_API_KEY)}")
    logger.info(f"Supabase configured: {bool(settings.SUPABASE_URL)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("VidyaMitra API shutting down...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to VidyaMitra API - Powered by Google Gemini",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "ai_model": "Google Gemini 1.5 Flash",
        "services": {
            "gemini": bool(settings.GEMINI_API_KEY),
            "supabase": bool(settings.SUPABASE_URL),
            "youtube": bool(settings.YOUTUBE_API_KEY),
            "google": bool(settings.GOOGLE_API_KEY)
        }
    }
