import { useState } from 'react'
import { Upload, CheckCircle, AlertCircle, FileText, Loader, Award, Code, TrendingUp, ExternalLink, Copy, Building } from 'lucide-react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api'

function ContextAwareResume() {
  // Step tracking
  const [currentStep, setCurrentStep] = useState(1)
  
  // Career Intent State
  const [careerIntent, setCareerIntent] = useState({
    desired_role: '',
    experience_level: '0-2 years',
    target_companies: [],
    preferred_industries: []
  })
  const [intentId, setIntentId] = useState(null)
  
  // Resume State
  const [file, setFile] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  
  // UI State
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const companyTypes = [
    'Product-based companies',
    'Startups',
    'Enterprise/Corporate',
    'Consulting firms',
    'Tech giants (FAANG)',
    'Mid-size companies'
  ]

  const industries = [
    'Tech/Software',
    'E-commerce',
    'Finance/Fintech',
    'Healthcare',
    'Education',
    'Gaming',
    'AI/ML',
    'Cloud/DevOps'
  ]

  const experienceLevels = [
    '0-2 years',
    '3-5 years',
    '5+ years'
  ]

  const handleCompanyToggle = (company) => {
    setCareerIntent(prev => ({
      ...prev,
      target_companies: prev.target_companies.includes(company)
        ? prev.target_companies.filter(c => c !== company)
        : [...prev.target_companies, company]
    }))
  }

  const handleIndustryToggle = (industry) => {
    setCareerIntent(prev => ({
      ...prev,
      preferred_industries: prev.preferred_industries.includes(industry)
        ? prev.preferred_industries.filter(i => i !== industry)
        : [...prev.preferred_industries, industry]
    }))
  }

  const handleSubmitIntent = async () => {
    if (!careerIntent.desired_role || careerIntent.target_companies.length === 0) {
      setError('Please fill in desired role and select at least one target company type')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.post(`${API_URL}/career-intent`, careerIntent)
      setIntentId(response.data.intent_id)
      setCurrentStep(2)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit career intent')
    }
    
    setLoading(false)
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    setFile(selectedFile)
    setError(null)
  }

  const handleAnalyze = async () => {
    if (!file || !intentId) return
    
    setLoading(true)
    setError(null)
    
    try {
      // Upload resume
      const formData = new FormData()
      formData.append('file', file)
      const uploadRes = await axios.post(`${API_URL}/resume/upload`, formData)
      const resumeText = uploadRes.data.data?.full_text || uploadRes.data.full_text
      
      // Analyze with context
      const analysisRes = await axios.post(`${API_URL}/context-aware-analyze`, {
        resume_text: resumeText,
        intent_id: intentId
      })
      
      setAnalysis(analysisRes.data.data || analysisRes.data)
      setCurrentStep(3)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze resume')
    }
    
    setLoading(false)
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  return (
    <div className="container">
      <h1 style={{ color: 'white', marginBottom: '8px', fontSize: '36px', fontWeight: '800' }}>
        🎯 Context-Aware Resume Analysis
      </h1>
      <p style={{ color: 'rgba(255,255,255,0.9)', marginBottom: '32px', fontSize: '16px' }}>
        Get personalized insights based on your career goals
      </p>

      {/* Progress Steps */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        gap: '20px', 
        marginBottom: '40px',
        flexWrap: 'wrap'
      }}>
        {[
          { num: 1, label: 'Career Goals' },
          { num: 2, label: 'Upload Resume' },
          { num: 3, label: 'Get Insights' }
        ].map(step => (
          <div key={step.num} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '12px 24px',
            background: currentStep >= step.num ? 'rgba(102, 126, 234, 0.2)' : 'rgba(255,255,255,0.1)',
            borderRadius: '12px',
            border: currentStep === step.num ? '2px solid #667eea' : '2px solid transparent'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: currentStep >= step.num ? '#667eea' : '#a0aec0',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold'
            }}>
              {currentStep > step.num ? '✓' : step.num}
            </div>
            <span style={{ 
              color: 'white', 
              fontWeight: currentStep === step.num ? 'bold' : 'normal' 
            }}>
              {step.label}
            </span>
          </div>
        ))}
      </div>

      {error && (
        <div className="card" style={{ 
          background: '#fff5f5', 
          border: '2px solid #fc8181',
          marginBottom: '24px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <AlertCircle color="#f56565" size={24} />
            <span style={{ color: '#c53030', fontWeight: '500' }}>{error}</span>
          </div>
        </div>
      )}

      {/* STEP 1: Career Intent */}
      {currentStep === 1 && (
        <div className="card">
          <h2 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <TrendingUp size={28} color="#667eea" />
            Tell Us About Your Career Goals
          </h2>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#2d3748' }}>
              Desired Role *
            </label>
            <input
              type="text"
              className="input"
              placeholder="e.g., Data Analyst, Software Engineer, Product Manager"
              value={careerIntent.desired_role}
              onChange={(e) => setCareerIntent({...careerIntent, desired_role: e.target.value})}
              style={{ width: '100%' }}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#2d3748' }}>
              Experience Level *
            </label>
            <select
              className="input"
              value={careerIntent.experience_level}
              onChange={(e) => setCareerIntent({...careerIntent, experience_level: e.target.value})}
              style={{ width: '100%' }}
            >
              {experienceLevels.map(level => (
                <option key={level} value={level}>{level}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '12px', fontWeight: '600', color: '#2d3748' }}>
              Target Company Types * (Select at least one)
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
              {companyTypes.map(company => (
                <div
                  key={company}
                  onClick={() => handleCompanyToggle(company)}
                  style={{
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: '2px solid',
                    borderColor: careerIntent.target_companies.includes(company) ? '#667eea' : '#e2e8f0',
                    background: careerIntent.target_companies.includes(company) ? '#edf2f7' : 'white',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <div style={{
                    width: '20px',
                    height: '20px',
                    borderRadius: '4px',
                    border: '2px solid',
                    borderColor: careerIntent.target_companies.includes(company) ? '#667eea' : '#cbd5e0',
                    background: careerIntent.target_companies.includes(company) ? '#667eea' : 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '12px'
                  }}>
                    {careerIntent.target_companies.includes(company) && '✓'}
                  </div>
                  <span style={{ fontSize: '14px', fontWeight: '500' }}>{company}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '12px', fontWeight: '600', color: '#2d3748' }}>
              Preferred Industries (Optional)
            </label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {industries.map(industry => (
                <div
                  key={industry}
                  onClick={() => handleIndustryToggle(industry)}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '20px',
                    border: '2px solid',
                    borderColor: careerIntent.preferred_industries.includes(industry) ? '#48bb78' : '#e2e8f0',
                    background: careerIntent.preferred_industries.includes(industry) ? '#f0fff4' : 'white',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '500',
                    transition: 'all 0.2s'
                  }}
                >
                  {industry}
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={handleSubmitIntent}
            className="btn btn-primary"
            disabled={loading || !careerIntent.desired_role || careerIntent.target_companies.length === 0}
            style={{ width: '100%', fontSize: '16px', padding: '14px' }}
          >
            {loading ? (
              <>
                <Loader size={20} className="spinner" />
                Processing...
              </>
            ) : (
              <>
                Continue to Resume Upload →
              </>
            )}
          </button>
        </div>
      )}

      {/* STEP 2: Resume Upload */}
      {currentStep === 2 && (
        <div className="card">
          <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <FileText size={28} color="#667eea" />
            Upload Your Resume
          </h2>

          <div style={{ 
            background: '#f0fff4',
            padding: '16px',
            borderRadius: '8px',
            marginBottom: '20px',
            border: '1px solid #9ae6b4'
          }}>
            <p style={{ color: '#2f855a', fontWeight: '500', marginBottom: '8px' }}>
              ✓ Career goals captured!
            </p>
            <p style={{ color: '#38a169', fontSize: '14px' }}>
              Analyzing for: <strong>{careerIntent.desired_role}</strong> ({careerIntent.experience_level})
            </p>
          </div>

          <div style={{ 
            border: '2px dashed #cbd5e0', 
            borderRadius: '12px', 
            padding: '40px', 
            textAlign: 'center',
            background: '#f7fafc',
            marginBottom: '20px'
          }}>
            <Upload size={48} color="#cbd5e0" style={{ marginBottom: '16px' }} />
            <p style={{ color: '#4a5568', marginBottom: '12px', fontSize: '16px', fontWeight: '500' }}>
              Upload your resume for context-aware analysis
            </p>
            <input
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileChange}
              style={{ display: 'none' }}
              id="file-upload"
            />
            <label htmlFor="file-upload" style={{
              display: 'inline-block',
              padding: '10px 24px',
              background: 'white',
              border: '2px solid #e2e8f0',
              borderRadius: '8px',
              cursor: 'pointer',
              color: '#4a5568',
              fontWeight: '500'
            }}>
              Choose File
            </label>
            <p style={{ color: '#a0aec0', marginTop: '12px', fontSize: '14px' }}>
              Supported: PDF, DOC, DOCX, TXT
            </p>
          </div>

          {file && (
            <div style={{ 
              background: '#f0fff4', 
              padding: '16px', 
              borderRadius: '10px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              border: '1px solid #9ae6b4'
            }}>
              <CheckCircle size={20} color="#48bb78" />
              <span style={{ color: '#2f855a', fontWeight: '500' }}>Selected: {file.name}</span>
            </div>
          )}

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => setCurrentStep(1)}
              className="btn"
              style={{ flex: 1, background: '#e2e8f0', color: '#4a5568' }}
            >
              ← Back
            </button>
            <button
              onClick={handleAnalyze}
              className="btn btn-primary"
              disabled={!file || loading}
              style={{ flex: 2 }}
            >
              {loading ? (
                <>
                  <Loader size={20} className="spinner" />
                  Analyzing...
                </>
              ) : (
                <>
                  Analyze Resume
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Results */}
      {currentStep === 3 && analysis && (
        <>
          {/* Role Fit Score */}
          <div className="card" style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}>
            <h2 style={{ color: 'white', marginBottom: '16px' }}>
              🎯 Role Fit Analysis
            </h2>
            <div style={{ 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '20px'
            }}>
              <div>
                <p style={{ fontSize: '16px', marginBottom: '8px', opacity: 0.9 }}>
                  {careerIntent.desired_role} • {careerIntent.experience_level}
                </p>
                <p style={{ fontSize: '14px', opacity: 0.8 }}>
                  Target: {careerIntent.target_companies.join(', ')}
                </p>
              </div>
              <div style={{
                fontSize: '48px',
                fontWeight: '800',
                background: 'rgba(255,255,255,0.2)',
                padding: '20px 40px',
                borderRadius: '12px'
              }}>
                {analysis.role_fit_score}%
              </div>
            </div>
          </div>

          {/* Skills Overview */}
          <div className="card">
            <h2 style={{ marginBottom: '20px' }}>📊 Skills Overview</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
              <div style={{ padding: '20px', background: '#f0fff4', borderRadius: '8px', border: '2px solid #48bb78' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#48bb78', marginBottom: '8px' }}>
                  {analysis.existing_skills?.length || 0}
                </div>
                <div style={{ color: '#2f855a', fontWeight: '600' }}>Existing Skills</div>
              </div>
              <div style={{ padding: '20px', background: '#fff5f5', borderRadius: '8px', border: '2px solid #ed8936' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#ed8936', marginBottom: '8px' }}>
                  {analysis.missing_skills?.length || 0}
                </div>
                <div style={{ color: '#c05621', fontWeight: '600' }}>Skills to Acquire</div>
              </div>
            </div>

            <div style={{ marginTop: '20px' }}>
              <h3 style={{ marginBottom: '12px', color: '#48bb78' }}>✅ Your Strengths</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '20px' }}>
                {analysis.existing_skills?.map((skill, idx) => (
                  <span key={idx} style={{
                    background: '#f0fff4',
                    color: '#2f855a',
                    padding: '8px 16px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: '600',
                    border: '1px solid #9ae6b4'
                  }}>
                    {skill}
                  </span>
                ))}
              </div>

              <h3 style={{ marginBottom: '12px', color: '#ed8936' }}>❌ Skills Gap</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {analysis.missing_skills?.map((skill, idx) => (
                  <span key={idx} style={{
                    background: '#fff5f5',
                    color: '#c05621',
                    padding: '8px 16px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: '600',
                    border: '1px solid #fc8181'
                  }}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Technical Skills Required */}
          {analysis.technical_skills_required && analysis.technical_skills_required.length > 0 && (
            <div className="card">
              <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Code size={28} color="#667eea" />
                Technical Skills Required
              </h2>
              <div style={{ display: 'grid', gap: '16px' }}>
                {analysis.technical_skills_required.map((skillObj, idx) => {
                  const importanceColors = {
                    'High': '#e53e3e',
                    'Medium': '#ed8936',
                    'Low': '#4299e1'
                  }
                  return (
                    <div key={idx} style={{
                      padding: '20px',
                      background: '#f7fafc',
                      borderRadius: '12px',
                      borderLeft: `4px solid ${importanceColors[skillObj.importance] || '#667eea'}`
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px', flexWrap: 'wrap', gap: '12px' }}>
                        <div>
                          <h3 style={{ color: '#2d3748', marginBottom: '4px', fontSize: '18px' }}>
                            {skillObj.skill}
                          </h3>
                          <span style={{
                            background: importanceColors[skillObj.importance] || '#667eea',
                            color: 'white',
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: 'bold'
                          }}>
                            {skillObj.importance} Priority
                          </span>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '14px', color: '#718096', marginBottom: '4px' }}>
                            Current: <strong>{skillObj.current_level}</strong>
                          </div>
                          <div style={{ fontSize: '14px', color: '#718096' }}>
                            Target: <strong>{skillObj.target_level}</strong>
                          </div>
                        </div>
                      </div>
                      <p style={{ color: '#4a5568', marginBottom: '8px', lineHeight: '1.6' }}>
                        {skillObj.why}
                      </p>
                      <div style={{ fontSize: '14px', color: '#667eea', fontWeight: '600' }}>
                        ⏱️ Learning Time: {skillObj.estimated_learning_time}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Certifications */}
          {analysis.certifications && analysis.certifications.length > 0 && (
            <div className="card">
              <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Award size={28} color="#9f7aea" />
                Recommended Certifications
              </h2>
              <div style={{ display: 'grid', gap: '20px' }}>
                {analysis.certifications.map((cert, idx) => {
                  const priorityColors = {
                    'High': '#e53e3e',
                    'Medium': '#ed8936',
                    'Low': '#4299e1'
                  }
                  return (
                    <div key={idx} style={{
                      padding: '24px',
                      background: 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)',
                      borderRadius: '12px',
                      border: '2px solid #d6bcfa'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px', flexWrap: 'wrap', gap: '12px' }}>
                        <div style={{ flex: 1 }}>
                          <h3 style={{ color: '#553c9a', marginBottom: '8px', fontSize: '20px', fontWeight: '700' }}>
                            {cert.name}
                          </h3>
                          <div style={{ fontSize: '14px', color: '#6b46c1', marginBottom: '4px' }}>
                            📚 Provider: <strong>{cert.provider}</strong>
                          </div>
                          <div style={{ fontSize: '14px', color: '#6b46c1', marginBottom: '4px' }}>
                            ⏱️ Duration: <strong>{cert.duration}</strong>
                          </div>
                          <div style={{ fontSize: '14px', color: '#6b46c1' }}>
                            📊 Level: <strong>{cert.level}</strong>
                          </div>
                        </div>
                        <span style={{
                          background: priorityColors[cert.priority] || '#ed8936',
                          color: 'white',
                          padding: '8px 16px',
                          borderRadius: '20px',
                          fontSize: '12px',
                          fontWeight: 'bold',
                          textTransform: 'uppercase'
                        }}>
                          {cert.priority} Priority
                        </span>
                      </div>
                      
                      <p style={{ color: '#4a5568', marginBottom: '12px', lineHeight: '1.6' }}>
                        {cert.description}
                      </p>
                      
                      <div style={{ 
                        background: '#fff5f5',
                        padding: '12px',
                        borderRadius: '8px',
                        marginBottom: '16px',
                        borderLeft: '3px solid #ed8936'
                      }}>
                        <strong style={{ color: '#c05621' }}>Why recommended:</strong>
                        <p style={{ color: '#744210', marginTop: '4px' }}>{cert.why_recommended}</p>
                      </div>

                      <a
                        href={cert.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '12px 24px',
                          background: '#667eea',
                          color: 'white',
                          borderRadius: '8px',
                          textDecoration: 'none',
                          fontWeight: '600',
                          transition: 'all 0.3s'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.background = '#5568d3'}
                        onMouseLeave={(e) => e.currentTarget.style.background = '#667eea'}
                      >
                        View Certification
                        <ExternalLink size={16} />
                      </a>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Project Ideas */}
          {analysis.projects && analysis.projects.length > 0 && (
            <div className="card">
              <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                💡 Resume-Boosting Project Ideas
              </h2>
              <div style={{ display: 'grid', gap: '24px' }}>
                {analysis.projects.map((project, idx) => (
                  <div key={idx} style={{
                    padding: '24px',
                    background: 'linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%)',
                    borderRadius: '12px',
                    border: '2px solid #9ae6b4'
                  }}>
                    <h3 style={{ color: '#22543d', marginBottom: '12px', fontSize: '22px', fontWeight: '700' }}>
                      {project.title}
                    </h3>
                    
                    <div style={{ marginBottom: '16px' }}>
                      <strong style={{ color: '#2f855a' }}>Skills Covered:</strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
                        {project.skills_covered?.map((skill, sidx) => (
                          <span key={sidx} style={{
                            background: '#f0fff4',
                            color: '#22543d',
                            padding: '6px 12px',
                            borderRadius: '16px',
                            fontSize: '13px',
                            fontWeight: '600',
                            border: '1px solid #9ae6b4'
                          }}>
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>

                    <p style={{ color: '#2d3748', marginBottom: '16px', lineHeight: '1.6' }}>
                      {project.project_idea}
                    </p>

                    <div style={{ marginBottom: '16px' }}>
                      <strong style={{ color: '#2f855a' }}>Learning Outcomes:</strong>
                      <ul style={{ paddingLeft: '20px', marginTop: '8px', color: '#2d3748' }}>
                        {project.learning_outcomes?.map((outcome, oidx) => (
                          <li key={oidx} style={{ marginBottom: '4px' }}>{outcome}</li>
                        ))}
                      </ul>
                    </div>

                    {project.resources && (
                      <div style={{ 
                        background: 'white',
                        padding: '16px',
                        borderRadius: '8px',
                        marginBottom: '16px'
                      }}>
                        <strong style={{ color: '#2f855a' }}>Resources:</strong>
                        <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          {project.resources.dataset && (
                            <div>
                              <span style={{ color: '#718096', fontSize: '14px' }}>Dataset: </span>
                              <a href={project.resources.dataset} target="_blank" rel="noopener noreferrer" style={{ color: '#667eea', textDecoration: 'underline' }}>
                                {project.resources.dataset}
                              </a>
                            </div>
                          )}
                          {project.resources.reference_repo && (
                            <div>
                              <span style={{ color: '#718096', fontSize: '14px' }}>Reference: </span>
                              <a href={project.resources.reference_repo} target="_blank" rel="noopener noreferrer" style={{ color: '#667eea', textDecoration: 'underline' }}>
                                {project.resources.reference_repo}
                              </a>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    <div style={{ 
                      background: '#fff5f5',
                      padding: '16px',
                      borderRadius: '8px',
                      border: '2px solid #fc8181'
                    }}>
                      <strong style={{ color: '#c53030', marginBottom: '12px', display: 'block' }}>
                        📝 Ready-to-Use Resume Bullets:
                      </strong>
                      {project.resume_bullets?.map((bullet, bidx) => (
                        <div key={bidx} style={{
                          background: 'white',
                          padding: '12px',
                          borderRadius: '6px',
                          marginBottom: '8px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          gap: '12px'
                        }}>
                          <span style={{ color: '#2d3748', flex: 1 }}>• {bullet}</span>
                          <button
                            onClick={() => copyToClipboard(bullet)}
                            style={{
                              padding: '8px 16px',
                              background: '#667eea',
                              color: 'white',
                              border: 'none',
                              borderRadius: '6px',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                              fontSize: '14px',
                              fontWeight: '600'
                            }}
                          >
                            <Copy size={14} />
                            Copy
                          </button>
                        </div>
                      ))}
                    </div>

                    <div style={{ marginTop: '16px', display: 'flex', gap: '16px', fontSize: '14px', color: '#718096' }}>
                      <span>⏱️ Time: <strong>{project.estimated_time}</strong></span>
                      <span>📊 Difficulty: <strong>{project.difficulty}</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Company-Specific Advice */}
          {analysis.company_specific_advice && analysis.company_specific_advice.length > 0 && (
            <div className="card">
              <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Building size={28} color="#667eea" />
                Company-Specific Advice
              </h2>
              <div style={{ display: 'grid', gap: '16px' }}>
                {analysis.company_specific_advice.map((advice, idx) => (
                  <div key={idx} style={{
                    padding: '20px',
                    background: '#edf2f7',
                    borderRadius: '12px',
                    borderLeft: '4px solid #667eea'
                  }}>
                    <h3 style={{ color: '#667eea', marginBottom: '12px', fontSize: '18px', fontWeight: '700' }}>
                      {advice.company_type}
                    </h3>
                    <div style={{ marginBottom: '12px' }}>
                      <strong style={{ color: '#2d3748' }}>What they look for:</strong>
                      <p style={{ color: '#4a5568', marginTop: '4px' }}>{advice.what_they_look_for}</p>
                    </div>
                    <div>
                      <strong style={{ color: '#2d3748' }}>How to stand out:</strong>
                      <p style={{ color: '#4a5568', marginTop: '4px' }}>{advice.how_to_stand_out}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ATS Optimization */}
          {analysis.ats_optimization && (
            <div className="card">
              <h2 style={{ marginBottom: '20px' }}>📈 ATS Optimization</h2>
              <div style={{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                padding: '24px',
                borderRadius: '12px',
                marginBottom: '20px'
              }}>
                <div style={{ fontSize: '48px', fontWeight: '800', marginBottom: '8px' }}>
                  {analysis.ats_optimization.score}/100
                </div>
                <div style={{ fontSize: '16px', opacity: 0.9' }}>
                  ATS Compatibility Score
                </div>
              </div>

              {analysis.ats_optimization.missing_keywords && analysis.ats_optimization.missing_keywords.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                  <strong style={{ color: '#2d3748' }}>Missing Keywords:</strong>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
                    {analysis.ats_optimization.missing_keywords.map((keyword, idx) => (
                      <span key={idx} style={{
                        background: '#fff5f5',
                        color: '#c05621',
                        padding: '6px 12px',
                        borderRadius: '16px',
                        fontSize: '13px',
                        fontWeight: '600'
                      }}>
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {analysis.ats_optimization.suggestions && analysis.ats_optimization.suggestions.length > 0 && (
                <div>
                  <strong style={{ color: '#2d3748' }}>Suggestions:</strong>
                  <ul style={{ paddingLeft: '20px', marginTop: '8px', color: '#4a5568' }}>
                    {analysis.ats_optimization.suggestions.map((suggestion, idx) => (
                      <li key={idx} style={{ marginBottom: '8px' }}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div style={{ textAlign: 'center', marginTop: '32px' }}>
            <button
              onClick={() => {
                setCurrentStep(1)
                setAnalysis(null)
                setFile(null)
                setIntentId(null)
                setCareerIntent({
                  desired_role: '',
                  experience_level: '0-2 years',
                  target_companies: [],
                  preferred_industries: []
                })
              }}
              className="btn btn-primary"
              style={{ padding: '14px 32px', fontSize: '16px' }}
            >
              Analyze Another Resume
            </button>
          </div>
        </>
      )}
    </div>
  )
}

export default ContextAwareResume
