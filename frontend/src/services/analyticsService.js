import apiClient from './apiClient'

class AnalyticsService {
  // System Analytics
  async getOverview(days = 30) {
    return await apiClient.get(`/api/analytics/overview?days=${days}`)
  }

  async getUserAnalytics(userId) {
    return await apiClient.get(`/api/analytics/user/${userId}`)
  }

  async getQuizAnalytics(quizId) {
    return await apiClient.get(`/api/analytics/quiz/${quizId}`)
  }
}

export default new AnalyticsService()
