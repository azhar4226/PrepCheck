import apiClient from './apiClient'

class UserService {
  // Dashboard and navigation
  async getDashboard() {
    return await apiClient.get('/api/user/dashboard')
  }

  async getSubjects() {
    return await apiClient.get('/api/user/subjects')
  }

  async getChapters(subjectId) {
    return await apiClient.get(`/api/user/chapters/${subjectId}`)
  }

  async getMockTests(chapterId) {
    return await apiClient.get(`/api/user/mock-tests/${chapterId}`)
  }

  async getHistory(page = 1, perPage = 20) {
    return await apiClient.get(`/api/user/attempts/history?page=${page}&per_page=${perPage}`)
  }

  async getProgress() {
    return await apiClient.get('/api/user/progress')
  }

  // Profile Management
  async getProfile() {
    return await apiClient.get('/api/user/profile')
  }

  async updateProfile(profileData) {
    return await apiClient.put('/api/user/profile', profileData)
  }

  async changePassword(passwordData) {
    return await apiClient.put('/api/user/profile/password', passwordData)
  }

  async uploadProfilePicture(formData) {
    return await apiClient.post('/api/user/profile/picture', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }

  async deleteProfilePicture() {
    return await apiClient.delete('/api/user/profile/picture')
  }

  // Data Export
  async exportData() {
    return await apiClient.post('/api/user/export')
  }

  async getExportStatus(taskId) {
    return await apiClient.get(`/api/user/export/${taskId}`)
  }

  async downloadExportFile(filename) {
    return await apiClient.downloadFile(`/api/user/download/${filename}`)
  }
}

export default new UserService()
