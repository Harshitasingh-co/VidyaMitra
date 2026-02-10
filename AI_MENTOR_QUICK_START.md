# AI Mentor Quick Start Guide

## ✅ Status: WORKING

The Agora Conversational AI Agent integration is now fully functional!

## What You Have

A voice-powered AI mentor that provides:
- Real-time voice conversations
- Career guidance and advice
- Personalized recommendations based on user profile
- Natural language understanding with Google Gemini
- High-quality voice synthesis with Cartesia TTS

## How to Use

### 1. Start the Backend

```bash
cd backend
source venv_py312/bin/activate
python -m uvicorn main:app --reload --port 8001
```

### 2. Start the Frontend

```bash
cd frontend
npm run dev
```

### 3. Use AI Mentor

1. **Login to VidyaMitra** - You must be logged in first
2. **Navigate to AI Mentor** - Click on "AI Mentor" in the navigation
3. **Start Session** - Click the "Start Session" button
4. **Allow Microphone** - Grant microphone permission when prompted
5. **Talk to AI** - Speak naturally, the AI will respond in real-time
6. **End Session** - Click "End Session" when done

## Features Working

✅ Voice input (Speech-to-Text with Agora Ares)
✅ AI processing (Google Gemini 2.0 Flash)
✅ Voice output (Cartesia TTS with Sonic-2)
✅ Real-time conversation
✅ Context-aware responses
✅ Personalized guidance
✅ Session management
✅ Mute/unmute controls

## Configuration

All configuration is in `backend/.env`:

```env
# Agora Credentials
AGORA_APP_ID=bb1ca613e3b94aa7af3eec189d172e99
AGORA_APP_CERTIFICATE=1128e52b74a944c7b9e5ec04e93425cb
AGORA_CUSTOMER_ID=188c574d56ae405e916449df64e28945
AGORA_CUSTOMER_SECRET=3f7c4ded78e1444fa4ed50ac273cad11

# LLM (Google Gemini)
AGORA_LLM_API_KEY=AIzaSyCLEf-v7DVXcfh6PNsOOdFtH6eRz8_G2H0
AGORA_LLM_MODEL=gemini-2.0-flash

# TTS (Cartesia)
AGORA_TTS_VENDOR=cartesia
AGORA_TTS_API_KEY=sk_car_6trWSv23KdCNswkDj7tPdh
AGORA_TTS_MODEL_ID=sonic-2
AGORA_TTS_VOICE_ID=95d51f79-c397-46f9-b49a-23763d3eaa2d

# ASR (Agora Ares)
AGORA_ASR_VENDOR=ares
AGORA_ASR_LANGUAGE=en-US
```

## API Endpoints

### Start Session
```
POST /api/ai/mentor/session/start
Authorization: Bearer <jwt_token>

Body:
{
  "user_profile": {
    "current_role": "Software Developer",
    "target_role": "Senior Engineer",
    "skills": ["Python", "JavaScript"],
    "experience_years": 3
  }
}
```

### Stop Session
```
POST /api/ai/mentor/session/stop
Authorization: Bearer <jwt_token>

Body:
{
  "agent_id": "agent_id_here"
}
```

### Get Config
```
GET /api/ai/mentor/config
Authorization: Bearer <jwt_token>
```

### Get Status
```
GET /api/ai/mentor/session/status/{agent_id}
Authorization: Bearer <jwt_token>
```

## Testing

### Test Agora Connection
```bash
cd backend
source venv_py312/bin/activate
python test_agora_connection.py
```

### Test Agent Creation
```bash
cd backend
source venv_py312/bin/activate
python test_agora_agent.py
```

## Troubleshooting

### "Please log in first to use AI Mentor"
- You need to be logged in to VidyaMitra
- Go to Login page and create an account or sign in

### "Failed to fetch"
- Make sure backend is running on port 8001
- Check that frontend is using the correct port (8001)

### "Microphone access denied"
- Allow microphone permission in your browser
- Check browser settings for microphone access

### Agent not responding
- Check backend logs for errors
- Verify Gemini API key is valid
- Verify Cartesia API key is valid
- Check network connection

## Architecture

```
User Browser
    ↓ (Voice Input)
Agora RTC SDK
    ↓
Agora RTC Channel
    ↓
Agora AI Agent
    ↓
┌─────────────────┐
│ ASR (Ares STT)  │ → Text
└─────────────────┘
    ↓
┌─────────────────┐
│ LLM (Gemini)    │ → Response
└─────────────────┘
    ↓
┌─────────────────┐
│ TTS (Cartesia)  │ → Audio
└─────────────────┘
    ↓
Agora RTC Channel
    ↓
User Browser (Audio Output)
```

## What to Ask the AI Mentor

- "What skills should I learn to become a senior developer?"
- "How can I prepare for technical interviews?"
- "What's the best career path for a Python developer?"
- "Can you review my career goals?"
- "What certifications should I pursue?"
- "How do I transition from frontend to full-stack?"

## Next Steps

1. **Customize System Prompt** - Edit `backend/services/agora_service.py` to change AI personality
2. **Add More Features** - Integrate with resume analysis, job matching, etc.
3. **Improve UI** - Add conversation history, transcript display
4. **Production Setup** - Implement proper RTC token generation
5. **Analytics** - Track conversation metrics and user engagement

## Support

- Agora Documentation: https://docs.agora.io/en/conversational-ai-agent/
- Gemini API: https://ai.google.dev/docs
- Cartesia TTS: https://cartesia.ai/docs

## Success! 🎉

Your AI Mentor is now ready to provide voice-based career guidance to VidyaMitra users!
