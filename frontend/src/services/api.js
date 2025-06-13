import axios from 'axios'

class ApiService {
  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    this.http = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // Add token to requests
    this.http.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('prepcheck_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Handle responses
    this.http.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('prepcheck_token')
          localStorage.removeItem('prepcheck_user')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async login(credentials) {
    const response = await this.http.post('/api/auth/login', credentials)
    return response.data
  }

  async register(userData) {
    const response = await this.http.post('/api/auth/register', userData)
    return response.data
  }

  async getProfile() {
    const response = await this.http.get('/api/auth/profile')
    return response.data
  }

  async updateProfile(userData) {
    const response = await this.http.put('/api/auth/profile', userData)
    return response.data
  }

  // User endpoints
  async getUserDashboard() {
    const response = await this.http.get('/api/user/dashboard')
    return response.data
  }

  async getUserSubjects() {
    const response = await this.http.get('/api/user/subjects')
    return response.data
  }

  async getUserChapters(subjectId) {
    const response = await this.http.get(`/api/user/chapters/${subjectId}`)
    return response.data
  }

  async getUserQuizzes(chapterId) {
    const response = await this.http.get(`/api/user/quizzes/${chapterId}`)
    return response.data
  }

  async getUserHistory(page = 1, perPage = 20) {
    const response = await this.http.get(`/api/user/history?page=${page}&per_page=${perPage}`)
    return response.data
  }

  async exportUserData() {
    const response = await this.http.post('/api/user/export')
    return response.data
  }

  async getUserExportStatus(taskId) {
    const response = await this.http.get(`/api/user/export/${taskId}`)
    return response.data
  }

  // Quiz endpoints
  async previewQuiz(quizId) {
    const response = await this.http.get(`/api/quiz/${quizId}/preview`)
    return response.data
  }

  async startQuiz(quizId) {
    const response = await this.http.post(`/api/quiz/${quizId}/start`)
    return response.data
  }

  async saveQuizProgress(quizId, answers) {
    const response = await this.http.post(`/api/quiz/${quizId}/save`, { answers })
    return response.data
  }

  async submitQuiz(quizId, answers) {
    const response = await this.http.post(`/api/quiz/${quizId}/submit`, { answers })
    return response.data
  }

  async getQuizResults(attemptId) {
    const response = await this.http.get(`/api/quiz/attempt/${attemptId}/results`)
    return response.data
  }

  // Admin endpoints
  async getAdminDashboard() {
    const response = await this.http.get('/api/admin/dashboard')
    return response.data
  }

  // Admin - Subjects
  async getSubjects() {
    const response = await this.http.get('/api/admin/subjects')
    return response.data
  }

  async createSubject(subjectData) {
    const response = await this.http.post('/api/admin/subjects', subjectData)
    return response.data
  }

  async updateSubject(subjectId, subjectData) {
    const response = await this.http.put(`/api/admin/subjects/${subjectId}`, subjectData)
    return response.data
  }

  async deleteSubject(subjectId) {
    const response = await this.http.delete(`/api/admin/subjects/${subjectId}`)
    return response.data
  }

  // Admin - Chapters
  async getChapters(subjectId = null) {
    const url = subjectId ? `/api/admin/chapters?subject_id=${subjectId}` : '/api/admin/chapters'
    const response = await this.http.get(url)
    return response.data
  }

  async createChapter(chapterData) {
    const response = await this.http.post('/api/admin/chapters', chapterData)
    return response.data
  }

  // Admin - Quizzes
  async getQuizzes(chapterId = null) {
    const url = chapterId ? `/api/admin/quizzes?chapter_id=${chapterId}` : '/api/admin/quizzes'
    const response = await this.http.get(url)
    return response.data
  }

  async createQuiz(quizData) {
    const response = await this.http.post('/api/admin/quizzes', quizData)
    return response.data
  }

  // Admin - Questions
  async getQuizQuestions(quizId) {
    const response = await this.http.get(`/api/admin/questions/${quizId}`)
    return response.data
  }

  async createQuestion(questionData) {
    const response = await this.http.post('/api/admin/questions', questionData)
    return response.data
  }

  // Admin - Users
  async getUsers(page = 1, perPage = 20) {
    const response = await this.http.get(`/api/admin/users?page=${page}&per_page=${perPage}`)
    return response.data
  }

  // Admin - Export
  async exportAdminData(type = 'all') {
    const response = await this.http.post('/api/admin/export', { type })
    return response.data
  }

  async getAdminExportStatus(taskId) {
    const response = await this.http.get(`/api/admin/export/${taskId}`)
    return response.data
  }

  // AI endpoints
  async generateQuiz(quizData) {
    const response = await this.http.post('/api/ai/generate-quiz', quizData)
    return response.data
  }

  async verifyAnswers(quizId) {
    const response = await this.http.post('/api/ai/verify-answers', { quiz_id: quizId })
    return response.data
  }

  async publishAIQuiz(quizId, updates = {}) {
    const response = await this.http.post('/api/ai/publish-quiz', { quiz_id: quizId, ...updates })
    return response.data
  }

  async getQuizSuggestions(subject, difficultyLevels = ['easy', 'medium', 'hard'], numSuggestions = 10) {
    const response = await this.http.post('/api/ai/quiz-suggestions', {
      subject,
      difficulty_levels: difficultyLevels,
      num_suggestions: numSuggestions
    })
    return response.data
  }

  // Generic HTTP methods for flexibility
  async get(url) {
    const response = await this.http.get(url)
    return response.data
  }

  async post(url, data) {
    const response = await this.http.post(url, data)
    return response.data
  }

  async put(url, data) {
    const response = await this.http.put(url, data)
    return response.data
  }

  async delete(url) {
    const response = await this.http.delete(url)
    return response.data
  }
}

export default new ApiService()
