import apiClient from './apiClient'

class NotificationsService {
  async getNotifications(limit = 20) {
    return await apiClient.get(`/api/notifications?limit=${limit}`)
  }

  async markAsRead(notificationId) {
    return await apiClient.post(`/api/notifications/${notificationId}/read`)
  }

  async markAllAsRead() {
    return await apiClient.post('/api/notifications/mark-all-read')
  }

  async getPreferences() {
    return await apiClient.get('/api/notifications/preferences')
  }

  async updatePreferences(preferences) {
    return await apiClient.put('/api/notifications/preferences', preferences)
  }

  async sendTest() {
    return await apiClient.post('/api/notifications/send-test')
  }
}

export default new NotificationsService()
