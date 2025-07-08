<template>
  <div class="container-fluid vh-100">
    <div class="row h-100">
      <!-- Left Side - Hero Section -->
      <div class="col-lg-6 d-none d-lg-flex align-items-center justify-content-center bg-success text-white">
        <div class="text-center">
          <i class="bi bi-person-plus display-1 mb-4"></i>
          <h1 class="display-4 fw-bold mb-3">Join PrepCheck</h1>
          <p class="lead mb-4">Start your exam preparation journey with AI-powered learning</p>
          <div class="row text-center">
            <div class="col-4">
              <i class="bi bi-check-circle display-6"></i>
              <p class="mt-2">Free Account</p>
            </div>
            <div class="col-4">
              <i class="bi bi-trophy display-6"></i>
              <p class="mt-2">Achievement Tracking</p>
            </div>
            <div class="col-4">
              <i class="bi bi-people display-6"></i>
              <p class="mt-2">Study Groups</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - Register Form -->
      <div class="col-lg-6 d-flex align-items-center justify-content-center">
        <div class="w-100" style="max-width: 400px;">
          <div class="text-center mb-4">
            <h2 class="fw-bold text-success">Create Account</h2>
            <p class="text-muted">Join thousands of students preparing for success!</p>
          </div>

          <form @submit.prevent="handleRegister">
            <div class="mb-3">
              <label for="fullName" class="form-label">Full Name</label>
              <div class="input-group">
                <span class="input-group-text"><i class="bi bi-person"></i></span>
                <input
                  type="text"
                  class="form-control"
                  id="fullName"
                  v-model="form.full_name"
                  :class="{ 'is-invalid': errors.full_name }"
                  placeholder="Enter your full name"
                  required
                >
              </div>
              <div v-if="errors.full_name" class="invalid-feedback">{{ errors.full_name }}</div>
            </div>

            <div class="mb-3">
              <label for="email" class="form-label">Email Address</label>
              <div class="input-group">
                <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="form.email"
                  :class="{ 'is-invalid': errors.email }"
                  placeholder="Enter your email"
                  required
                >
              </div>
              <div v-if="errors.email" class="invalid-feedback">{{ errors.email }}</div>
            </div>

            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <div class="input-group">
                <span class="input-group-text"><i class="bi bi-lock"></i></span>
                <input
                  :type="showPassword ? 'text' : 'password'"
                  class="form-control"
                  id="password"
                  v-model="form.password"
                  :class="{ 'is-invalid': errors.password }"
                  placeholder="Create a password"
                  required
                >
                <button 
                  type="button" 
                  class="btn btn-outline-secondary"
                  @click="showPassword = !showPassword"
                >
                  <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
              <div v-if="errors.password" class="invalid-feedback">{{ errors.password }}</div>
              <div class="form-text">
                Password must be at least 8 characters with uppercase, lowercase, and numbers.
              </div>
            </div>

            <div class="mb-3">
              <label for="confirmPassword" class="form-label">Confirm Password</label>
              <div class="input-group">
                <span class="input-group-text"><i class="bi bi-lock-fill"></i></span>
                <input
                  :type="showConfirmPassword ? 'text' : 'password'"
                  class="form-control"
                  id="confirmPassword"
                  v-model="form.confirm_password"
                  :class="{ 'is-invalid': errors.confirm_password }"
                  placeholder="Confirm your password"
                  required
                >
                <button 
                  type="button" 
                  class="btn btn-outline-secondary"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
              <div v-if="errors.confirm_password" class="invalid-feedback">{{ errors.confirm_password }}</div>
            </div>

            <div class="mb-3 form-check">
              <input 
                type="checkbox" 
                class="form-check-input" 
                id="agreeTerms"
                v-model="form.agree_terms"
                :class="{ 'is-invalid': errors.agree_terms }"
                required
              >
              <label class="form-check-label" for="agreeTerms">
                I agree to the <a href="#" class="text-decoration-none">Terms of Service</a> and 
                <a href="#" class="text-decoration-none">Privacy Policy</a>
              </label>
              <div v-if="errors.agree_terms" class="invalid-feedback">{{ errors.agree_terms }}</div>
            </div>

            <div v-if="message" class="alert" :class="alertClass" role="alert">
              <i :class="messageIcon" class="me-2"></i>{{ message }}
            </div>

            <div class="d-grid">
              <button 
                type="submit" 
                class="btn btn-success btn-lg"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-person-plus me-2"></i>
                {{ loading ? 'Creating Account...' : 'Create Account' }}
              </button>
            </div>
          </form>

          <hr class="my-4">

          <div class="text-center">
            <p class="mb-0">Already have an account?</p>
            <router-link to="/login" class="btn btn-outline-success">
              <i class="bi bi-box-arrow-in-right me-2"></i>Sign In
            </router-link>
          </div>

          <!-- Features Section -->
          <div class="mt-4 p-3 bg-light rounded">
            <h6 class="text-center mb-3">What you'll get:</h6>
            <div class="row text-center small">
              <div class="col-6 mb-2">
                <i class="bi bi-check-circle-fill text-success me-1"></i>
                Unlimited Mock Tests
              </div>
              <div class="col-6 mb-2">
                <i class="bi bi-check-circle-fill text-success me-1"></i>
                Progress Tracking
              </div>
              <div class="col-6 mb-2">
                <i class="bi bi-check-circle-fill text-success me-1"></i>
                AI-Generated Questions
              </div>
              <div class="col-6 mb-2">
                <i class="bi bi-check-circle-fill text-success me-1"></i>
                Performance Analytics
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/authService'
import { validateEmail, validatePassword } from '@/services/utils'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    
    const form = ref({
      full_name: '',
      email: '',
      password: '',
      confirm_password: '',
      agree_terms: false
    })
    
    const errors = ref({})
    const loading = ref(false)
    const message = ref('')
    const messageType = ref('')
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
    
    const alertClass = computed(() => {
      return messageType.value === 'error' 
        ? 'alert-danger' 
        : 'alert-success'
    })
    
    const messageIcon = computed(() => {
      return messageType.value === 'error' 
        ? 'bi bi-exclamation-triangle-fill' 
        : 'bi bi-check-circle-fill'
    })
    
    const validateForm = () => {
      errors.value = {}
      
      // Full name validation
      if (!form.value.full_name.trim()) {
        errors.value.full_name = 'Full name is required'
      } else if (form.value.full_name.trim().length < 2) {
        errors.value.full_name = 'Full name must be at least 2 characters'
      }
      
      // Email validation
      if (!form.value.email) {
        errors.value.email = 'Email is required'
      } else if (!validateEmail(form.value.email)) {
        errors.value.email = 'Please enter a valid email address'
      }
      
      // Password validation
      if (!form.value.password) {
        errors.value.password = 'Password is required'
      } else if (!validatePassword(form.value.password)) {
        errors.value.password = 'Password must be at least 8 characters with uppercase, lowercase, and numbers'
      }
      
      // Confirm password validation
      if (!form.value.confirm_password) {
        errors.value.confirm_password = 'Please confirm your password'
      } else if (form.value.password !== form.value.confirm_password) {
        errors.value.confirm_password = 'Passwords do not match'
      }
      
      // Terms agreement validation
      if (!form.value.agree_terms) {
        errors.value.agree_terms = 'You must agree to the terms and conditions'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const handleRegister = async () => {
      if (!validateForm()) {
        return
      }
      
      loading.value = true
      message.value = ''
      
      try {
        const response = await authService.register({
          full_name: form.value.full_name.trim(),
          email: form.value.email.toLowerCase().trim(),
          password: form.value.password
        })
        
        message.value = 'Account created successfully! Please sign in.'
        messageType.value = 'success'
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
          router.push('/login')
        }, 2000)
        
      } catch (error) {
        console.error('Registration error:', error)
        
        if (error.response?.data?.message) {
          message.value = error.response.data.message
        } else if (error.response?.data?.errors) {
          // Handle validation errors from backend
          errors.value = error.response.data.errors
          message.value = 'Please fix the errors below'
        } else {
          message.value = 'Registration failed. Please try again.'
        }
        
        messageType.value = 'error'
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      errors,
      loading,
      message,
      messageType,
      alertClass,
      messageIcon,
      showPassword,
      showConfirmPassword,
      handleRegister
    }
  }
}
</script>

<style scoped>
.form-control:focus {
  border-color: #198754;
  box-shadow: 0 0 0 0.2rem rgba(25, 135, 84, 0.25);
}

.btn-success {
  background-color: #198754;
  border-color: #198754;
}

.btn-success:hover {
  background-color: #157347;
  border-color: #146c43;
}

.btn-outline-success {
  color: #198754;
  border-color: #198754;
}

.btn-outline-success:hover {
  background-color: #198754;
  border-color: #198754;
}

.bg-success {
  background-color: #198754 !important;
}

.text-success {
  color: #198754 !important;
}

.alert-success {
  color: #0f5132;
  background-color: #d1e7dd;
  border-color: #badbcc;
}

.alert-danger {
  color: #842029;
  background-color: #f8d7da;
  border-color: #f5c2c7;
}
</style>