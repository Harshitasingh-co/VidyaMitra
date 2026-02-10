import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { User, TrendingUp, LogOut, Menu, X } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import ResumeAnalysis from './pages/ResumeAnalysis'
import ContextAwareResume from './pages/ContextAwareResume'
import MockInterview from './pages/MockInterview'
import CareerPath from './pages/CareerPath'
import AIMentor from './pages/AIMentor'
import InternshipProfile from './pages/InternshipProfile'
import Login from './pages/Login'
import Register from './pages/Register'
import './App.css'

function Navbar({ setIsAuthenticated }) {
  const [showDropdown, setShowDropdown] = useState(false)
  const [showMobileMenu, setShowMobileMenu] = useState(false)
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
    setShowDropdown(false)
  }

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-brand">VidyaMitra</Link>
        
        {/* Desktop Navigation */}
        <div className="nav-links">
          <Link to="/" className={isActive('/') ? 'active' : ''}>Dashboard</Link>
          <Link to="/resume" className={isActive('/resume') ? 'active' : ''}>Resume Analysis</Link>
          <Link to="/interview" className={isActive('/interview') ? 'active' : ''}>Mock Interview</Link>
          <Link to="/career" className={isActive('/career') ? 'active' : ''}>Career Path</Link>
          
          {/* Profile Dropdown */}
          <div className="profile-dropdown">
            <div 
              className="profile-avatar"
              onClick={() => setShowDropdown(!showDropdown)}
            >
              <User size={20} />
            </div>
            <div className={`dropdown-menu ${showDropdown ? 'show' : ''}`}>
              <button className="dropdown-item">
                <User size={18} />
                Profile
              </button>
              <button className="dropdown-item">
                <TrendingUp size={18} />
                Progress
              </button>
              <div className="dropdown-divider"></div>
              <button className="dropdown-item danger" onClick={handleLogout}>
                <LogOut size={18} />
                Logout
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu Button */}
        <button 
          className="mobile-menu-btn"
          onClick={() => setShowMobileMenu(!showMobileMenu)}
        >
          {showMobileMenu ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      <div className={`mobile-menu ${showMobileMenu ? 'show' : ''}`}>
        <Link 
          to="/" 
          className={isActive('/') ? 'active' : ''}
          onClick={() => setShowMobileMenu(false)}
        >
          Dashboard
        </Link>
        <Link 
          to="/resume" 
          className={isActive('/resume') ? 'active' : ''}
          onClick={() => setShowMobileMenu(false)}
        >
          Resume Analysis
        </Link>
        <Link 
          to="/interview" 
          className={isActive('/interview') ? 'active' : ''}
          onClick={() => setShowMobileMenu(false)}
        >
          Mock Interview
        </Link>
        <Link 
          to="/career" 
          className={isActive('/career') ? 'active' : ''}
          onClick={() => setShowMobileMenu(false)}
        >
          Career Path
        </Link>
        <div className="dropdown-divider"></div>
        <button className="dropdown-item" onClick={handleLogout}>
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </nav>
  )
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(true) // Set to true for demo mode

  return (
    <Router>
      <div className="app">
        {isAuthenticated && <Navbar setIsAuthenticated={setIsAuthenticated} />}
        
        <Routes>
          <Route path="/login" element={<Login setAuth={setIsAuthenticated} />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={isAuthenticated ? <Dashboard /> : <Login setAuth={setIsAuthenticated} />} />
          <Route path="/resume" element={<ContextAwareResume />} />
          <Route path="/resume-old" element={<ResumeAnalysis />} />
          <Route path="/interview" element={<MockInterview />} />
          <Route path="/career" element={<CareerPath />} />
          <Route path="/ai-mentor" element={<AIMentor />} />
          <Route path="/internship-profile" element={<InternshipProfile />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
