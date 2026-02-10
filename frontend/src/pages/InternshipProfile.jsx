import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, GraduationCap, BookOpen, Code, Briefcase, MapPin, DollarSign, Building, Upload, X, Plus, Check } from 'lucide-react'
import { internshipAPI } from '../services/internshipApi'
import './InternshipProfile.css'

function InternshipProfile() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [skillInput, setSkillInput] = useState('')
  const [roleInput, setRoleInput] = useState('')
  const [companyInput, setCompanyInput] = useState('')
  
  const [formData, setFormData] = useState({
    graduation_year: new Date().getFullYear() + 2,
    current_semester: 1,
    degree: '',
    branch: '',
    skills: [],
    preferred_roles: [],
    internship_type: 'Remote',
    compensation_preference: 'Paid',
    target_companies: [],
    resume_url: ''
  })

  const [validationErrors, setValidationErrors] = useState({})

  // Predefined options
  const degrees = ['B.Tech', 'M.Tech', 'BCA', 'MCA', 'B.Sc', 'M.Sc', 'MBA', 'Other']
  const branches = [
    'Computer Science',
    'Information Technology',
    'Electronics and Communication',
    'Electrical Engineering',
    'Mechanical Engineering',
    'Civil Engineering',
    'Data Science',
    'Artificial Intelligence',
    'Other'
  ]
  const internshipTypes = ['Remote', 'On-site', 'Hybrid']
  const compensationPreferences = ['Paid', 'Unpaid', 'Any']
  
  // Common skills for autocomplete
  const commonSkills = [
    'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'Django', 'Flask',
    'SQL', 'MongoDB', 'PostgreSQL', 'AWS', 'Docker', 'Kubernetes', 'Git',
    'Machine Learning', 'Data Analysis', 'REST API', 'HTML', 'CSS', 'TypeScript',
    'Angular', 'Vue.js', 'Spring Boot', 'Express.js', 'TensorFlow', 'PyTorch'
  ]

  // Common roles for autocomplete
  const commonRoles = [
    'Software Engineer',
    'Frontend Developer',
    'Backend Developer',
    'Full Stack Developer',
    'Data Analyst',
    'Data Scientist',
    'Machine Learning Engineer',
    'DevOps Engineer',
    'UI/UX Designer',
    'Product Manager',
    'Business Analyst',
    'QA Engineer'
  ]

  // Load existing profile
  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      setLoading(true)
      setError('') // Clear any previous errors
      const response = await internshipAPI.profile.get()
      if (response.data && response.data.success) {
        setFormData(response.data.data)
      }
    } catch (err) {
      // Profile doesn't exist yet (404), that's okay - user will create one
      if (err.status === 404) {
        console.log('No profile found - user will create a new one')
      } else {
        console.error('Error loading profile:', err)
        // Only show error for non-404 errors
        if (err.status !== 404) {
          setError(`Failed to load profile: ${err.message || 'Please try again'}`)
        }
      }
    } finally {
      setLoading(false)
    }
  }

  const validateForm = () => {
    const errors = {}

    // Graduation year validation
    const currentYear = new Date().getFullYear()
    if (formData.graduation_year < currentYear || formData.graduation_year > currentYear + 10) {
      errors.graduation_year = `Graduation year must be between ${currentYear} and ${currentYear + 10}`
    }

    // Semester validation
    if (formData.current_semester < 1 || formData.current_semester > 8) {
      errors.current_semester = 'Semester must be between 1 and 8'
    }

    // Required fields
    if (!formData.degree) {
      errors.degree = 'Degree is required'
    }
    if (!formData.branch) {
      errors.branch = 'Branch is required'
    }
    if (formData.skills.length === 0) {
      errors.skills = 'At least one skill is required'
    }
    if (formData.preferred_roles.length === 0) {
      errors.preferred_roles = 'At least one preferred role is required'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      setError('Please fix the validation errors')
      window.scrollTo({ top: 0, behavior: 'smooth' })
      return
    }

    try {
      setSaving(true)
      setError('')
      setSuccess('')
      
      const response = await internshipAPI.profile.createOrUpdate(formData)
      
      if (response.data && response.data.success) {
        setSuccess('Profile saved successfully! You can now explore internship opportunities.')
        window.scrollTo({ top: 0, behavior: 'smooth' })
        // Navigate to dashboard after 2 seconds
        setTimeout(() => {
          navigate('/dashboard')
        }, 2000)
      }
    } catch (err) {
      const errorMessage = err.message || 'Failed to save profile. Please try again.'
      setError(errorMessage)
      window.scrollTo({ top: 0, behavior: 'smooth' })
      console.error('Error saving profile:', err)
    } finally {
      setSaving(false)
    }
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const addSkill = (skill) => {
    const trimmedSkill = skill.trim()
    if (trimmedSkill && !formData.skills.includes(trimmedSkill)) {
      handleInputChange('skills', [...formData.skills, trimmedSkill])
      setSkillInput('')
    }
  }

  const removeSkill = (skillToRemove) => {
    handleInputChange('skills', formData.skills.filter(s => s !== skillToRemove))
  }

  const addRole = (role) => {
    const trimmedRole = role.trim()
    if (trimmedRole && !formData.preferred_roles.includes(trimmedRole)) {
      handleInputChange('preferred_roles', [...formData.preferred_roles, trimmedRole])
      setRoleInput('')
    }
  }

  const removeRole = (roleToRemove) => {
    handleInputChange('preferred_roles', formData.preferred_roles.filter(r => r !== roleToRemove))
  }

  const addCompany = (company) => {
    const trimmedCompany = company.trim()
    if (trimmedCompany && !formData.target_companies.includes(trimmedCompany)) {
      handleInputChange('target_companies', [...formData.target_companies, trimmedCompany])
      setCompanyInput('')
    }
  }

  const removeCompany = (companyToRemove) => {
    handleInputChange('target_companies', formData.target_companies.filter(c => c !== companyToRemove))
  }

  const handleResumeUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a PDF or Word document')
      return
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB')
      return
    }

    // TODO: Implement actual file upload to server
    // For now, just store the file name
    handleInputChange('resume_url', file.name)
    setSuccess('Resume uploaded successfully!')
    setTimeout(() => setSuccess(''), 3000)
  }

  const filteredSkills = commonSkills.filter(skill => 
    skill.toLowerCase().includes(skillInput.toLowerCase()) &&
    !formData.skills.includes(skill)
  )

  const filteredRoles = commonRoles.filter(role => 
    role.toLowerCase().includes(roleInput.toLowerCase()) &&
    !formData.preferred_roles.includes(role)
  )

  if (loading) {
    return (
      <div className="profile-container">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-header-content">
          <div className="profile-icon-wrapper">
            <User size={32} />
          </div>
          <div>
            <h1 className="profile-title">Internship Profile</h1>
            <p className="profile-subtitle">
              Complete your profile to get personalized internship recommendations
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <X size={20} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <Check size={20} />
          <span>{success}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="profile-form">
        {/* Academic Information */}
        <div className="form-section">
          <div className="section-header">
            <GraduationCap size={24} />
            <h2>Academic Information</h2>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="graduation_year">
                Graduation Year <span className="required">*</span>
              </label>
              <input
                id="graduation_year"
                type="number"
                className={`input ${validationErrors.graduation_year ? 'input-error' : ''}`}
                value={formData.graduation_year}
                onChange={(e) => handleInputChange('graduation_year', parseInt(e.target.value))}
                min={new Date().getFullYear()}
                max={new Date().getFullYear() + 10}
                required
              />
              {validationErrors.graduation_year && (
                <span className="error-text">{validationErrors.graduation_year}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="current_semester">
                Current Semester <span className="required">*</span>
              </label>
              <select
                id="current_semester"
                className={`input ${validationErrors.current_semester ? 'input-error' : ''}`}
                value={formData.current_semester}
                onChange={(e) => handleInputChange('current_semester', parseInt(e.target.value))}
                required
              >
                {[1, 2, 3, 4, 5, 6, 7, 8].map(sem => (
                  <option key={sem} value={sem}>Semester {sem}</option>
                ))}
              </select>
              {validationErrors.current_semester && (
                <span className="error-text">{validationErrors.current_semester}</span>
              )}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="degree">
                Degree <span className="required">*</span>
              </label>
              <select
                id="degree"
                className={`input ${validationErrors.degree ? 'input-error' : ''}`}
                value={formData.degree}
                onChange={(e) => handleInputChange('degree', e.target.value)}
                required
              >
                <option value="">Select Degree</option>
                {degrees.map(degree => (
                  <option key={degree} value={degree}>{degree}</option>
                ))}
              </select>
              {validationErrors.degree && (
                <span className="error-text">{validationErrors.degree}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="branch">
                Branch/Specialization <span className="required">*</span>
              </label>
              <select
                id="branch"
                className={`input ${validationErrors.branch ? 'input-error' : ''}`}
                value={formData.branch}
                onChange={(e) => handleInputChange('branch', e.target.value)}
                required
              >
                <option value="">Select Branch</option>
                {branches.map(branch => (
                  <option key={branch} value={branch}>{branch}</option>
                ))}
              </select>
              {validationErrors.branch && (
                <span className="error-text">{validationErrors.branch}</span>
              )}
            </div>
          </div>
        </div>

        {/* Skills */}
        <div className="form-section">
          <div className="section-header">
            <Code size={24} />
            <h2>Skills</h2>
          </div>

          <div className="form-group">
            <label htmlFor="skills">
              Your Skills <span className="required">*</span>
            </label>
            <div className="tag-input-wrapper">
              <input
                id="skills"
                type="text"
                className={`input ${validationErrors.skills ? 'input-error' : ''}`}
                placeholder="Type a skill and press Enter"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addSkill(skillInput)
                  }
                }}
              />
              <button
                type="button"
                className="add-button"
                onClick={() => addSkill(skillInput)}
                disabled={!skillInput.trim()}
              >
                <Plus size={20} />
              </button>
            </div>
            
            {/* Autocomplete suggestions */}
            {skillInput && filteredSkills.length > 0 && (
              <div className="autocomplete-dropdown">
                {filteredSkills.slice(0, 5).map(skill => (
                  <div
                    key={skill}
                    className="autocomplete-item"
                    onClick={() => addSkill(skill)}
                  >
                    {skill}
                  </div>
                ))}
              </div>
            )}

            {/* Display selected skills */}
            <div className="tags-container">
              {formData.skills.map(skill => (
                <div key={skill} className="tag">
                  <span>{skill}</span>
                  <button
                    type="button"
                    className="tag-remove"
                    onClick={() => removeSkill(skill)}
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
            {validationErrors.skills && (
              <span className="error-text">{validationErrors.skills}</span>
            )}
          </div>
        </div>

        {/* Preferred Roles */}
        <div className="form-section">
          <div className="section-header">
            <Briefcase size={24} />
            <h2>Preferred Roles</h2>
          </div>

          <div className="form-group">
            <label htmlFor="roles">
              Roles You're Interested In <span className="required">*</span>
            </label>
            <div className="tag-input-wrapper">
              <input
                id="roles"
                type="text"
                className={`input ${validationErrors.preferred_roles ? 'input-error' : ''}`}
                placeholder="Type a role and press Enter"
                value={roleInput}
                onChange={(e) => setRoleInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addRole(roleInput)
                  }
                }}
              />
              <button
                type="button"
                className="add-button"
                onClick={() => addRole(roleInput)}
                disabled={!roleInput.trim()}
              >
                <Plus size={20} />
              </button>
            </div>

            {/* Autocomplete suggestions */}
            {roleInput && filteredRoles.length > 0 && (
              <div className="autocomplete-dropdown">
                {filteredRoles.slice(0, 5).map(role => (
                  <div
                    key={role}
                    className="autocomplete-item"
                    onClick={() => addRole(role)}
                  >
                    {role}
                  </div>
                ))}
              </div>
            )}

            {/* Display selected roles */}
            <div className="tags-container">
              {formData.preferred_roles.map(role => (
                <div key={role} className="tag">
                  <span>{role}</span>
                  <button
                    type="button"
                    className="tag-remove"
                    onClick={() => removeRole(role)}
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
            {validationErrors.preferred_roles && (
              <span className="error-text">{validationErrors.preferred_roles}</span>
            )}
          </div>
        </div>

        {/* Preferences */}
        <div className="form-section">
          <div className="section-header">
            <BookOpen size={24} />
            <h2>Internship Preferences</h2>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="internship_type">
                <MapPin size={18} className="inline-icon" />
                Internship Type
              </label>
              <select
                id="internship_type"
                className="input"
                value={formData.internship_type}
                onChange={(e) => handleInputChange('internship_type', e.target.value)}
              >
                {internshipTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="compensation_preference">
                <DollarSign size={18} className="inline-icon" />
                Compensation Preference
              </label>
              <select
                id="compensation_preference"
                className="input"
                value={formData.compensation_preference}
                onChange={(e) => handleInputChange('compensation_preference', e.target.value)}
              >
                {compensationPreferences.map(pref => (
                  <option key={pref} value={pref}>{pref}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Target Companies (Optional) */}
        <div className="form-section">
          <div className="section-header">
            <Building size={24} />
            <h2>Target Companies (Optional)</h2>
          </div>

          <div className="form-group">
            <label htmlFor="companies">Companies You'd Like to Work For</label>
            <div className="tag-input-wrapper">
              <input
                id="companies"
                type="text"
                className="input"
                placeholder="Type a company name and press Enter"
                value={companyInput}
                onChange={(e) => setCompanyInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addCompany(companyInput)
                  }
                }}
              />
              <button
                type="button"
                className="add-button"
                onClick={() => addCompany(companyInput)}
                disabled={!companyInput.trim()}
              >
                <Plus size={20} />
              </button>
            </div>

            {/* Display selected companies */}
            <div className="tags-container">
              {formData.target_companies.map(company => (
                <div key={company} className="tag">
                  <span>{company}</span>
                  <button
                    type="button"
                    className="tag-remove"
                    onClick={() => removeCompany(company)}
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Resume Upload */}
        <div className="form-section">
          <div className="section-header">
            <Upload size={24} />
            <h2>Resume Upload (Optional)</h2>
          </div>

          <div className="form-group">
            <label htmlFor="resume">Upload Your Resume</label>
            <p className="help-text">
              Upload your resume to automatically extract skills (PDF or Word, max 5MB)
            </p>
            <div className="file-upload-wrapper">
              <input
                id="resume"
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleResumeUpload}
                className="file-input"
              />
              <label htmlFor="resume" className="file-upload-label">
                <Upload size={20} />
                <span>Choose File</span>
              </label>
              {formData.resume_url && (
                <span className="file-name">{formData.resume_url}</span>
              )}
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="form-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate('/')}
            disabled={saving}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default InternshipProfile
