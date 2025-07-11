import apiClient from './apiClient'

class AnalyticsService {
  // System Analytics
  async getOverview(days = 30) {
    return await apiClient.get(`/api/v1/analytics/overview?days=${days}`)
  }

  async getUserAnalytics(params = {}) {
    try {
      const response = await apiClient.get('/api/v1/analytics/user', { params })
      return response.data
    } catch (error) {
      console.error('Error fetching user analytics:', error)
      throw error
    }
  }

  async getMockTestAnalytics(mockTestId) {
    return await apiClient.get(`/api/v1/analytics/mock-test/${mockTestId}`)
  }

  async exportAnalytics(format = 'pdf') {
    try {
      const response = await apiClient.get(`/api/v1/analytics/export?format=${format}`, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('Error exporting analytics:', error)
      throw error
    }
  }
}

export default new AnalyticsService()
