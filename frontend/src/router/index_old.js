import { createRouter, createWebHistory } from 'vue-router'

// Import views
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'

// User views
import UserDashboard from '@/views/user/Dashboard.vue'
import QuizBrowse from '@/views/quiz/Browse.vue'
import QuizTaking from '@/views/quiz/Taking.vue'

// Admin views (to be created)
// import AdminDashboard from '@/views/admin/Dashboard.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  
  // User routes
  {
    path: '/quizzes',
    name: 'QuizList',
    component: QuizList,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/quiz/:id/take',
    name: 'QuizTake',
    component: QuizTake,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/quiz/results/:attemptId',
    name: 'QuizResults',
    component: QuizResults,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/history',
    name: 'UserHistory',
    component: UserHistory,
    meta: { requiresAuth: true, requiresUser: true }
  },
  
  // Admin routes
  {
    path: '/admin',
    redirect: '/admin/dashboard'
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/subjects',
    name: 'AdminSubjects',
    component: AdminSubjects,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes',
    name: 'AdminQuizzes',
    component: AdminQuizzes,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: AdminUsers,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/ai-quiz',
    name: 'AIQuizGenerator',
    component: AIQuizGenerator,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  
  // 404 page
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('prepcheck_token')
  const userData = localStorage.getItem('prepcheck_user')
  const user = userData ? JSON.parse(userData) : null
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }
  
  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && isAuthenticated) {
    if (user?.is_admin) {
      next('/admin/dashboard')
    } else {
      next('/dashboard')
    }
    return
  }
  
  // Check if route requires admin
  if (to.meta.requiresAdmin && (!user || !user.is_admin)) {
    next('/dashboard')
    return
  }
  
  // Check if route requires regular user (not admin)
  if (to.meta.requiresUser && user?.is_admin) {
    next('/admin/dashboard')
    return
  }
  
  next()
})

export default router
