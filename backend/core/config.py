from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # App
    APP_NAME: str = "VidyaMitra API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Supabase (Legacy - replaced by MongoDB)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "vidyamitra")
    
    # OpenAI (Legacy - not used)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.3
    
    # Google Gemini (Primary AI)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # External APIs
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID: str = os.getenv("GOOGLE_CSE_ID", "")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    
    # Agora Conversational AI Agent
    AGORA_APP_ID: str = os.getenv("AGORA_APP_ID", "")
    AGORA_APP_CERTIFICATE: str = os.getenv("AGORA_APP_CERTIFICATE", "")
    AGORA_CUSTOMER_ID: str = os.getenv("AGORA_CUSTOMER_ID", "")
    AGORA_CUSTOMER_SECRET: str = os.getenv("AGORA_CUSTOMER_SECRET", "")
    AGORA_LLM_API_KEY: str = os.getenv("AGORA_LLM_API_KEY", "")
    AGORA_LLM_MODEL: str = os.getenv("AGORA_LLM_MODEL", "gemini-2.5-flash")
    AGORA_TTS_VENDOR: str = os.getenv("AGORA_TTS_VENDOR", "cartesia")
    AGORA_TTS_API_KEY: str = os.getenv("AGORA_TTS_API_KEY", "")
    AGORA_TTS_MODEL_ID: str = os.getenv("AGORA_TTS_MODEL_ID", "sonic-3")
    AGORA_TTS_VOICE_ID: str = os.getenv("AGORA_TTS_VOICE_ID", "")
    AGORA_ASR_VENDOR: str = os.getenv("AGORA_ASR_VENDOR", "ares")
    AGORA_ASR_LANGUAGE: str = os.getenv("AGORA_ASR_LANGUAGE", "en-US")
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
