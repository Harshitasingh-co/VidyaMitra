"""
Authentication Service using MongoDB
"""
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from app.models.user import UserCreate, User
from core.database import get_database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db.users if self.db is not None else None
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            # Bcrypt has a 72 byte limit - truncate if necessary
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            return bcrypt.checkpw(
                password_bytes,
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password using bcrypt"""
        try:
            # Bcrypt has a 72 byte limit - truncate if necessary
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise
    
    async def create_user(self, user: UserCreate) -> User:
        """Create a new user"""
        if self.users_collection is None:
            raise Exception("Database not connected")
        
        # Check if user already exists
        existing_user = await self.users_collection.find_one({"email": user.email})
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user document
        logger.info(f"Creating user with email: {user.email}")
        user_doc = {
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": self.get_password_hash(user.password),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.users_collection.insert_one(user_doc)
        user_doc["id"] = str(result.inserted_id)
        
        logger.info(f"User created successfully: {user.email}")
        return User(
            id=user_doc["id"],
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            created_at=user_doc["created_at"]
        )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        if self.users_collection is None:
            return None
        
        user_doc = await self.users_collection.find_one({"email": email})
        if not user_doc:
            return None
        
        if not self.verify_password(password, user_doc["hashed_password"]):
            return None
        
        return User(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            created_at=user_doc["created_at"]
        )
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        if self.users_collection is None:
            return None
        
        user_doc = await self.users_collection.find_one({"email": email})
        if not user_doc:
            return None
        
        return User(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            created_at=user_doc["created_at"]
        )

def get_auth_service() -> AuthService:
    """Get AuthService instance"""
    return AuthService()
