import apiClient from './apiClient'

class AdminService {
  // Dashboard
  async getDashboard() {
    return await apiClient.get('/api/admin/dashboard')
  }

  async getDashboardStats() {
    return await apiClient.get('/api/admin/dashboard')
  }

  async getRecentActivity() {
    // For now, return the same dashboard data as it might include recent activity
    // Or create a separate endpoint in the backend if needed
    const response = await apiClient.get('/api/admin/dashboard')
    return { data: response.data?.recent_activity || [] }
  }

  // Profile Management
  async getProfile() {
    return await apiClient.get('/api/admin/profile')
  }

  async updateProfile(profileData) {
    return await apiClient.put('/api/admin/profile', profileData)
  }

  async changePassword(passwordData) {
    return await apiClient.put('/api/admin/profile/password', passwordData)
  }

  // Subjects Management
  async getSubjects() {
    return await apiClient.get('/api/admin/subjects')
  }

  async createSubject(subjectData) {
    return await apiClient.post('/api/admin/subjects', subjectData)
  }

  async updateSubject(subjectId, subjectData) {
    return await apiClient.put(`/api/admin/subjects/${subjectId}`, subjectData)
  }

  async deleteSubject(subjectId) {
    return await apiClient.delete(`/api/admin/subjects/${subjectId}`)
  }

  // Chapters Management
  async getChapters(subjectId = null) {
    const url = subjectId ? `/api/admin/chapters?subject_id=${subjectId}` : '/api/admin/chapters'
    return await apiClient.get(url)
  }

  async createChapter(chapterData) {
    return await apiClient.post('/api/admin/chapters', chapterData)
  }

  // UGC NET Mock Tests Management (replaces legacy quiz management)
  async getMockTests(chapterId = null) {
    const url = chapterId ? `/api/admin/ugc-net/mock-tests?chapter_id=${chapterId}` : '/api/admin/ugc-net/mock-tests'
    return await apiClient.get(url)
  }

  async createMockTest(mockTestData) {
    return await apiClient.post('/api/admin/ugc-net/mock-tests', mockTestData)
  }

  async updateMockTest(mockTestId, mockTestData) {
    return await apiClient.put(`/api/admin/ugc-net/mock-tests/${mockTestId}`, mockTestData)
  }

  async updateMockTestStatus(mockTestId, isActive) {
    return await apiClient.put(`/api/admin/ugc-net/mock-tests/${mockTestId}/status`, { is_active: isActive })
  }

  async deleteMockTest(mockTestId) {
    return await apiClient.delete(`/api/admin/ugc-net/mock-tests/${mockTestId}`)
  }

  // Question Bank Management (replaces legacy question management)
  async getMockTestQuestions(mockTestId) {
    return await apiClient.get(`/api/admin/ugc-net/mock-tests/${mockTestId}/questions`)
  }

  async getQuestions(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return await apiClient.get(`/api/admin/question-bank/?${queryString}`)
  }

  async getQuestionById(questionId) {
    return await apiClient.get(`/api/admin/question-bank/${questionId}`)
  }

  async createQuestion(questionData) {
    return await apiClient.post('/api/admin/question-bank/', questionData)
  }

  async updateQuestion(questionId, questionData) {
    return await apiClient.put(`/api/admin/question-bank/${questionId}`, questionData)
  }

  async deleteQuestion(questionId) {
    return await apiClient.delete(`/api/admin/question-bank/${questionId}`)
  }

  async bulkCreateQuestions(questionsData) {
    return await apiClient.post('/api/admin/question-bank/bulk', questionsData)
  }

  async deleteQuestions(questionIds) {
    return await apiClient.post('/api/admin/question-bank/bulk-delete', { question_ids: questionIds })
  }

  async exportQuestions(filters = {}) {
    const queryString = new URLSearchParams(filters).toString()
    return await apiClient.downloadFile(`/api/admin/question-bank/export?${queryString}`)
  }

  async importQuestions(formData) {
    return await apiClient.post('/api/admin/question-bank/import', formData)
  }

  // UGC NET Attempts Management
  async getMockAttempts(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return await apiClient.get(`/api/admin/ugc-net/mock-attempts/?${queryString}`)
  }

  async getPracticeAttempts(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return await apiClient.get(`/api/admin/ugc-net/practice-attempts/?${queryString}`)
  }

  async getAllAttempts(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return await apiClient.get(`/api/admin/ugc-net/attempts/?${queryString}`)
  }

  // Users Management
  async getUsers(page = 1, perPage = 20, search = '', filter = 'all', role = '', status = '') {
    let url = `/api/admin/users?page=${page}&per_page=${perPage}&search=${search}`
    
    // Add separate role and status parameters if provided
    if (role) {
      url += `&role=${role}`
    }
    if (status) {
      url += `&status=${status}`
    }
    
    // Add legacy filter parameter for backward compatibility
    if (filter && filter !== 'all') {
      url += `&filter=${filter}`
    }
    
    return await apiClient.get(url)
  }

  async getAllUsers(page = 1, perPage = 20, search = '', filter = 'all', role = '', status = '') {
    let url = `/api/admin/users?page=${page}&per_page=${perPage}&search=${search}`
    
    // Add separate role and status parameters if provided
    if (role) {
      url += `&role=${role}`
    }
    if (status) {
      url += `&status=${status}`
    }
    
    // Add legacy filter parameter for backward compatibility
    if (filter && filter !== 'all') {
      url += `&filter=${filter}`
    }
    
    return await apiClient.get(url)
  }

  async getUserById(userId) {
    return await apiClient.get(`/api/admin/users/${userId}`)
  }

  async updateUserByAdmin(userId, userData) {
    return await apiClient.put(`/api/admin/users/${userId}/profile`, userData)
  }

  async createUserByAdmin(userData) {
    return await apiClient.post('/api/admin/users/create', userData)
  }

  async deleteUserByAdmin(userId) {
    return await apiClient.delete(`/api/admin/users/${userId}`)
  }

  // Additional convenience methods
  async deleteUser(userId) {
    return await this.deleteUserByAdmin(userId)
  }

  async updateUser(userId, userData) {
    return await this.updateUserByAdmin(userId, userData)
  }

  async createUser(userData) {
    return await this.createUserByAdmin(userData)
  }

  // Data Export
  async exportData(type = 'all') {
    return await apiClient.post('/api/admin/export', { type })
  }

  async getExportStatus(taskId) {
    return await apiClient.get(`/api/admin/export/${taskId}`)
  }

  async downloadExportFile(filename) {
    return await apiClient.downloadFile(`/api/admin/download/${filename}`)
  }
}

export default new AdminService()
