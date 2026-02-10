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

// Auth APIs
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', new URLSearchParams(data), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  }),
  getCurrentUser: () => api.get('/auth/me')
}

// Resume APIs
export const resumeAPI = {
  analyze: (data) => api.post('/ai/resume/analyze', data),
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/ai/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// Interview APIs
export const interviewAPI = {
  generateQuestions: (data) => api.post('/ai/interview/start', data),
  evaluate: (data) => api.post('/ai/interview/answer', data),
  feedback: (data) => api.post('/ai/interview/feedback', data)
}

// Career APIs
export const careerAPI = {
  recommend: (data) => api.post('/ai/career/roadmap', data),
  getSkills: (role) => api.get(`/ai/career/skills/${role}`)
}

// Resource APIs
export const resourceAPI = {
  searchCourses: (query) => api.get(`/resources/courses?query=${query}`),
  searchVideos: (topic) => api.get(`/resources/videos?topic=${topic}`),
  searchImages: (query) => api.get(`/resources/images?query=${query}`),
  getNews: (topic) => api.get(`/resources/news?topic=${topic}`)
}

export default api
