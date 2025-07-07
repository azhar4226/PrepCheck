import apiClient from './apiClient'

class UGCNetService {
  constructor() {
    this.baseUrl = '/api/ugc-net'
  }

  // ============================================================================
  // Subject Management
  // ============================================================================

  async getSubjects() {
    try {
      console.log('🔍 UGCNetService: Calling getSubjects API...')
      const response = await apiClient.get(`${this.baseUrl}/subjects`)
      console.log('✅ UGCNetService: getSubjects response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: getSubjects error:', error)
      console.error('❌ Error response:', error.response?.data)
      console.error('❌ Error status:', error.response?.status)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch subjects'
      }
    }
  }

  async getSubjectChapters(subjectId) {
    try {
      console.log('🔍 UGCNetService: Calling getSubjectChapters API for subject:', subjectId)
      const response = await apiClient.get(`${this.baseUrl}/subjects/${subjectId}/chapters`)
      console.log('✅ UGCNetService: getSubjectChapters response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: getSubjectChapters error:', error)
      console.error('❌ Error response:', error.response?.data)
      console.error('❌ Error status:', error.response?.status)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch chapters'
      }
    }
  }

  // ============================================================================
  // Mock Test Management
  // ============================================================================

  async generateMockTest(config) {
    try {
      const response = await apiClient.post(`${this.baseUrl}/mock-tests/generate`, config)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to generate mock test'
      }
    }
  }

  async getMockTests(params = {}) {
    try {
      console.log('🔍 UGCNetService: Calling getMockTests API...')
      const response = await apiClient.get(`${this.baseUrl}/mock-tests`, { params })
      console.log('✅ UGCNetService: getMockTests response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: getMockTests error:', error)
      console.error('❌ Error response:', error.response?.data)
      console.error('❌ Error status:', error.response?.status)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch mock tests'
      }
    }
  }

  async getMockTestDetails(testId) {
    try {
      const response = await apiClient.get(`${this.baseUrl}/mock-tests/${testId}`)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to fetch test details'
      }
    }
  }

  // ============================================================================
  // Test Attempts
  // ============================================================================

  async startAttempt(testId) {
    try {
      console.log('🔍 UGCNetService: Starting attempt for test:', testId)
      const response = await apiClient.post(`${this.baseUrl}/mock-tests/${testId}/attempt`)
      console.log('✅ UGCNetService: startAttempt response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: startAttempt error:', error)
      console.error('❌ Error response:', error.response?.data)
      console.error('❌ Error status:', error.response?.status)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to start test attempt'
      }
    }
  }

  async submitAttempt(testId, attemptId, answers) {
    try {
      console.log('🔄 Submitting UGC NET attempt:', { testId, attemptId, answers })
      
      const response = await apiClient.post(
        `${this.baseUrl}/mock-tests/${testId}/attempt/${attemptId}/submit`,
        { answers }
      )
      
      console.log('✅ UGC NET submission response:', response)
      
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGC NET submission error:', error)
      console.error('Error response:', error.response?.data)
      
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to submit answers'
      }
    }
  }

  async getAttemptResults(testId, attemptId, includeSolutions = true) {
    try {
      console.log('🔍 UGCNetService: Getting attempt results for:', { testId, attemptId, includeSolutions })
      const params = includeSolutions ? { include_solutions: 'true' } : {}
      const response = await apiClient.get(`${this.baseUrl}/mock-tests/${testId}/attempt/${attemptId}/results`, { params })
      console.log('✅ UGCNetService: getAttemptResults response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: getAttemptResults error:', error)
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to fetch results'
      }
    }
  }

  async getUserAttempts(testId) {
    try {
      console.log('🔍 UGCNetService: Getting user attempts for test:', testId)
      const response = await apiClient.get(`${this.baseUrl}/mock-tests/${testId}/attempts`)
      console.log('✅ UGCNetService: getUserAttempts response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: getUserAttempts error:', error)
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to fetch user attempts'
      }
    }
  }

  // ============================================================================
  // Statistics & Analytics
  // ============================================================================

  async getStatistics() {
    try {
      console.log('🔍 UGCNetService: Calling getStatistics API...')
      const response = await apiClient.get(`${this.baseUrl}/statistics`)
      console.log('✅ UGCNetService: getStatistics response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: getStatistics error:', error)
      console.error('❌ Error response:', error.response?.data)
      console.error('❌ Error status:', error.response?.status)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch statistics'
      }
    }
  }

  // ============================================================================
  // Question Bank
  // ============================================================================

  async addQuestion(questionData) {
    try {
      const response = await apiClient.post(`${this.baseUrl}/question-bank/add`, questionData)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to add question'
      }
    }
  }

  async bulkImportQuestions(questionsData) {
    try {
      const response = await apiClient.post(`${this.baseUrl}/question-bank/bulk-import`, questionsData)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to import questions'
      }
    }
  }

  // ============================================================================
  // Admin Functions
  // ============================================================================

  async createSubject(subjectData) {
    try {
      const response = await apiClient.post(`${this.baseUrl}/admin/subjects`, subjectData)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to create subject'
      }
    }
  }

  async createChapter(subjectId, chapterData) {
    try {
      const response = await apiClient.post(`${this.baseUrl}/admin/subjects/${subjectId}/chapters`, chapterData)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to create chapter'
      }
    }
  }

  // ============================================================================
  // Practice Test Management  
  // ============================================================================

  async generatePracticeTest(config) {
    try {
      console.log('🔍 UGCNetService: Generating practice test with config:', config)
      const response = await apiClient.post(`${this.baseUrl}/practice-tests/generate`, config)
      console.log('✅ UGCNetService: generatePracticeTest response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: generatePracticeTest error:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to generate practice test'
      }
    }
  }

  async getPracticeTests(params = {}) {
    try {
      console.log('🔍 UGCNetService: Calling getPracticeTests API...')
      const response = await apiClient.get(`${this.baseUrl}/practice-tests`, { params })
      console.log('✅ UGCNetService: getPracticeTests response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: getPracticeTests error:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch practice tests'
      }
    }
  }

  async startPracticeTest(testId) {
    try {
      console.log('🔍 UGCNetService: Starting practice test:', testId)
      const response = await apiClient.post(`${this.baseUrl}/practice-tests/${testId}/start`)
      console.log('✅ UGCNetService: startPracticeTest response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: startPracticeTest error:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to start practice test'
      }
    }
  }

  async submitPracticeTest(attemptId, answers) {
    try {
      console.log('🔍 UGCNetService: Submitting practice test:', attemptId)
      console.log('🔍 UGCNetService: Answers being submitted:', answers)
      console.log('🔍 UGCNetService: Answers keys:', Object.keys(answers))
      const response = await apiClient.post(`${this.baseUrl}/practice-tests/attempts/${attemptId}/submit`, {
        answers
      })
      console.log('✅ UGCNetService: submitPracticeTest response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: submitPracticeTest error:', error)
      console.error('❌ UGCNetService: Error response data:', error.response?.data)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to submit practice test'
      }
    }
  }

  async getPracticeTestResults(attemptId) {
    try {
      console.log('🔍 UGCNetService: Getting practice test results:', attemptId)
      const response = await apiClient.get(`${this.baseUrl}/practice-tests/attempts/${attemptId}/results`)
      console.log('✅ UGCNetService: getPracticeTestResults response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: getPracticeTestResults error:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to get practice test results'
      }
    }
  }

  async getPracticeTest(attemptId) {
    try {
      console.log('🔍 UGCNetService: Getting practice test:', attemptId)
      const response = await apiClient.get(`${this.baseUrl}/practice-tests/attempts/${attemptId}`)
      console.log('✅ UGCNetService: getPracticeTest response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: getPracticeTest error:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to get practice test'
      }
    }
  }

  async savePracticeAnswers(attemptId, answers) {
    try {
      console.log('🔍 UGCNetService: Saving practice answers:', attemptId)
      console.log('🔍 UGCNetService: Answers data:', answers)
      console.log('🔍 UGCNetService: Answers type:', typeof answers)
      console.log('🔍 UGCNetService: Answers keys:', Object.keys(answers))
      const response = await apiClient.put(`${this.baseUrl}/practice-tests/attempts/${attemptId}/answers`, {
        answers
      })
      console.log('✅ UGCNetService: savePracticeAnswers response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: savePracticeAnswers error:', error)
      console.error('❌ UGCNetService: Error response data:', error.response?.data)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to save answers'
      }
    }
  }

  async getPracticeHistory(params = {}) {
    try {
      console.log('🔍 UGCNetService: Getting practice history')
      const response = await apiClient.get(`${this.baseUrl}/practice-tests/history`, { params })
      console.log('✅ UGCNetService: getPracticeHistory response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: getPracticeHistory error:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to get practice history'
      }
    }
  }

  async getPracticeResults(attemptId) {
    try {
      console.log('🔍 UGCNetService: Getting practice results:', attemptId)
      const response = await apiClient.get(`${this.baseUrl}/practice-tests/attempts/${attemptId}/results`)
      console.log('✅ UGCNetService: getPracticeResults response:', response)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('❌ UGCNetService: getPracticeResults error:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to get practice results'
      }
    }
  }

  // ============================================================================
  // Utility Methods
  // ============================================================================

  formatTime(seconds) {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`
    } else {
      return `${secs}s`
    }
  }

  calculatePercentage(score, total) {
    if (total === 0) return 0
    return Math.round((score / total) * 100)
  }

  getQualificationStatus(percentage) {
    if (percentage >= 40) return { status: 'qualified', class: 'success' }
    if (percentage >= 35) return { status: 'borderline', class: 'warning' }
    return { status: 'not_qualified', class: 'danger' }
  }
}

export default new UGCNetService()
