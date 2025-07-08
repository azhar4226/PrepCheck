import apiClient from './apiClient'

class AIService {
  // Question Generation (UGC NET focused)
  async generateQuestions(questionData) {
    return await apiClient.post('/api/ai/generate-questions', questionData)
  }

  async getQuestionSuggestions(subject, difficultyLevels = ['easy', 'medium', 'hard'], numSuggestions = 10) {
    return await apiClient.post('/api/ai/question-suggestions', {
      subject,
      difficulty_levels: difficultyLevels,
      num_suggestions: numSuggestions
    })
  }

  // Answer Verification
  async verifyAnswers(mockTestId) {
    return await apiClient.post('/api/ai/verify-answers', { mock_test_id: mockTestId })
  }

  async getVerificationStatus(taskId) {
    return await apiClient.get(`/api/ai/verification-status/${taskId}`)
  }

  async getMockTestVerificationSummary(mockTestId) {
    return await apiClient.get(`/api/ai/mock-test-verification-summary/${mockTestId}`)
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
  async publishMockTest(mockTestId, updates = {}) {
    return await apiClient.post('/api/ai/publish-mock-test', { mock_test_id: mockTestId, ...updates })
  }
}

export default new AIService()
