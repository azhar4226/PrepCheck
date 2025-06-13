import { createRouter, createWebHistory } from 'vue-router'

// Auth Components
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'

// User Components
import UserDashboard from '@/views/user/Dashboard.vue'

// Quiz Components
import QuizBrowse from '@/views/quiz/Browse.vue'
import QuizTaking from '@/views/quiz/Taking.vue'

// Admin Components
import AdminDashboard from '@/views/admin/Dashboard.vue'
import SubjectManagement from '@/views/admin/SubjectManagement.vue'

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
    name: 'Dashboard',
    component: UserDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/quiz',
    name: 'QuizBrowse',
    component: QuizBrowse,
    meta: { requiresAuth: true }
  },
  {
    path: '/quiz/:id/take',
    name: 'QuizTaking',
    component: QuizTaking,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/user/History.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/user/Profile.vue'),
    meta: { requiresAuth: true }
  },
  // Admin Routes
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
    name: 'SubjectManagement',
    component: SubjectManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('prepcheck_token')
  const user = JSON.parse(localStorage.getItem('prepcheck_user') || '{}')
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }
  
  // Check if route requires admin privileges
  if (to.meta.requiresAdmin && (!user.is_admin || !token)) {
    next('/dashboard')
    return
  }
  
  // Redirect authenticated users away from guest pages
  if (to.meta.guest && token) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router