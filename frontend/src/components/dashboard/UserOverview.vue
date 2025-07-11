<template>
  <div class="user-overview">
    <!-- Welcome Section -->
    <WelcomeCard
      :title="`Welcome back, ${user?.full_name}!`"
      icon="bi bi-sun"
      icon-class="text-warning"
      subtitle="Let's get started!"
    />

    <!-- Quick Stats -->
    <StatsGrid 
      :stats="dashboardStats" 
      @stat-click="handleStatClick"
    />

    <!-- UGC NET Quick Access -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card bg-gradient-primary text-white">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-8">
                <h5 class="card-title mb-2">
                  <i class="bi bi-mortarboard me-2"></i>
                  UGC NET Preparation
                </h5>
                <p class="card-text mb-3">
                  Prepare for UGC NET exam with our comprehensive mock tests and chapter-wise practice.
                </p>
                <div class="d-flex flex-wrap gap-2">
                  <button class="btn btn-light btn-sm" @click="goToUGCNet">
                    <i class="bi bi-arrow-right me-1"></i>
                    Start Mock Test
                  </button>
                  <button class="btn btn-outline-light btn-sm" @click="goToTestGenerator">
                    <i class="bi bi-gear me-1"></i>
                    Practice Questions
                  </button>
                </div>
              </div>
              <div class="col-md-4 text-center">
                <i class="bi bi-book display-1 opacity-25"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recommendations Section -->
    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-lightbulb me-2"></i>
              AI-Powered Recommendations
            </h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <h6 class="text-primary">Recommended Study Areas</h6>
              <p class="text-muted mb-2">
                Based on your preparation subject and overall performance trends, focus on these areas:
              </p>
              <div class="d-flex flex-wrap gap-2">
                <span v-for="subject in userRecommendedSubjects" :key="subject" 
                      class="badge bg-primary">
                  {{ subject }}
                </span>
              </div>
            </div>
            
            <div class="mb-3">
              <h6 class="text-success">Next Steps</h6>
              <div class="list-group list-group-flush">
                <div class="list-group-item border-0 px-0">
                  <i class="bi bi-check-circle text-success me-2"></i>
                  Start with a mock test to assess your current level
                </div>
                <div class="list-group-item border-0 px-0">
                  <i class="bi bi-check-circle text-success me-2"></i>
                  Focus on chapter-wise practice for weak areas
                </div>
                <div class="list-group-item border-0 px-0">
                  <i class="bi bi-check-circle text-success me-2"></i>
                  Review your performance analytics regularly
                </div>
              </div>
            </div>

            <div class="d-flex gap-2">
              <button class="btn btn-primary" @click="startMockTest">
                <i class="bi bi-play-circle me-1"></i>
                Start Mock Test
              </button>
              <button class="btn btn-outline-primary" @click="goToTestGenerator">
                <i class="bi bi-gear me-1"></i>
                Practice Questions
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-target me-2"></i>
              Study Goals
            </h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <h6 class="text-success">Weekly Progress</h6>
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

export default {
  name: 'UserOverview',
  components: {
    WelcomeCard,
    StatsGrid
  },
  setup() {
    const router = useRouter()
    const { user } = useAuth()
    const {
      loading,
      dashboardStats,
      userRecommendedSubjects,
      userStudyProgress,
      refreshDashboard
    } = useDashboard()

    const startMockTest = () => {
      router.push('/ugc-net')
    }

    const goToUGCNet = () => {
      router.push('/ugc-net')
    }

    const goToTestGenerator = () => {
      router.push('/ugc-net/test-generator')
    }

    const handleStatClick = (stat) => {
      // Handle stat card clicks
      switch (stat.key) {
        case 'tests_taken':
          router.push('/history')
          break
        case 'average_score':
          router.push('/analytics')
          break
        default:
          console.log('Stat clicked:', stat)
      }
    }

    return {
      user,
      loading,
      dashboardStats,
      userRecommendedSubjects,
      userStudyProgress,
      startMockTest,
      goToUGCNet,
      goToTestGenerator,
      handleStatClick,
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
  border-radius: 8px;

}

.card:hover {
  transform: translateY(-2px);
}

.progress {
  background-color: #e9ecef;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
}

.bg-gradient-primary .btn-light:hover {
  background-color: #f8f9fa;
  border-color: #f8f9fa;
}
</style>