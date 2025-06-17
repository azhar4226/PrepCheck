<template>
  <div class="user-overview">
    <!-- Welcome Section -->
    <WelcomeCard
      :title="`Welcome back, ${user?.full_name}!`"
      subtitle="Ready to continue your learning journey? Here's your progress overview."
      icon="bi bi-sun"
      icon-class="text-warning"
    />

    <!-- Quick Stats -->
    <StatsGrid 
      :stats="dashboardStats" 
      @stat-click="handleStatClick"
    />

    <!-- Recent Activity & Recommendations -->
    <div class="row">
      <div class="col-md-8">
        <ActivityCard
          title="Recent Activity"
          icon="bi bi-clock-history"
          :items="recentActivity"
          empty-message="No recent quiz attempts"
          empty-icon="bi bi-list-check"
        >
          <template #empty-action>
            <button class="btn btn-primary" @click="startQuiz">
              Take Your First Quiz
            </button>
          </template>
          
          <template #item="{ item }">
            <h6 class="mb-1">{{ item.title }}</h6>
            <p class="mb-1 text-muted">{{ item.subtitle }}</p>
            <small class="text-muted">{{ formatDate(item.timestamp) }}</small>
          </template>
        </ActivityCard>
      </div>

      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-lightbulb me-2"></i>
              Recommendations
            </h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <h6 class="text-primary">Improve Your Skills</h6>
              <p class="small text-muted mb-2">
                Based on your recent performance, we recommend focusing on:
              </p>
              <div class="d-flex flex-wrap gap-1">
                <span v-for="subject in userRecommendedSubjects" :key="subject" 
                      class="badge bg-light text-dark">
                  {{ subject }}
                </span>
              </div>
            </div>
            
            <div class="mb-3">
              <h6 class="text-success">Study Goal</h6>
              <div class="progress mb-2" style="height: 8px;">
                <div class="progress-bar bg-success" 
                     :style="{ width: userStudyProgress + '%' }">
                </div>
              </div>
              <small class="text-muted">
                {{ userStudyProgress }}% of weekly goal completed
              </small>
            </div>

            <button class="btn btn-sm btn-outline-primary w-100">
              <i class="bi bi-gear me-1"></i>
              Set Study Goals
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading your dashboard...</p>
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
  name: 'UserOverview',
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
      userRecommendedSubjects,
      userStudyProgress,
      refreshDashboard
    } = useDashboard()

    const startQuiz = () => {
      router.push('/quiz')
    }

    const handleStatClick = (stat) => {
      // Handle stat card clicks
      switch (stat.key) {
        case 'quizzes_taken':
          router.push('/history')
          break
        case 'average_score':
          router.push('/analytics')
          break
        default:
          console.log('Stat clicked:', stat)
      }
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
      userRecommendedSubjects,
      userStudyProgress,
      startQuiz,
      handleStatClick,
      formatDate,
      refreshDashboard
    }
  }
}
</script>

<style scoped>
.user-overview {
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

.progress {
  background-color: #e9ecef;
}
</style>
