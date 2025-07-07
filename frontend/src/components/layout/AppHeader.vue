<template>
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
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
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
              <router-link class="nav-link" to="/dashboard" exact>
                <i class="bi bi-speedometer2 me-1"></i>
                Dashboard
              </router-link>
            </li>
            
            <li v-if="!user?.is_admin" class="nav-item">
              <router-link class="nav-link" to="/ugc-net" exact>
                <i class="bi bi-mortarboard me-1"></i>
                UGC NET
              </router-link>
            </li>
            
            <li v-if="!user?.is_admin" class="nav-item">
            </li>
            
            <li v-if="!user?.is_admin" class="nav-item">
              <router-link class="nav-link" to="/history" exact>
                <i class="bi bi-clock-history me-1"></i>
                History
              </router-link>
            </li>
            
            <!-- Notifications Dropdown -->
            <li v-if="isAuthenticated" class="nav-item">
              <NotificationsDropdown />
            </li>
            
            <li class="nav-item dropdown">
              <a 
                class="nav-link dropdown-toggle" 
                href="#" 
                id="profileDropdown"
                role="button"
                @click.prevent="toggleDropdown"
                aria-expanded="false"
              >
                <i class="bi bi-person-circle me-1"></i>
                {{ user?.full_name }}
              </a>
              <ul class="dropdown-menu" :class="{ show: dropdownOpen }" aria-labelledby="profileDropdown">
                <li>
                  <router-link class="dropdown-item" to="/profile">
                    <i class="bi bi-person me-2"></i>
                    Profile
                  </router-link>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item" href="#" @click="handleLogout">
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
</template>

<script setup>
import { computed, onMounted, nextTick, ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth.js'
import NotificationsDropdown from '@/components/layout/NotificationsDropdown.vue'

const { isAuthenticated, user, logout } = useAuth()
const router = useRouter()
const dropdownOpen = ref(false)

const handleLogout = () => {
  logout()
  router.push('/login')
}

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
}

const closeDropdown = (event) => {
  if (!event.target.closest('.dropdown')) {
    dropdownOpen.value = false
  }
}

// Close dropdown when clicking outside
onMounted(() => {
  document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
})
</script>

<style scoped>
/* ==========================================================================
   NAVBAR CONSISTENCY STYLES
   ========================================================================== */

/* 1. Override the NotificationsDropdown button to match navbar theme */
.navbar :deep(.notifications-dropdown .btn) {
  /* Remove Bootstrap button defaults */
  border: none;
  background: transparent;
  
  /* Match navbar link styling */
  color: rgba(255, 255, 255, 0.8);
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  transition: all 0.15s ease-in-out;
  
  /* Ensure proper sizing */
  font-size: 1rem;
  line-height: 1.5;
}

/* 2. Hover state - consistent with other nav links */
.navbar :deep(.notifications-dropdown .btn:hover) {
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
  transform: none; /* Remove scale effect for consistency */
}

/* 3. Focus state - accessibility */
/* .navbar :deep(.notifications-dropdown .btn:focus) {
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.25);
  outline: none;
} */

/* 4. Active state */
.navbar :deep(.notifications-dropdown .btn:active),
.navbar :deep(.notifications-dropdown .btn.show) {
  color: white;
  background-color: rgba(255, 255, 255, 0.15);
}

/* 5. Icon sizing consistency */
.navbar :deep(.notifications-dropdown .btn i) {
  font-size: 1.1rem; /* Slightly larger but not oversized */
}

/* 6. Dropdown menu positioning and styling */
.navbar :deep(.notifications-dropdown .dropdown-menu) {
  min-width: 350px;
  margin-top: 0.5rem;
  max-height: 400px;
  overflow-y: auto;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  background-color: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

/* 7. Badge positioning fine-tuning */
.navbar :deep(.notifications-dropdown .badge) {
  font-size: 0.65rem;
  padding: 0.25em 0.4em;
}

/* 8. Consistent sizing and styling for all nav links */
.navbar .nav-link {
  color: rgba(255, 255, 255, 0.8) !important;
  padding: 0.5rem 0.75rem !important;
  border-radius: 0.375rem;
  transition: all 0.15s ease-in-out;
  font-size: 1rem;
  line-height: 1.5;
  display: flex;
  align-items: center;
  white-space: nowrap;
}

/* 9. Consistent hover styling for all nav links */
.navbar .nav-link:hover {
  color: white !important;
  background-color: rgba(255, 255, 255, 0.1) !important;
}



/* 11. Consistent icon sizing for nav links */
.navbar .nav-link i {
  font-size: 1.1rem;
}

/* 12. Ensure dropdown toggle has consistent styling */
.navbar .dropdown-toggle {
  color: rgba(255, 255, 255, 0.8) !important;
  padding: 0.5rem 0.75rem !important;
  border-radius: 0.375rem;
  transition: all 0.15s ease-in-out;
  font-size: 1rem;
  line-height: 1.5;
  display: flex;
  align-items: center;
  text-decoration: none;
}

.navbar .dropdown-toggle:hover {
  color: white !important;
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.navbar .dropdown-toggle.show {
  color: white !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
}
</style>
