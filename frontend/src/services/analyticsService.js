import apiClient from './apiClient'

class AnalyticsService {
  // System Analytics
  async getOverview(days = 30) {
    return await apiClient.get(`/api/analytics/overview?days=${days}`)
  }

  async getUserAnalytics(userId) {
    return await apiClient.get(`/api/analytics/user/${userId}`)
  }

  async getMockTestAnalytics(mockTestId) {
    return await apiClient.get(`/api/analytics/mock-test/${mockTestId}`)
  }
}

export default new AnalyticsService()
