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
              
              <!-- Admin Dropdown -->
              <li v-if="user?.is_admin" class="nav-item dropdown">
                <a 
                  class="nav-link dropdown-toggle" 
                  href="#" 
                  role="button" 
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
                    <li><hr class="dropdown-divider"></li>
                    <li>
                      <router-link class="dropdown-item" to="/admin/settings">
                        <i class="bi bi-sliders me-2"></i>
                        Settings
                      </router-link>
                    </li>
                  </ul>
              </li>
              
              <!-- User Dropdown -->
              <li class="nav-item dropdown">
                <a 
                  class="nav-link dropdown-toggle" 
                  href="#" 
                  role="button" 
                  data-bs-toggle="dropdown"
                >
                  <i class="bi bi-person-circle me-1"></i>
                  {{ user?.username || 'User' }}
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
export default {
  name: 'App',
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
.navbar-brand {
  font-size: 1.5rem;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

/* Card Styles */
.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transition: box-shadow 0.15s ease-in-out;
}

.card:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

/* Button Styles */
.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover {
  background-color: #0056b3;
  border-color: #004085;
}

.btn-success {
  background-color: #28a745;
  border-color: #28a745;
}

.btn-success:hover {
  background-color: #1e7e34;
  border-color: #1c7430;
}

.btn-warning {
  background-color: #ffc107;
  border-color: #ffc107;
}

.btn-warning:hover {
  background-color: #d39e00;
  border-color: #c69500;
}

.btn-danger {
  background-color: #dc3545;
  border-color: #dc3545;
}

.btn-danger:hover {
  background-color: #bd2130;
  border-color: #b21f2d;
}

/* Form Styles */
.form-control:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-select:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

/* Quiz Styles */
.quiz-option {
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.quiz-option:hover {
  background-color: #f8f9fa;
  border-color: #007bff;
}

.quiz-option.selected {
  background-color: #e3f2fd;
  border-color: #007bff;
}

.quiz-option.correct {
  background-color: #d4edda;
  border-color: #28a745;
}

.quiz-option.incorrect {
  background-color: #f8d7da;
  border-color: #dc3545;
}

/* Progress Bar */
.progress {
  height: 8px;
}

/* Stats Cards */
.stats-card {
  background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
}

.stats-card .card-body {
  padding: 1.5rem;
}

.stats-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

/* Animation */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in {
  animation: fadeIn 0.5s ease-out;
}

/* Responsive */
@media (max-width: 768px) {
  .navbar-brand {
    font-size: 1.25rem;
  }
  
  .stats-icon {
    font-size: 2rem;
  }
  
  .card-body {
    padding: 1rem;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .card {
    background-color: #343a40;
    color: #fff;
  }
  
  .card-header {
    background-color: #495057;
    border-bottom-color: #6c757d;
  }
}
</style>
