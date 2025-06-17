<template>
  <div class="quiz-results-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="bi bi-bar-chart me-2"></i>Quiz Results & Reports</h2>
      <div class="btn-group">
        <button class="btn btn-outline-primary" @click="exportResults">
          <i class="bi bi-download me-1"></i>Export Results
        </button>
        <button class="btn btn-outline-secondary" @click="loadResults">
          <i class="bi bi-arrow-clockwise me-1"></i>Refresh
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card border-primary">
          <div class="card-body text-center">
            <i class="bi bi-people-fill text-primary display-4"></i>
            <h3 class="text-primary mt-2">{{ summary.total_attempts || 0 }}</h3>
            <p class="text-muted mb-0">Total Attempts</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-success">
          <div class="card-body text-center">
            <i class="bi bi-check-circle-fill text-success display-4"></i>
            <h3 class="text-success mt-2">{{ summary.avg_score || 0 }}%</h3>
            <p class="text-muted mb-0">Average Score</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-warning">
          <div class="card-body text-center">
            <i class="bi bi-clock-fill text-warning display-4"></i>
            <h3 class="text-warning mt-2">{{ formatTime(summary.avg_time || 0) }}</h3>
            <p class="text-muted mb-0">Average Time</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-info">
          <div class="card-body text-center">
            <i class="bi bi-graph-up text-info display-4"></i>
            <h3 class="text-info mt-2">{{ summary.pass_rate || 0 }}%</h3>
            <p class="text-muted mb-0">Pass Rate</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label">Quiz</label>
            <select v-model="filters.quiz_id" class="form-select" @change="loadResults">
              <option value="">All Quizzes</option>
              <option v-for="quiz in quizzes" :key="quiz.id" :value="quiz.id">
                {{ quiz.title }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">User</label>
            <select v-model="filters.user_id" class="form-select" @change="loadResults">
              <option value="">All Users</option>
              <option v-for="user in users" :key="user.id" :value="user.id">
                {{ user.full_name }} ({{ user.email }})
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Date Range</label>
            <select v-model="filters.date_range" class="form-select" @change="loadResults">
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Status</label>
            <select v-model="filters.status" class="form-select" @change="loadResults">
              <option value="">All Status</option>
              <option value="completed">Completed</option>
              <option value="in_progress">In Progress</option>
              <option value="abandoned">Abandoned</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Results Table -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading results...</p>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          <i class="bi bi-exclamation-triangle me-2"></i>
          {{ error }}
        </div>

        <div v-else>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead class="table-light">
                <tr>
                  <th>User</th>
                  <th>Quiz</th>
                  <th>Score</th>
                  <th>Percentage</th>
                  <th>Time Taken</th>
                  <th>Status</th>
                  <th>Submitted At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="attempt in attempts" :key="attempt.id">
                  <td>
                    <div class="d-flex align-items-center">
                      <img 
                        :src="attempt.user.profile_picture_url || '/default-avatar.png'" 
                        :alt="attempt.user.full_name"
                        class="rounded-circle me-2"
                        width="32"
                        height="32"
                      >
                      <div>
                        <div class="fw-medium">{{ attempt.user.full_name }}</div>
                        <small class="text-muted">{{ attempt.user.email }}</small>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div>
                      <div class="fw-medium">{{ attempt.quiz.title }}</div>
                      <small class="text-muted">{{ attempt.quiz.subject_name }}</small>
                    </div>
                  </td>
                  <td>
                    <span class="fw-medium">{{ attempt.score || 0 }}</span>
                    <span class="text-muted">/ {{ attempt.total_marks || 0 }}</span>
                  </td>
                  <td>
                    <div class="d-flex align-items-center">
                      <div class="progress me-2" style="width: 60px; height: 8px;">
                        <div 
                          class="progress-bar"
                          :class="{
                            'bg-success': attempt.percentage >= 80,
                            'bg-warning': attempt.percentage >= 60 && attempt.percentage < 80,
                            'bg-danger': attempt.percentage < 60
                          }"
                          :style="{ width: attempt.percentage + '%' }"
                        ></div>
                      </div>
                      <span class="fw-medium">{{ attempt.percentage || 0 }}%</span>
                    </div>
                  </td>
                  <td>{{ formatTime(attempt.time_taken) }}</td>
                  <td>
                    <span 
                      class="badge"
                      :class="{
                        'bg-success': attempt.is_completed,
                        'bg-warning': !attempt.is_completed && attempt.started_at,
                        'bg-secondary': !attempt.started_at
                      }"
                    >
                      {{ getAttemptStatus(attempt) }}
                    </span>
                  </td>
                  <td>{{ formatDate(attempt.completed_at || attempt.started_at) }}</td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button 
                        class="btn btn-outline-info"
                        @click="viewDetails(attempt)"
                        title="View Details"
                      >
                        <i class="bi bi-eye"></i>
                      </button>
                      <button 
                        class="btn btn-outline-primary"
                        @click="downloadReport(attempt)"
                        title="Download Report"
                      >
                        <i class="bi bi-download"></i>
                      </button>
                      <button 
                        v-if="!attempt.is_completed"
                        class="btn btn-outline-warning"
                        @click="resetAttempt(attempt)"
                        title="Reset Attempt"
                      >
                        <i class="bi bi-arrow-clockwise"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <div v-if="attempts.length === 0" class="text-center py-4">
              <i class="bi bi-clipboard-data text-muted" style="font-size: 3rem;"></i>
              <p class="text-muted mt-2">No quiz attempts found matching your criteria</p>
            </div>
          </div>

          <!-- Pagination -->
          <nav v-if="totalPages > 1" class="mt-4">
            <ul class="pagination justify-content-center">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link" @click="changePage(currentPage - 1)">Previous</button>
              </li>
              <li 
                v-for="page in totalPages" 
                :key="page" 
                class="page-item" 
                :class="{ active: page === currentPage }"
              >
                <button class="page-link" @click="changePage(page)">{{ page }}</button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link" @click="changePage(currentPage + 1)">Next</button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- Detailed Results Modal -->
    <AttemptDetailsModal
      v-if="showDetailsModal"
      :show="showDetailsModal"
      :attempt="selectedAttempt"
      @close="showDetailsModal = false"
    />
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import adminService from '@/services/adminService'
import analyticsService from '@/services/analyticsService'
import apiClient from '@/services/apiClient'
import AttemptDetailsModal from '@/components/modals/AttemptDetailsModal.vue'

export default {
  name: 'QuizResults',
  components: {
    AttemptDetailsModal
  },
  setup() {
    
    // State
    const loading = ref(false)
    const error = ref('')
    const attempts = ref([])
    const quizzes = ref([])
    const users = ref([])
    const summary = ref({})
    
    // Pagination
    const currentPage = ref(1)
    const totalPages = ref(1)
    const perPage = ref(20)
    
    // Modal
    const showDetailsModal = ref(false)
    const selectedAttempt = ref(null)
    
    // Filters
    const filters = reactive({
      quiz_id: '',
      user_id: '',
      date_range: '',
      status: ''
    })
    
    // Load data
    const loadResults = async () => {
      try {
        loading.value = true
        error.value = ''
        
        const params = {
          page: currentPage.value,
          per_page: perPage.value,
          ...filters
        }
        
        const response = await apiClient.get('/admin/quiz-attempts', { params })
        
        attempts.value = response.attempts || []
        totalPages.value = response.total_pages || 1
        summary.value = response.summary || {}
        
      } catch (err) {
        error.value = err.response?.data?.message || 'Failed to load results'
        console.error('Error loading results:', err)
      } finally {
        loading.value = false
      }
    }
    
    const loadQuizzes = async () => {
      try {
        const response = await adminService.getQuizzes()
        quizzes.value = response.quizzes || []
      } catch (err) {
        console.error('Error loading quizzes:', err)
      }
    }
    
    const loadUsers = async () => {
      try {
        const response = await adminService.getAllUsers()
        users.value = response.users || []
      } catch (err) {
        console.error('Error loading users:', err)
      }
    }
    
    // Actions
    const viewDetails = (attempt) => {
      selectedAttempt.value = attempt
      showDetailsModal.value = true
    }
    
    const downloadReport = async (attempt) => {
      try {
        const response = await apiClient.downloadFile(`/admin/quiz-attempts/${attempt.id}/report`)
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `quiz-report-${attempt.id}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to download report')
        console.error('Error downloading report:', err)
      }
    }
    
    const resetAttempt = async (attempt) => {
      if (confirm('Are you sure you want to reset this attempt? This will allow the user to retake the quiz.')) {
        try {
          await apiClient.post(`/admin/quiz-attempts/${attempt.id}/reset`)
          await loadResults()
          alert('Attempt reset successfully!')
        } catch (err) {
          alert(err.response?.data?.message || 'Failed to reset attempt')
          console.error('Error resetting attempt:', err)
        }
      }
    }
    
    const exportResults = async () => {
      try {
        const response = await apiClient.post('/admin/export/quiz-results', filters)
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'quiz-results.csv')
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to export results')
        console.error('Error exporting results:', err)
      }
    }
    
    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadResults()
      }
    }
    
    // Utility functions
    const formatTime = (seconds) => {
      if (!seconds) return 'N/A'
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
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    }
    
    const getAttemptStatus = (attempt) => {
      if (attempt.is_completed) {
        return 'Completed'
      } else if (attempt.started_at) {
        return 'In Progress'
      } else {
        return 'Not Started'
      }
    }
    
    // Initialize
    onMounted(async () => {
      await Promise.all([
        loadResults(),
        loadQuizzes(),
        loadUsers()
      ])
    })
    
    return {
      // State
      loading,
      error,
      attempts,
      quizzes,
      users,
      summary,
      currentPage,
      totalPages,
      filters,
      
      // Modal
      showDetailsModal,
      selectedAttempt,
      
      // Methods
      loadResults,
      viewDetails,
      downloadReport,
      resetAttempt,
      exportResults,
      changePage,
      formatTime,
      formatDate,
      getAttemptStatus
    }
  }
}
</script>

<style scoped>
.quiz-results-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.table td {
  vertical-align: middle;
}

.progress {
  border-radius: 10px;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.page-link {
  cursor: pointer;
}

.page-item.disabled .page-link {
  cursor: not-allowed;
}
</style>
