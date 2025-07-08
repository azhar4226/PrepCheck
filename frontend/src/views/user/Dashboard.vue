<template>
  <div class="container-fluid">
    <!-- Header Section -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="h2 text-primary">
              <i class="bi bi-speedometer2 me-2"></i>Dashboard
            </h1>
            <p class="text-muted mb-0">Welcome back, {{ user?.phone || 'Student' }}!</p>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-primary" @click="refreshDashboard">
              <i class="bi bi-arrow-clockwise me-1"></i>Refresh
            </button>              <router-link to="/ugc-net" class="btn btn-primary">
                <i class="bi bi-play-circle me-1"></i>Take Test
              </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="row mb-4">
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-white bg-primary">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h5 class="card-title">{{ stats.total_attempts || 0 }}</h5>
                <p class="card-text small">Total Attempts</p>
              </div>
              <div class="align-self-center">
                <i class="bi bi-clipboard-check display-6"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-white bg-success">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h5 class="card-title">{{ stats.average_score || 0 }}%</h5>
                <p class="card-text small">Average Score</p>
              </div>
              <div class="align-self-center">
                <i class="bi bi-trophy display-6"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-white bg-info">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h5 class="card-title">{{ stats.time_spent || 0 }}</h5>
                <p class="card-text small">Hours Studied</p>
              </div>
              <div class="align-self-center">
                <i class="bi bi-clock display-6"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-white bg-warning">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h5 class="card-title">{{ stats.subjects_covered || 0 }}</h5>
                <p class="card-text small">Subjects Covered</p>
              </div>
              <div class="align-self-center">
                <i class="bi bi-book display-6"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- User Analytics Section -->
    <div class="row mb-4">
      <div class="col-12">
        <UserAnalytics />
      </div>
    </div>

    <div class="row">
      <!-- Recent Activity -->
      <div class="col-lg-8 mb-4">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
              <i class="bi bi-clock-history me-2"></i>Recent Activity
            </h5>
            <router-link to="/history" class="btn btn-sm btn-outline-primary">
              View All
            </router-link>
          </div>
          <div class="card-body">
            <div v-if="loading.activity" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="recentActivity.length === 0" class="text-center py-4 text-muted">
              <i class="bi bi-inbox display-4 mb-3"></i>
              <p>No recent activity. Start taking tests to see your progress!</p>
              <router-link to="/ugc-net" class="btn btn-primary">
                Browse Mock Tests
              </router-link>
            </div>
            
            <div v-else class="list-group list-group-flush">
              <div 
                v-for="activity in recentActivity" 
                :key="activity.id"
                class="list-group-item border-0 px-0"
              >
                <div class="d-flex justify-content-between align-items-start">
                  <div class="flex-grow-1">
                    <h6 class="mb-1">{{ activity.test_title || activity.title }}</h6>
                    <p class="mb-1 text-muted small">
                      {{ activity.subject_name }} • {{ activity.paper_type || activity.chapter_name }}
                    </p>
                    <small class="text-muted">
                      {{ formatDate(activity.completed_at) }}
                    </small>
                  </div>
                  <div class="text-end">
                    <span 
                      class="badge"
                      :class="getScoreBadgeClass(activity.percentage)"
                    >
                      {{ activity.percentage }}%
                    </span>
                    <div class="small text-muted mt-1">
                      {{ activity.score }}/{{ activity.total_marks }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions & Progress -->
      <div class="col-lg-4">
        <!-- Quick Actions -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <i class="bi bi-lightning me-2"></i>Quick Actions
            </h5>
          </div>
          <div class="card-body">
            <div class="d-grid gap-2">
              <router-link to="/ugc-net" class="btn btn-primary">
                <i class="bi bi-play-circle me-2"></i>Take Mock Test
              </router-link>
              <router-link to="/ugc-net/practice" class="btn btn-outline-primary">
                <i class="bi bi-pencil-square me-2"></i>Practice Test
              </router-link>
              <router-link to="/history" class="btn btn-outline-secondary">
                <i class="bi bi-clock-history me-2"></i>View History
              </router-link>
              <button class="btn btn-outline-success" @click="exportData">
                <i class="bi bi-download me-2"></i>Export Data
              </button>
            </div>
          </div>
        </div>

        <!-- Progress Chart -->
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <i class="bi bi-graph-up me-2"></i>Weekly Progress
            </h5>
          </div>
          <div class="card-body">
            <div v-if="loading.progress" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="progressData.length === 0" class="text-center py-4 text-muted">
              <i class="bi bi-graph-up display-4 mb-3"></i>
              <p class="small">Take more tests to see your progress chart</p>
            </div>
            
            <canvas v-else ref="progressChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading.main" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-light bg-opacity-75" style="z-index: 1050;">
      <div class="text-center">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p>Loading dashboard...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import userService from '@/services/userService'
import { formatDate, formatTime } from '@/services/utils'
import UserAnalytics from '@/components/features/UserAnalytics.vue'

export default {
  name: 'UserDashboard',
  components: {
    UserAnalytics
  },
  setup() {
    const router = useRouter()
    
    const user = ref(null)
    const stats = ref({})
    const recentActivity = ref([])
    const progressData = ref([])
    
    const loading = ref({
      main: true,
      activity: false,
      progress: false
    })
    
    const loadDashboard = async () => {
      try {
        loading.value.main = true
        
        // Load user info and stats
        const [userResponse, statsResponse] = await Promise.all([
          userService.getProfile(),
          userService.getDashboard()
        ])
        
        user.value = userResponse.user
        stats.value = statsResponse.stats
        
        // Load recent activity
        await loadRecentActivity()
        
        // Load progress data
        await loadProgressData()
        
      } catch (error) {
        console.error('Error loading dashboard:', error)
        if (error.response?.status === 401) {
          router.push('/login')
        }
      } finally {
        loading.value.main = false
      }
    }
    
    const loadRecentActivity = async () => {
      try {
        loading.value.activity = true
        const response = await userService.getHistory(1, 5)
        recentActivity.value = response.attempts
      } catch (error) {
        console.error('Error loading recent activity:', error)
      } finally {
        loading.value.activity = false
      }
    }
    
    const loadProgressData = async () => {
      try {
        loading.value.progress = true
        const response = await userService.getProgress()
        progressData.value = response.progress
        
        // Create chart after data is loaded
        if (progressData.value.length > 0) {
          createProgressChart()
        }
      } catch (error) {
        console.error('Error loading progress data:', error)
      } finally {
        loading.value.progress = false
      }
    }
    
    const createProgressChart = () => {
      // This would use Chart.js to create a progress chart
      // For now, we'll skip the actual chart implementation
      console.log('Progress chart data:', progressData.value)
    }
    
    const refreshDashboard = () => {
      loadDashboard()
    }
    
    const exportData = async () => {
      try {
        const response = await userService.exportData()
        
        if (response.files_created && response.files_created.length > 0) {
          // Try to download each file
          const downloadPromises = response.files_created.map(async (filePath) => {
            const filename = filePath.split('/').pop() // Get filename from path
            try {
              const downloadResponse = await userService.downloadExportFile(filename)
              
              // Create download link
              const blob = new Blob([downloadResponse.data], { 
                type: downloadResponse.headers['content-type'] || 'application/octet-stream' 
              })
              const url = window.URL.createObjectURL(blob)
              const link = document.createElement('a')
              link.href = url
              link.download = filename
              document.body.appendChild(link)
              link.click()
              document.body.removeChild(link)
              window.URL.revokeObjectURL(url)
              
              return filename
            } catch (downloadErr) {
              console.error(`Failed to download ${filename}:`, downloadErr)
              return null
            }
          })
          
          const downloadedFiles = await Promise.all(downloadPromises)
          const successfulDownloads = downloadedFiles.filter(f => f !== null)
          
          if (successfulDownloads.length > 0) {
            alert(`Export completed! Downloaded files: ${successfulDownloads.join(', ')}`)
          } else {
            alert(`Export completed! Files created: ${response.files_created.join(', ')}`)
          }
        } else if (response.message) {
          alert(response.message)
        } else {
          alert('Export completed successfully!')
        }
      } catch (error) {
        console.error('Error exporting data:', error)
        alert('Failed to export data: ' + (error.response?.data?.error || error.message))
      }
    }
    
    const getScoreBadgeClass = (percentage) => {
      if (percentage >= 90) return 'bg-success'
      if (percentage >= 80) return 'bg-info'
      if (percentage >= 70) return 'bg-warning'
      return 'bg-danger'
    }
    
    onMounted(() => {
      loadDashboard()
    })
    
    return {
      user,
      stats,
      recentActivity,
      progressData,
      loading,
      refreshDashboard,
      exportData,
      formatDate,
      getScoreBadgeClass
    }
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.bg-primary {
  background-color: #0d6efd !important;
}

.bg-success {
  background-color: #198754 !important;
}

.bg-info {
  background-color: #0dcaf0 !important;
}

.bg-warning {
  background-color: #ffc107 !important;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.badge {
  font-size: 0.75em;
}
</style>