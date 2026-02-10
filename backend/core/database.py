"""
MongoDB Database Configuration and Connection Management
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB"""
    try:
        mongodb.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000
        )
        # Test connection
        await mongodb.client.admin.command('ping')
        mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]
        logger.info(f"Connected to MongoDB database: {settings.MONGODB_DB_NAME}")
        
        # Create indexes
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        mongodb.client = None
        mongodb.db = None
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        mongodb.client = None
        mongodb.db = None

async def close_mongo_connection():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Closed MongoDB connection")

async def create_indexes():
    """Create database indexes for better performance"""
    if mongodb.db is None:
        return
    
    try:
        # Users collection indexes
        await mongodb.db.users.create_index("email", unique=True)
        
        # Internship profiles collection indexes
        await mongodb.db.internship_profiles.create_index("user_id", unique=True)
        await mongodb.db.internship_profiles.create_index("graduation_year")
        await mongodb.db.internship_profiles.create_index("skills")
        await mongodb.db.internship_profiles.create_index("preferred_roles")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Failed to create indexes: {e}")

def get_database():
    """Get MongoDB database instance"""
    return mongodb.db
