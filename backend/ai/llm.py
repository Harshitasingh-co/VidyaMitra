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
        
        # List available models to find the right one
        try:
            available_models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            
            logger.info(f"Available models: {available_models}")
            
            # Try to use the first available model that supports generateContent
            if available_models:
                # Remove 'models/' prefix if present
                model_name = available_models[0].replace('models/', '')
                self.model = genai.GenerativeModel(model_name)
                logger.info(f"LLM initialized with {model_name}")
            else:
                raise ValueError("No models available that support generateContent")
                
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            # Fallback to a common model name
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info(f"LLM initialized with fallback model: gemini-1.5-flash")
    
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
