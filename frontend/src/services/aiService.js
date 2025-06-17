import apiClient from './apiClient'

class AIService {
  // Quiz Generation
  async generateQuiz(quizData) {
    return await apiClient.post('/api/ai/generate-quiz', quizData)
  }

  async getQuizSuggestions(subject, difficultyLevels = ['easy', 'medium', 'hard'], numSuggestions = 10) {
    return await apiClient.post('/api/ai/quiz-suggestions', {
      subject,
      difficulty_levels: difficultyLevels,
      num_suggestions: numSuggestions
    })
  }

  // Answer Verification
  async verifyAnswers(quizId) {
    return await apiClient.post('/api/ai/verify-answers', { quiz_id: quizId })
  }

  async getVerificationStatus(taskId) {
    return await apiClient.get(`/api/ai/verification-status/${taskId}`)
  }

  async getQuizVerificationSummary(quizId) {
    return await apiClient.get(`/api/ai/quiz-verification-summary/${quizId}`)
  }

  async retryVerification(data) {
    return await apiClient.post('/api/ai/retry-verification', data)
  }

  async manualApproveQuestion(questionId, reason = '') {
    return await apiClient.post('/api/ai/manual-approve-question', {
      question_id: questionId,
      reason: reason
    })
  }

  // Configuration
  async getVerificationConfig() {
    return await apiClient.get('/api/ai/verification-config')
  }

  async updateVerificationConfig(config) {
    return await apiClient.post('/api/ai/verification-config', config)
  }

  // Publishing
  async publishQuiz(quizId, updates = {}) {
    return await apiClient.post('/api/ai/publish-quiz', { quiz_id: quizId, ...updates })
  }
}

export default new AIService()
