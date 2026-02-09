import { useState } from 'react'
import { careerAPI } from '../services/api'
import { TrendingUp, Award, Clock } from 'lucide-react'

function CareerPath() {
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
        current_skills: formData.skills.split(',').map(s => s.trim()),
        experience_years: formData.experience_years
      })
      setRecommendation(response.data.data || response.data)
    } catch (error) {
      console.error('Failed to get recommendation:', error)
    }
    setLoading(false)
  }

  return (
    <div className="container">
      <h1 style={{ color: 'white', marginBottom: '24px' }}>Career Path Planner</h1>

      <div className="card">
        <h2>Tell Us About Your Career Goals</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Current Role"
            className="input"
            value={formData.current_role}
            onChange={(e) => setFormData({ ...formData, current_role: e.target.value })}
            required
          />
          <input
            type="text"
            placeholder="Target Role"
            className="input"
            value={formData.target_role}
            onChange={(e) => setFormData({ ...formData, target_role: e.target.value })}
            required
          />
          <input
            type="text"
            placeholder="Current Skills (comma-separated)"
            className="input"
            value={formData.skills}
            onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
            required
          />
          <input
            type="number"
            placeholder="Years of Experience"
            className="input"
            value={formData.experience_years}
            onChange={(e) => setFormData({ ...formData, experience_years: parseInt(e.target.value) })}
            required
          />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            <TrendingUp size={20} style={{ marginRight: '8px', display: 'inline' }} />
            {loading ? 'Generating Plan...' : 'Get Career Roadmap'}
          </button>
        </form>
      </div>

      {recommendation && (
        <>
          <div className="card">
            <h2>Your Career Transition Plan</h2>
            <div style={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
              color: 'white', 
              padding: '20px', 
              borderRadius: '8px',
              marginBottom: '16px'
            }}>
              <h3 style={{ color: 'white', marginBottom: '8px' }}>
                {formData.current_role} → {formData.target_role}
              </h3>
              <p style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                <Clock size={20} style={{ marginRight: '8px' }} />
                Timeline: {recommendation.estimated_timeline || 'N/A'}
              </p>
              <p style={{ fontSize: '14px', opacity: 0.9 }}>
                Feasibility: <strong>{recommendation.transition_feasibility || 'N/A'}</strong>
              </p>
            </div>
          </div>

          {recommendation.transferable_skills && recommendation.transferable_skills.length > 0 && (
            <div className="card">
              <h2>✅ Your Transferable Skills</h2>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {recommendation.transferable_skills.map((skill, idx) => (
                  <span key={idx} style={{ 
                    background: '#48bb78', 
                    color: 'white', 
                    padding: '8px 16px', 
                    borderRadius: '20px',
                    fontSize: '14px'
                  }}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {recommendation.skills_to_acquire && recommendation.skills_to_acquire.length > 0 && (
            <div className="card">
              <h2>🎯 Skills to Acquire</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {recommendation.skills_to_acquire.map((skillObj, idx) => {
                  const skill = typeof skillObj === 'string' ? skillObj : skillObj.skill;
                  const priority = skillObj.priority || 'important';
                  const time = skillObj.estimated_learning_time || 'N/A';
                  
                  const priorityColors = {
                    critical: '#e53e3e',
                    important: '#ed8936',
                    'nice-to-have': '#4299e1'
                  };
                  
                  return (
                    <div key={idx} style={{ 
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '12px',
                      background: '#f7fafc',
                      borderRadius: '8px',
                      borderLeft: `4px solid ${priorityColors[priority] || '#ed8936'}`
                    }}>
                      <div>
                        <strong style={{ fontSize: '16px' }}>{skill}</strong>
                        <div style={{ fontSize: '13px', color: '#718096', marginTop: '4px' }}>
                          ⏱️ {time}
                        </div>
                      </div>
                      <span style={{ 
                        background: priorityColors[priority] || '#ed8936',
                        color: 'white',
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        textTransform: 'uppercase',
                        fontWeight: 'bold'
                      }}>
                        {priority}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {recommendation.learning_path && recommendation.learning_path.length > 0 && (
            <div className="card">
              <h2>📚 Learning Path</h2>
              {recommendation.learning_path.map((phase, idx) => (
                <div key={idx} style={{ 
                  background: '#f7fafc', 
                  padding: '16px', 
                  borderRadius: '8px', 
                  marginBottom: '16px',
                  borderLeft: '4px solid #667eea'
                }}>
                  <h3 style={{ color: '#667eea', marginBottom: '8px' }}>
                    Phase {phase.phase || idx + 1}: {phase.title}
                  </h3>
                  <p style={{ color: '#718096', marginBottom: '12px' }}>
                    <Clock size={16} style={{ display: 'inline', marginRight: '4px' }} />
                    Duration: {phase.duration}
                  </p>
                  
                  {phase.focus_areas && phase.focus_areas.length > 0 && (
                    <div style={{ marginBottom: '12px' }}>
                      <strong>Focus Areas:</strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
                        {phase.focus_areas.map((area, aidx) => (
                          <span key={aidx} style={{ 
                            background: '#e6fffa',
                            color: '#234e52',
                            padding: '4px 10px',
                            borderRadius: '12px',
                            fontSize: '13px'
                          }}>
                            {area}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {phase.activities && phase.activities.length > 0 && (
                    <div style={{ marginBottom: '12px' }}>
                      <strong>Activities:</strong>
                      <ul style={{ paddingLeft: '20px', marginTop: '6px' }}>
                        {phase.activities.map((activity, aidx) => (
                          <li key={aidx} style={{ marginBottom: '4px' }}>{activity}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {phase.resources_needed && phase.resources_needed.length > 0 && (
                    <div>
                      <strong>Resources Needed:</strong>
                      <ul style={{ paddingLeft: '20px', marginTop: '6px' }}>
                        {phase.resources_needed.map((resource, ridx) => (
                          <li key={ridx} style={{ marginBottom: '4px' }}>{resource}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {recommendation.certifications && recommendation.certifications.length > 0 && (
            <div className="card">
              <h2>
                <Award size={24} style={{ display: 'inline', marginRight: '8px' }} color="#9f7aea" />
                Recommended Certifications
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {recommendation.certifications.map((cert, idx) => {
                  const certName = typeof cert === 'string' ? cert : cert.name;
                  const provider = cert.provider || '';
                  const priority = cert.priority || 'medium';
                  const cost = cert.estimated_cost || '';
                  
                  return (
                    <div key={idx} style={{ 
                      padding: '12px',
                      background: '#faf5ff',
                      borderRadius: '8px',
                      borderLeft: '4px solid #9f7aea'
                    }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '4px' }}>
                        {certName}
                      </div>
                      {provider && (
                        <div style={{ fontSize: '14px', color: '#718096', marginBottom: '4px' }}>
                          Provider: {provider}
                        </div>
                      )}
                      <div style={{ display: 'flex', gap: '12px', fontSize: '13px', color: '#718096' }}>
                        {priority && <span>Priority: <strong>{priority}</strong></span>}
                        {cost && <span>Cost: {cost}</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {recommendation.milestones && recommendation.milestones.length > 0 && (
            <div className="card">
              <h2>🎯 Milestones</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {recommendation.milestones.map((milestone, idx) => (
                  <div key={idx} style={{ 
                    padding: '12px',
                    background: '#f0fff4',
                    borderRadius: '8px',
                    borderLeft: '4px solid #48bb78'
                  }}>
                    <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#48bb78', marginBottom: '4px' }}>
                      Month {milestone.month}
                    </div>
                    <div style={{ fontSize: '15px', marginBottom: '4px' }}>
                      {milestone.goal}
                    </div>
                    <div style={{ fontSize: '13px', color: '#718096' }}>
                      Success: {milestone.success_criteria}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {recommendation.job_search_tips && recommendation.job_search_tips.length > 0 && (
            <div className="card">
              <h2>💼 Job Search Tips</h2>
              <ul style={{ paddingLeft: '20px' }}>
                {recommendation.job_search_tips.map((tip, idx) => (
                  <li key={idx} style={{ marginBottom: '8px', fontSize: '15px' }}>{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default CareerPath
