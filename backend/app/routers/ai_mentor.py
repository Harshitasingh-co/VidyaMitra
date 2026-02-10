"""
AI Mentor Router - Agora Conversational AI Agent Integration
Provides voice-based AI mentoring with real-time conversation
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from services.agora_service import get_agora_service
from core.security import get_current_user
from utils.response_formatter import get_response_formatter
from agora_token_builder import RtcTokenBuilder
from core.config import get_settings
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class StartMentorSessionRequest(BaseModel):
    """Request to start an AI mentor session"""
    user_profile: Optional[Dict[str, Any]] = None
    

class StopMentorSessionRequest(BaseModel):
    """Request to stop an AI mentor session"""
    agent_id: str


class RtcTokenRequest(BaseModel):
    """Request to generate RTC token"""
    channel_name: str
    uid: str


@router.post("/session/start")
async def start_mentor_session(
    request: StartMentorSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Start a new AI Mentor conversational session
    
    Creates an Agora RTC channel and starts a conversational AI agent
    that can provide voice-based career guidance and mentoring.
    
    Returns:
        - channel_name: RTC channel to join
        - token: Authentication token for the channel
        - agent_id: ID of the created AI agent
        - user_uid: User's UID for the channel
        - agent_uid: Agent's UID in the channel
    """
    try:
        logger.info(f"User {current_user['email']} starting AI mentor session")
        
        # Generate unique channel name
        channel_name = f"mentor_{current_user['id']}_{int(time.time())}"
        
        # Generate UIDs (must be integers for token generation)
        user_uid = 1000 + (hash(current_user['id']) % 9000)
        agent_uid = 2000 + (hash(channel_name) % 9000)
        
        # Generate RTC tokens with proper Agora token builder
        user_token = _generate_rtc_token(channel_name, user_uid)
        agent_token = _generate_rtc_token(channel_name, agent_uid)
        
        # Enhance user profile with current user data
        user_profile = request.user_profile or {}
        user_profile["user_id"] = current_user["id"]
        user_profile["email"] = current_user["email"]
        
        # Create AI agent
        agora_service = get_agora_service()
        agent_result = await agora_service.create_agent(
            channel_name=channel_name,
            token=agent_token,
            agent_uid=str(agent_uid),
            user_uid=str(user_uid),
            user_profile=user_profile
        )
        
        formatter = get_response_formatter()
        return formatter.success({
            "channel_name": channel_name,
            "user_token": user_token,
            "user_uid": str(user_uid),
            "agent_id": agent_result.get("agent_id"),
            "agent_uid": str(agent_uid),
            "status": agent_result.get("status"),
            "created_at": agent_result.get("create_ts")
        }, "AI Mentor session started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start mentor session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@router.post("/session/stop")
async def stop_mentor_session(
    request: StopMentorSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Stop an active AI Mentor session
    
    Gracefully stops the conversational AI agent and cleans up resources.
    """
    try:
        logger.info(f"User {current_user['email']} stopping AI mentor session: {request.agent_id}")
        
        agora_service = get_agora_service()
        result = await agora_service.stop_agent(request.agent_id)
        
        formatter = get_response_formatter()
        return formatter.success(result, "AI Mentor session stopped successfully")
        
    except Exception as e:
        logger.error(f"Failed to stop mentor session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop session: {str(e)}")


@router.get("/session/status/{agent_id}")
async def get_session_status(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get the status of an AI Mentor session
    
    Returns current status and information about the conversational agent.
    """
    try:
        agora_service = get_agora_service()
        status = await agora_service.get_agent_status(agent_id)
        
        formatter = get_response_formatter()
        return formatter.success(status, "Session status retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/config")
async def get_mentor_config(
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI Mentor configuration
    
    Returns configuration needed for the frontend to initialize
    the Agora RTC client.
    """
    try:
        from core.config import get_settings
        settings = get_settings()
        
        formatter = get_response_formatter()
        return formatter.success({
            "app_id": settings.AGORA_APP_ID,
            "features": {
                "voice_chat": True,
                "real_time_response": True,
                "context_aware": True,
                "personalized_guidance": True
            }
        }, "Configuration retrieved")
        
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_rtc_token(channel_name: str, uid: int) -> str:
    """
    Generate a proper Agora RTC token
    
    Args:
        channel_name: Channel name
        uid: User ID (integer)
        
    Returns:
        Token string
    """
    app_id = settings.AGORA_APP_ID
    app_certificate = settings.AGORA_APP_CERTIFICATE
    
    if not app_certificate:
        logger.warning("AGORA_APP_CERTIFICATE not set - using empty token")
        return ""
    
    # Token expires in 24 hours
    expiration_time_in_seconds = 3600 * 24
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_time_in_seconds
    
    # Role: 1 = Publisher (can send and receive)
    role = 1
    
    token = RtcTokenBuilder.buildTokenWithUid(
        app_id,
        app_certificate,
        channel_name,
        uid,
        role,
        privilege_expired_ts
    )
    
    return token
