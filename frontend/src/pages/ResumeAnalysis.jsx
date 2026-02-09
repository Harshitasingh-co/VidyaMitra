import { useState } from 'react'
import { resumeAPI } from '../services/api'
import { Upload, CheckCircle, AlertCircle, FileText, Loader } from 'lucide-react'

function ResumeAnalysis() {
  const [file, setFile] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    setFile(selectedFile)
    setError(null)
  }

  const handleAnalyze = async () => {
    if (!file) return
    
    setLoading(true)
    setError(null)
    try {
      const uploadRes = await resumeAPI.upload(file)
      // Backend returns { success: true, data: {...}, message: "..." }
      const uploadData = uploadRes.data.data || uploadRes.data
      const analysisRes = await resumeAPI.analyze({
        resume_text: uploadData.full_text,
        target_role: "General"
      })
      // Backend returns { success: true, data: {...}, message: "..." }
      const analysisData = analysisRes.data.data || analysisRes.data
      setAnalysis(analysisData)
    } catch (error) {
      console.error('Analysis failed:', error)
      setError(error.response?.data?.detail || 'Failed to analyze resume. Please try again.')
    }
    setLoading(false)
  }

  return (
    <div className="container">
      <h1 style={{ color: 'white', marginBottom: '8px', fontSize: '36px', fontWeight: '800' }}>
        AI Resume Analyzer
      </h1>
      <p style={{ color: 'rgba(255,255,255,0.9)', marginBottom: '32px', fontSize: '16px' }}>
        Get AI-powered insights and skill gap analysis
      </p>
      
      <div className="card" style={{ marginBottom: '24px' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
          <FileText size={28} color="#667eea" />
          Upload Your Resume
        </h2>
        
        <div style={{ 
          border: '2px dashed #cbd5e0', 
          borderRadius: '12px', 
          padding: '40px', 
          textAlign: 'center',
          background: '#f7fafc',
          marginBottom: '20px',
          transition: 'all 0.3s ease'
        }}
        onDragOver={(e) => {
          e.preventDefault()
          e.currentTarget.style.borderColor = '#667eea'
          e.currentTarget.style.background = '#edf2f7'
        }}
        onDragLeave={(e) => {
          e.currentTarget.style.borderColor = '#cbd5e0'
          e.currentTarget.style.background = '#f7fafc'
        }}
        onDrop={(e) => {
          e.preventDefault()
          e.currentTarget.style.borderColor = '#cbd5e0'
          e.currentTarget.style.background = '#f7fafc'
          const droppedFile = e.dataTransfer.files[0]
          if (droppedFile) {
            setFile(droppedFile)
            setError(null)
          }
        }}
        >
          <Upload size={48} color="#cbd5e0" style={{ marginBottom: '16px' }} />
          <p style={{ color: '#4a5568', marginBottom: '12px', fontSize: '16px', fontWeight: '500' }}>
            Drag and drop your resume here, or click to browse
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
            fontWeight: '500',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#667eea'
            e.currentTarget.style.color = '#667eea'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#e2e8f0'
            e.currentTarget.style.color = '#4a5568'
          }}
          >
            Choose File
          </label>
          <p style={{ color: '#a0aec0', marginTop: '12px', fontSize: '14px' }}>
            Supported formats: PDF, DOC, DOCX, TXT
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
          onClick={handleAnalyze} 
          className="btn btn-primary"
          disabled={!file || loading}
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
              Analyzing Your Resume...
            </>
          ) : (
            <>
              <Upload size={20} />
              Analyze Resume
            </>
          )}
        </button>
      </div>

      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div className="spinner" style={{ margin: '0 auto 20px' }}></div>
          <h3 style={{ color: '#4a5568', marginBottom: '8px' }}>Analyzing your resume...</h3>
          <p style={{ color: '#a0aec0' }}>Our AI is reviewing your skills and experience</p>
        </div>
      )}

      {!loading && !analysis && !file && (
        <div className="empty-state">
          <div className="empty-state-icon">📄</div>
          <h3>No resume uploaded yet</h3>
          <p>Upload your resume to get started with AI-powered analysis</p>
        </div>
      )}

      {analysis && !loading && (
        <>
          <div className="card" style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            marginBottom: '24px'
          }}>
            <h2 style={{ color: 'white', marginBottom: '16px' }}>Analysis Summary</h2>
            <p style={{ fontSize: '18px', marginBottom: '24px', lineHeight: '1.6' }}>{analysis.summary}</p>
            <div style={{ 
              background: 'rgba(255, 255, 255, 0.2)', 
              backdropFilter: 'blur(10px)',
              padding: '24px', 
              borderRadius: '12px',
              fontSize: '32px',
              fontWeight: '800',
              textAlign: 'center'
            }}>
              ATS Score: {analysis.ats_score}/100
            </div>
          </div>

          <div className="card">
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
              <CheckCircle color="#48bb78" size={28} />
              Strengths
            </h2>
            <ul style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
              {analysis.strengths?.map((strength, idx) => (
                <li key={idx} style={{ 
                  marginBottom: '12px', 
                  color: '#2d3748',
                  fontSize: '16px'
                }}>
                  {strength}
                </li>
              ))}
            </ul>
          </div>

          {analysis.weaknesses && analysis.weaknesses.length > 0 && (
            <div className="card">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <AlertCircle color="#ed8936" size={28} />
                Areas for Improvement
              </h2>
              <ul style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
                {analysis.weaknesses.map((weakness, idx) => (
                  <li key={idx} style={{ 
                    marginBottom: '12px', 
                    color: '#2d3748',
                    fontSize: '16px'
                  }}>
                    {weakness}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysis.missing_skills && analysis.missing_skills.length > 0 && (
            <div className="card">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <AlertCircle color="#ed8936" size={28} />
                Missing Skills
              </h2>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                {analysis.missing_skills.map((skill, idx) => (
                  <span key={idx} style={{ 
                    background: 'linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%)', 
                    padding: '10px 16px', 
                    borderRadius: '20px', 
                    color: '#c05621',
                    fontSize: '14px',
                    fontWeight: '600',
                    border: '1px solid #ed8936'
                  }}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {analysis.recommendations && analysis.recommendations.length > 0 && (
            <div className="card">
              <h2 style={{ marginBottom: '20px' }}>📚 Recommendations</h2>
              <div style={{ display: 'grid', gap: '16px' }}>
                {analysis.recommendations.map((rec, idx) => (
                  <div key={idx} style={{ 
                    background: 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)', 
                    padding: '20px', 
                    borderRadius: '12px',
                    border: '1px solid #e2e8f0',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)'
                    e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.1)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)'
                    e.currentTarget.style.boxShadow = 'none'
                  }}
                  >
                    <div style={{ 
                      display: 'inline-block',
                      background: rec.priority === 'high' ? '#fed7d7' : '#bee3f8',
                      color: rec.priority === 'high' ? '#c05621' : '#2c5282',
                      padding: '4px 12px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: '700',
                      marginBottom: '12px',
                      textTransform: 'uppercase'
                    }}>
                      {rec.priority} Priority
                    </div>
                    <h3 style={{ color: '#667eea', marginBottom: '8px', fontSize: '18px', fontWeight: '700' }}>
                      {rec.category}
                    </h3>
                    <p style={{ color: '#4a5568', lineHeight: '1.6' }}>
                      {rec.suggestion}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default ResumeAnalysis
