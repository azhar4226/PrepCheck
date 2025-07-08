<template>
  <div class="admin-overview">
    <!-- Welcome Section -->
    <WelcomeCard
      title="Admin Control Panel"
      subtitle="Manage your PrepCheck platform. Monitor system performance and user activity."
      icon="bi bi-shield-check"
      icon-class="text-success"
    />

    <!-- System Statistics -->
    <StatsGrid 
      :stats="dashboardStats" 
      @stat-click="handleStatClick"
    />

    <!-- System Status & Recent Activity -->
    <div class="row">
      <div class="col-md-8">
        <ActivityCard
          title="Recent System Activity"
          icon="bi bi-activity"
          :items="recentActivity"
          empty-message="No recent activity"
          empty-icon="bi bi-activity"
        >
          <template #item="{ item }">
            <h6 class="mb-1">{{ item.title }}</h6>
            <p class="mb-1">{{ item.subtitle }}</p>
            <small class="text-muted">{{ formatDate(item.timestamp) }}</small>
          </template>
        </ActivityCard>
      </div>

      <div class="col-md-4">
        <!-- System Status Card -->
        <div class="card mb-3">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-gear me-2"></i>
              System Status
            </h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center">
                <span>Database</span>
                <span class="badge" :class="getStatusBadgeClass(systemStatus.database)">
                  {{ systemStatus.database }}
                </span>
              </div>
            </div>
            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center">
                <span>Redis Cache</span>
                <span class="badge" :class="getStatusBadgeClass(systemStatus.redis)">
                  {{ systemStatus.redis }}
                </span>
              </div>
            </div>
            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center">
                <span>Celery Worker</span>
                <span class="badge" :class="getStatusBadgeClass(systemStatus.celery)">
                  {{ systemStatus.celery }}
                </span>
              </div>
            </div>
            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center">
                <span>AI Service</span>
                <span class="badge" :class="getStatusBadgeClass(systemStatus.ai_service)">
                  {{ systemStatus.ai_service }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions Card -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-lightning me-2"></i>
              Quick Actions
            </h5>
          </div>
          <div class="card-body">
            <div class="d-grid gap-2">
              <button class="btn btn-outline-primary btn-sm" @click="navigateToAIQuestions">
                <i class="bi bi-robot me-1"></i>
                AI Question Generator
              </button>
              <button class="btn btn-outline-success btn-sm" @click="exportData">
                <i class="bi bi-download me-1"></i>
                Export Data
              </button>
              <button class="btn btn-outline-info btn-sm" @click="systemMaintenance">
                <i class="bi bi-tools me-1"></i>
                System Maintenance
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading admin dashboard...</p>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useDashboard } from '@/composables/useDashboard'
import WelcomeCard from '@/components/ui/WelcomeCard.vue'
import StatsGrid from '@/components/ui/StatsGrid.vue'
import ActivityCard from '@/components/ui/ActivityCard.vue'

export default {
  name: 'AdminOverview',
  components: {
    WelcomeCard,
    StatsGrid,
    ActivityCard
  },
  setup() {
    const router = useRouter()
    const { user } = useAuth()
    const {
      loading,
      dashboardStats,
      recentActivity,
      systemStatus,
      refreshDashboard
    } = useDashboard()

    const handleStatClick = (stat) => {
      // Handle stat card clicks - navigate to appropriate admin section
      switch (stat.key) {
        case 'users':
          router.push({ name: 'Dashboard', query: { tab: 'users' } })
          break
        case 'mock_tests':
          router.push({ name: 'Dashboard', query: { tab: 'mock_tests' } })
          break
        case 'attempts':
          router.push({ name: 'Dashboard', query: { tab: 'analytics' } })
          break
        case 'questions':
          router.push({ name: 'Dashboard', query: { tab: 'questions' } })
          break
        default:
          console.log('Stat clicked:', stat)
      }
    }

    const getStatusBadgeClass = (status) => {
      const statusLower = status?.toLowerCase()
      if (statusLower === 'online' || statusLower === 'connected' || statusLower === 'active' || statusLower === 'available') {
        return 'bg-success'
      }
      if (statusLower === 'warning' || statusLower === 'slow') {
        return 'bg-warning'
      }
      return 'bg-danger'
    }

    const navigateToAIQuestions = () => {
      router.push('/admin/ai-questions')
    }

    const exportData = () => {
      // Implement data export functionality
      console.log('Exporting data...')
    }

    const systemMaintenance = () => {
      // Implement system maintenance functionality
      console.log('Opening system maintenance...')
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now - date
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      const diffHours = Math.floor(diffMinutes / 60)
      const diffDays = Math.floor(diffHours / 24)

      if (diffMinutes < 60) return `${diffMinutes}m ago`
      if (diffHours < 24) return `${diffHours}h ago`
      if (diffDays < 7) return `${diffDays}d ago`
      return date.toLocaleDateString()
    }

    return {
      user,
      loading,
      dashboardStats,
      recentActivity,
      systemStatus,
      handleStatClick,
      getStatusBadgeClass,
      navigateToAIQuestions,
      exportData,
      systemMaintenance,
      formatDate,
      refreshDashboard
    }
  }
}
</script>

<style scoped>
.admin-overview {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.card {
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
}

.d-grid {
  display: grid;
}

.gap-2 {
  gap: 0.5rem;
}
</style>
