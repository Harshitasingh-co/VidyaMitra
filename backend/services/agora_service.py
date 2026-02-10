"""
Agora Conversational AI Agent Service
Handles creation, management, and interaction with Agora AI agents
"""
import httpx
import base64
import logging
import time
from typing import Optional, Dict, Any
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AgoraService:
    """Service for managing Agora Conversational AI Agents"""
    
    def __init__(self):
        self.base_url = "https://api.agora.io/api/conversational-ai-agent/v2"
        self.app_id = settings.AGORA_APP_ID
        self.customer_id = settings.AGORA_CUSTOMER_ID
        self.customer_secret = settings.AGORA_CUSTOMER_SECRET
        
        # Create Basic Auth credentials
        credentials = f"{self.customer_id}:{self.customer_secret}"
        self.auth_header = base64.b64encode(credentials.encode()).decode()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json"
        }
    
    async def create_agent(
        self,
        channel_name: str,
        token: str,
        agent_uid: str,
        user_uid: str,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create and start a conversational AI agent
        
        Args:
            channel_name: RTC channel name
            token: RTC authentication token
            agent_uid: Agent's user ID in the channel
            user_uid: User's ID to subscribe to
            user_profile: Optional user profile for personalization
            
        Returns:
            Agent creation response with agent_id and status
        """
        try:
            # Generate unique agent name
            agent_name = f"vidyamitra_mentor_{int(time.time())}"
            
            # Build system message with user context
            system_message = self._build_system_message(user_profile)
            
            # Construct request payload
            payload = {
                "name": agent_name,
                "properties": {
                    "channel": channel_name,
                    "token": token,
                    "agent_rtc_uid": agent_uid,
                    "remote_rtc_uids": [user_uid],
                    "idle_timeout": 300,  # 5 minutes
                    "llm": {
                        "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?alt=sse&key={settings.AGORA_LLM_API_KEY}",
                        "system_messages": [
                            {
                                "parts": [
                                    {
                                        "text": system_message
                                    }
                                ],
                                "role": "user"
                            }
                        ],
                        "max_history": 32,
                        "greeting_message": "Hello! I'm your VidyaMitra AI Mentor. I'm here to help you with career guidance, learning paths, and skill development. How can I assist you today?",
                        "failure_message": "I apologize, I'm having trouble processing that. Could you please rephrase your question?",
                        "style": "gemini",
                        "ignore_empty": True,
                        "params": {
                            "model": "gemini-2.0-flash"
                        }
                    },
                    "tts": {
                        "vendor": "cartesia",
                        "params": {
                            "api_key": settings.AGORA_TTS_API_KEY,
                            "model_id": settings.AGORA_TTS_MODEL_ID,
                            "voice": {
                                "mode": "id",
                                "id": settings.AGORA_TTS_VOICE_ID
                            },
                            "output_format": {
                                "container": "raw",
                                "sample_rate": 16000
                            },
                            "language": "en"
                        }
                    },
                    "asr": {
                        "language": settings.AGORA_ASR_LANGUAGE,
                        "vendor": settings.AGORA_ASR_VENDOR,
                        "params": {}
                    },
                    "turn_detection": {
                        "mode": "default",
                        "config": {
                            "speech_threshold": 0.5,
                            "start_of_speech": {
                                "mode": "vad",
                                "vad_config": {
                                    "interrupt_duration_ms": 160,
                                    "speaking_interrupt_duration_ms": 160,
                                    "prefix_padding_ms": 800
                                }
                            },
                            "end_of_speech": {
                                "mode": "semantic",
                                "semantic_config": {
                                    "silence_duration_ms": 320,
                                    "max_wait_ms": 3000
                                }
                            }
                        }
                    },
                    "advanced_features": {
                        "enable_rtm": True,
                        "enable_aivad": False
                    },
                    "parameters": {
                        "silence_config": {
                            "timeout_ms": 30000,
                            "action": "speak",
                            "content": "Are you still there? Feel free to ask me anything about your career or learning journey."
                        },
                        "farewell_config": {
                            "graceful_enabled": True,
                            "graceful_timeout_seconds": 30
                        },
                        "data_channel": "rtm",
                        "enable_metrics": True,
                        "enable_error_message": True
                    }
                }
            }
            
            # Make API request
            url = f"{self.base_url}/projects/{self.app_id}/join"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers()
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Agent created successfully: {result.get('agent_id')}")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Agora API error: {e.response.status_code} - {e.response.text}")
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                error_detail = error_json.get('message', error_detail)
            except:
                pass
            raise Exception(f"Failed to create agent: {error_detail}")
        except httpx.RequestError as e:
            logger.error(f"Network error connecting to Agora: {e}")
            raise Exception(f"Network error: Unable to connect to Agora API")
        except Exception as e:
            logger.error(f"Agent creation failed: {e}")
            raise
    
    async def stop_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Stop a running conversational AI agent
        
        Args:
            agent_id: The agent ID to stop
            
        Returns:
            Stop response
        """
        try:
            url = f"{self.base_url}/projects/{self.app_id}/agents/{agent_id}/leave"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=self._get_headers()
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Agent stopped successfully: {agent_id}")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Agora API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to stop agent: {e.response.text}")
        except Exception as e:
            logger.error(f"Agent stop failed: {e}")
            raise
    
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the status of a conversational AI agent
        
        Args:
            agent_id: The agent ID to query
            
        Returns:
            Agent status information
        """
        try:
            url = f"{self.base_url}/projects/{self.app_id}/agents/{agent_id}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    headers=self._get_headers()
                )
                
                response.raise_for_status()
                result = response.json()
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Agora API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to get agent status: {e.response.text}")
        except Exception as e:
            logger.error(f"Agent status query failed: {e}")
            raise
    
    def _build_system_message(self, user_profile: Optional[Dict[str, Any]] = None) -> str:
        """
        Build personalized system message for the AI agent
        
        Args:
            user_profile: User profile information
            
        Returns:
            System message string
        """
        base_message = """You are VidyaMitra AI Mentor, an intelligent career guidance and learning assistant. 
Your role is to help students and professionals with:

1. Career Path Guidance: Provide personalized career recommendations based on skills, interests, and goals
2. Skill Development: Suggest learning resources, courses, and certifications
3. Resume & Interview Prep: Offer tips for resume optimization and interview preparation
4. Job Market Insights: Share information about industry trends and job opportunities
5. Educational Planning: Help plan learning paths and upskilling strategies

Guidelines:
- Be encouraging, supportive, and professional
- Provide actionable, specific advice
- Ask clarifying questions when needed
- Keep responses concise but informative
- Focus on practical, real-world guidance
- Adapt your advice to the user's experience level"""
        
        if user_profile:
            context = "\n\nUser Context:"
            if user_profile.get("current_role"):
                context += f"\n- Current Role: {user_profile['current_role']}"
            if user_profile.get("target_role"):
                context += f"\n- Target Role: {user_profile['target_role']}"
            if user_profile.get("skills"):
                context += f"\n- Skills: {', '.join(user_profile['skills'])}"
            if user_profile.get("experience_years"):
                context += f"\n- Experience: {user_profile['experience_years']} years"
            
            base_message += context
        
        return base_message


def get_agora_service() -> AgoraService:
    """Get AgoraService instance"""
    return AgoraService()
