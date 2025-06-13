<template>
  <div id="app">
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
      <div class="container">
        <router-link class="navbar-brand fw-bold" to="/">
          <i class="bi bi-book me-2"></i>
          PrepCheck
        </router-link>
        
        <button 
          class="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <template v-if="!isAuthenticated">
              <li class="nav-item">
                <router-link class="nav-link" to="/login">Login</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/register">Register</router-link>
              </li>
            </template>
            
            <template v-else>
              <li class="nav-item">
                <router-link class="nav-link" to="/dashboard">
                  <i class="bi bi-speedometer2 me-1"></i>
                  Dashboard
                </router-link>
              </li>
              
              <li v-if="!user?.is_admin" class="nav-item">
                <router-link class="nav-link" to="/quiz">
                  <i class="bi bi-list-check me-1"></i>
                  Quizzes
                </router-link>
              </li>
              
              <li v-if="!user?.is_admin" class="nav-item">
                <router-link class="nav-link" to="/history">
                  <i class="bi bi-clock-history me-1"></i>
                  History
                </router-link>
              </li>
              
              <template v-if="user?.is_admin">
                <li class="nav-item dropdown">
                  <a 
                    class="nav-link dropdown-toggle" 
                    href="#" 
                    data-bs-toggle="dropdown"
                  >
                    <i class="bi bi-gear me-1"></i>
                    Admin
                  </a>
                  <ul class="dropdown-menu">
                    <li>
                      <router-link class="dropdown-item" to="/admin/subjects">
                        <i class="bi bi-collection me-2"></i>
                        Subjects
                      </router-link>
                    </li>
                    <li>
                      <router-link class="dropdown-item" to="/admin/analytics">
                        <i class="bi bi-bar-chart me-2"></i>
                        Analytics
                      </router-link>
                    </li>
                    <li>
                      <router-link class="dropdown-item" to="/admin/quizzes">
                        <i class="bi bi-question-circle me-2"></i>
                        Quizzes
                      </router-link>
                    </li>
                    <li>
                      <router-link class="dropdown-item" to="/admin/users">
                        <i class="bi bi-people me-2"></i>
                        Users
                      </router-link>
                    </li>
                    <li>
                      <router-link class="dropdown-item" to="/admin/ai-quiz">
                        <i class="bi bi-robot me-2"></i>
                        AI Quiz Generator
                      </router-link>
                    </li>
                  </ul>
                </li>
              </template>
              
              <!-- Notifications Dropdown -->
              <li v-if="isAuthenticated" class="nav-item">
                <NotificationsDropdown />
              </li>
              
              <li class="nav-item dropdown">
                <a 
                  class="nav-link dropdown-toggle" 
                  href="#" 
                  data-bs-toggle="dropdown"
                >
                  <i class="bi bi-person-circle me-1"></i>
                  {{ user?.full_name }}
                </a>
                <ul class="dropdown-menu">
                  <li>
                    <router-link class="dropdown-item" to="/profile">
                      <i class="bi bi-person me-2"></i>
                      Profile
                    </router-link>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <a class="dropdown-item" href="#" @click="logout">
                      <i class="bi bi-box-arrow-right me-2"></i>
                      Logout
                    </a>
                  </li>
                </ul>
              </li>
            </template>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-light py-4 mt-5">
      <div class="container">
        <div class="row">
          <div class="col-md-6">
            <h5>PrepCheck</h5>
            <p class="mb-0">Your comprehensive exam preparation platform.</p>
          </div>
          <div class="col-md-6 text-md-end">
            <p class="mb-0">&copy; 2025 PrepCheck. All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script>
import NotificationsDropdown from '@/components/NotificationsDropdown.vue'

export default {
  name: 'App',
  components: {
    NotificationsDropdown
  },
  data() {
    return {
      isLoading: false
    }
  },
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('prepcheck_token')
    },
    user() {
      const userData = localStorage.getItem('prepcheck_user')
      return userData ? JSON.parse(userData) : null
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('prepcheck_token')
      localStorage.removeItem('prepcheck_user')
      this.$router.push('/login')
    }
  },
  mounted() {
    // Set global loading state
    this.$root.setLoading = (loading) => {
      this.isLoading = loading
    }
  }
}
</script>

<style>
/* Global Styles */
* {
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  padding-top: 76px; /* Account for fixed navbar */
}

.main-content {
  min-height: calc(100vh - 200px);
}

/* Custom Components */
.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transition: box-shadow 0.15s ease-in-out;
}

.card:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.btn {
  border-radius: 0.375rem;
  font-weight: 500;
}

.form-control, .form-select {
  border-radius: 0.375rem;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

/* Custom animations */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .container {
    padding-left: 15px;
    padding-right: 15px;
  }
  
  .card {
    margin-bottom: 1rem;
  }
}

/* Quiz specific styles */
.quiz-timer {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 1000;
  background: white;
  border: 2px solid #dc3545;
  border-radius: 8px;
  padding: 10px 15px;
  font-weight: bold;
  color: #dc3545;
}

.question-card {
  border-left: 4px solid #007bff;
}

.option-button {
  text-align: left;
  border: 2px solid #e9ecef;
  background: white;
  transition: all 0.2s;
}

.option-button:hover {
  border-color: #007bff;
  background-color: #f8f9fa;
}

.option-button.selected {
  border-color: #007bff;
  background-color: #e3f2fd;
  color: #1976d2;
}

.option-button.correct {
  border-color: #28a745;
  background-color: #d4edda;
  color: #155724;
}

.option-button.incorrect {
  border-color: #dc3545;
  background-color: #f8d7da;
  color: #721c24;
}

/* Stats cards */
.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.success {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card.warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card.info {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

/* Notifications dropdown in navbar */
.navbar .notifications-dropdown .btn {
  color: rgba(255, 255, 255, 0.8);
  border-color: rgba(255, 255, 255, 0.3);
}

.navbar .notifications-dropdown .btn:hover {
  color: white;
  border-color: rgba(255, 255, 255, 0.5);
  background-color: rgba(255, 255, 255, 0.1);
}

.navbar .notifications-dropdown .dropdown-menu {
  margin-top: 0.5rem;
}
</style>
