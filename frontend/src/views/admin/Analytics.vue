<template>
  <div class="analytics-dashboard">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">Analytics Dashboard</h2>
      <div class="d-flex gap-2">
        <select v-model="selectedPeriod" @change="loadAnalytics" class="form-select" style="width: auto;">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="365">Last year</option>
        </select>
        <button class="btn btn-outline-primary" @click="loadAnalytics">
          <i class="bi bi-arrow-clockwise me-2"></i>Refresh
        </button>
        <button class="btn btn-success" @click="exportAnalytics">
          <i class="bi bi-download me-2"></i>Export
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading analytics...</span>
      </div>
    </div>

    <!-- Analytics Content -->
    <div v-else-if="analytics">
      <!-- Key Metrics Cards -->
      <div class="row mb-4">
        <div class="col-md-3 mb-3">
          <div class="card bg-primary text-white">
            <div class="card-body text-center">
              <i class="bi bi-people display-4 mb-3"></i>
              <h3 class="mb-1">{{ analytics.stats.total_users }}</h3>
              <p class="mb-0">Total Users</p>
              <small class="opacity-75">{{ analytics.stats.active_users }} active</small>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-success text-white">
            <div class="card-body text-center">
              <i class="bi bi-clipboard-check display-4 mb-3"></i>
              <h3 class="mb-1">{{ analytics.stats.total_attempts }}</h3>
              <p class="mb-0">Total Attempts</p>
              <small class="opacity-75">{{ analytics.stats.recent_attempts }} recent</small>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-info text-white">
            <div class="card-body text-center">
              <i class="bi bi-graph-up display-4 mb-3"></i>
              <h3 class="mb-1">{{ analytics.performance.average_percentage }}%</h3>
              <p class="mb-0">Avg Score</p>
              <small class="opacity-75">{{ analytics.performance.pass_rate }}% pass rate</small>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-warning text-white">
            <div class="card-body text-center">
              <i class="bi bi-clock display-4 mb-3"></i>
              <h3 class="mb-1">{{ analytics.performance.average_time_minutes }}</h3>
              <p class="mb-0">Avg Time (min)</p>
              <small class="opacity-75">per quiz</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="row mb-4">
        <!-- Daily Trends Chart -->
        <div class="col-lg-8 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-graph-up me-2"></i>Daily Activity Trends
              </h5>
            </div>
            <div class="card-body">
              <canvas ref="dailyChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- User Engagement -->
        <div class="col-lg-4 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-people me-2"></i>User Engagement
              </h5>
            </div>
            <div class="card-body">
              <div class="text-center mb-3">
                <div class="display-6 fw-bold text-success">{{ analytics.engagement.retention_rate }}%</div>
                <small class="text-muted">Retention Rate</small>
              </div>
              
              <div class="row text-center">
                <div class="col-6">
                  <div class="h5 mb-0">{{ analytics.engagement.total_registered }}</div>
                  <small class="text-muted">Registered</small>
                </div>
                <div class="col-6">
                  <div class="h5 mb-0">{{ analytics.engagement.active_users }}</div>
                  <small class="text-muted">Active</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Subject Performance -->
      <div class="row mb-4">
        <div class="col-lg-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-book me-2"></i>Subject Performance
              </h5>
            </div>
            <div class="card-body">
              <div v-if="analytics.subjects.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-book display-4 mb-3"></i>
                <p>No subject data available</p>
              </div>
              <div v-else>
                <div 
                  v-for="subject in analytics.subjects" 
                  :key="subject.subject"
                  class="mb-3"
                >
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="fw-medium">{{ subject.subject }}</span>
                    <span class="badge bg-primary">{{ subject.attempts }} attempts</span>
                  </div>
                  <div class="progress">
                    <div 
                      class="progress-bar" 
                      :class="getScoreColor(subject.average_percentage)"
                      :style="{ width: subject.average_percentage + '%' }"
                    >
                      {{ subject.average_percentage }}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Performers -->
        <div class="col-lg-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-trophy me-2"></i>Recent Top Performers
              </h5>
            </div>
            <div class="card-body">
              <div v-if="topPerformers.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-trophy display-4 mb-3"></i>
                <p>Loading top performers...</p>
              </div>
              <div v-else class="list-group list-group-flush">
                <div 
                  v-for="(performer, index) in topPerformers" 
                  :key="performer.id"
                  class="list-group-item d-flex justify-content-between align-items-center px-0"
                >
                  <div class="d-flex align-items-center">
                    <span class="badge bg-warning rounded-pill me-3">{{ index + 1 }}</span>
                    <div>
                      <div class="fw-medium">{{ performer.user_name }}</div>
                      <small class="text-muted">{{ performer.quiz_title }}</small>
                    </div>
                  </div>
                  <span class="badge bg-success">{{ performer.percentage }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Analytics Table -->
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">
            <i class="bi bi-table me-2"></i>Detailed Analytics
          </h5>
          <div class="btn-group btn-group-sm">
            <button 
              v-for="tab in analyticsTab" 
              :key="tab.key"
              class="btn btn-outline-primary"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>
        <div class="card-body">
          <!-- Users Tab -->
          <div v-if="activeTab === 'users'" class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Total Attempts</th>
                  <th>Average Score</th>
                  <th>Last Activity</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in detailedUsers" :key="user.id">
                  <td>
                    <div>
                      <div class="fw-medium">{{ user.full_name }}</div>
                      <small class="text-muted">{{ user.email }}</small>
                    </div>
                  </td>
                  <td>{{ user.total_attempts || 0 }}</td>
                  <td>
                    <span class="badge" :class="getScoreColor(user.average_score || 0)">
                      {{ user.average_score || 0 }}%
                    </span>
                  </td>
                  <td>{{ formatDate(user.last_login) }}</td>
                  <td>
                    <button 
                      class="btn btn-sm btn-outline-primary"
                      @click="viewUserAnalytics(user.id)"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Quizzes Tab -->
          <div v-if="activeTab === 'quizzes'" class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Quiz</th>
                  <th>Subject</th>
                  <th>Attempts</th>
                  <th>Average Score</th>
                  <th>Difficulty</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="quiz in detailedQuizzes" :key="quiz.id">
                  <td>
                    <div>
                      <div class="fw-medium">{{ quiz.title }}</div>
                      <small class="text-muted">{{ quiz.total_questions }} questions</small>
                    </div>
                  </td>
                  <td>{{ quiz.subject_name }}</td>
                  <td>{{ quiz.attempts_count || 0 }}</td>
                  <td>
                    <span class="badge" :class="getScoreColor(quiz.average_score || 0)">
                      {{ quiz.average_score || 0 }}%
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="getDifficultyColor(quiz.difficulty)">
                      {{ quiz.difficulty || 'Medium' }}
                    </span>
                  </td>
                  <td>
                    <button 
                      class="btn btn-sm btn-outline-primary"
                      @click="viewQuizAnalytics(quiz.id)"
                    >
                      Analyze
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'

export default {
  name: 'AnalyticsDashboard',
  setup() {
    const loading = ref(false)
    const error = ref('')
    const analytics = ref(null)
    const selectedPeriod = ref(30)
    const activeTab = ref('users')
    const topPerformers = ref([])
    const detailedUsers = ref([])
    const detailedQuizzes = ref([])

    const analyticsTab = [
      { key: 'users', label: 'Users' },
      { key: 'quizzes', label: 'Quizzes' }
    ]

    const loadAnalytics = async () => {
      try {
        loading.value = true
        error.value = ''

        const response = await api.get(`/analytics/overview?days=${selectedPeriod.value}`)
        analytics.value = response.data

        // Load additional data
        await loadTopPerformers()
        await loadDetailedData()

      } catch (err) {
        console.error('Analytics error:', err)
        error.value = err.response?.data?.error || 'Failed to load analytics'
      } finally {
        loading.value = false
      }
    }

    const loadTopPerformers = async () => {
      try {
        const response = await api.get('/admin/dashboard')
        topPerformers.value = response.data.recent_attempts || []
      } catch (err) {
        console.error('Top performers error:', err)
      }
    }

    const loadDetailedData = async () => {
      try {
        // Load users with stats
        const usersResponse = await api.get('/admin/users?per_page=50')
        detailedUsers.value = usersResponse.data.users || []

        // Load quizzes with stats
        const quizzesResponse = await api.get('/admin/quizzes')
        detailedQuizzes.value = quizzesResponse.data || []

      } catch (err) {
        console.error('Detailed data error:', err)
      }
    }

    const exportAnalytics = async () => {
      try {
        const response = await api.post('/admin/export', { type: 'analytics' })
        if (response.data.task_id) {
          alert(`Export started! Task ID: ${response.data.task_id}`)
        }
      } catch (err) {
        console.error('Export error:', err)
        alert('Failed to start export')
      }
    }

    const viewUserAnalytics = (userId) => {
      // Navigate to detailed user analytics
      window.open(`/admin/analytics/user/${userId}`, '_blank')
    }

    const viewQuizAnalytics = (quizId) => {
      // Navigate to detailed quiz analytics
      window.open(`/admin/analytics/quiz/${quizId}`, '_blank')
    }

    const getScoreColor = (percentage) => {
      if (percentage >= 90) return 'bg-success'
      if (percentage >= 80) return 'bg-info'
      if (percentage >= 70) return 'bg-warning'
      return 'bg-danger'
    }

    const getDifficultyColor = (difficulty) => {
      switch (difficulty?.toLowerCase()) {
        case 'easy': return 'bg-success'
        case 'medium': return 'bg-warning'
        case 'hard': return 'bg-danger'
        default: return 'bg-secondary'
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Never'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(() => {
      loadAnalytics()
    })

    return {
      loading,
      error,
      analytics,
      selectedPeriod,
      activeTab,
      analyticsTab,
      topPerformers,
      detailedUsers,
      detailedQuizzes,
      loadAnalytics,
      exportAnalytics,
      viewUserAnalytics,
      viewQuizAnalytics,
      getScoreColor,
      getDifficultyColor,
      formatDate
    }
  }
}
</script>

<style scoped>
.analytics-dashboard {
  padding: 1rem;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.progress {
  height: 8px;
}

.badge {
  font-size: 0.75em;
}

.opacity-75 {
  opacity: 0.75;
}

.table th {
  border-top: none;
  font-weight: 600;
}

.btn-group .btn.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: white;
}
</style>
