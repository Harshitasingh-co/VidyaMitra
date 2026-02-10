import { Link } from 'react-router-dom'
import { FileText, MessageSquare, TrendingUp, Bot, Sparkles, Briefcase } from 'lucide-react'
import './Dashboard.css'

function Dashboard() {
  const modules = [
    {
      title: 'AI Resume Analyzer',
      description: 'Upload your resume for AI-powered evaluation and skill gap identification',
      icon: FileText,
      link: '/resume',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      iconColor: '#667eea'
    },
    {
      title: 'AI Interview Simulator',
      description: 'Practice with AI-driven interview simulator and get personalized feedback',
      icon: MessageSquare,
      link: '/interview',
      gradient: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
      iconColor: '#48bb78'
    },
    {
      title: 'AI Career Roadmap',
      description: 'Get personalized career recommendations and upskilling roadmap',
      icon: TrendingUp,
      link: '/career',
      gradient: 'linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)',
      iconColor: '#ed8936'
    },
    {
      title: 'Internship Discovery',
      description: 'Find genuine, skill-aligned internships with fraud detection and personalized recommendations',
      icon: Briefcase,
      link: '/internship-profile',
      gradient: 'linear-gradient(135deg, #3182ce 0%, #2c5282 100%)',
      iconColor: '#3182ce'
    },
    {
      title: 'AI Mentor',
      description: 'Chat with your personal AI guide for learning and career guidance',
      icon: Bot,
      link: '/ai-mentor',
      gradient: 'linear-gradient(135deg, #9f7aea 0%, #805ad5 100%)',
      iconColor: '#9f7aea'
    }
  ]

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1 className="dashboard-title">
          <Sparkles className="title-icon" size={36} />
          Welcome to VidyaMitra
        </h1>
        <p className="dashboard-subtitle">
          Your AI-powered companion for career growth and learning
        </p>
      </div>
      
      <div className="modules-grid">
        {modules.map((module) => {
          const Icon = module.icon
          return (
            <Link 
              key={module.title} 
              to={module.link} 
              className="module-card-link"
            >
              <div className="module-card">
                <div className="module-icon-wrapper" style={{ background: module.gradient }}>
                  <Icon size={32} color="white" strokeWidth={2.5} />
                </div>
                <div className="module-content">
                  <h3 className="module-title">{module.title}</h3>
                  <p className="module-description">{module.description}</p>
                </div>
                <div className="module-arrow">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      <div className="dashboard-footer">
        <p>Powered by AI • Built for your success</p>
      </div>
    </div>
  )
}

export default Dashboard
