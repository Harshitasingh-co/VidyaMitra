import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Format error response consistently
    if (error.response) {
      // Server responded with error status
      const errorData = error.response.data
      
      // Handle different error formats from backend
      let code = 'UNKNOWN_ERROR'
      let message = error.message
      let details = {}
      
      if (errorData?.detail) {
        // FastAPI format: { detail: { code, message, details } } or { detail: "string" }
        if (typeof errorData.detail === 'string') {
          message = errorData.detail
        } else {
          code = errorData.detail.code || code
          message = errorData.detail.message || message
          details = errorData.detail.details || details
        }
      } else if (errorData?.error) {
        // Custom format: { error: { code, message, details } }
        code = errorData.error.code || code
        message = errorData.error.message || message
        details = errorData.error.details || details
      } else if (errorData?.message) {
        message = errorData.message
      }
      
      return Promise.reject({
        status: error.response.status,
        code: code,
        message: message,
        details: details
      })
    } else if (error.request) {
      // Request made but no response received
      return Promise.reject({
        status: 503,
        code: 'NETWORK_ERROR',
        message: 'Unable to reach the server. Please check your connection.',
        details: {}
      })
    } else {
      // Error in request setup
      return Promise.reject({
        status: 500,
        code: 'REQUEST_ERROR',
        message: error.message,
        details: {}
      })
    }
  }
)

// Internship Profile APIs
export const profileAPI = {
  /**
   * Create or update student profile
   * @param {Object} profileData - Profile information
   * @param {number} profileData.graduation_year - Year of graduation
   * @param {number} profileData.current_semester - Current semester (1-8)
   * @param {string} profileData.degree - Degree type (B.Tech, M.Tech, etc.)
   * @param {string} profileData.branch - Branch/specialization
   * @param {string[]} profileData.skills - List of skills
   * @param {string[]} profileData.preferred_roles - Preferred job roles
   * @param {string} profileData.internship_type - Remote/On-site/Hybrid
   * @param {string} profileData.compensation_preference - Paid/Unpaid/Any
   * @param {string[]} [profileData.target_companies] - Optional target companies
   * @param {string} [profileData.resume_url] - Optional resume URL
   * @returns {Promise} Profile creation/update response
   */
  createOrUpdate: (profileData) => api.post('/internships/profile', profileData),

  /**
   * Get current user's profile
   * @returns {Promise} User profile data
   */
  get: () => api.get('/internships/profile')
}

// Internship Search APIs
export const searchAPI = {
  /**
   * Search internships with filters
   * @param {Object} filters - Search filters
   * @param {string[]} [filters.skills] - Filter by skills
   * @param {string[]} [filters.roles] - Filter by roles
   * @param {string} [filters.internship_type] - Filter by type (Remote/On-site/Hybrid)
   * @param {string} [filters.compensation] - Filter by compensation (Paid/Unpaid)
   * @param {string} [filters.location] - Filter by location
   * @param {number} [filters.min_match_percentage] - Minimum skill match percentage
   * @returns {Promise} List of matching internships with match scores
   */
  search: (filters = {}) => api.post('/internships/search', filters),

  /**
   * Get detailed internship information
   * @param {string} internshipId - Internship ID
   * @returns {Promise} Detailed internship data
   */
  getDetails: (internshipId) => api.get(`/internships/${internshipId}`)
}

// Internship Calendar APIs
export const calendarAPI = {
  /**
   * Get personalized internship calendar based on user's semester
   * @returns {Promise} Calendar with application windows and deadlines
   */
  get: () => api.get('/internships/calendar')
}

// Verification APIs
export const verificationAPI = {
  /**
   * Get verification status and fraud analysis for an internship
   * @param {string} internshipId - Internship ID
   * @returns {Promise} Verification result with trust score and red flags
   */
  verify: (internshipId) => api.get(`/internships/${internshipId}/verify`)
}

// Skill Matching APIs
export const matchingAPI = {
  /**
   * Calculate skill match percentage and identify gaps
   * @param {string} internshipId - Internship ID
   * @returns {Promise} Match percentage, matching skills, missing skills, and learning path
   */
  calculateMatch: (internshipId) => api.post(`/internships/${internshipId}/match`)
}

// Career Guidance APIs
export const guidanceAPI = {
  /**
   * Get AI-powered career guidance for an internship
   * @param {string} internshipId - Internship ID
   * @returns {Promise} Personalized career guidance
   */
  get: (internshipId) => api.get(`/internships/${internshipId}/guidance`)
}

// Readiness Score APIs
export const readinessAPI = {
  /**
   * Calculate readiness score and get recommendations
   * @param {string} internshipId - Internship ID
   * @returns {Promise} Readiness score with component breakdown and improvement actions
   */
  calculate: (internshipId) => api.get(`/internships/${internshipId}/readiness`)
}

// Alert APIs
export const alertAPI = {
  /**
   * Get personalized alerts and notifications
   * @param {number} [limit=20] - Maximum number of alerts to retrieve
   * @returns {Promise} List of user alerts
   */
  getAll: (limit = 20) => api.get(`/internships/alerts?limit=${limit}`),

  /**
   * Mark an alert as read
   * @param {string} alertId - Alert ID
   * @returns {Promise} Update confirmation
   */
  markAsRead: (alertId) => api.patch(`/internships/alerts/${alertId}/read`)
}

// Scam Reporting APIs
export const reportAPI = {
  /**
   * Report a suspicious internship listing
   * @param {Object} reportData - Report information
   * @param {string} reportData.internship_id - ID of the internship to report
   * @param {string} reportData.reason - Reason for reporting
   * @param {string} [reportData.details] - Optional additional details
   * @returns {Promise} Report submission confirmation
   */
  reportScam: (reportData) => api.post('/internships/report-scam', reportData)
}

// Combined export for convenience
export const internshipAPI = {
  profile: profileAPI,
  search: searchAPI,
  calendar: calendarAPI,
  verification: verificationAPI,
  matching: matchingAPI,
  guidance: guidanceAPI,
  readiness: readinessAPI,
  alerts: alertAPI,
  report: reportAPI
}

export default internshipAPI
