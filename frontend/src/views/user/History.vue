<template>
  <div class="container-fluid py-4">
    <!-- Toast Notifications Container -->
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1060;">
      <div v-for="(notification, index) in notifications" :key="notification.id"
           class="toast show align-items-center border-0"
           :class="getNotificationClass(notification.type)"
           role="alert">
        <div class="d-flex">
          <div class="toast-body text-white">
            <i :class="getNotificationIcon(notification.type)" class="me-2"></i>
            {{ notification.message }}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                  @click="removeNotification(index)"></button>
        </div>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div class="modal fade" id="confirmModal" tabindex="-1" ref="confirmModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ confirmModal.title }}</h5>
            <button type="button" class="btn-close" @click="closeModal()"></button>
          </div>
          <div class="modal-body">
            <p>{{ confirmModal.message }}</p>
            <div v-if="confirmModal.details" class="alert alert-info">
              <small v-html="confirmModal.details"></small>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal()">Cancel</button>
            <button type="button" class="btn" :class="confirmModal.buttonClass" 
                    @click="confirmModal.action(); closeModal()">
              {{ confirmModal.buttonText }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2><i class="bi bi-clock-history me-2"></i>Test History</h2>
          <div class="btn-group" role="group">
            <router-link to="/ugc-net/generate-test" class="btn btn-outline-primary">
              <i class="bi bi-mortarboard me-2"></i>
              Take New Test
            </router-link>
            <router-link to="/ugc-net/practice/setup" class="btn btn-outline-success">
              <i class="bi bi-play-circle me-2"></i>
              Practice Tests
            </router-link>
          </div>
        </div>

        <!-- Filter Tabs -->
        <div class="card mb-4">
          <div class="card-header">
            <ul class="nav nav-tabs card-header-tabs" role="tablist">
              <li class="nav-item" role="presentation">
                <button 
                  class="nav-link" 
                  :class="{ active: activeTab === 'all' }"
                  @click="changeTab('all')"
                  type="button"
                >
                  <i class="bi bi-list me-2"></i>All Tests
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button 
                  class="nav-link" 
                  :class="{ active: activeTab === 'mock' }"
                  @click="changeTab('mock')"
                  type="button"
                >
                  <i class="bi bi-clipboard-check me-2"></i>Mock Tests
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button 
                  class="nav-link" 
                  :class="{ active: activeTab === 'practice' }"
                  @click="changeTab('practice')"
                  type="button"
                >
                  <i class="bi bi-mortarboard me-2"></i>Practice Tests
                </button>
              </li>
            </ul>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3">Loading test history...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger">
          <i class="bi bi-exclamation-triangle me-2"></i>
          {{ error }}
          <div v-if="error.includes('not logged in')" class="mt-3">
            <p class="mb-2"><strong>Quick Test Login:</strong></p>
            <div class="d-flex gap-2 align-items-center">
              <button @click="quickLogin" class="btn btn-sm btn-primary" :disabled="loggingIn">
                <span v-if="loggingIn" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-box-arrow-in-right me-1"></i>
                {{ loggingIn ? 'Logging in...' : 'Test Login (student1@test.com)' }}
              </button>
              <small class="text-muted">or <router-link to="/login">go to login page</router-link></small>
            </div>
          </div>
        </div>

        <!-- Statistics Cards -->
        <div v-else class="row mb-4">
          <div class="col-md-3">
            <div class="card bg-primary text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h6 class="card-title">Total Tests</h6>
                    <h3 class="mb-0">{{ currentStatistics.totalTests }}</h3>
                  </div>
                  <div class="align-self-center">
                    <i class="bi bi-clipboard-check display-4 opacity-75"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-success text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h6 class="card-title">Completed</h6>
                    <h3 class="mb-0">{{ currentStatistics.completedTests }}</h3>
                  </div>
                  <div class="align-self-center">
                    <i class="bi bi-check-circle display-4 opacity-75"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-info text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h6 class="card-title">Average Score</h6>
                    <h3 class="mb-0">{{ currentStatistics.averageScore }}%</h3>
                  </div>
                  <div class="align-self-center">
                    <i class="bi bi-graph-up display-4 opacity-75"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-warning text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h6 class="card-title">Best Score</h6>
                    <h3 class="mb-0">{{ currentStatistics.bestScore }}%</h3>
                  </div>
                  <div class="align-self-center">
                    <i class="bi bi-trophy display-4 opacity-75"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Test History Content -->
        <div v-if="filteredAttempts.length === 0 && !loading" class="card">
          <div class="card-body">
            <div class="text-center py-5">
              <i class="bi bi-clock-history display-1 text-muted mb-3"></i>
              <h4 class="text-muted">No Test History Yet</h4>
              <p class="text-muted mb-4">Start taking UGC NET tests to see your history here.</p>
              <!-- Debug information -->
              <div class="alert alert-info mt-3">
                <small>
                  <strong>Debug Info:</strong><br>
                  <strong>Authentication:</strong> {{ isAuthenticated ? 'Logged in' : 'Not logged in' }}<br>
                  <strong>API Status:</strong> {{ error ? 'Error occurred' : 'Connected successfully' }}<br>
                  <strong>Data loaded:</strong> Mock attempts: {{ mockAttempts.length }}, Practice attempts: {{ practiceAttempts.length }}<br>
                  <strong>Overall Statistics:</strong> Total tests: {{ statistics.totalTests }}, Best score: {{ statistics.bestScore }}%<br>
                  <strong>Current Tab ({{ activeTab }}):</strong> {{ currentStatistics.totalTests }} tests, Best: {{ currentStatistics.bestScore }}%<br>
                  <span v-if="statistics.totalTests > 0"><strong>Note:</strong> Statistics show {{ statistics.totalTests }} tests taken, but detailed history may not be available yet.</span><br>
                  <strong>Next steps:</strong> Take some tests to see your history here
                </small>
              </div>
              <div class="d-flex justify-content-center gap-2">
                <router-link to="/ugc-net" class="btn btn-primary">
                  <i class="bi bi-mortarboard me-2"></i>
                  Browse Mock Tests
                </router-link>
                <router-link to="/ugc-net/practice/setup" class="btn btn-success">
                  <i class="bi bi-play-circle me-2"></i>
                  Start Practice Test
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Test History List -->
        <div v-else class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-list-ul me-2"></i>
              Test History 
              <span class="badge bg-secondary ms-2">{{ filteredAttempts.length }}</span>
            </h5>
            <small class="text-muted">
              Showing {{ paginatedAttempts.length }} of {{ filteredAttempts.length }} tests
            </small>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Type</th>
                    <th>Subject</th>
                    <th>Test/Chapter</th>
                    <th>Questions</th>
                    <th>Score</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="attempt in paginatedAttempts" :key="`${attempt.type}-${attempt.id}`">
                    <td>
                      <span class="badge" :class="getTypeBadgeClass(attempt.type)">
                        {{ attempt.type === 'mock' ? 'Mock Test' : 'Practice' }}
                      </span>
                    </td>
                    <td>
                      <strong>{{ attempt.subject_name }}</strong>
                    </td>
                    <td>
                      <span v-if="attempt.type === 'mock'" class="text-primary">
                        {{ attempt.test_name }}
                      </span>
                      <span v-else class="badge bg-light text-dark">
                        {{ attempt.chapter_name }}
                      </span>
                    </td>
                    <td>{{ attempt.total_questions }}</td>
                    <td>
                      <span v-if="attempt.is_completed" class="badge" :class="getScoreBadgeClass(attempt.percentage)">
                        {{ attempt.percentage }}%
                      </span>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td>
                      <span class="badge" :class="getStatusBadgeClass(attempt.is_completed)">
                        {{ attempt.is_completed ? 'Completed' : 'In Progress' }}
                      </span>
                    </td>
                    <td>{{ formatDate(attempt.created_at) }}</td>
                    <td>
                      <div class="btn-group btn-group-sm" role="group">
                        <button 
                          v-if="!attempt.is_completed" 
                          @click="resumeTest(attempt)"
                          class="btn btn-outline-primary"
                          :disabled="actionLoading[`resume-${attempt.type}-${attempt.id}`]"
                          title="Resume Test"
                        >
                          <span v-if="actionLoading[`resume-${attempt.type}-${attempt.id}`]" 
                                class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                          <i v-else class="bi bi-play-fill"></i>
                          <span class="visually-hidden">Resume Test</span>
                        </button>
                        <button 
                          v-if="attempt.is_completed" 
                          @click="viewResults(attempt)"
                          class="btn btn-outline-success"
                          :disabled="actionLoading[`view-${attempt.type}-${attempt.id}`]"
                          title="View Results"
                        >
                          <span v-if="actionLoading[`view-${attempt.type}-${attempt.id}`]" 
                                class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                          <i v-else class="bi bi-eye"></i>
                          <span class="visually-hidden">View Results</span>
                        </button>
                        <button 
                          @click="retakeTest(attempt)"
                          class="btn btn-outline-info"
                          :disabled="actionLoading[`retake-${attempt.type}-${attempt.id}`]"
                          title="Retake Test"
                        >
                          <span v-if="actionLoading[`retake-${attempt.type}-${attempt.id}`]" 
                                class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                          <i v-else class="bi bi-arrow-clockwise"></i>
                          <span class="visually-hidden">Retake Test</span>
                        </button>
                        <button 
                          @click="deleteAttempt(attempt)"
                          class="btn btn-outline-danger"
                          :disabled="actionLoading[`delete-${attempt.type}-${attempt.id}`] || attempt.is_test_metadata"
                          :title="attempt.is_test_metadata ? 'Cannot delete test metadata - no specific attempts found' : 'Delete'"
                        >
                          <span v-if="actionLoading[`delete-${attempt.type}-${attempt.id}`]" 
                                class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                          <i v-else-if="attempt.is_test_metadata" class="bi bi-exclamation-triangle text-muted"></i>
                          <i v-else class="bi bi-trash"></i>
                          <span class="visually-hidden">{{ attempt.is_test_metadata ? 'Cannot Delete' : 'Delete' }}</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- Pagination Controls -->
          <div v-if="totalPages > 1" class="card-footer">
            <nav aria-label="Test history pagination">
              <ul class="pagination pagination-sm justify-content-center mb-0">
                <li class="page-item" :class="{ disabled: !hasPreviousPage }">
                  <button 
                    class="page-link" 
                    @click="currentPage = 1" 
                    :disabled="!hasPreviousPage"
                    title="First page"
                  >
                    <i class="bi bi-chevron-double-left"></i>
                  </button>
                </li>
                <li class="page-item" :class="{ disabled: !hasPreviousPage }">
                  <button 
                    class="page-link" 
                    @click="currentPage--" 
                    :disabled="!hasPreviousPage"
                    title="Previous page"
                  >
                    <i class="bi bi-chevron-left"></i>
                  </button>
                </li>
                
                <li 
                  v-for="page in pageNumbers" 
                  :key="page" 
                  class="page-item" 
                  :class="{ active: page === currentPage }"
                >
                  <button class="page-link" @click="currentPage = page">
                    {{ page }}
                  </button>
                </li>
                
                <li class="page-item" :class="{ disabled: !hasNextPage }">
                  <button 
                    class="page-link" 
                    @click="currentPage++" 
                    :disabled="!hasNextPage"
                    title="Next page"
                  >
                    <i class="bi bi-chevron-right"></i>
                  </button>
                </li>
                <li class="page-item" :class="{ disabled: !hasNextPage }">
                  <button 
                    class="page-link" 
                    @click="currentPage = totalPages" 
                    :disabled="!hasNextPage"
                    title="Last page"
                  >
                    <i class="bi bi-chevron-double-right"></i>
                  </button>
                </li>
              </ul>
            </nav>
            <div class="text-center mt-2">
              <small class="text-muted">
                Page {{ currentPage }} of {{ totalPages }} 
                ({{ filteredAttempts.length }} total tests)
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '@/services/api'

export default {
  name: 'UserHistory',
  data() {
    return {
      activeTab: 'all',
      mockAttempts: [],
      practiceAttempts: [],
      loading: true,
      error: null,
      currentPage: 1,
      itemsPerPage: 10,
      actionLoading: {}, // Track loading state for individual actions
      notifications: [], // Toast notifications
      notificationId: 0,
      confirmModal: {
        title: '',
        message: '',
        details: '',
        buttonText: '',
        buttonClass: '',
        action: null
      },
      statistics: {
        totalTests: 0,
        completedTests: 0,
        averageScore: 0,
        bestScore: 0
      },
      loggingIn: false
    }
  },
  computed: {
    allAttempts() {
      const mock = this.mockAttempts.map(attempt => ({
        ...attempt,
        type: 'mock'
      }))
      const practice = this.practiceAttempts.map(attempt => ({
        ...attempt,
        type: 'practice'
      }))
      return [...mock, ...practice].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    },
    filteredAttempts() {
      let filtered = []
      if (this.activeTab === 'all') filtered = this.allAttempts
      else if (this.activeTab === 'mock') filtered = this.allAttempts.filter(a => a.type === 'mock')
      else if (this.activeTab === 'practice') filtered = this.allAttempts.filter(a => a.type === 'practice')
      
      return filtered
    },
    paginatedAttempts() {
      const startIndex = (this.currentPage - 1) * this.itemsPerPage
      const endIndex = startIndex + this.itemsPerPage
      return this.filteredAttempts.slice(startIndex, endIndex)
    },
    totalPages() {
      return Math.ceil(this.filteredAttempts.length / this.itemsPerPage)
    },
    hasPreviousPage() {
      return this.currentPage > 1
    },
    hasNextPage() {
      return this.currentPage < this.totalPages
    },
    pageNumbers() {
      const pages = []
      const maxVisible = 5
      let start = Math.max(1, this.currentPage - Math.floor(maxVisible / 2))
      let end = Math.min(this.totalPages, start + maxVisible - 1)
      
      if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1)
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    },
    // Tab-specific statistics
    currentStatistics() {
      const attempts = this.filteredAttempts
      const completed = attempts.filter(a => a.is_completed)
      const scores = completed.map(a => a.percentage || 0).filter(score => score > 0)
      
      return {
        totalTests: attempts.length,
        completedTests: completed.length,
        averageScore: scores.length > 0 ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : 0,
        bestScore: scores.length > 0 ? Math.max(...scores) : 0
      }
    },
    isAuthenticated() {
      return !!window.localStorage.getItem('prepcheck_token')
    }
  },
  async mounted() {
    console.log('🔍 History.vue mounted - starting authentication check...')
    
    // Check if user is authenticated
    const token = localStorage.getItem('prepcheck_token')
    console.log('🔍 Auth token exists:', !!token)
    
    if (!token) {
      console.log('❌ No authentication token found')
      this.error = 'You are not logged in. Please log in to view your test history.'
      this.loading = false
      return
    }
    
    if (token) {
      console.log('🔍 Auth token preview:', token.substring(0, 50) + '...')
      
      // Try to decode the token to check if it's expired (basic check)
      try {
        const tokenParts = token.split('.')
        if (tokenParts.length === 3) {
          const payload = JSON.parse(atob(tokenParts[1]))
          const currentTime = Math.floor(Date.now() / 1000)
          if (payload.exp && payload.exp < currentTime) {
            console.log('❌ Authentication token has expired')
            this.error = 'Your session has expired. Please log in again.'
            this.loading = false
            // Optionally redirect to login
            // this.$router.push('/login')
            return
          }
          console.log('✅ Authentication token is valid (not expired)')
        }
      } catch (tokenError) {
        console.log('⚠️ Could not parse token:', tokenError.message)
      }
    }
    
    await this.fetchHistory()
  },
  methods: {
    async fetchHistory() {
      try {
        this.loading = true
        this.error = null
        
        console.log('🔍 History.vue: Starting fetchHistory...')
        
        // First, get statistics from UGC NET (this has real data)
        let ugcStats = null
        try {
          console.log('🔍 Fetching UGC NET statistics...')
          const statsResponse = await apiService.ugcNet.getStatistics()
          console.log('📊 UGC NET Statistics response:', statsResponse)
          
          if (statsResponse.success && statsResponse.data) {
            ugcStats = statsResponse.data
            // Set statistics from UGC NET data
            if (ugcStats.user_stats) {
              this.statistics = {
                totalTests: ugcStats.user_stats.total_attempts || 0,
                completedTests: ugcStats.user_stats.completed_attempts || ugcStats.user_stats.total_attempts || 0,
                averageScore: Math.round(ugcStats.user_stats.average_score || 0),
                bestScore: Math.round(ugcStats.user_stats.best_score || 0)
              }
              console.log('✅ Statistics loaded from UGC NET:', this.statistics)
            }
          } else {
            console.log('⚠️ UGC NET statistics response not successful:', statsResponse)
          }
        } catch (statsError) {
          console.error('❌ UGC NET statistics error:', statsError)
          console.log('📝 Stats error details:', {
            message: statsError.message,
            status: statsError.response?.status,
            data: statsError.response?.data
          })
        }

        // Try to get actual mock test attempts (not just test metadata)
        try {
          console.log('🔍 Fetching actual mock test attempts...')
          // We need to get actual attempts, not just test metadata
          // For now, let's try to get mock tests and then fetch their attempts
          const mockTestsResponse = await apiService.ugcNet.getMockTests()
          console.log('📋 Mock tests response:', mockTestsResponse)
          
          if (mockTestsResponse.success && mockTestsResponse.data) {
            const mockTests = mockTestsResponse.data.mock_tests || mockTestsResponse.data || []
            console.log('📝 Available mock tests:', mockTests.length)
            
            // For each test that has attempts, try to get the actual attempt data
            const allMockAttempts = []
            for (const test of mockTests) {
              console.log(`🔍 Processing test ${test.id}: ${test.title}, user_attempts: ${test.user_attempts}`)
              
              if (test.user_attempts > 0) {
                try {
                  console.log(`� Fetching attempts for test ${test.id}...`)
                  const attemptsResponse = await apiService.ugcNet.getUserAttempts(test.id)
                  console.log(`📊 Attempts for test ${test.id}:`, attemptsResponse)
                  
                  if (attemptsResponse.success && attemptsResponse.data && attemptsResponse.data.attempts) {
                    // Add actual attempt data
                    const testAttempts = attemptsResponse.data.attempts.map(attempt => ({
                      ...attempt,
                      type: 'mock',
                      test_name: test.title,
                      subject_name: test.subject_name || 'UGC NET'
                    }))
                    allMockAttempts.push(...testAttempts)
                    console.log(`✅ Added ${testAttempts.length} attempts for test ${test.id}`)
                  } else {
                    console.log(`⚠️ No attempt data in response for test ${test.id}:`, attemptsResponse)
                  }
                } catch (attemptError) {
                  console.error(`❌ Failed to fetch attempts for test ${test.id}:`, attemptError)
                  console.log('📝 Attempt error details:', {
                    message: attemptError.message,
                    status: attemptError.response?.status,
                    data: attemptError.response?.data
                  })
                  
                  // Fallback: create a display entry from test data (but mark it as non-deletable)
                  console.log(`🔄 Creating fallback entry for test ${test.id}`)
                  allMockAttempts.push({
                    id: `test-${test.id}`, // Prefix to indicate this is test data, not attempt data
                    test_id: test.id,
                    test_name: test.title,
                    subject_name: test.subject_name || 'UGC NET',
                    total_questions: test.total_questions,
                    percentage: test.best_score || 0,
                    is_completed: test.best_score !== null,
                    created_at: test.last_attempt_date || test.created_at,
                    type: 'mock',
                    is_test_metadata: true // Flag to indicate this is not a real attempt
                  })
                }
              }
            }
            
            this.mockAttempts = allMockAttempts
            console.log('✅ Final mock attempts loaded:', this.mockAttempts.length)
          } else {
            console.log('⚠️ Mock tests response not successful:', mockTestsResponse)
          }
        } catch (mockError) {
          console.error('❌ Mock tests error:', mockError)
          console.log('📝 Mock error details:', {
            message: mockError.message,
            status: mockError.response?.status,
            data: mockError.response?.data
          })
          this.mockAttempts = []
        }

        // Try to get practice history separately
        try {
          console.log('🔍 Fetching practice test history...')
          const practiceResponse = await apiService.ugcNet.getPracticeHistory()
          console.log('📋 Practice response:', practiceResponse)
          
          if (practiceResponse.success && practiceResponse.data) {
            this.practiceAttempts = (practiceResponse.data.practice_attempts || practiceResponse.data.attempts || practiceResponse.data || [])
              .map(attempt => ({
                ...attempt,
                type: 'practice'
              }))
            console.log('✅ Practice attempts loaded:', this.practiceAttempts.length)
          } else {
            console.log('⚠️ Practice response not successful:', practiceResponse)
            this.practiceAttempts = []
          }
        } catch (practiceError) {
          console.error('❌ Practice history error:', practiceError)
          console.log('📝 Practice error details:', {
            message: practiceError.message,
            status: practiceError.response?.status,
            data: practiceError.response?.data
          })
          this.practiceAttempts = []
        }

        // If we have statistics but no detailed attempts, we still show the stats
        if (this.mockAttempts.length === 0 && this.practiceAttempts.length === 0 && ugcStats) {
          // Create placeholder entries if we have stats but no detailed history
          console.log('No detailed history found, but statistics indicate tests were taken')
        }
        
        // If no statistics were set from UGC NET, calculate them from attempts
        if (this.statistics.totalTests === 0) {
          this.calculateStatistics()
        }
        
        console.log('📊 Final summary:')
        console.log('  - Mock attempts:', this.mockAttempts.length)
        console.log('  - Practice attempts:', this.practiceAttempts.length)
        console.log('  - Statistics:', this.statistics)
        console.log('  - Total attempts available for delete testing:', this.allAttempts.length)
        
        // If we have no data at all, it might be an authentication or API issue
        if (this.mockAttempts.length === 0 && this.practiceAttempts.length === 0 && this.statistics.totalTests === 0) {
          console.log('⚠️ No data loaded - checking possible causes...')
          
          // Check authentication
          const token = localStorage.getItem('prepcheck_token')
          if (!token) {
            console.log('❌ No authentication token found')
            this.error = 'You are not logged in. Please log in to view your test history.'
            return
          }
          
          console.log('✅ Authentication token exists')
          console.log('🔍 This might be a new user with no test history, or an API connectivity issue')
        }
        
      } catch (error) {
        console.error('❌ Critical error in fetchHistory:', error)
        console.log('📝 Critical error details:', {
          message: error.message,
          stack: error.stack,
          name: error.name
        })
        
        // Check if it's a network error
        if (error.message && error.message.includes('fetch')) {
          this.error = 'Cannot connect to the server. Please check your internet connection and try again.'
        } else if (error.response?.status === 401) {
          this.error = 'Your session has expired. Please log in again.'
        } else if (error.response?.status === 403) {
          this.error = 'You do not have permission to access this data.'
        } else {
          this.error = 'Failed to load test history. Please refresh the page and try again.'
        }
      } finally {
        this.loading = false
      }
    },
    calculateStatistics() {
      const all = this.allAttempts
      const completed = all.filter(a => a.is_completed)
      
      this.statistics = {
        totalTests: all.length,
        completedTests: completed.length,
        averageScore: completed.length > 0 ? 
          Math.round(completed.reduce((sum, a) => sum + (a.percentage || 0), 0) / completed.length) : 0,
        bestScore: completed.length > 0 ? 
          Math.max(...completed.map(a => a.percentage || 0)) : 0
      }
    },
    async resumeTest(attempt) {
      const loadingKey = `resume-${attempt.type}-${attempt.id}`
      
      if (!attempt || !attempt.id) {
        this.showNotification('Invalid test data. Please refresh the page and try again.', 'error')
        return
      }
      
      try {
        this.actionLoading[loadingKey] = true
        console.log('Resuming test:', attempt)
        
        if (attempt.type === 'mock') {
          // For mock tests, navigate directly to test taking page
          const testId = attempt.mock_test_id || attempt.test_id || attempt.id
          const attemptId = attempt.id
          console.log('Resuming mock test with testId:', testId, 'attemptId:', attemptId)
          
          // Navigate directly using URL path with attempt ID for proper resume
          const testUrl = `/ugc-net/test/${testId}/attempt/${attemptId}`
          console.log('Mock test URL:', testUrl)
          await this.$router.push(testUrl)
          this.showNotification('Resuming test...', 'success')
          
        } else {
          // For practice tests, navigate directly to practice taking page
          console.log('Resuming practice test with attemptId:', attempt.id)
          
          const practiceUrl = `/ugc-net/practice/${attempt.id}/take`
          console.log('Practice test URL:', practiceUrl)
          await this.$router.push(practiceUrl)
          this.showNotification('Resuming practice test...', 'success')
        }
      } catch (error) {
        console.error('Error resuming test:', error)
        
        // Specific fallback based on test type
        if (attempt.type === 'mock') {
          console.log('Mock test resume failed, redirecting to UGC NET dashboard')
          this.$router.push('/ugc-net')
          this.showNotification('Unable to resume the specific test. Redirected to UGC NET dashboard where you can find and restart the test.', 'warning', 6000)
        } else {
          console.log('Practice test resume failed, redirecting to practice setup')
          this.$router.push('/ugc-net/practice/setup')
          this.showNotification('Unable to resume the practice test. Redirected to practice setup where you can start a new test.', 'warning', 6000)
        }
      } finally {
        this.actionLoading[loadingKey] = false
      }
    },
    async viewResults(attempt) {
      const loadingKey = `view-${attempt.type}-${attempt.id}`
      
      if (!attempt || !attempt.id) {
        this.showNotification('Invalid test data. Please refresh the page and try again.', 'error')
        return
      }
      
      try {
        this.actionLoading[loadingKey] = true
        console.log('Viewing results for:', attempt)
        console.log('Attempt details:', {
          id: attempt.id,
          test_id: attempt.test_id,
          type: attempt.type,
          is_completed: attempt.is_completed
        })
        
        if (attempt.type === 'mock') {
          // For mock tests, navigate directly to results page using URL path
          const testId = attempt.test_id || attempt.id
          console.log('Navigating directly to mock test results with testId:', testId, 'attemptId:', attempt.id)
          
          // Try direct URL navigation first
          let resultsUrl = `/ugc-net/test/${testId}/results`
          if (attempt.id && attempt.test_id && attempt.id !== attempt.test_id) {
            // If we have a specific attempt ID different from test ID, use it
            resultsUrl = `/ugc-net/test/${testId}/attempt/${attempt.id}/results`
          }
          
          console.log('Mock test results URL:', resultsUrl)
          await this.$router.push(resultsUrl)
          this.showNotification('Loading test results...', 'success')
          
        } else {
          // For practice tests, navigate directly to practice results page
          console.log('Navigating directly to practice results with attemptId:', attempt.id)
          
          const practiceResultsUrl = `/ugc-net/practice/${attempt.id}/results`
          console.log('Practice results URL:', practiceResultsUrl)
          await this.$router.push(practiceResultsUrl)
          this.showNotification('Loading practice test results...', 'success')
        }
      } catch (error) {
        console.error('Error viewing results:', error)
        
        // More specific fallback based on test type
        if (attempt.type === 'mock') {
          console.log('Mock test results failed, redirecting to UGC NET dashboard')
          this.$router.push('/ugc-net')
          this.showNotification('Unable to load specific test results. Redirected to UGC NET dashboard where you can find your test history.', 'warning', 6000)
        } else {
          console.log('Practice results failed, redirecting to practice setup')
          this.$router.push('/ugc-net/practice/setup')
          this.showNotification('Unable to load practice test results. Redirected to practice setup where you can start a new test.', 'warning', 6000)
        }
      } finally {
        this.actionLoading[loadingKey] = false
      }
    },
    async deleteAttempt(attempt) {
      const loadingKey = `delete-${attempt.type}-${attempt.id}`
      
      if (!attempt || !attempt.id) {
        this.showNotification('Invalid test data. Please refresh the page and try again.', 'error')
        return
      }
      
      // Check if this is test metadata rather than an actual attempt
      if (attempt.is_test_metadata) {
        this.showNotification('Cannot delete test metadata. This entry represents a test you took, but the specific attempt data is not available.', 'warning', 8000)
        return
      }
      
      // Show confirmation dialog instead of browser confirm
      const details = `<strong>Test:</strong> ${attempt.test_name || attempt.chapter_name}<br>
                      <strong>Score:</strong> ${attempt.percentage || 0}%<br><br>
                      <strong>This action cannot be undone.</strong>`
      
      this.showConfirmDialog(
        'Delete Test Attempt',
        `Are you sure you want to delete this ${attempt.type} test attempt?`,
        details,
        'Delete',
        'btn-danger',
        async () => {
          try {
            this.actionLoading[loadingKey] = true
            console.log('Deleting attempt:', attempt)
            
            let deleteResult = null
            
            // Call the appropriate backend API
            console.log('🔍 About to call delete API for:', { 
              type: attempt.type, 
              id: attempt.id, 
              test_id: attempt.test_id,
              fullAttempt: attempt 
            })
            
            // Check if this is actually a real attempt or just display data
            if (attempt.type === 'mock') {
              // For mock tests, the ID might be the test ID, not the attempt ID
              // Let's check if we have actual attempt data
              console.log('🔍 Mock test data analysis:', {
                hasTestId: !!attempt.test_id,
                hasAttemptId: !!attempt.id,
                isTestIdSameAsId: attempt.test_id === attempt.id,
                hasUserAttempts: attempt.user_attempts,
                isTestMetadata: attempt.is_test_metadata,
                dataSource: 'Mock test attempt data'
              })
              
              if (attempt.is_test_metadata) {
                console.log('⚠️ This is test metadata, not an actual attempt. Should have been caught earlier.')
                this.showNotification('Cannot delete test metadata.', 'warning')
                return
              }
              
              console.log('🔍 Calling deleteMockTestAttempt with ID:', attempt.id)
              deleteResult = await apiService.ugcNet.deleteMockTestAttempt(attempt.id)
            } else {
              console.log('🔍 Calling deletePracticeTestAttempt with ID:', attempt.id)
              deleteResult = await apiService.ugcNet.deletePracticeTestAttempt(attempt.id)
            }
            console.log('🔍 Delete API result:', deleteResult)
            
            if (deleteResult && deleteResult.success) {
              // Remove from local state after successful backend deletion
              if (attempt.type === 'mock') {
                this.mockAttempts = this.mockAttempts.filter(a => a.id !== attempt.id)
              } else {
                this.practiceAttempts = this.practiceAttempts.filter(a => a.id !== attempt.id)
              }
              
              // Recalculate statistics
              this.calculateStatistics()
              
              // Show success notification
              this.showNotification(
                `${attempt.type === 'mock' ? 'Mock test' : 'Practice test'} attempt deleted successfully.`,
                'success'
              )
              
              // Reset to first page if current page is now empty
              if (this.paginatedAttempts.length === 0 && this.currentPage > 1) {
                this.currentPage = Math.max(1, this.currentPage - 1)
              }
            } else {
              console.error('Delete failed:', deleteResult?.error)
              console.error('Full delete result:', deleteResult)
              const errorMessage = deleteResult?.error || 'Failed to delete test attempt. Please try again.'
              console.error('Showing error notification:', errorMessage)
              this.showNotification(errorMessage, 'error')
            }
            
          } catch (error) {
            console.error('Error deleting attempt:', error)
            let errorMessage = 'Failed to delete test attempt. Please try again.'
            
            // Check for specific error types
            if (error.response?.status === 401) {
              errorMessage = 'You are not authenticated. Please log in and try again.'
            } else if (error.response?.status === 404) {
              errorMessage = 'Test attempt not found. It may have already been deleted.'
            } else if (error.response?.status === 403) {
              errorMessage = 'You do not have permission to delete this test attempt.'
            } else if (error.message) {
              errorMessage = `Error: ${error.message}`
            }
            
            console.error('Showing error notification:', errorMessage)
            this.showNotification(errorMessage, 'error')
          } finally {
            this.actionLoading[loadingKey] = false
          }
        }
      )
    },
    getTypeBadgeClass(type) {
      return type === 'mock' ? 'bg-primary' : 'bg-success'
    },
    getScoreBadgeClass(score) {
      if (score >= 80) return 'bg-success'
      if (score >= 60) return 'bg-warning'
      return 'bg-danger'
    },
    getStatusBadgeClass(isCompleted) {
      return isCompleted ? 'bg-success' : 'bg-warning'
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    async retakeTest(attempt) {
      const loadingKey = `retake-${attempt.type}-${attempt.id}`
      
      if (!attempt || !attempt.type) {
        this.showNotification('Invalid test data. Please refresh the page and try again.', 'error')
        return
      }
      
      try {
        this.actionLoading[loadingKey] = true
        console.log('Retaking test:', attempt)
        
        // Debug the attempt data
        this.debugAttemptData(attempt)
        
        // Show initial feedback
        this.showNotification('Preparing to retake test...', 'info', 2000)
        
        // Add a small delay to show loading state
        await new Promise(resolve => setTimeout(resolve, 300))
        
        if (attempt.type === 'mock') {
          // For mock tests, navigate directly to test taking page
          const testId = attempt.test_id || attempt.id
          console.log('Navigating directly to mock test taking page with testId:', testId)
          
          // Navigate directly to test taking page without checking route resolution
          await this.$router.push(`/ugc-net/test/${testId}/take`)
          this.showNotification('Starting mock test...', 'success')
          
        } else {
          // For practice tests, navigate to practice setup with parameters
          console.log('Navigating to practice setup with parameters')
          
          let practiceUrl = '/ugc-net/practice/setup'
          const params = []
          
          if (attempt.subject_id) {
            params.push(`subject_id=${attempt.subject_id}`)
          }
          if (attempt.chapter_id) {
            params.push(`chapter_id=${attempt.chapter_id}`)
          }
          
          if (params.length > 0) {
            practiceUrl += '?' + params.join('&')
          }
          
          console.log('Practice URL:', practiceUrl)
          await this.$router.push(practiceUrl)
          this.showNotification('Redirected to practice setup with your previous selection.', 'success')
        }
        
      } catch (error) {
        console.error('Error retaking test:', error)
        
        // Specific fallback based on test type - no more general dashboard fallback
        if (attempt.type === 'mock') {
          console.log('Mock test retake failed, redirecting to UGC NET dashboard')
          this.$router.push('/ugc-net')
          this.showNotification('Unable to directly retake the test. Redirected to UGC NET dashboard where you can find and retake the test.', 'warning', 6000)
        } else {
          console.log('Practice test retake failed, redirecting to practice setup')
          this.$router.push('/ugc-net/practice/setup')
          this.showNotification('Unable to directly retake the test. Redirected to practice setup where you can configure and start a new practice test.', 'warning', 6000)
        }
      } finally {
        this.actionLoading[loadingKey] = false
      }
    },
    changeTab(tab) {
      console.log('🔍 Changing tab from', this.activeTab, 'to', tab)
      console.log('📊 Current data state:', {
        mockAttempts: this.mockAttempts.length,
        practiceAttempts: this.practiceAttempts.length,
        allAttempts: this.allAttempts.length
      })
      
      // Log detailed data for debugging
      console.log('📝 Mock attempts data:', this.mockAttempts)
      console.log('📝 Practice attempts data:', this.practiceAttempts)
      console.log('📝 All attempts data:', this.allAttempts)
      
      this.activeTab = tab
      this.currentPage = 1 // Reset to first page when changing tabs
      
      console.log('✅ Tab changed to:', this.activeTab)
      console.log('📋 Filtered attempts for', tab, ':', this.filteredAttempts.length)
      console.log('📋 Filtered attempts data:', this.filteredAttempts)
      
      // Force reactivity update
      this.$forceUpdate()
    },
    // Notification system methods
    showNotification(message, type = 'info', duration = 5000) {
      const notification = {
        id: ++this.notificationId,
        message,
        type
      }
      this.notifications.push(notification)
      
      // Auto remove after duration
      setTimeout(() => {
        this.removeNotification(this.notifications.findIndex(n => n.id === notification.id))
      }, duration)
    },
    removeNotification(index) {
      if (index >= 0 && index < this.notifications.length) {
        this.notifications.splice(index, 1)
      }
    },
    getNotificationClass(type) {
      const classes = {
        success: 'bg-success',
        error: 'bg-danger',
        warning: 'bg-warning',
        info: 'bg-info'
      }
      return classes[type] || 'bg-info'
    },
    getNotificationIcon(type) {
      const icons = {
        success: 'bi bi-check-circle-fill',
        error: 'bi bi-exclamation-triangle-fill',
        warning: 'bi bi-exclamation-triangle-fill',
        info: 'bi bi-info-circle-fill'
      }
      return icons[type] || 'bi bi-info-circle-fill'
    },
    showConfirmDialog(title, message, details, buttonText, buttonClass, action) {
      this.confirmModal = {
        title,
        message,
        details,
        buttonText,
        buttonClass,
        action
      }
      
      // Show the modal using Bootstrap's modal API
      this.$nextTick(() => {
        const modalElement = this.$refs.confirmModal
        if (modalElement) {
          // Use Bootstrap 5 modal
          if (window.bootstrap && window.bootstrap.Modal) {
            const modal = new window.bootstrap.Modal(modalElement)
            modal.show()
          } else {
            // Fallback: manually trigger modal
            modalElement.classList.add('show')
            modalElement.style.display = 'block'
            document.body.classList.add('modal-open')
            
            // Auto close after 10 seconds if user doesn't interact
            setTimeout(() => {
              if (modalElement.classList.contains('show')) {
                this.closeModal()
              }
            }, 10000)
          }
        }
      })
    },
    closeModal() {
      const modalElement = this.$refs.confirmModal
      if (modalElement) {
        modalElement.classList.remove('show')
        modalElement.style.display = 'none'
        document.body.classList.remove('modal-open')
      }
    },
    debugAttemptData(attempt) {
      // Helper method to debug attempt data structure
      console.log('Attempt Data Debug:', {
        id: attempt.id,
        type: attempt.type,
        test_id: attempt.test_id,
        test_name: attempt.test_name,
        chapter_id: attempt.chapter_id,
        chapter_name: attempt.chapter_name,
        subject_id: attempt.subject_id,
        subject_name: attempt.subject_name,
        is_completed: attempt.is_completed,
        allKeys: Object.keys(attempt)
      })
      
      // Show debug info to user in development
      if (process.env.NODE_ENV === 'development') {
        this.showNotification(`Debug: ${attempt.type} test - ID: ${attempt.id}`, 'info', 3000)
      }
    },
    async quickLogin() {
      try {
        this.loggingIn = true
        this.showNotification('Attempting to log in...', 'info')
        
        // Use the API service to login
        const response = await apiService.auth.login({
          email: 'student1@test.com',
          password: 'Student123'
        })
        
        console.log('Quick login response:', response)
        
        if (response.success && response.data?.access_token) {
          // Store the token
          localStorage.setItem('prepcheck_token', response.data.access_token)
          
          this.showNotification('✅ Login successful! Refreshing test history...', 'success')
          
          // Clear error and reload data
          this.error = null
          await this.fetchHistory()
        } else {
          console.error('Login failed:', response)
          this.showNotification('❌ Login failed. Please try again.', 'error')
        }
      } catch (error) {
        console.error('Quick login error:', error)
        this.showNotification(`❌ Login error: ${error.message}`, 'error')
      } finally {
        this.loggingIn = false
      }
    }
  }
}
</script>

<style scoped>
.container-fluid {
  max-width: 1200px;
}

.nav-tabs .nav-link {
  border: none;
  color: #6c757d;
  padding: 0.75rem 1rem;
}

.nav-tabs .nav-link.active {
  color: #495057;
  background-color: #fff;
  border-bottom: 2px solid #007bff;
}

.nav-tabs .nav-link:hover {
  color: #007bff;
}

.table th {
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

.table td {
  vertical-align: middle;
}

.badge {
  font-size: 0.75rem;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  min-width: 32px;
  min-height: 32px;
}

.btn-group-sm .btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.btn-group-sm .btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-group-sm .btn .spinner-border-sm {
  width: 0.75rem;
  height: 0.75rem;
}

.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.display-4 {
  font-size: 2.5rem;
}

.opacity-75 {
  opacity: 0.75;
}

@media (max-width: 768px) {
  .btn-group {
    flex-direction: column;
  }
  
  .btn-group .btn {
    margin-bottom: 0.25rem;
  }
  
  .nav-tabs .nav-link {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
  }
  
  .toast-container {
    left: 50%;
    transform: translateX(-50%);
    right: auto;
  }
}

/* Toast notifications */
.toast {
  min-width: 300px;
  margin-bottom: 0.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toast .toast-body {
  padding: 0.75rem 1rem;
  font-weight: 500;
}

.toast.bg-success {
  background-color: #198754 !important;
}

.toast.bg-danger {
  background-color: #dc3545 !important;
}

.toast.bg-warning {
  background-color: #fd7e14 !important;
}

.toast.bg-info {
  background-color: #0dcaf0 !important;
}

/* Modal improvements */
.modal-content {
  border-radius: 0.5rem;
  border: none;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.modal-header {
  border-bottom: 1px solid #dee2e6;
  padding: 1.25rem;
}

.modal-body {
  padding: 1.25rem;
}

.modal-footer {
  border-top: 1px solid #dee2e6;
  padding: 1rem 1.25rem;
}
</style>
