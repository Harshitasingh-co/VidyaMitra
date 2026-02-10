import { useState, useEffect, useRef } from 'react'
import { Bot, Mic, MicOff, Phone, PhoneOff, Sparkles, User, Volume2, LogIn } from 'lucide-react'
import AgoraRTC from 'agora-rtc-sdk-ng'

function AIMentor() {
  const [isSessionActive, setIsSessionActive] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [sessionInfo, setSessionInfo] = useState(null)
  const [agentStatus, setAgentStatus] = useState('idle')
  const [error, setError] = useState(null)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [showLoginForm, setShowLoginForm] = useState(false)
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  
  const clientRef = useRef(null)
  const localAudioTrackRef = useRef(null)
  const remoteAudioTrackRef = useRef(null)

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token')
    setIsLoggedIn(!!token)
    
    return () => {
      if (isSessionActive) {
        handleEndSession()
      }
    }
  }, [])

  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      const formData = new URLSearchParams()
      formData.append('username', loginEmail)
      formData.append('password', loginPassword)

      const response = await fetch('http://localhost:8001/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('token', data.access_token)
        setIsLoggedIn(true)
        setShowLoginForm(false)
        setError(null)
      } else {
        setError('Login failed. Please try again.')
      }
    } catch (err) {
      setError('Login failed. Please try again.')
    }
  }

  const startSession = async () => {
    try {
      setIsConnecting(true)
      setError(null)

      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('Please log in first to use AI Mentor')
      }

      const userProfile = {
        current_role: localStorage.getItem('current_role') || '',
        target_role: localStorage.getItem('target_role') || '',
        skills: JSON.parse(localStorage.getItem('skills') || '[]'),
        experience_years: parseInt(localStorage.getItem('experience_years') || '0')
      }

      const response = await fetch('http://localhost:8001/api/ai/mentor/session/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ user_profile: userProfile })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to start session' }))
        throw new Error(errorData.detail || errorData.message || 'Failed to start session')
      }

      const data = await response.json()
      const session = data.data
      setSessionInfo(session)
      setAgentStatus('connecting')

      const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' })
      clientRef.current = client

      const configResponse = await fetch('http://localhost:8001/api/ai/mentor/config', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const configData = await configResponse.json()
      const appId = configData.data.app_id

      await client.join(appId, session.channel_name, session.user_token, parseInt(session.user_uid))

      const localAudioTrack = await AgoraRTC.createMicrophoneAudioTrack()
      localAudioTrackRef.current = localAudioTrack
      await client.publish([localAudioTrack])

      client.on('user-published', async (user, mediaType) => {
        await client.subscribe(user, mediaType)
        if (mediaType === 'audio') {
          remoteAudioTrackRef.current = user.audioTrack
          user.audioTrack.play()
          setAgentStatus('connected')
        }
      })

      client.on('user-unpublished', () => setAgentStatus('disconnected'))

      setIsSessionActive(true)
      setIsConnecting(false)

    } catch (err) {
      console.error('Failed to start session:', err)
      setError(err.message || 'Failed to start AI Mentor session')
      setIsConnecting(false)
    }
  }

  const handleEndSession = async () => {
    try {
      if (localAudioTrackRef.current) {
        localAudioTrackRef.current.stop()
        localAudioTrackRef.current.close()
      }

      if (clientRef.current) await clientRef.current.leave()

      if (sessionInfo?.agent_id) {
        const token = localStorage.getItem('token')
        await fetch('http://localhost:8001/api/ai/mentor/session/stop', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ agent_id: sessionInfo.agent_id })
        })
      }

      setIsSessionActive(false)
      setSessionInfo(null)
      setAgentStatus('idle')
      setIsMuted(false)

    } catch (err) {
      console.error('Failed to end session:', err)
      setError('Failed to end session properly')
    }
  }

  const toggleMute = () => {
    if (localAudioTrackRef.current) {
      localAudioTrackRef.current.setEnabled(isMuted)
      setIsMuted(!isMuted)
    }
  }

  const getStatusColor = () => {
    const colors = {
      connected: '#48bb78',
      connecting: '#ed8936',
      disconnected: '#f56565',
      idle: '#718096'
    }
    return colors[agentStatus] || colors.idle
  }

  const getStatusText = () => {
    const texts = {
      connected: 'AI Mentor is listening',
      connecting: 'Connecting to AI Mentor...',
      disconnected: 'AI Mentor disconnected',
      idle: 'Ready to start'
    }
    return texts[agentStatus] || texts.idle
  }

  return (
    <div className="container">
      <h1 style={{ color: 'white', marginBottom: '8px', fontSize: '36px', fontWeight: '800' }}>
        AI Mentor
      </h1>
      <p style={{ color: 'rgba(255,255,255,0.9)', marginBottom: '32px', fontSize: '16px' }}>
        Voice-powered AI guidance for your career journey
      </p>

      <div className="card" style={{ textAlign: 'center', padding: '60px 40px' }}>
        <div style={{ 
          width: '160px', 
          height: '160px', 
          margin: '0 auto 32px',
          background: isSessionActive 
            ? `linear-gradient(135deg, ${getStatusColor()} 0%, ${getStatusColor()}dd 100%)`
            : 'linear-gradient(135deg, #9f7aea 0%, #805ad5 100%)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `0 20px 40px ${getStatusColor()}40`,
          animation: isSessionActive ? 'pulse 2s ease-in-out infinite' : 'none',
          transition: 'all 0.3s ease',
          position: 'relative'
        }}>
          <Bot size={80} color="white" strokeWidth={2} />
          
          {isSessionActive && (
            <div style={{
              position: 'absolute',
              bottom: '10px',
              right: '10px',
              width: '24px',
              height: '24px',
              background: getStatusColor(),
              borderRadius: '50%',
              border: '3px solid white',
              animation: agentStatus === 'connected' ? 'blink 1.5s ease-in-out infinite' : 'none'
            }} />
          )}
        </div>

        <h2 style={{ fontSize: '28px', marginBottom: '12px', color: '#2d3748' }}>
          {getStatusText()}
        </h2>

        {error && (
          <div style={{
            background: '#fed7d7',
            color: '#c53030',
            padding: '12px 20px',
            borderRadius: '8px',
            marginBottom: '24px',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        {!isLoggedIn ? (
          <div style={{ maxWidth: '400px', margin: '0 auto' }}>
            {!showLoginForm ? (
              <div>
                <p style={{ color: '#718096', marginBottom: '24px', fontSize: '16px' }}>
                  Please log in to use the AI Mentor feature
                </p>
                <button
                  onClick={() => setShowLoginForm(true)}
                  style={{
                    background: 'linear-gradient(135deg, #9f7aea 0%, #805ad5 100%)',
                    color: 'white',
                    border: 'none',
                    padding: '16px 48px',
                    borderRadius: '12px',
                    fontSize: '18px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    margin: '0 auto',
                    boxShadow: '0 4px 12px rgba(159, 122, 234, 0.3)'
                  }}
                >
                  <LogIn size={24} />
                  Quick Login
                </button>
                <p style={{ color: '#718096', marginTop: '16px', fontSize: '14px' }}>
                  No account needed - just enter any email and password
                </p>
              </div>
            ) : (
              <form onSubmit={handleLogin} style={{ textAlign: 'left' }}>
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', color: '#2d3748', fontWeight: '600' }}>
                    Email
                  </label>
                  <input
                    type="email"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="your@email.com"
                    required
                    style={{
                      width: '100%',
                      padding: '12px',
                      borderRadius: '8px',
                      border: '1px solid #e2e8f0',
                      fontSize: '16px'
                    }}
                  />
                </div>
                <div style={{ marginBottom: '24px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', color: '#2d3748', fontWeight: '600' }}>
                    Password
                  </label>
                  <input
                    type="password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="Enter any password"
                    required
                    style={{
                      width: '100%',
                      padding: '12px',
                      borderRadius: '8px',
                      border: '1px solid #e2e8f0',
                      fontSize: '16px'
                    }}
                  />
                </div>
                <button
                  type="submit"
                  style={{
                    width: '100%',
                    background: 'linear-gradient(135deg, #9f7aea 0%, #805ad5 100%)',
                    color: 'white',
                    border: 'none',
                    padding: '14px',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Login
                </button>
                <button
                  type="button"
                  onClick={() => setShowLoginForm(false)}
                  style={{
                    width: '100%',
                    background: 'transparent',
                    color: '#718096',
                    border: 'none',
                    padding: '14px',
                    fontSize: '14px',
                    cursor: 'pointer',
                    marginTop: '8px'
                  }}
                >
                  Cancel
                </button>
              </form>
            )}
          </div>
        ) : (
          <>
            <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginBottom: '40px' }}>
          {!isSessionActive ? (
            <button
              onClick={startSession}
              disabled={isConnecting}
              style={{
                background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
                color: 'white',
                border: 'none',
                padding: '16px 48px',
                borderRadius: '12px',
                fontSize: '18px',
                fontWeight: '600',
                cursor: isConnecting ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                boxShadow: '0 4px 12px rgba(72, 187, 120, 0.3)',
                transition: 'all 0.2s',
                opacity: isConnecting ? 0.6 : 1
              }}
            >
              <Phone size={24} />
              {isConnecting ? 'Connecting...' : 'Start Session'}
            </button>
          ) : (
            <>
              <button onClick={toggleMute} style={{
                background: isMuted ? '#f56565' : '#4299e1',
                color: 'white',
                border: 'none',
                padding: '16px 32px',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                {isMuted ? <MicOff size={20} /> : <Mic size={20} />}
                {isMuted ? 'Unmute' : 'Mute'}
              </button>

              <button onClick={handleEndSession} style={{
                background: 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)',
                color: 'white',
                border: 'none',
                padding: '16px 32px',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <PhoneOff size={20} />
                End Session
              </button>
            </>
          )}
        </div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px',
          maxWidth: '800px',
          margin: '0 auto',
          textAlign: 'left'
        }}>
          {[
            { icon: Volume2, title: 'Voice Interaction', desc: 'Natural voice conversations with AI-powered career guidance' },
            { icon: Sparkles, title: 'Real-time Responses', desc: 'Instant AI responses with intelligent turn detection' },
            { icon: User, title: 'Personalized Advice', desc: 'Context-aware guidance based on your profile and goals' }
          ].map(({ icon: Icon, title, desc }, i) => (
            <div key={i} style={{ 
              background: 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)',
              padding: '24px',
              borderRadius: '12px',
              border: '1px solid #e2e8f0'
            }}>
              <Icon size={32} color="#9f7aea" style={{ marginBottom: '12px' }} />
              <h3 style={{ fontSize: '18px', marginBottom: '8px', color: '#2d3748' }}>{title}</h3>
              <p style={{ color: '#718096', fontSize: '14px', lineHeight: '1.6' }}>{desc}</p>
            </div>
          ))}
        </div>
        </>
        )}

        {!isSessionActive && isLoggedIn && (
          <div style={{ 
            marginTop: '48px',
            padding: '24px',
            background: 'linear-gradient(135deg, rgba(159, 122, 234, 0.1) 0%, rgba(128, 90, 213, 0.1) 100%)',
            borderRadius: '12px',
            border: '1px solid rgba(159, 122, 234, 0.2)',
            textAlign: 'left'
          }}>
            <h3 style={{ color: '#553c9a', fontWeight: '600', fontSize: '18px', marginBottom: '16px' }}>
              💡 How to use AI Mentor
            </h3>
            <ul style={{ color: '#553c9a', fontSize: '14px', lineHeight: '1.8', paddingLeft: '20px' }}>
              <li>Click "Start Session" to begin a voice conversation</li>
              <li>Allow microphone access when prompted</li>
              <li>Speak naturally - the AI will respond in real-time</li>
              <li>Ask about career paths, skills, interviews, or job search</li>
              <li>Use the mute button if you need a moment</li>
              <li>Click "End Session" when you're done</li>
            </ul>
          </div>
        )}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  )
}

export default AIMentor
