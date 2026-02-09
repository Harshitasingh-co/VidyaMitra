import { Bot, Sparkles } from 'lucide-react'

function AIMentor() {
  return (
    <div className="container">
      <h1 style={{ color: 'white', marginBottom: '8px', fontSize: '36px', fontWeight: '800' }}>
        AI Mentor
      </h1>
      <p style={{ color: 'rgba(255,255,255,0.9)', marginBottom: '32px', fontSize: '16px' }}>
        Your personal AI guide for learning and career guidance
      </p>

      <div className="card" style={{ textAlign: 'center', padding: '80px 40px' }}>
        <div style={{ 
          width: '120px', 
          height: '120px', 
          margin: '0 auto 32px',
          background: 'linear-gradient(135deg, #9f7aea 0%, #805ad5 100%)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 20px 40px rgba(159, 122, 234, 0.3)',
          animation: 'pulse 2s ease-in-out infinite'
        }}>
          <Bot size={64} color="white" strokeWidth={2} />
        </div>

        <h2 style={{ 
          fontSize: '32px', 
          marginBottom: '16px',
          background: 'linear-gradient(135deg, #9f7aea 0%, #805ad5 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          Coming Soon!
        </h2>
        
        <p style={{ 
          fontSize: '18px', 
          color: '#718096', 
          marginBottom: '32px',
          maxWidth: '600px',
          margin: '0 auto 32px',
          lineHeight: '1.7'
        }}>
          We're building an intelligent AI mentor that will provide personalized guidance, 
          answer your questions, and help you navigate your learning journey.
        </p>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px',
          maxWidth: '800px',
          margin: '0 auto',
          textAlign: 'left'
        }}>
          <div style={{ 
            background: 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)',
            padding: '24px',
            borderRadius: '12px',
            border: '1px solid #e2e8f0'
          }}>
            <Sparkles size={32} color="#9f7aea" style={{ marginBottom: '12px' }} />
            <h3 style={{ fontSize: '18px', marginBottom: '8px', color: '#2d3748' }}>
              24/7 Guidance
            </h3>
            <p style={{ color: '#718096', fontSize: '14px', lineHeight: '1.6' }}>
              Get instant answers to your career and learning questions anytime
            </p>
          </div>

          <div style={{ 
            background: 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)',
            padding: '24px',
            borderRadius: '12px',
            border: '1px solid #e2e8f0'
          }}>
            <Sparkles size={32} color="#9f7aea" style={{ marginBottom: '12px' }} />
            <h3 style={{ fontSize: '18px', marginBottom: '8px', color: '#2d3748' }}>
              Personalized Advice
            </h3>
            <p style={{ color: '#718096', fontSize: '14px', lineHeight: '1.6' }}>
              Receive tailored recommendations based on your goals and progress
            </p>
          </div>

          <div style={{ 
            background: 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)',
            padding: '24px',
            borderRadius: '12px',
            border: '1px solid #e2e8f0'
          }}>
            <Sparkles size={32} color="#9f7aea" style={{ marginBottom: '12px' }} />
            <h3 style={{ fontSize: '18px', marginBottom: '8px', color: '#2d3748' }}>
              Smart Insights
            </h3>
            <p style={{ color: '#718096', fontSize: '14px', lineHeight: '1.6' }}>
              Discover learning paths and opportunities you might have missed
            </p>
          </div>
        </div>

        <div style={{ 
          marginTop: '48px',
          padding: '24px',
          background: 'linear-gradient(135deg, rgba(159, 122, 234, 0.1) 0%, rgba(128, 90, 213, 0.1) 100%)',
          borderRadius: '12px',
          border: '1px solid rgba(159, 122, 234, 0.2)'
        }}>
          <p style={{ color: '#553c9a', fontWeight: '600', fontSize: '16px' }}>
            🚀 This feature is under development and will be available soon!
          </p>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
            box-shadow: 0 20px 40px rgba(159, 122, 234, 0.3);
          }
          50% {
            transform: scale(1.05);
            box-shadow: 0 25px 50px rgba(159, 122, 234, 0.4);
          }
        }
      `}</style>
    </div>
  )
}

export default AIMentor
