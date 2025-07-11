import apiClient from './apiClient'

class UserService {
  // Dashboard and navigation
  async getDashboard() {
    return await apiClient.get('/api/v1/users/dashboard')
  }

  async getSubjects() {
    return await apiClient.get('/api/v1/users/subjects')
  }

  async getPaper2Subjects() {
    return await apiClient.get('/api/v1/users/subjects/paper2')
  }

  async getChapters(subjectId) {
    return await apiClient.get(`/api/v1/users/chapters/${subjectId}`)
  }

  async getMockTests(chapterId) {
    return await apiClient.get(`/api/v1/users/mock-tests/${chapterId}`)
  }

  async getHistory(page = 1, perPage = 20) {
    return await apiClient.get(`/api/v1/users/attempts/history?page=${page}&per_page=${perPage}`)
  }

  async getProgress() {
    return await apiClient.get('/api/v1/users/progress')
  }

  // Profile Management
  async getProfile() {
    return await apiClient.get('/api/v1/users/profile')
  }

  async updateProfile(profileData) {
    return await apiClient.put('/api/v1/users/profile', profileData)
  }

  async changePassword(passwordData) {
    return await apiClient.put('/api/v1/users/profile/password', passwordData)
  }

  async uploadProfilePicture(formData) {
    return await apiClient.post('/api/v1/users/profile/picture', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }

  // Mock Test Management
  async startMockTest(mockTestId) {
    return await apiClient.post(`/api/v1/users/mock-tests/${mockTestId}/start`)
  }

  async submitMockTest(mockTestId, answers) {
    return await apiClient.post(`/api/v1/users/mock-tests/${mockTestId}/submit`, answers)
  }

  async getMockTestQuestions(mockTestId) {
    return await apiClient.get(`/api/v1/users/mock-tests/${mockTestId}/questions`)
  }

  async getMockTestResults(mockTestId) {
    return await apiClient.get(`/api/v1/users/mock-tests/${mockTestId}/results`)
  }

  async getMockTestAttempt(attemptId) {
    return await apiClient.get(`/api/v1/users/mock-tests/attempts/${attemptId}`)
  }

  async getMockTestSummary(mockTestId) {
    return await apiClient.get(`/api/v1/users/mock-tests/${mockTestId}/summary`)
  }

  // Practice Test Management
  async startPracticeTest(chapterId) {
    return await apiClient.post(`/api/v1/users/practice/${chapterId}/start`)
  }

  async submitPracticeTest(testId, answers) {
    return await apiClient.post(`/api/v1/users/practice/${testId}/submit`, answers)
  }

  async getPracticeQuestions(testId) {
    return await apiClient.get(`/api/v1/users/practice/${testId}/questions`)
  }

  async getPracticeResults(testId) {
    return await apiClient.get(`/api/v1/users/practice/${testId}/results`)
  }

  async getPracticeAttempt(attemptId) {
    return await apiClient.get(`/api/v1/users/practice/attempts/${attemptId}`)
  }

  async getPracticeSummary(testId) {
    return await apiClient.get(`/api/v1/users/practice/${testId}/summary`)
  }
}

export default new UserService()
