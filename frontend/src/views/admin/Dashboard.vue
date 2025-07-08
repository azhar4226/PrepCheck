<template>
  <div class="admin-dashboard">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">Admin Dashboard</h2>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary" @click="refreshData">
          <i class="fas fa-refresh me-2"></i>Refresh
        </button>
        <button class="btn btn-success" @click="$router.push('/admin/ai-questions')">
          <i class="fas fa-magic me-2"></i>AI Question Generator
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading dashboard data...</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Statistics Cards -->
      <div class="row mb-4">
        <div class="col-md-3 mb-3">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h5 class="card-title">Total Users</h5>
                  <h3 class="mb-0">{{ stats.total_users }}</h3>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-users fa-2x opacity-75"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-success text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h5 class="card-title">Mock Tests</h5>
                  <h3 class="mb-0">{{ stats.total_mock_tests || 0 }}</h3>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-clipboard-check fa-2x opacity-75"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-info text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h5 class="card-title">Test Attempts</h5>
                  <h3 class="mb-0">{{ stats.total_attempts || 0 }}</h3>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-chart-line fa-2x opacity-75"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-warning text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h5 class="card-title">Active Subjects</h5>
                  <h3 class="mb-0">{{ stats.total_subjects }}</h3>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-book fa-2x opacity-75"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Quick Actions</h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-3 mb-2">
                  <button class="btn btn-outline-primary w-100" @click="$router.push('/admin/subjects')">
                    <i class="fas fa-book me-2"></i>Manage Subjects
                  </button>
                </div>
                <div class="col-md-3 mb-2">
                  <button class="btn btn-outline-success w-100" @click="$router.push('/admin/ugc-net')">
                    <i class="fas fa-clipboard-check me-2"></i>Manage Mock Tests
                  </button>
                </div>
                <div class="col-md-3 mb-2">
                  <button class="btn btn-outline-info w-100" @click="$router.push('/admin/users')">
                    <i class="fas fa-users me-2"></i>Manage Users
                  </button>
                </div>
                <div class="col-md-3 mb-2">
                  <button class="btn btn-outline-warning w-100" @click="exportData">
                    <i class="fas fa-download me-2"></i>Export Data
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="row">
        <div class="col-md-8">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Recent Test Attempts</h5>
            </div>
            <div class="card-body">
              <div v-if="recentAttempts.length === 0" class="text-center text-muted py-3">
                <i class="fas fa-chart-line fa-3x mb-3 opacity-50"></i>
                <p>No recent test attempts</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>User</th>
                      <th>Test</th>
                      <th>Score</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="attempt in recentAttempts" :key="attempt.id">
                      <td>{{ attempt.user_name || 'Unknown User' }}</td>
                      <td>{{ attempt.test_title || attempt.mock_test_title || 'Unknown Test' }}</td>
                      <td>
                        <span class="badge" :class="getScoreBadgeClass(attempt.percentage)">
                          {{ attempt.score }}/{{ attempt.total_marks }} ({{ attempt.percentage }}%)
                        </span>
                      </td>
                      <td>{{ formatDate(attempt.completed_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">System Status</h5>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center">
                  <span>Database</span>
                  <span class="badge bg-success">Online</span>
                </div>
              </div>
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center">
                  <span>Redis Cache</span>
                  <span class="badge bg-success">Connected</span>
                </div>
              </div>
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center">
                  <span>Celery Worker</span>
                  <span class="badge bg-success">Active</span>
                </div>
              </div>
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center">
                  <span>AI Service</span>
                  <span class="badge bg-warning">Not Configured</span>
                </div>
              </div>
            </div>
          </div>

          <div class="card mt-3">
            <div class="card-header">
              <h5 class="mb-0">Quick Stats</h5>
            </div>
            <div class="card-body">
              <div class="mb-2">
                <small class="text-muted">Today's Attempts</small>
                <div class="fw-bold">{{ stats.today_attempts || 0 }}</div>
              </div>
              <div class="mb-2">
                <small class="text-muted">This Week's Attempts</small>
                <div class="fw-bold">{{ stats.week_attempts || 0 }}</div>
              </div>
              <div class="mb-2">
                <small class="text-muted">Average Score</small>
                <div class="fw-bold">{{ stats.average_score || 0 }}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger" role="alert">
      <i class="fas fa-exclamation-triangle me-2"></i>
      {{ error }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import adminService from '@/services/adminService'

export default {
  name: 'AdminDashboard',
  setup() {
    const loading = ref(true)
    const error = ref('')
    const stats = ref({
      total_users: 0,
      total_mock_tests: 0,
      total_attempts: 0,
      total_subjects: 0,
      total_questions: 0,
      today_attempts: 0,
      week_attempts: 0,
      average_score: 0
    })
    const recentAttempts = ref([])

    const loadDashboardData = async () => {
      console.log('🚀 loadDashboardData function started!')
      try {
        loading.value = true
        error.value = ''

        console.log('Calling adminService.getDashboard()...')
        const response = await adminService.getDashboard()
        console.log('Raw API response:', response)
        
        // Extract data from response object
        const dashboardData = response.data || response
        console.log('Extracted dashboard data:', dashboardData)
        
        stats.value = dashboardData
        recentAttempts.value = dashboardData.recent_attempts || dashboardData.top_performers || []
        
        console.log('Final stats object:', stats.value)
        console.log('Total users from stats:', stats.value?.total_users)
      } catch (err) {
        error.value = 'Failed to load dashboard data. Please try again.'
        console.error('Dashboard load error:', err)
        console.error('Error details:', err.response?.data || err.message)
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      loadDashboardData()
    }

    const exportData = async () => {
      try {
        // This would trigger a CSV export
        await api.exportAdminData()
        // Show success message or download file
      } catch (err) {
        console.error('Export error:', err)
      }
    }

    const getScoreBadgeClass = (percentage) => {
      if (percentage >= 80) return 'bg-success'
      if (percentage >= 60) return 'bg-warning'
      return 'bg-danger'
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      console.log('🔥 Dashboard component mounted!')
      console.log('📊 About to call loadDashboardData()')
      loadDashboardData()
    })

    return {
      loading,
      error,
      stats,
      recentAttempts,
      refreshData,
      exportData,
      getScoreBadgeClass,
      formatDate
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  padding: 1rem;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.opacity-75 {
  opacity: 0.75;
}

.opacity-50 {
  opacity: 0.5;
}
</style>
