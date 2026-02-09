import google.generativeai as genai
from core.config import get_settings
import json
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class LLMService:
    """Centralized LLM service using Google Gemini"""
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info(f"LLM initialized with Gemini 1.5 Flash")
    
    async def generate_json_response(self, system_prompt: str, user_prompt: str) -> dict:
        """
        Generate a JSON response from the LLM
        
        Args:
            system_prompt: System context and instructions
            user_prompt: User query or data to process
            
        Returns:
            Parsed JSON response as dictionary
        """
        try:
            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nIMPORTANT: Return ONLY valid JSON, no markdown formatting."
            
            response = self.model.generate_content(full_prompt)
            content = response.text.strip()
            
            # Handle markdown code blocks
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            result = json.loads(content)
            logger.info("Successfully generated JSON response")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Raw content: {content}")
            raise ValueError(f"LLM did not return valid JSON: {str(e)}")
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise
    
    async def generate_text_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate a text response from the LLM
        
        Args:
            system_prompt: System context and instructions
            user_prompt: User query
            
        Returns:
            Text response
        """
        try:
            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.model.generate_content(full_prompt)
            logger.info("Successfully generated text response")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise

# Singleton instance
_llm_service = None

def get_llm_service() -> LLMService:
    """Get or create LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
