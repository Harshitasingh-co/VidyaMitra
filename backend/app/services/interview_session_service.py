from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

class InterviewSessionService:
    """Service for managing interview sessions and state"""
    
    def __init__(self):
        # In-memory storage (for demo/development)
        # In production, use Supabase or database
        self._sessions: Dict[str, dict] = {}
        self._cleanup_interval = timedelta(hours=24)
    
    def create_session(
        self,
        user_id: str,
        interview_type: str,
        config: Dict
    ) -> str:
        """
        Create new interview session
        
        Args:
            user_id: User identifier
            interview_type: Type of interview
            config: Interview configuration
            
        Returns:
            Session ID
        """
        try:
            session_id = f"interview_{user_id}_{uuid.uuid4().hex[:8]}"
            
            self._sessions[session_id] = {
                "session_id": session_id,
                "user_id": user_id,
                "interview_type": interview_type,
                "config": config,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active",
                "current_question": 0,
                "technical_evaluations": [],
                "aptitude_evaluations": [],
                "soft_skills_evaluations": [],
                "cheating_indicators": {
                    "tab_switches": 0,
                    "paste_attempts": 0
                },
                "start_time": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Created interview session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self._sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict):
        """Update session data"""
        if session_id in self._sessions:
            self._sessions[session_id].update(updates)
            logger.info(f"Updated session: {session_id}")
    
    def add_evaluation(
        self,
        session_id: str,
        evaluation_type: str,
        evaluation: Dict
    ):
        """Add evaluation to session"""
        if session_id in self._sessions:
            key = f"{evaluation_type}_evaluations"
            self._sessions[session_id][key].append(evaluation)
            logger.info(f"Added {evaluation_type} evaluation to {session_id}")
    
    def increment_cheating_indicator(
        self,
        session_id: str,
        indicator_type: str
    ):
        """Increment cheating indicator count"""
        if session_id in self._sessions:
            self._sessions[session_id]["cheating_indicators"][indicator_type] += 1
            logger.warning(f"Cheating indicator {indicator_type} incremented for {session_id}")
    
    def complete_session(self, session_id: str):
        """Mark session as completed"""
        if session_id in self._sessions:
            self._sessions[session_id]["status"] = "completed"
            self._sessions[session_id]["completed_at"] = datetime.utcnow().isoformat()
            
            # Calculate duration
            start = datetime.fromisoformat(self._sessions[session_id]["start_time"])
            duration = (datetime.utcnow() - start).total_seconds()
            self._sessions[session_id]["duration"] = int(duration)
            
            logger.info(f"Completed session: {session_id}")
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    def _cleanup_old_sessions(self):
        """Remove sessions older than cleanup_interval"""
        try:
            now = datetime.utcnow()
            to_delete = []
            
            for session_id, data in self._sessions.items():
                created_at = datetime.fromisoformat(data["created_at"])
                if now - created_at > self._cleanup_interval:
                    to_delete.append(session_id)
            
            for session_id in to_delete:
                del self._sessions[session_id]
            
            if to_delete:
                logger.info(f"Cleaned up {len(to_delete)} old sessions")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        return {
            "total_sessions": len(self._sessions),
            "active_sessions": sum(1 for s in self._sessions.values() if s["status"] == "active"),
            "completed_sessions": sum(1 for s in self._sessions.values() if s["status"] == "completed"),
            "storage_type": "in-memory"
        }

# Singleton instance
_interview_session_service = None

def get_interview_session_service() -> InterviewSessionService:
    """Get InterviewSessionService singleton instance"""
    global _interview_session_service
    if _interview_session_service is None:
        _interview_session_service = InterviewSessionService()
    return _interview_session_service
