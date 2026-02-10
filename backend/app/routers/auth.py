from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, field_validator
from core.security import (
    create_access_token,
    get_current_user
)
from core.config import get_settings
from core.database import get_database
from app.services.auth_service_mongo import get_auth_service
from utils.response_formatter import get_response_formatter
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        # Bcrypt has a 72 byte limit
        if len(v.encode('utf-8')) > 72:
            # Truncate to 72 bytes
            v_bytes = v.encode('utf-8')[:72]
            v = v_bytes.decode('utf-8', errors='ignore')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register")
async def register(user: UserRegister):
    """
    Register a new user
    Uses MongoDB for user management
    """
    try:
        logger.info(f"Registering new user: {user.email}")
        
        auth_service = get_auth_service()
        
        # Create user with MongoDB
        from app.models.user import UserCreate
        user_create = UserCreate(
            email=user.email,
            password=user.password,
            full_name=user.full_name
        )
        
        new_user = await auth_service.create_user(user_create)
        
        formatter = get_response_formatter()
        return formatter.success({
            "user_id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name
        }, "User registered successfully")
            
    except ValueError as e:
        logger.warning(f"Registration validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
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
        
        auth_service = get_auth_service()
        
        # Authenticate with MongoDB
        user = await auth_service.authenticate_user(form_data.username, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Create JWT token with user ID
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
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
