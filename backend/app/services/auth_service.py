from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.models.user import UserCreate, User
from supabase import create_client, Client
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        self.secret_key = os.getenv("SECRET_KEY")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    async def create_user(self, user: UserCreate) -> User:
        hashed_password = self.get_password_hash(user.password)
        response = self.supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {"data": {"full_name": user.full_name}}
        })
        return User(
            id=response.user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=datetime.utcnow()
        )
    
    async def authenticate_user(self, email: str, password: str):
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return User(
                id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name", ""),
                created_at=datetime.utcnow()
            )
        except:
            return None
    
    async def get_current_user(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                return None
            # Fetch user from Supabase
            response = self.supabase.auth.get_user(token)
            return User(
                id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name", ""),
                created_at=datetime.utcnow()
            )
        except JWTError:
            return None
