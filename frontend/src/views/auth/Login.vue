<template>
  <div class="container-fluid vh-100">
    <div class="row h-100">
      <!-- Left Side - Hero Section -->
      <div class="col-lg-6 d-none d-lg-flex align-items-center justify-content-center bg-primary text-white">
        <div class="text-center">
          <i class="bi bi-book display-1 mb-4"></i>
          <h1 class="display-4 fw-bold mb-3">Welcome to PrepCheck</h1>
          <p class="lead mb-4">Your comprehensive exam preparation platform with AI-powered mock tests</p>
          <div class="row text-center">
            <div class="col-4">
              <i class="bi bi-lightning display-6"></i>
              <p class="mt-2">Fast Learning</p>
            </div>
            <div class="col-4">
              <i class="bi bi-robot display-6"></i>
              <p class="mt-2">AI Powered</p>
            </div>
            <div class="col-4">
              <i class="bi bi-graph-up display-6"></i>
              <p class="mt-2">Track Progress</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - Login Form -->
      <div class="col-lg-6 d-flex align-items-center justify-content-center">
        <div class="w-100" style="max-width: 400px;">
          <div class="text-center mb-4">
            <h2 class="fw-bold text-primary">Sign In</h2>
            <p class="text-muted">Welcome back! Please sign in to your account.</p>
          </div>

          <form @submit.prevent="handleLogin">
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
                  placeholder="Enter your password"
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
            </div>

            <div class="mb-3 form-check">
              <input type="checkbox" class="form-check-input" id="remember" v-model="form.remember">
              <label class="form-check-label" for="remember">Remember me</label>
            </div>

            <div v-if="errors.general" class="alert alert-danger" role="alert">
              <i class="bi bi-exclamation-triangle me-2"></i>
              {{ errors.general }}
            </div>

            <button
              type="submit"
              class="btn btn-primary w-100 mb-3"
              :disabled="isLoading"
            >
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-box-arrow-in-right me-2"></i>
              {{ isLoading ? 'Signing In...' : 'Sign In' }}
            </button>
          </form>

          <div class="text-center">
            <p class="mb-0">Don't have an account?</p>
            <router-link to="/register" class="text-decoration-none fw-bold">
              Create Account
            </router-link>
          </div>

          <!-- Demo Credentials
          <div class="mt-4 p-3 bg-light rounded">
            <h6 class="text-muted mb-2">Demo Credentials:</h6>
            <div class="row">
              <div class="col-6">
                <small class="text-muted d-block">Admin:</small>
                <small class="fw-bold">admin@prepcheck.com</small><br>
                <small class="fw-bold">admin123</small>
              </div>
              <div class="col-6">
                <button class="btn btn-sm btn-outline-primary" @click="fillDemoCredentials">
                  Use Demo
                </button>
              </div>
            </div>
          </div> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import authService from '@/services/authService'

export default {
  name: 'Login',
  data() {
    return {
      form: {
        email: '',
        password: '',
        remember: false
      },
      errors: {},
      isLoading: false,
      showPassword: false
    }
  },
  methods: {
    async handleLogin() {
      this.clearErrors()
      
      if (!this.validateForm()) {
        return
      }

      this.isLoading = true

      try {
        const data = await authService.login({
          email: this.form.email,
          password: this.form.password
        })

        localStorage.setItem('prepcheck_token', data.access_token)
        localStorage.setItem('prepcheck_user', JSON.stringify(data.user))

        // Ensure token is set before redirecting
        setTimeout(() => {
          this.$router.push('/dashboard')
        }, 100)

      } catch (error) {
        this.handleError(error)
      } finally {
        this.isLoading = false
      }
    },

    validateForm() {
      let isValid = true

      if (!this.form.email) {
        this.errors.email = 'Email is required'
        isValid = false
      } else if (!this.isValidEmail(this.form.email)) {
        this.errors.email = 'Please enter a valid email'
        isValid = false
      }

      if (!this.form.password) {
        this.errors.password = 'Password is required'
        isValid = false
      }

      return isValid
    },

    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    },

    handleError(error) {
      // Try to extract error message from backend response
      if (error.response && error.response.data) {
        if (error.response.data.message) {
          this.errors.general = error.response.data.message
        } else if (error.response.data.error) {
          this.errors.general = error.response.data.error
        } else {
          this.errors.general = 'Login failed. Please try again.'
        }
      } else {
        this.errors.general = 'Network error. Please check your connection.'
      }
    },

    clearErrors() {
      this.errors = {}
    },

    fillDemoCredentials() {
      this.form.email = 'admin@prepcheck.com'
      this.form.password = 'admin123'
    }
  }
}
</script>

<style scoped>
.vh-100 {
  min-height: 100vh;
}

.input-group-text {
  background-color: #f8f9fa;
  border-right: none;
}

.form-control {
  border-left: none;
}

.form-control:focus {
  border-color: #007bff;
  box-shadow: none;
}

.input-group-text + .form-control:focus {
  border-left: 1px solid #007bff;
}
</style>
