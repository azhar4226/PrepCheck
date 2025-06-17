import apiClient from './apiClient'

class QuizService {
  // Quiz browsing and discovery
  async browseQuizzes() {
    return await apiClient.get('/api/quiz/browse')
  }

  async getSubjects() {
    return await apiClient.get('/api/quiz/subjects')
  }

  async getChapters() {
    return await apiClient.get('/api/quiz/chapters')
  }

  // Quiz taking
  async previewQuiz(quizId) {
    return await apiClient.get(`/api/quiz/${quizId}/preview`)
  }

  async startQuiz(quizId) {
    return await apiClient.post(`/api/quiz/${quizId}/start`)
  }

  async saveProgress(quizId, answers) {
    return await apiClient.post(`/api/quiz/${quizId}/save`, { answers })
  }

  async submitQuiz(quizId, answers) {
    return await apiClient.post(`/api/quiz/${quizId}/submit`, { answers })
  }

  async getResults(attemptId) {
    return await apiClient.get(`/api/quiz/attempt/${attemptId}/results`)
  }

  // User analytics (replacing userAnalyticsService.js)
  async getUserAnalytics(filters = {}) {
    const params = new URLSearchParams()
    
    if (filters.days) params.append('days', filters.days)
    if (filters.subject_id) params.append('subject_id', filters.subject_id)
    if (filters.chapter_id) params.append('chapter_id', filters.chapter_id)
    
    return await apiClient.get(`/quiz/user-analytics?${params}`)
  }
}

export default new QuizService()
