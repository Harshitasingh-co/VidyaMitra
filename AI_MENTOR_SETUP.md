# AI Mentor - Agora Conversational AI Integration

## Overview
The AI Mentor feature integrates Agora's Conversational AI Agent to provide voice-based career guidance and mentoring through real-time audio conversations.

## Architecture

### Backend Components

1. **Agora Service** (`backend/services/agora_service.py`)
   - Manages Agora Conversational AI Agent lifecycle
   - Creates and configures AI agents with custom LLM, TTS, and ASR
   - Handles agent start, stop, and status queries

2. **AI Mentor Router** (`backend/app/routers/ai_mentor.py`)
   - REST API endpoints for session management
   - Token generation for RTC authentication
   - User profile integration for personalized guidance

3. **Configuration** (`backend/core/config.py`)
   - Agora credentials and API keys
   - LLM, TTS, and ASR vendor settings

### Frontend Components

1. **AIMentor Component** (`frontend/src/pages/AIMentor.jsx`)
   - Voice session UI with real-time status
   - Agora RTC SDK integration
   - Audio track management (microphone and remote audio)

## Configuration

### Environment Variables

Add these to `backend/.env`:

```env
# Agora Conversational AI Agent Configuration
AGORA_APP_ID=your-agora-app-id
AGORA_APP_CERTIFICATE=your-agora-app-certificate
AGORA_CUSTOMER_ID=your-agora-customer-id
AGORA_CUSTOMER_SECRET=your-agora-customer-secret

# LLM Configuration (Using Google Gemini)
AGORA_LLM_API_KEY=your-gemini-api-key
AGORA_LLM_MODEL=gemini-2.5-flash

# TTS Configuration (Using Cartesia)
AGORA_TTS_VENDOR=cartesia
AGORA_TTS_API_KEY=your-cartesia-api-key
AGORA_TTS_MODEL_ID=sonic-3
AGORA_TTS_VOICE_ID=your-voice-id

# ASR Configuration (Using Agora's Ares STT)
AGORA_ASR_VENDOR=ares
AGORA_ASR_LANGUAGE=en-US
```

## API Endpoints

### 1. Start Mentor Session
```
POST /api/ai/mentor/session/start
Authorization: Bearer <token>

Request Body:
{
  "user_profile": {
    "current_role": "Software Developer",
    "target_role": "Senior Engineer",
    "skills": ["Python", "JavaScript"],
    "experience_years": 3
  }
}

Response:
{
  "success": true,
  "data": {
    "channel_name": "mentor_123_1234567890",
    "user_token": "rtc_token",
    "user_uid": "1234",
    "agent_id": "agent_xyz",
    "agent_uid": "5678",
    "status": "RUNNING"
  }
}
```

### 2. Stop Mentor Session
```
POST /api/ai/mentor/session/stop
Authorization: Bearer <token>

Request Body:
{
  "agent_id": "agent_xyz"
}
```

### 3. Get Session Status
```
GET /api/ai/mentor/session/status/{agent_id}
Authorization: Bearer <token>
```

### 4. Get Configuration
```
GET /api/ai/mentor/config
Authorization: Bearer <token>

Response:
{
  "success": true,
  "data": {
    "app_id": "your-agora-app-id",
    "features": {
      "voice_chat": true,
      "real_time_response": true,
      "context_aware": true,
      "personalized_guidance": true
    }
  }
}
```

## Features

### AI Agent Capabilities

1. **Voice Interaction**
   - Natural voice conversations
   - Real-time speech recognition (ASR)
   - High-quality text-to-speech (TTS)

2. **Intelligent Turn Detection**
   - VAD-based start of speech detection
   - Semantic-based end of speech detection
   - Configurable interruption handling

3. **Personalized Guidance**
   - Context-aware responses based on user profile
   - Career path recommendations
   - Skill development advice
   - Interview preparation tips

4. **Advanced Features**
   - Silence detection with timeout prompts
   - Graceful session termination
   - Real-time metrics and error reporting
   - RTM integration for enhanced messaging

### Frontend Features

1. **Session Management**
   - One-click session start/stop
   - Real-time connection status
   - Visual feedback with animated avatar

2. **Audio Controls**
   - Mute/unmute microphone
   - Automatic remote audio playback
   - Audio track lifecycle management

3. **User Experience**
   - Status indicators (idle, connecting, connected, disconnected)
   - Error handling and display
   - Responsive design
   - Helpful usage instructions

## Installation

### Backend Setup

1. Install Python dependencies:
```bash
cd backend
source venv_py312/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables in `.env`

3. Start the backend server:
```bash
python main.py
# or
uvicorn main:app --reload
```

### Frontend Setup

1. Install Node dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

## Usage Flow

1. **User Authentication**
   - User logs in to VidyaMitra
   - JWT token stored in localStorage

2. **Start Session**
   - User clicks "Start Session" button
   - Frontend requests session creation from backend
   - Backend creates Agora AI agent with user profile
   - Frontend joins RTC channel with provided credentials

3. **Voice Conversation**
   - User speaks into microphone
   - Audio sent to Agora RTC channel
   - AI agent processes speech with ASR
   - LLM generates response based on context
   - TTS converts response to speech
   - Audio played back to user

4. **End Session**
   - User clicks "End Session" button
   - Frontend leaves RTC channel
   - Backend stops AI agent
   - Resources cleaned up

## Customization

### System Prompt

Edit the `_build_system_message` method in `backend/services/agora_service.py` to customize the AI mentor's personality and capabilities.

### Voice Settings

Modify TTS configuration in `.env`:
- Change `AGORA_TTS_VOICE_ID` for different voice characteristics
- Adjust `AGORA_TTS_MODEL_ID` for different quality levels

### Turn Detection

Adjust turn detection parameters in `agora_service.py`:
```python
"turn_detection": {
    "config": {
        "speech_threshold": 0.5,  # Voice detection sensitivity
        "start_of_speech": {
            "vad_config": {
                "interrupt_duration_ms": 160,
                "prefix_padding_ms": 800
            }
        },
        "end_of_speech": {
            "semantic_config": {
                "silence_duration_ms": 320,
                "max_wait_ms": 3000
            }
        }
    }
}
```

## Troubleshooting

### Common Issues

1. **"Failed to start session"**
   - Check Agora credentials in `.env`
   - Verify API keys are valid
   - Check backend logs for detailed error

2. **"Microphone access denied"**
   - Browser needs microphone permission
   - Check browser settings
   - Use HTTPS in production

3. **"Agent not responding"**
   - Verify LLM API key is valid
   - Check network connectivity
   - Review agent status endpoint

4. **Audio not playing**
   - Check browser audio permissions
   - Verify remote user published audio
   - Check Agora RTC connection status

### Debug Mode

Enable detailed logging:
```python
# In backend/services/agora_service.py
logger.setLevel(logging.DEBUG)
```

## Production Considerations

1. **Token Generation**
   - Implement proper Agora RTC token generation
   - Use official Agora token library
   - Set appropriate expiration times

2. **Security**
   - Store API keys securely
   - Validate user authentication
   - Implement rate limiting

3. **Scalability**
   - Monitor concurrent agent sessions
   - Implement session cleanup
   - Use connection pooling

4. **Monitoring**
   - Track agent creation/termination
   - Monitor API usage and costs
   - Log conversation metrics

## Resources

- [Agora Conversational AI Documentation](https://docs.agora.io/en/conversational-ai-agent/)
- [Agora RTC SDK Documentation](https://docs.agora.io/en/video-calling/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Cartesia TTS](https://cartesia.ai/docs)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Agora documentation
3. Check backend logs for errors
4. Contact Agora support for platform issues
