from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user
)
from core.config import get_settings
from utils.response_formatter import get_response_formatter
from datetime import timedelta
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Initialize Supabase client (only if valid credentials provided)
supabase: Client = None
try:
    if settings.SUPABASE_URL and settings.SUPABASE_KEY and \
       not settings.SUPABASE_URL.startswith('your-') and \
       not settings.SUPABASE_KEY.startswith('your-'):
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    else:
        logger.warning("Supabase not configured - using in-memory storage")
except Exception as e:
    logger.warning(f"Failed to initialize Supabase: {e}. Using in-memory storage.")

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register")
async def register(user: UserRegister):
    """
    Register a new user
    Uses Supabase Auth for user management
    """
    try:
        logger.info(f"Registering new user: {user.email}")
        
        if not supabase:
            raise HTTPException(
                status_code=500,
                detail="Authentication service not configured"
            )
        
        # Register with Supabase
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "full_name": user.full_name
                }
            }
        })
        
        if response.user:
            formatter = get_response_formatter()
            return formatter.success({
                "user_id": response.user.id,
                "email": response.user.email,
                "full_name": user.full_name
            }, "User registered successfully")
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
            
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login user and return JWT access token
    """
    try:
        logger.info(f"Login attempt for: {form_data.username}")
        
        if not supabase:
            # Fallback: Create token without Supabase
            logger.warning("Supabase not configured, using fallback auth")
            access_token = create_access_token(
                data={"sub": form_data.username},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            return {"access_token": access_token, "token_type": "bearer"}
        
        # Authenticate with Supabase
        response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": response.user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"Login successful for: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@router.get("/me")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user profile"""
    formatter = get_response_formatter()
    return formatter.success({
        "email": current_user["email"]
    }, "User profile retrieved")

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (client should discard token)"""
    logger.info(f"User logged out: {current_user['email']}")
    formatter = get_response_formatter()
    return formatter.success(None, "Logged out successfully")
