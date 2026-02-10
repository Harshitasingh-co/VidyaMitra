"""
Test script to create and verify Agora Conversational AI Agent
"""
import asyncio
import sys
from services.agora_service import get_agora_service
from core.config import get_settings

async def test_agent_creation():
    """Test creating an Agora AI agent"""
    
    settings = get_settings()
    
    print("=" * 60)
    print("Testing Agora Conversational AI Agent Creation")
    print("=" * 60)
    
    # Verify credentials
    print("\n1. Checking credentials...")
    if not settings.AGORA_APP_ID:
        print("❌ AGORA_APP_ID not set")
        return False
    if not settings.AGORA_CUSTOMER_ID:
        print("❌ AGORA_CUSTOMER_ID not set")
        return False
    if not settings.AGORA_CUSTOMER_SECRET:
        print("❌ AGORA_CUSTOMER_SECRET not set")
        return False
    if not settings.AGORA_LLM_API_KEY:
        print("❌ AGORA_LLM_API_KEY not set")
        return False
    if not settings.AGORA_TTS_API_KEY:
        print("❌ AGORA_TTS_API_KEY not set")
        return False
    
    print("✅ All credentials configured")
    
    # Test agent creation
    print("\n2. Creating test agent...")
    agora_service = get_agora_service()
    
    try:
        result = await agora_service.create_agent(
            channel_name="test_channel_123",
            token="test_token_456",
            agent_uid="9999",
            user_uid="8888",
            user_profile={
                "current_role": "Software Developer",
                "target_role": "Senior Engineer",
                "skills": ["Python", "JavaScript"],
                "experience_years": 3
            }
        )
        
        print(f"✅ Agent created successfully!")
        print(f"   Agent ID: {result.get('agent_id')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Created at: {result.get('create_ts')}")
        
        # Get agent status
        print("\n3. Checking agent status...")
        agent_id = result.get('agent_id')
        status = await agora_service.get_agent_status(agent_id)
        print(f"✅ Agent status: {status.get('status')}")
        
        # Stop agent
        print("\n4. Stopping agent...")
        stop_result = await agora_service.stop_agent(agent_id)
        print(f"✅ Agent stopped successfully")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease check:")
        print("1. Agora credentials are correct")
        print("2. Gemini API key is valid")
        print("3. Cartesia API key is valid")
        print("4. Network connection is working")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agent_creation())
    sys.exit(0 if success else 1)
