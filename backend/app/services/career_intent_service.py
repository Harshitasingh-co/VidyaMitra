from app.models.career_intent import CareerIntent
from typing import Optional, Dict
import uuid
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CareerIntentService:
    """Service for managing career intent data"""
    
    def __init__(self):
        # In-memory storage (for demo/development)
        # In production, this should use Supabase or a database
        self._storage: Dict[str, dict] = {}
        self._cleanup_interval = timedelta(hours=24)  # Clean up after 24 hours
    
    def store_intent(self, career_intent: CareerIntent) -> str:
        """
        Store career intent and return unique ID
        
        Args:
            career_intent: User's career intent data
            
        Returns:
            Unique intent ID
        """
        try:
            intent_id = str(uuid.uuid4())
            
            self._storage[intent_id] = {
                "intent": career_intent.model_dump(),
                "created_at": datetime.utcnow().isoformat(),
                "accessed_count": 0
            }
            
            logger.info(f"Stored career intent: {intent_id} for role: {career_intent.desired_role}")
            
            # Cleanup old entries
            self._cleanup_old_intents()
            
            return intent_id
            
        except Exception as e:
            logger.error(f"Failed to store career intent: {e}")
            raise
    
    def get_intent(self, intent_id: str) -> Optional[CareerIntent]:
        """
        Retrieve career intent by ID
        
        Args:
            intent_id: Unique intent ID
            
        Returns:
            CareerIntent object or None if not found
        """
        try:
            if intent_id not in self._storage:
                logger.warning(f"Career intent not found: {intent_id}")
                return None
            
            intent_data = self._storage[intent_id]
            intent_data["accessed_count"] += 1
            
            return CareerIntent(**intent_data["intent"])
            
        except Exception as e:
            logger.error(f"Failed to retrieve career intent: {e}")
            return None
    
    def delete_intent(self, intent_id: str) -> bool:
        """
        Delete career intent
        
        Args:
            intent_id: Unique intent ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            if intent_id in self._storage:
                del self._storage[intent_id]
                logger.info(f"Deleted career intent: {intent_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete career intent: {e}")
            return False
    
    def _cleanup_old_intents(self):
        """Remove intents older than cleanup_interval"""
        try:
            now = datetime.utcnow()
            to_delete = []
            
            for intent_id, data in self._storage.items():
                created_at = datetime.fromisoformat(data["created_at"])
                if now - created_at > self._cleanup_interval:
                    to_delete.append(intent_id)
            
            for intent_id in to_delete:
                del self._storage[intent_id]
            
            if to_delete:
                logger.info(f"Cleaned up {len(to_delete)} old career intents")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        return {
            "total_intents": len(self._storage),
            "storage_type": "in-memory"
        }

# Singleton instance
_career_intent_service = None

def get_career_intent_service() -> CareerIntentService:
    """Get CareerIntentService singleton instance"""
    global _career_intent_service
    if _career_intent_service is None:
        _career_intent_service = CareerIntentService()
    return _career_intent_service
