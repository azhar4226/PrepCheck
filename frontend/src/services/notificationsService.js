import apiClient from './apiClient'

class NotificationsService {
  async getNotifications(limit = 20) {
    return await apiClient.get(`/api/v1/notifications?limit=${limit}`)
  }

  async markAsRead(notificationId) {
    return await apiClient.post(`/api/v1/notifications/${notificationId}/read`)
  }

  async markAllAsRead() {
    return await apiClient.post('/api/v1/notifications/mark-all-read')
  }

  async getPreferences() {
    return await apiClient.get('/api/v1/notifications/preferences')
  }

  async updatePreferences(preferences) {
    return await apiClient.put('/api/v1/notifications/preferences', preferences)
  }

  async sendTest() {
    return await apiClient.post('/api/v1/notifications/send-test')
  }
}

export default new NotificationsService()
