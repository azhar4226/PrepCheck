<template>
  <div class="container-fluid">
    <!-- Header Section -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <p class="text-muted mb-0">Welcome back, {{ user?.full_name || 'Student' }}!</p>
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