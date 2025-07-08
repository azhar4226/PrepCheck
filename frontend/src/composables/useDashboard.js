import { ref, computed, onMounted } from 'vue'
import { useAuth } from './useAuth.js'
import userService from '@/services/userService.js'
import adminService from '@/services/adminService.js'

export function useDashboard() {
  const { user } = useAuth()
  const loading = ref(false)
  const error = ref('')
  
  // User dashboard data
  const userStats = ref({
    tests_taken: 0,
    average_score: 0,
    study_streak: 0,
    rank: null
  })
  
  const userRecentTests = ref([])
  const userRecommendedSubjects = ref(['Mathematics', 'Science'])
  const userStudyProgress = ref(65)
  
  // Admin dashboard data
  const adminStats = ref({
    total_users: 0,
    total_mock_tests: 0,
    total_attempts: 0,
    total_subjects: 0,
    total_questions: 0
  })
  
  const adminRecentActivity = ref([])
  const systemStatus = ref({
    database: 'online',
    redis: 'connected',
    celery: 'active',
    ai_service: 'available'
  })

  // Computed dashboard data based on user role
  const dashboardStats = computed(() => {
    if (!user.value) return []
    
    if (user.value.is_admin) {
      const stats = adminStats.value || {}
      // Ensure stats has the expected properties with fallback values
      const safeStats = {
        total_users: stats.total_users || 0,
        total_mock_tests: stats.total_mock_tests || 0,
        total_attempts: stats.total_attempts || 0,
        total_subjects: stats.total_subjects || 0,
        total_questions: stats.total_questions || 0
      }
      
      return [
        {
          key: 'users',
          title: 'Total Users',
          value: safeStats.total_users,
          icon: 'bi bi-people',
          variant: 'primary',
          clickable: true
        },
        {
          key: 'mock_tests',
          title: 'Mock Tests',
          value: safeStats.total_mock_tests,
          icon: 'bi bi-clipboard-check',
          variant: 'success',
          clickable: true
        },
        {
          key: 'attempts',
          title: 'Test Attempts',
          value: safeStats.total_attempts,
          icon: 'bi bi-bar-chart',
          variant: 'info',
          clickable: true
        },
        {
          key: 'questions',
          title: 'Question Bank',
          value: safeStats.total_questions,
          icon: 'bi bi-patch-question',
          variant: 'warning',
          clickable: true
        },
        {
          key: 'subjects',
          title: 'Active Subjects',
          value: safeStats.total_subjects,
          icon: 'bi bi-collection',
          variant: 'warning',
          clickable: true
        }
      ]
    } else {
      return [
        {
          key: 'tests_taken',
          title: 'Tests Taken',
          value: userStats.value.tests_taken || 0,
          icon: 'bi bi-clipboard-check',
          variant: 'primary'
        },
        {
          key: 'average_score',
          title: 'Average Score',
          value: `${userStats.value.average_score || 0}%`,
          icon: 'bi bi-trophy',
          variant: 'success'
        },
        {
          key: 'study_streak',
          title: 'Study Streak',
          value: `${userStats.value.study_streak || 0} days`,
          icon: 'bi bi-fire',
          variant: 'info'
        },
        {
          key: 'rank',
          title: 'Rank',
          value: userStats.value.rank ? `#${userStats.value.rank}` : '--',
          icon: 'bi bi-award',
          variant: 'warning'
        }
      ]
    }
  })

  const recentActivity = computed(() => {
    if (!user.value) return []
    
    if (user.value.is_admin) {
      return adminRecentActivity.value.map(activity => ({
        id: activity.id,
        title: activity.user_name,
        subtitle: `${activity.action} - ${activity.test_title || activity.activity_title}`,
        timestamp: activity.timestamp,
        badge: activity.type,
        badgeClass: getActivityBadgeClass(activity.type)
      }))
    } else {
      return userRecentTests.value.map(test => ({
        id: test.id,
        title: test.test_title || test.title,
        subtitle: `${test.subject_name || test.subject} • ${test.paper_type || 'Practice'}`,
        timestamp: test.completed_at,
        badge: `${test.percentage || test.score}%`,
        clickable: true
      }))
    }
  })

  // Load user dashboard data
  const loadUserDashboard = async () => {
    try {
      loading.value = true
      error.value = ''
      
      const [dashboardRes, historyRes] = await Promise.all([
        userService.getDashboard(),
        userService.getHistory(1, 5)
      ])
      
      // Extract stats from dashboard response
      const stats = dashboardRes.stats || {}
      userStats.value = {
        tests_taken: stats.total_attempts || 0,
        average_score: stats.average_score || 0,
        study_streak: stats.study_streak || 0,
        rank: stats.rank || null
      }
      
      // Extract recent test attempts from history response
      userRecentTests.value = historyRes.attempts || []
      
    } catch (err) {
      console.error('Error loading user dashboard:', err)
      error.value = 'Failed to load dashboard data'
    } finally {
      loading.value = false
    }
  }

  // Load admin dashboard data
  const loadAdminDashboard = async () => {
    try {
      loading.value = true
      error.value = ''
      
      console.log('🔥 useDashboard: loadAdminDashboard called')
      
      // Initialize with fallback data first
      adminStats.value = {
        total_users: 0,
        total_mock_tests: 0,
        total_attempts: 0,
        total_subjects: 0,
        total_questions: 0
      }
      adminRecentActivity.value = []
      
      console.log('📊 Calling adminService.getDashboard()...')
      const response = await adminService.getDashboard()
      console.log('🎯 Admin dashboard response:', response)
      
      // Update with actual data if API calls succeed
      if (response) {
        console.log('✅ Updating admin stats with real data')
        adminStats.value = {
          total_users: response.total_users || 0,
          total_mock_tests: response.total_mock_tests || 0,
          total_attempts: response.total_attempts || 0,
          total_subjects: response.total_subjects || 0,
          total_questions: response.total_questions || 0
        }
        console.log('📈 Final admin stats:', adminStats.value)
        
        // Also update recent activity if available
        if (response.top_performers) {
          adminRecentActivity.value = response.top_performers || []
        }
      }
      
    } catch (err) {
      console.error('Error loading admin dashboard:', err)
      error.value = 'Failed to load admin dashboard data'
      // Fallback data is already set above
    } finally {
      loading.value = false
    }
  }

  // Main load function
  const loadDashboard = async () => {
    if (!user.value) return
    
    if (user.value.is_admin) {
      await loadAdminDashboard()
    } else {
      await loadUserDashboard()
    }
  }

  // Refresh dashboard data
  const refreshDashboard = async () => {
    await loadDashboard()
  }

  // Helper functions
  const getActivityBadgeClass = (type) => {
    const typeMap = {
      'mock_test_completed': 'bg-success',
      'practice_test_completed': 'bg-info',
      'test_started': 'bg-info',
      'user_registered': 'bg-primary',
      'mock_test_created': 'bg-warning',
      'error': 'bg-danger'
    }
    return typeMap[type] || 'bg-secondary'
  }

  const getScoreBadgeClass = (score) => {
    if (score >= 80) return 'bg-success'
    if (score >= 60) return 'bg-warning'
    return 'bg-danger'
  }

  // Auto-load on mount
  onMounted(() => {
    loadDashboard()
  })

  return {
    // State
    loading,
    error,
    userStats,
    adminStats,
    userRecentTests, // Renamed from userRecentQuizzes to match the ref
    adminRecentActivity,
    userRecommendedSubjects,
    userStudyProgress,
    systemStatus,
    
    // Computed
    dashboardStats,
    recentActivity,
    
    // Methods
    loadDashboard,
    refreshDashboard,
    loadUserDashboard,
    loadAdminDashboard,
    getActivityBadgeClass,
    getScoreBadgeClass
  }
}
