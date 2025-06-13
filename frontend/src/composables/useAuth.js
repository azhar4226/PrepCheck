import { ref, computed } from 'vue'
import axios from 'axios'

// Shared state
const user = ref(null)
const token = ref(null)
const loading = ref(false)

// Initialize from localStorage
const initializeAuth = () => {
  const savedToken = localStorage.getItem('prepcheck_token')
  const savedUser = localStorage.getItem('prepcheck_user')
  
  if (savedToken) {
    token.value = savedToken
    // Set default axios authorization header
    setAuthHeader(savedToken)
  }
  
  if (savedUser) {
    try {
      user.value = JSON.parse(savedUser)
    } catch (error) {
      console.error('Error parsing saved user:', error)
      localStorage.removeItem('prepcheck_user')
    }
  }
}

// Set authorization header for axios
const setAuthHeader = (authToken) => {
  if (authToken) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`
  } else {
    delete axios.defaults.headers.common['Authorization']
  }
}

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' 
    ? 'http://localhost:8000'  // Docker backend URL
    : 'http://localhost:5000', // Development backend URL
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const authToken = token.value || localStorage.getItem('prepcheck_token')
    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      logout()
      // Redirect to login page if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export function useAuth() {
  // Computed properties
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  const userRole = computed(() => user.value?.role || 'user')
  
  // Login function
  const login = async (credentials) => {
    try {
      loading.value = true
      
      const response = await api.post('/api/auth/login', credentials)
      
      if (response.data.success) {
        const { token: authToken, user: userData } = response.data.data
        
        // Store in reactive state
        token.value = authToken
        user.value = userData
        
        // Store in localStorage
        localStorage.setItem('prepcheck_token', authToken)
        localStorage.setItem('prepcheck_user', JSON.stringify(userData))
        
        // Set axios auth header
        setAuthHeader(authToken)
        
        return { success: true, user: userData }
      } else {
        throw new Error(response.data.message || 'Login failed')
      }
    } catch (error) {
      console.error('Login error:', error)
      return {
        success: false,
        message: error.response?.data?.message || error.message || 'Login failed'
      }
    } finally {
      loading.value = false
    }
  }
  
  // Register function
  const register = async (registrationData) => {
    try {
      loading.value = true
      
      const response = await api.post('/api/auth/register', registrationData)
      
      if (response.data.success) {
        const { token: authToken, user: userData } = response.data.data
        
        // Store in reactive state
        token.value = authToken
        user.value = userData
        
        // Store in localStorage
        localStorage.setItem('prepcheck_token', authToken)
        localStorage.setItem('prepcheck_user', JSON.stringify(userData))
        
        // Set axios auth header
        setAuthHeader(authToken)
        
        return { success: true, user: userData }
      } else {
        throw new Error(response.data.message || 'Registration failed')
      }
    } catch (error) {
      console.error('Registration error:', error)
      return {
        success: false,
        message: error.response?.data?.message || error.message || 'Registration failed'
      }
    } finally {
      loading.value = false
    }
  }
  
  // Logout function
  const logout = async () => {
    try {
      // Try to call logout endpoint
      if (token.value) {
        await api.post('/api/auth/logout')
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear state regardless of API call result
      token.value = null
      user.value = null
      
      // Clear localStorage
      localStorage.removeItem('prepcheck_token')
      localStorage.removeItem('prepcheck_user')
      
      // Clear axios auth header
      setAuthHeader(null)
    }
  }
  
  // Update user profile
  const updateProfile = async (profileData) => {
    try {
      loading.value = true
      
      const response = await api.put('/api/auth/profile', profileData)
      
      if (response.data.success) {
        const updatedUser = response.data.data
        
        // Update reactive state
        user.value = updatedUser
        
        // Update localStorage
        localStorage.setItem('prepcheck_user', JSON.stringify(updatedUser))
        
        return { success: true, user: updatedUser }
      } else {
        throw new Error(response.data.message || 'Profile update failed')
      }
    } catch (error) {
      console.error('Profile update error:', error)
      return {
        success: false,
        message: error.response?.data?.message || error.message || 'Profile update failed'
      }
    } finally {
      loading.value = false
    }
  }
  
  // Change password
  const changePassword = async (passwordData) => {
    try {
      loading.value = true
      
      const response = await api.put('/api/auth/password', passwordData)
      
      if (response.data.success) {
        return { success: true, message: 'Password changed successfully' }
      } else {
        throw new Error(response.data.message || 'Password change failed')
      }
    } catch (error) {
      console.error('Password change error:', error)
      return {
        success: false,
        message: error.response?.data?.message || error.message || 'Password change failed'
      }
    } finally {
      loading.value = false
    }
  }
  
  // Refresh user data
  const refreshUser = async () => {
    if (!token.value) return { success: false, message: 'Not authenticated' }
    
    try {
      loading.value = true
      
      const response = await api.get('/api/auth/me')
      
      if (response.data.success) {
        const userData = response.data.data
        
        // Update reactive state
        user.value = userData
        
        // Update localStorage
        localStorage.setItem('prepcheck_user', JSON.stringify(userData))
        
        return { success: true, user: userData }
      } else {
        throw new Error(response.data.message || 'Failed to refresh user data')
      }
    } catch (error) {
      console.error('Refresh user error:', error)
      
      // If token is invalid, logout
      if (error.response?.status === 401) {
        logout()
      }
      
      return {
        success: false,
        message: error.response?.data?.message || error.message || 'Failed to refresh user data'
      }
    } finally {
      loading.value = false
    }
  }
  
  // Check if user has permission
  const hasPermission = (permission) => {
    if (!user.value) return false
    if (user.value.is_admin) return true
    return user.value.permissions?.includes(permission) || false
  }
  
  // Check if user has role
  const hasRole = (role) => {
    if (!user.value) return false
    return user.value.role === role || user.value.is_admin
  }
  
  // Initialize auth state when composable is first used
  if (!token.value && !user.value) {
    initializeAuth()
  }
  
  return {
    // State
    user: computed(() => user.value),
    token: computed(() => token.value),
    loading: computed(() => loading.value),
    
    // Computed
    isAuthenticated,
    isAdmin,
    userRole,
    
    // Methods
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    refreshUser,
    hasPermission,
    hasRole,
    
    // API instance
    api
  }
}

// Export for direct use if needed
export { api }
