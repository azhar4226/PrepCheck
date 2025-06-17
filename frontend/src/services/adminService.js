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

  // Quizzes Management
  async getQuizzes(chapterId = null) {
    const url = chapterId ? `/api/admin/quizzes?chapter_id=${chapterId}` : '/api/admin/quizzes'
    return await apiClient.get(url)
  }

  async createQuiz(quizData) {
    return await apiClient.post('/api/admin/quizzes', quizData)
  }

  async updateQuiz(quizId, quizData) {
    return await apiClient.put(`/api/admin/quizzes/${quizId}`, quizData)
  }

  async toggleQuizStatus(quizId) {
    return await apiClient.put(`/api/admin/quizzes/${quizId}/toggle-status`)
  }

  async updateQuizStatus(quizId, isActive) {
    return await apiClient.put(`/api/admin/quizzes/${quizId}/status`, { is_active: isActive })
  }

  async deleteQuiz(quizId) {
    return await apiClient.delete(`/api/admin/quizzes/${quizId}`)
  }

  // Questions Management
  async getQuizQuestions(quizId) {
    return await apiClient.get(`/api/admin/questions/${quizId}`)
  }

  async getQuestions(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return await apiClient.get(`/api/admin/questions/?${queryString}`)
  }

  async getQuestionById(questionId) {
    return await apiClient.get(`/api/admin/questions/${questionId}`)
  }

  async createQuestion(questionData) {
    return await apiClient.post('/api/admin/questions/', questionData)
  }

  async updateQuestion(questionId, questionData) {
    return await apiClient.put(`/api/admin/questions/${questionId}`, questionData)
  }

  async deleteQuestion(questionId) {
    return await apiClient.delete(`/api/admin/questions/${questionId}`)
  }

  async bulkCreateQuestions(questionsData) {
    return await apiClient.post('/api/admin/questions/bulk', questionsData)
  }

  async deleteQuestions(questionIds) {
    return await apiClient.post('/api/admin/questions/bulk-delete', { question_ids: questionIds })
  }

  async exportQuestions(filters = {}) {
    const queryString = new URLSearchParams(filters).toString()
    return await apiClient.downloadFile(`/api/admin/questions/export?${queryString}`)
  }

  async importQuestions(formData) {
    return await apiClient.post('/api/admin/questions/import', formData)
  }

  // Users Management
  async getUsers(page = 1, perPage = 20, search = '', filter = 'all') {
    return await apiClient.get(`/api/admin/users?page=${page}&per_page=${perPage}&search=${search}&filter=${filter}`)
  }

  async getAllUsers(page = 1, perPage = 20, search = '', filter = 'all') {
    return await apiClient.get(`/api/admin/users?page=${page}&per_page=${perPage}&search=${search}&filter=${filter}`)
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
