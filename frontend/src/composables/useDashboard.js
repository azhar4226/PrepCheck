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
      // Map backend stats to new stat cards
      const stats = userStats.value || {}
      // Helper for relative time
      function getRelativeTime(dateString) {
        if (!dateString) return 'N/A'
        const now = new Date()
        const date = new Date(dateString)
        const diff = Math.floor((now - date) / 1000)
        if (diff < 60) return 'just now'
        if (diff < 3600) return `${Math.floor(diff/60)} min ago`
        if (diff < 86400) return `${Math.floor(diff/3600)} hr ago`
        if (diff < 2592000) return `${Math.floor(diff/86400)} days ago`
        return date.toLocaleDateString()
      }
      return [
        {
          key: 'hours_studied',
          title: 'Hours Studied',
          value: stats.hours_studied != null ? stats.hours_studied : 0,
          subtitle: 'Total study time',
          icon: 'bi bi-clock-history',
          variant: 'info',
        },
        {
          key: 'study_streak',
          title: 'Current Streak',
          value: stats.study_streak != null ? stats.study_streak : 0,
          subtitle: 'Days in a row',
          icon: 'bi bi-fire',
          variant: 'warning',
        },
        {
          key: 'last_activity',
          title: 'Last Activity',
          value: getRelativeTime(stats.last_activity),
          subtitle: 'Recent session',
          icon: 'bi bi-calendar-check',
          variant: 'primary',
        },
        {
          key: 'accuracy_rate',
          title: 'Accuracy Rate',
          value: stats.accuracy_rate != null ? stats.accuracy_rate.toFixed(1) + '%' : '0%',
          subtitle: 'Correct answers',
          icon: 'bi bi-bullseye',
          variant: 'success',
        },
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
        hours_studied: stats.hours_studied || 0,
        study_streak: stats.study_streak || 0,
        accuracy_rate: stats.accuracy_rate || 0,
        last_activity: stats.last_activity || null
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