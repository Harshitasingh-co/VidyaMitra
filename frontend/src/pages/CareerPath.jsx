import { useState } from 'react'
import { careerAPI } from '../services/api'
import { TrendingUp, Award, Clock, Target, BookOpen, CheckCircle, Circle, ArrowRight, Zap, Star } from 'lucide-react'

function CareerPath() {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    current_role: '',
    target_role: '',
    skills: '',
    experience_years: 0
  })
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await careerAPI.recommend({
        current_role: formData.current_role,
        target_role: formData.target_role,
        current_skills: formData.skills.split(',').map(s => s.trim()).filter(s => s),
        experience_years: formData.experience_years
      })
      setRecommendation(response.data.data || response.data)
      setStep(2)
    } catch (error) {
      console.error('Failed to get recommendation:', error)
      alert('Failed to generate roadmap. Please try again.')
    }
    setLoading(false)
  }

  const resetForm = () => {
    setStep(1)
    setRecommendation(null)
    setFormData({
      current_role: '',
      target_role: '',
      skills: '',
      experience_years: 0
    })
  }

  return (
    <div className="container">
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ color: 'white', marginBottom: '8px', fontSize: '36px', fontWeight: '800' }}>
          Career Roadmap Generator
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.9)', fontSize: '16px' }}>
          Get a personalized career transition plan powered by AI
        </p>
      </div>

      {/* Progress Steps */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        marginBottom: '32px',
        gap: '16px'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px',
          padding: '12px 24px',
          background: step === 1 ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#2d3748',
          borderRadius: '24px',
          color: 'white',
          fontWeight: '600'
        }}>
          {step > 1 ? <CheckCircle size={20} /> : <Circle size={20} />}
          <span>1. Your Profile</span>
        </div>
        <ArrowRight size={24} color="white" />
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px',
          padding: '12px 24px',
          background: step === 2 ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#2d3748',
          borderRadius: '24px',
          color: 'white',
          fontWeight: '600'
        }}>
          {step === 2 ? <CheckCircle size={20} /> : <Circle size={20} />}
          <span>2. Your Roadmap</span>
        </div>
      </div>

      {step === 1 && (
        <div className="card" style={{ maxWidth: '700px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{
              width: '80px',
              height: '80px',
              margin: '0 auto 16px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Target size={40} color="white" />
            </div>
            <h2 style={{ marginBottom: '8px' }}>Tell Us About Your Career Goals</h2>
            <p style={{ color: '#718096', fontSize: '14px' }}>
              Share your current situation and where you want to go
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '24px' }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontWeight: '600',
                color: '#2d3748'
              }}>
                Current Role
              </label>
              <input
                type="text"
                placeholder="e.g., Junior Developer, Student, Fresher"
                className="input"
                value={formData.current_role}
                onChange={(e) => setFormData({ ...formData, current_role: e.target.value })}
                required
                style={{ fontSize: '16px' }}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontWeight: '600',
                color: '#2d3748'
              }}>
                Target Role
              </label>
              <input
                type="text"
                placeholder="e.g., Senior Developer, Data Scientist, Product Manager"
                className="input"
                value={formData.target_role}
                onChange={(e) => setFormData({ ...formData, target_role: e.target.value })}
                required
                style={{ fontSize: '16px' }}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontWeight: '600',
                color: '#2d3748'
              }}>
                Current Skills
              </label>
              <textarea
                placeholder="List your skills separated by commas&#10;e.g., Python, JavaScript, React, SQL, Git"
                className="input"
                value={formData.skills}
                onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                required
                rows={4}
                style={{ fontSize: '16px', resize: 'vertical' }}
              />
              <p style={{ fontSize: '13px', color: '#718096', marginTop: '4px' }}>
                💡 Include programming languages, frameworks, tools, and soft skills
              </p>
            </div>

            <div style={{ marginBottom: '32px' }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontWeight: '600',
                color: '#2d3748'
              }}>
                Years of Experience
              </label>
              <input
                type="number"
                placeholder="0"
                className="input"
                value={formData.experience_years}
                onChange={(e) => setFormData({ ...formData, experience_years: parseInt(e.target.value) || 0 })}
                min="0"
                max="50"
                required
                style={{ fontSize: '16px' }}
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={loading}
              style={{
                width: '100%',
                padding: '16px',
                fontSize: '18px',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '12px'
              }}
            >
              {loading ? (
                <>
                  <div className="spinner" style={{ width: '20px', height: '20px' }}></div>
                  Generating Your Roadmap...
                </>
              ) : (
                <>
                  <Zap size={24} />
                  Generate My Career Roadmap
                </>
              )}
            </button>
          </form>
        </div>
      )}

      {step === 2 && recommendation && (
        <>
          {/* Header Card */}
          <div className="card" style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
            color: 'white',
            marginBottom: '24px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h2 style={{ color: 'white', marginBottom: '12px', fontSize: '28px' }}>
                  Your Personalized Career Roadmap
                </h2>
                <div style={{ fontSize: '20px', marginBottom: '16px', opacity: 0.95 }}>
                  {formData.current_role} → {formData.target_role}
                </div>
                <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Clock size={20} />
                    <span>Timeline: <strong>{recommendation.estimated_timeline || '6-12 months'}</strong></span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Star size={20} />
                    <span>Feasibility: <strong>{recommendation.transition_feasibility || 'High'}</strong></span>
                  </div>
                </div>
              </div>
              <button
                onClick={resetForm}
                style={{
                  background: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Start Over
              </button>
            </div>
          </div>

          {/* Transferable Skills */}
          {recommendation.transferable_skills && recommendation.transferable_skills.length > 0 && (
            <div className="card">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <CheckCircle size={28} color="#48bb78" />
                Your Transferable Skills
              </h2>
              <p style={{ color: '#718096', marginBottom: '16px' }}>
                Great news! You already have these valuable skills for your target role:
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                {recommendation.transferable_skills.map((skill, idx) => (
                  <span key={idx} style={{ 
                    background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)', 
                    color: 'white', 
                    padding: '10px 20px', 
                    borderRadius: '24px',
                    fontSize: '15px',
                    fontWeight: '600',
                    boxShadow: '0 2px 8px rgba(72, 187, 120, 0.3)'
                  }}>
                    ✓ {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Skills to Acquire */}
          {recommendation.skills_to_acquire && recommendation.skills_to_acquire.length > 0 && (
            <div className="card">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <Target size={28} color="#ed8936" />
                Skills to Acquire
              </h2>
              <p style={{ color: '#718096', marginBottom: '20px' }}>
                Focus on learning these skills to bridge the gap:
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {recommendation.skills_to_acquire.map((skillObj, idx) => {
                  const skill = typeof skillObj === 'string' ? skillObj : skillObj.skill;
                  const priority = skillObj.priority || 'important';
                  const time = skillObj.estimated_learning_time || 'N/A';
                  
                  const priorityConfig = {
                    critical: { color: '#e53e3e', bg: '#fff5f5', label: 'Critical' },
                    important: { color: '#ed8936', bg: '#fffaf0', label: 'Important' },
                    'nice-to-have': { color: '#4299e1', bg: '#ebf8ff', label: 'Nice to Have' }
                  };
                  
                  const config = priorityConfig[priority] || priorityConfig.important;
                  
                  return (
                    <div key={idx} style={{ 
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '16px',
                      background: config.bg,
                      borderRadius: '12px',
                      borderLeft: `5px solid ${config.color}`,
                      transition: 'transform 0.2s',
                      cursor: 'default'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.transform = 'translateX(4px)'}
                    onMouseOut={(e) => e.currentTarget.style.transform = 'translateX(0)'}
                    >
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '17px', fontWeight: '600', marginBottom: '6px' }}>
                          {skill}
                        </div>
                        <div style={{ fontSize: '14px', color: '#718096', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <Clock size={14} />
                          {time}
                        </div>
                      </div>
                      <span style={{ 
                        background: config.color,
                        color: 'white',
                        padding: '6px 16px',
                        borderRadius: '16px',
                        fontSize: '13px',
                        textTransform: 'uppercase',
                        fontWeight: '700',
                        letterSpacing: '0.5px'
                      }}>
                        {config.label}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Learning Path - Workflow Format */}
          {recommendation.learning_path && recommendation.learning_path.length > 0 && (
            <div className="card">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <BookOpen size={28} color="#667eea" />
                Your Learning Workflow
              </h2>
              <p style={{ color: '#718096', marginBottom: '24px' }}>
                Follow this step-by-step path to achieve your career goal:
              </p>
              
              <div style={{ position: 'relative' }}>
                {/* Vertical Timeline Line */}
                <div style={{
                  position: 'absolute',
                  left: '20px',
                  top: '40px',
                  bottom: '40px',
                  width: '3px',
                  background: 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
                  opacity: 0.3
                }}></div>

                {recommendation.learning_path.map((phase, idx) => (
                  <div key={idx} style={{ 
                    position: 'relative',
                    marginBottom: idx < recommendation.learning_path.length - 1 ? '32px' : '0',
                    marginLeft: '60px'
                  }}>
                    {/* Phase Number Circle */}
                    <div style={{
                      position: 'absolute',
                      left: '-60px',
                      top: '0',
                      width: '40px',
                      height: '40px',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontWeight: '700',
                      fontSize: '18px',
                      boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
                      zIndex: 1
                    }}>
                      {phase.phase || idx + 1}
                    </div>

                    <div style={{ 
                      background: '#f7fafc', 
                      padding: '20px', 
                      borderRadius: '12px',
                      border: '2px solid #e2e8f0',
                      transition: 'all 0.3s'
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.borderColor = '#667eea'
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.2)'
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.borderColor = '#e2e8f0'
                      e.currentTarget.style.boxShadow = 'none'
                    }}
                    >
                      <h3 style={{ color: '#667eea', marginBottom: '10px', fontSize: '20px', fontWeight: '700' }}>
                        {phase.title}
                      </h3>
                      <div style={{ 
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        background: '#e6fffa',
                        color: '#234e52',
                        padding: '6px 12px',
                        borderRadius: '16px',
                        fontSize: '14px',
                        fontWeight: '600',
                        marginBottom: '16px'
                      }}>
                        <Clock size={16} />
                        {phase.duration}
                      </div>
                      
                      {phase.focus_areas && phase.focus_areas.length > 0 && (
                        <div style={{ marginBottom: '16px' }}>
                          <div style={{ fontWeight: '600', marginBottom: '8px', color: '#2d3748' }}>
                            🎯 Focus Areas:
                          </div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {phase.focus_areas.map((area, aidx) => (
                              <span key={aidx} style={{ 
                                background: 'white',
                                color: '#667eea',
                                padding: '6px 14px',
                                borderRadius: '16px',
                                fontSize: '14px',
                                fontWeight: '500',
                                border: '1px solid #e2e8f0'
                              }}>
                                {area}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {phase.activities && phase.activities.length > 0 && (
                        <div style={{ marginBottom: '16px' }}>
                          <div style={{ fontWeight: '600', marginBottom: '8px', color: '#2d3748' }}>
                            📋 Activities:
                          </div>
                          <ul style={{ paddingLeft: '20px', margin: 0 }}>
                            {phase.activities.map((activity, aidx) => (
                              <li key={aidx} style={{ marginBottom: '6px', color: '#4a5568' }}>
                                {activity}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {phase.resources_needed && phase.resources_needed.length > 0 && (
                        <div>
                          <div style={{ fontWeight: '600', marginBottom: '8px', color: '#2d3748' }}>
                            📚 Resources:
                          </div>
                          <ul style={{ paddingLeft: '20px', margin: 0 }}>
                            {phase.resources_needed.map((resource, ridx) => (
                              <li key={ridx} style={{ marginBottom: '6px', color: '#4a5568' }}>
                                {resource}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Certifications */}
          {recommendation.certifications && recommendation.certifications.length > 0 && (
            <div className="card">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <Award size={28} color="#9f7aea" />
                Recommended Certifications
              </h2>
              <p style={{ color: '#718096', marginBottom: '20px' }}>
                Boost your credibility with these industry-recognized certifications:
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
                {recommendation.certifications.map((cert, idx) => {
                  const certName = typeof cert === 'string' ? cert : cert.name;
                  const provider = cert.provider || '';
                  const priority = cert.priority || 'medium';
                  const cost = cert.estimated_cost || '';
                  
                  return (
                    <div key={idx} style={{ 
                      padding: '16px',
                      background: 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)',
                      borderRadius: '12px',
                      border: '2px solid #e9d8fd',
                      transition: 'transform 0.2s'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
                    onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                    >
                      <div style={{ fontSize: '17px', fontWeight: '700', marginBottom: '8px', color: '#553c9a' }}>
                        {certName}
                      </div>
                      {provider && (
                        <div style={{ fontSize: '14px', color: '#6b46c1', marginBottom: '8px' }}>
                          📍 {provider}
                        </div>
                      )}
                      <div style={{ display: 'flex', gap: '12px', fontSize: '13px', color: '#6b46c1', flexWrap: 'wrap' }}>
                        {priority && (
                          <span style={{ 
                            background: '#9f7aea',
                            color: 'white',
                            padding: '4px 10px',
                            borderRadius: '12px',
                            fontWeight: '600'
                          }}>
                            {priority}
                          </span>
                        )}
                        {cost && <span>💰 {cost}</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Milestones */}
          {recommendation.milestones && recommendation.milestones.length > 0 && (
            <div className="card">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <Target size={28} color="#48bb78" />
                Key Milestones
              </h2>
              <p style={{ color: '#718096', marginBottom: '20px' }}>
                Track your progress with these important checkpoints:
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
                {recommendation.milestones.map((milestone, idx) => (
                  <div key={idx} style={{ 
                    padding: '16px',
                    background: 'linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%)',
                    borderRadius: '12px',
                    border: '2px solid #9ae6b4'
                  }}>
                    <div style={{ 
                      fontSize: '14px', 
                      fontWeight: '700', 
                      color: '#22543d', 
                      marginBottom: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}>
                      <Clock size={16} />
                      Month {milestone.month}
                    </div>
                    <div style={{ fontSize: '16px', marginBottom: '8px', fontWeight: '600', color: '#2f855a' }}>
                      {milestone.goal}
                    </div>
                    <div style={{ fontSize: '13px', color: '#38a169' }}>
                      ✓ {milestone.success_criteria}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Job Search Tips */}
          {recommendation.job_search_tips && recommendation.job_search_tips.length > 0 && (
            <div className="card">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                💼 Job Search Strategy
              </h2>
              <p style={{ color: '#718096', marginBottom: '16px' }}>
                Pro tips to land your dream role:
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {recommendation.job_search_tips.map((tip, idx) => (
                  <div key={idx} style={{ 
                    display: 'flex',
                    gap: '12px',
                    padding: '14px',
                    background: '#f7fafc',
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0'
                  }}>
                    <div style={{ 
                      minWidth: '28px',
                      height: '28px',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontWeight: '700',
                      fontSize: '14px'
                    }}>
                      {idx + 1}
                    </div>
                    <div style={{ fontSize: '15px', color: '#2d3748', lineHeight: '1.6' }}>
                      {tip}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Button */}
          <div className="card" style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            textAlign: 'center'
          }}>
            <h3 style={{ color: 'white', marginBottom: '12px', fontSize: '24px' }}>
              Ready to Start Your Journey?
            </h3>
            <p style={{ marginBottom: '20px', opacity: 0.9 }}>
              Save this roadmap and start working on your first milestone today!
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button
                onClick={() => window.print()}
                style={{
                  background: 'white',
                  color: '#667eea',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                📄 Download PDF
              </button>
              <button
                onClick={resetForm}
                style={{
                  background: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  border: '2px solid white',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                🔄 Create New Roadmap
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default CareerPath
