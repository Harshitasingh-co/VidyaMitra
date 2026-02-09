import { useState } from 'react'
import { interviewAPI } from '../services/api'
import { Play, Send, MessageSquare, Loader, CheckCircle, AlertCircle } from 'lucide-react'

function MockInterview() {
  const [formData, setFormData] = useState({
    role: '',
    experience_level: 'entry',
    industry: ''
  })
  const [questions, setQuestions] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answer, setAnswer] = useState('')
  const [feedback, setFeedback] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const generateQuestions = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await interviewAPI.generateQuestions(formData)
      // Backend returns { success: true, data: {...}, message: "..." }
      const data = response.data.data || response.data
      setQuestions(data.questions || [])
      setCurrentQuestion(0)
    } catch (error) {
      console.error('Failed to generate questions:', error)
      setError(error.response?.data?.detail || 'Failed to generate questions. Please try again.')
    }
    setLoading(false)
  }

  const submitAnswer = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await interviewAPI.evaluate({
        question: questions[currentQuestion]?.question,
        category: questions[currentQuestion]?.category,
        answer: answer
      })
      // Backend returns { success: true, data: {...}, message: "..." }
      const data = response.data.data || response.data
      setFeedback(data)
    } catch (error) {
      console.error('Failed to evaluate answer:', error)
      setError(error.response?.data?.detail || 'Failed to evaluate answer. Please try again.')
    }
    setLoading(false)
  }

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
      setAnswer('')
      setFeedback(null)
    }
  }

  return (
    <div className="container">
      <h1 style={{ color: 'white', marginBottom: '8px', fontSize: '36px', fontWeight: '800' }}>
        AI Interview Simulator
      </h1>
      <p style={{ color: 'rgba(255,255,255,0.9)', marginBottom: '32px', fontSize: '16px' }}>
        Practice with AI-driven interviews and get personalized feedback
      </p>

      {questions.length === 0 ? (
        <div className="card">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <MessageSquare size={28} color="#667eea" />
            Start Your Interview
          </h2>
          
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#2d3748' }}>
              Target Role *
            </label>
            <input
              type="text"
              placeholder="e.g., Software Engineer, Data Analyst"
              className="input"
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#2d3748' }}>
              Experience Level
            </label>
            <select
              className="input"
              value={formData.experience_level}
              onChange={(e) => setFormData({ ...formData, experience_level: e.target.value })}
            >
              <option value="entry">Entry Level (0-2 years)</option>
              <option value="mid">Mid Level (3-5 years)</option>
              <option value="senior">Senior Level (5+ years)</option>
            </select>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#2d3748' }}>
              Industry (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g., Technology, Finance, Healthcare"
              className="input"
              value={formData.industry}
              onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
            />
          </div>

          {error && (
            <div style={{ 
              background: '#fff5f5', 
              padding: '16px', 
              borderRadius: '10px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              border: '1px solid #fc8181'
            }}>
              <AlertCircle size={20} color="#f56565" />
              <span style={{ color: '#c53030', fontWeight: '500' }}>{error}</span>
            </div>
          )}

          <button 
            onClick={generateQuestions} 
            className="btn btn-primary" 
            disabled={!formData.role || loading}
            style={{ 
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              fontSize: '16px',
              padding: '14px'
            }}
          >
            {loading ? (
              <>
                <Loader size={20} className="spinner" style={{ animation: 'spin 1s linear infinite' }} />
                Generating Questions...
              </>
            ) : (
              <>
                <Play size={20} />
                Start Interview
              </>
            )}
          </button>
        </div>
      ) : (
        <>
          <div className="card">
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '24px',
              paddingBottom: '16px',
              borderBottom: '2px solid #e2e8f0'
            }}>
              <h2 style={{ margin: 0 }}>Question {currentQuestion + 1} of {questions.length}</h2>
              <div style={{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                padding: '8px 16px',
                borderRadius: '20px',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                {Math.round(((currentQuestion + 1) / questions.length) * 100)}% Complete
              </div>
            </div>

            <div style={{ 
              background: 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)', 
              padding: '24px', 
              borderRadius: '12px', 
              marginBottom: '24px',
              borderLeft: '4px solid #667eea'
            }}>
              <p style={{ fontSize: '18px', color: '#2d3748', lineHeight: '1.6', marginBottom: '16px' }}>
                {questions[currentQuestion]?.question}
              </p>
              <span style={{ 
                display: 'inline-block', 
                background: '#667eea', 
                color: 'white', 
                padding: '6px 16px', 
                borderRadius: '20px', 
                fontSize: '14px',
                fontWeight: '600'
              }}>
                {questions[currentQuestion]?.category}
              </span>
            </div>
            
            {!feedback && (
              <>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#2d3748' }}>
                    Your Answer
                  </label>
                  <textarea
                    className="input"
                    placeholder="Type your answer here... Be specific and provide examples."
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    rows={8}
                    style={{ resize: 'vertical', fontFamily: 'Inter, sans-serif' }}
                  />
                  <p style={{ color: '#a0aec0', fontSize: '14px', marginTop: '8px' }}>
                    {answer.length} characters
                  </p>
                </div>

                {error && (
                  <div style={{ 
                    background: '#fff5f5', 
                    padding: '16px', 
                    borderRadius: '10px',
                    marginBottom: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    border: '1px solid #fc8181'
                  }}>
                    <AlertCircle size={20} color="#f56565" />
                    <span style={{ color: '#c53030', fontWeight: '500' }}>{error}</span>
                  </div>
                )}

                <button 
                  onClick={submitAnswer} 
                  className="btn btn-primary" 
                  disabled={!answer || loading}
                  style={{ 
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    fontSize: '16px',
                    padding: '14px'
                  }}
                >
                  {loading ? (
                    <>
                      <Loader size={20} className="spinner" style={{ animation: 'spin 1s linear infinite' }} />
                      Evaluating Your Answer...
                    </>
                  ) : (
                    <>
                      <Send size={20} />
                      Submit Answer
                    </>
                  )}
                </button>
              </>
            )}
          </div>

          {loading && !feedback && (
            <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
              <div className="spinner" style={{ margin: '0 auto 20px' }}></div>
              <h3 style={{ color: '#4a5568', marginBottom: '8px' }}>Analyzing your response...</h3>
              <p style={{ color: '#a0aec0' }}>Our AI is evaluating your answer</p>
            </div>
          )}

          {feedback && (
            <>
              <div className="card" style={{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white'
              }}>
                <h2 style={{ color: 'white', marginBottom: '20px' }}>Your Performance</h2>
                <div style={{ 
                  background: 'rgba(255, 255, 255, 0.2)', 
                  backdropFilter: 'blur(10px)',
                  padding: '32px', 
                  borderRadius: '16px',
                  textAlign: 'center',
                  marginBottom: '24px'
                }}>
                  <div style={{ fontSize: '56px', fontWeight: '800', marginBottom: '8px' }}>
                    {feedback.overall_score}/100
                  </div>
                  <div style={{ fontSize: '18px', opacity: 0.9 }}>Overall Score</div>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ 
                    background: 'rgba(255, 255, 255, 0.15)', 
                    backdropFilter: 'blur(10px)',
                    padding: '16px', 
                    borderRadius: '12px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '4px' }}>Tone</div>
                    <div style={{ fontSize: '18px', fontWeight: '700' }}>{feedback.tone_analysis}</div>
                  </div>
                  <div style={{ 
                    background: 'rgba(255, 255, 255, 0.15)', 
                    backdropFilter: 'blur(10px)',
                    padding: '16px', 
                    borderRadius: '12px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '4px' }}>Confidence</div>
                    <div style={{ fontSize: '18px', fontWeight: '700' }}>{feedback.confidence_level}</div>
                  </div>
                </div>
              </div>

              <div className="card">
                <h2 style={{ marginBottom: '16px' }}>Detailed Feedback</h2>
                <p style={{ 
                  fontSize: '16px', 
                  lineHeight: '1.7', 
                  color: '#4a5568',
                  background: '#f7fafc',
                  padding: '20px',
                  borderRadius: '12px',
                  marginBottom: '24px'
                }}>
                  {feedback.detailed_feedback}
                </p>

                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ 
                    color: '#48bb78', 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '8px',
                    marginBottom: '16px'
                  }}>
                    <CheckCircle size={24} />
                    Strengths
                  </h3>
                  <ul style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
                    {feedback.strengths.map((s, idx) => (
                      <li key={idx} style={{ 
                        marginBottom: '12px',
                        color: '#2d3748',
                        fontSize: '16px'
                      }}>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>

                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ 
                    color: '#ed8936', 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '8px',
                    marginBottom: '16px'
                  }}>
                    <AlertCircle size={24} />
                    Areas for Improvement
                  </h3>
                  <ul style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
                    {feedback.improvements.map((i, idx) => (
                      <li key={idx} style={{ 
                        marginBottom: '12px',
                        color: '#2d3748',
                        fontSize: '16px'
                      }}>
                        {i}
                      </li>
                    ))}
                  </ul>
                </div>

                {currentQuestion < questions.length - 1 ? (
                  <button 
                    onClick={nextQuestion} 
                    className="btn btn-primary"
                    style={{ 
                      width: '100%',
                      fontSize: '16px',
                      padding: '14px'
                    }}
                  >
                    Next Question →
                  </button>
                ) : (
                  <div style={{ 
                    background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
                    color: 'white',
                    padding: '24px',
                    borderRadius: '12px',
                    textAlign: 'center'
                  }}>
                    <CheckCircle size={48} style={{ margin: '0 auto 16px' }} />
                    <h3 style={{ color: 'white', marginBottom: '8px' }}>Interview Complete!</h3>
                    <p style={{ opacity: 0.9 }}>Great job completing all questions</p>
                  </div>
                )}
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}

export default MockInterview
