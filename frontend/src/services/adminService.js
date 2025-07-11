import apiClient from './apiClient'

class AdminService {
  // Dashboard
  async getDashboard() {
    return await apiClient.get('/api/v1/admin/dashboard')
  }

  async getDashboardStats() {
    return await apiClient.get('/api/v1/admin/dashboard')
  }

  async getRecentActivity() {
    // For now, return the same dashboard data as it might include recent activity
    const response = await apiClient.get('/api/v1/admin/dashboard')
    return { data: response.data?.recent_activity || [] }
  }

  // Profile Management
  async getProfile() {
    return await apiClient.get('/api/v1/admin/profile')
  }

  async updateProfile(profileData) {
    return await apiClient.put('/api/v1/admin/profile', profileData)
  }

  async changePassword(passwordData) {
    return await apiClient.put('/api/v1/admin/profile/password', passwordData)
  }

  // Subjects Management
  async getSubjects() {
    const response = await apiClient.get('/api/v1/admin/subjects')
    return response // Return the array directly
  }

  async createSubject(subjectData) {
    return await apiClient.post('/api/v1/admin/subjects', subjectData)
  }

  async updateSubject(subjectId, subjectData) {
    return await apiClient.put(`/api/v1/admin/subjects/${subjectId}`, subjectData)
  }

  async deleteSubject(subjectId) {
    return await apiClient.delete(`/api/v1/admin/subjects/${subjectId}`)
  }

  // Chapters Management
  async getChapters(subjectId = null) {
    const url = subjectId ? `/api/v1/admin/chapters?subject_id=${subjectId}` : '/api/v1/admin/chapters'
    return await apiClient.get(url)
  }

  async createChapter(chapterData) {
    return await apiClient.post('/api/v1/admin/chapters', chapterData)
  }

  // UGC NET Mock Tests Management (replaces legacy quiz management)
  async getMockTests(chapterId = null) {
    const url = chapterId ? `/api/v1/admin/ugc-net/mock-tests?chapter_id=${chapterId}` : '/api/v1/admin/ugc-net/mock-tests'
    return await apiClient.get(url)
  }

  async createMockTest(mockTestData) {
    return await apiClient.post('/api/v1/admin/ugc-net/mock-tests', mockTestData)
  }

  async updateMockTest(mockTestId, mockTestData) {
    return await apiClient.put(`/api/v1/admin/ugc-net/mock-tests/${mockTestId}`, mockTestData)
  }

  async updateMockTestStatus(mockTestId, isActive) {
    return await apiClient.put(`/api/v1/admin/ugc-net/mock-tests/${mockTestId}/status`, { is_active: isActive })
  }

  async deleteMockTest(mockTestId) {
    return await apiClient.delete(`/api/v1/admin/ugc-net/mock-tests/${mockTestId}`)
  }

  // Question Bank Management (replaces legacy question management)
  async getMockTestQuestions(mockTestId) {
    return await apiClient.get(`/api/v1/admin/ugc-net/mock-tests/${mockTestId}/questions`)
  }

  async getQuestions(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return await apiClient.get(`/api/v1/admin/question-bank/?${queryString}`)
  }

  async getQuestionById(questionId) {
    return await apiClient.get(`/api/v1/admin/question-bank/${questionId}`)
  }

  async createQuestion(questionData) {
    return await apiClient.post('/api/v1/admin/question-bank/', questionData)
  }

  async updateQuestion(questionId, questionData) {
    return await apiClient.put(`/api/v1/admin/question-bank/${questionId}`, questionData)
  }

  async deleteQuestion(questionId) {
    return await apiClient.delete(`/api/v1/admin/question-bank/${questionId}`)
  }

  async bulkCreateQuestions(questionsData) {
    return await apiClient.post('/api/v1/admin/question-bank/bulk', questionsData)
  }

  async deleteQuestions(questionIds) {
    return await apiClient.post('/api/v1/admin/question-bank/bulk-delete', { question_ids: questionIds })
  }

  async exportQuestions(filters = {}) {
    const queryString = new URLSearchParams(filters).toString()
    return await apiClient.downloadFile(`/api/v1/admin/question-bank/export?${queryString}`)
  }

  async importQuestions(formData) {
    return await apiClient.post('/api/v1/admin/question-bank/import', formData)
  }

  // UGC NET Attempts Management
  async getMockAttempts(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return await apiClient.get(`/api/v1/admin/ugc-net/mock-attempts/?${queryString}`)
  }

  async getPracticeAttempts(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return await apiClient.get(`/api/v1/admin/ugc-net/practice-attempts/?${queryString}`)
  }

  async getAllAttempts(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return await apiClient.get(`/api/v1/admin/ugc-net/attempts/?${queryString}`)
  }

  // Users Management
  async getUsers(page = 1, perPage = 20, search = '', filter = 'all', role = '', status = '') {
    try {
      console.log('🔄 Getting users with params:', { page, perPage, search, filter, role, status })
      
      let url = `/api/v1/admin/users?page=${page}&per_page=${perPage}&search=${search}`
      
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
      
      console.log('🌐 Requesting URL:', url)
      const response = await apiClient.get(url)
      console.log('✅ Users response:', response)
      return response
    } catch (error) {
      console.error('❌ Error getting users:', error)
      throw error
    }
  }

  async getUserById(userId) {
    return await apiClient.get(`/api/v1/admin/users/${userId}`)
  }

  async updateUserByAdmin(userId, userData) {
    return await apiClient.put(`/api/v1/admin/users/${userId}/profile`, userData)
  }

  async createUserByAdmin(userData) {
    return await apiClient.post('/api/v1/admin/users/create', userData)
  }

  async deleteUserByAdmin(userId) {
    return await apiClient.delete(`/api/v1/admin/users/${userId}`)
  }

  // Data Export
  async exportData(type = 'all') {
    return await apiClient.post('/api/v1/admin/export', { type })
  }

  async getExportStatus(taskId) {
    return await apiClient.get(`/api/v1/admin/export/${taskId}`)
  }

  async downloadExportFile(filename) {
    return await apiClient.downloadFile(`/api/v1/admin/download/${filename}`)
  }

  // Chapter Weightage Management
  async getSubjectChapterWeightages(subjectId) {
    return await apiClient.get(`/api/v1/admin/subjects/${subjectId}/chapter-weightages`)
  }

  async updateSubjectChapterWeightages(subjectId, weightageData) {
    return await apiClient.put(`/api/v1/admin/subjects/${subjectId}/chapter-weightages`, weightageData)
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
}

export default new AdminService()
