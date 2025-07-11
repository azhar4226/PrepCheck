import { createRouter, createWebHistory } from 'vue-router'

// Auth Components
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'

// Unified Dashboard
import UnifiedDashboard from '@/views/UnifiedDashboard.vue'

// UGC NET Components
import UGCNetDashboard from '@/views/ugc-net/Dashboard.vue'
import UGCNetTestGenerator from '@/views/ugc-net/TestGenerator.vue'
import UGCNetTestTaking from '@/views/ugc-net/TestTaking.vue'
import UGCNetTestResults from '@/views/ugc-net/TestResults.vue'

// Legacy Components (keeping for compatibility)
import SubjectManagement from '@/views/admin/SubjectManagement.vue'
import Analytics from '@/views/admin/Analytics.vue'
import AIQuestionGenerator from '@/views/admin/AIQuestionGenerator.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guest: true }
  },
  {
    path: '/dashboard',
    name: 'UserDashboard',
    component: UnifiedDashboard,
    meta: { requiresAuth: true },
    props: route => ({
      activeTab: route.query.tab || 'overview'
    })
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: UnifiedDashboard,
    meta: { requiresAuth: true, requiresAdmin: true },
    props: route => ({
      activeTab: route.query.tab || 'overview'
    })
  },
  
  // UGC NET Routes
  {
    path: '/ugc-net',
    name: 'UGCNetDashboard',
    component: UGCNetDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/ugc-net/test-generator',
    name: 'UGCNetTestGenerator',
    component: UGCNetTestGenerator,
    meta: { requiresAuth: true }
  },
  {
    path: '/ugc-net/test/:testId/take',
    name: 'UGCNetTestTaking',
    component: UGCNetTestTaking,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/ugc-net/test/:testId/attempt/:attemptId/results',
    name: 'UGCNetTestResults',
    component: UGCNetTestResults,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/ugc-net/test/:testId/results',
    name: 'UGCNetLatestResults',
    component: UGCNetTestResults,
    meta: { requiresAuth: true },
    props: route => ({ testId: route.params.testId, findLatest: true })
  },
  // Additional UGC NET routes
  {
    path: '/ugc-net/generate-test',
    redirect: '/ugc-net/test-generator'
  },
  {
    path: '/ugc-net/test/:testId',
    name: 'UGCNetTestDetails',
    component: UGCNetTestTaking,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/ugc-net/test/:testId/attempt/:attemptId',
    name: 'UGCNetTestAttempt',
    component: UGCNetTestTaking,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/ugc-net/results/:testId/:attemptId',
    name: 'UGCNetResults',
    component: UGCNetTestResults,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/ugc-net/practice/:attemptId',
    name: 'PracticeTest',
    component: () => import('@/views/ugc-net/PracticeTest.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/ugc-net/practice/:attemptId/take',
    name: 'PracticeTaking',
    component: () => import('@/views/ugc-net/PracticeTaking.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/ugc-net/practice/setup',
    name: 'UGCNetPracticeSetup', 
    component: () => import('@/views/ugc-net/PracticeSetup.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ugc-net/practice/:attemptId/results',
    name: 'PracticeResults',
    component: () => import('@/views/ugc-net/PracticeResults.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/ugc-net/performance',
    redirect: '/ugc-net'
  },
  {
    path: '/ugc-net/syllabus',
    redirect: '/ugc-net'
  },
  {
    path: '/ugc-net/tests',
    redirect: '/ugc-net'
  },
  // User Routes - Consistent naming pattern
  {
    path: '/user/history',
    name: 'UserHistory',
    component: () => import('@/views/user/History.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/practice-tests',
    redirect: '/ugc-net/practice/setup'
  },
  {
    path: '/user/profile',
    name: 'UserProfile',
    component: () => import('@/views/user/ProfileSettings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/notifications',
    name: 'UserNotifications',
    component: () => import('@/views/user/Notifications.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/analytics',
    name: 'UserAnalytics',
    component: () => import('@/views/user/Analytics.vue'),
    meta: { requiresAuth: true }
  },
  // Legacy user routes - redirects for backward compatibility
  {
    path: '/history',
    redirect: '/user/history'
  },
  {
    path: '/practice-tests',
    redirect: '/ugc-net/practice/setup'
  },
  {
    path: '/profile',
    redirect: '/user/profile'
  },
  {
    path: '/notifications',
    redirect: '/user/notifications'
  },
  {
    path: '/analytics',
    redirect: '/user/analytics'
  },
  // Admin Routes
  {
    path: '/admin',
    redirect: '/dashboard'
  },
  {
    path: '/admin/subjects',
    name: 'SubjectManagement',
    component: SubjectManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/analytics',
    name: 'Analytics',
    component: Analytics,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/ai-questions',
    name: 'AIQuestionGenerator',
    component: AIQuestionGenerator,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/ai-quiz',
    redirect: '/admin/ai-questions'
  },
  {
    path: '/admin/quiz-generator',
    redirect: '/admin/ai-questions'
  },
  {
    path: '/admin/ugc-net',
    name: 'UGCNetManagement',
    component: () => import('@/views/admin/UGCNetManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/questions',
    name: 'QuestionManagement',
    component: () => import('@/views/admin/QuestionManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/question-bank',
    name: 'QuestionBankManagement',
    component: () => import('@/views/admin/QuestionBankManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/study-materials',
    name: 'StudyMaterialsManagement',
    component: () => import('@/views/admin/StudyMaterialsManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: () => import('@/views/admin/UserManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/profile',
    name: 'AdminProfile',
    component: () => import('@/views/admin/AdminProfileSettings.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('prepcheck_token')
  const user = JSON.parse(localStorage.getItem('prepcheck_user') || '{}')
  
  // Helper function to check if token is valid
  const isValidToken = (token) => {
    if (!token) return false
    try {
      // Simple check for JWT format (3 parts separated by dots)
      const parts = token.split('.')
      if (parts.length !== 3) return false
      
      // Decode payload to check expiration
      const payload = JSON.parse(atob(parts[1]))
      const now = Date.now() / 1000
      
      // Check if token is expired
      if (payload.exp && payload.exp < now) {
        // Token is expired, clear localStorage
        localStorage.removeItem('prepcheck_token')
        localStorage.removeItem('prepcheck_user')
        return false
      }
      
      return true
    } catch (error) {
      // Invalid token format, clear localStorage
      localStorage.removeItem('prepcheck_token')
      localStorage.removeItem('prepcheck_user')
      return false
    }
  }
  
  const hasValidToken = isValidToken(token)
  
  // Allow unauthenticated access to guest pages (login, register, etc.)
  if (to.meta.guest && !hasValidToken) {
    next()
    return
  }

  // Redirect authenticated users away from guest pages
  if (to.meta.guest && hasValidToken) {
    if (user.is_admin) {
      next('/admin/dashboard')
    } else {
      next('/dashboard')
    }
    return
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !hasValidToken) {
    next('/login')
    return
  }
  
  // Check if route requires admin privileges
  if (to.meta.requiresAdmin && (!user.is_admin || !hasValidToken)) {
    next('/dashboard')
    return
  }
  
  // Redirect root path to appropriate dashboard based on user role
  if (to.path === '/' && hasValidToken) {
    if (user.is_admin) {
      next('/admin/dashboard')
    } else {
      next('/dashboard')
    }
    return
  }

  // Redirect admin to admin dashboard if they try to access user dashboard
  if (to.path === '/dashboard' && user.is_admin) {
    next('/admin/dashboard')
    return
  }

  // Redirect user to user dashboard if they try to access admin dashboard
  if (to.path === '/admin/dashboard' && !user.is_admin) {
    next('/dashboard')
    return
  }

  // Redirect admin users away from user-specific routes
  if (hasValidToken && user.is_admin && to.path.startsWith('/user/')) {
    next('/admin/profile')
    return
  }

  // Redirect non-admin users away from admin routes
  if (hasValidToken && !user.is_admin && to.path.startsWith('/admin/')) {
    next('/user/profile')
    return
  }
  
  next()
})

export default router