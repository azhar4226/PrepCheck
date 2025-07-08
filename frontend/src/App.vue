<template>
  <div id="app">
    <!-- Navigation -->
    <AppHeader />

    <!-- Main Content -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- Footer -->
    <AppFooter />

    <!-- Loading Overlay -->
    <LoadingOverlay 
      :is-visible="isLoading" 
      :message="loadingMessage" 
      show-message 
    />
  </div>
</template>

<script>
import { onMounted } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import LoadingOverlay from '@/components/ui/LoadingOverlay.vue'
import { useAppState } from '@/composables/useAppState.js'
import { useAuth } from '@/composables/useAuth.js'

export default {
  name: 'App',
  components: {
    AppHeader,
    AppFooter,
    LoadingOverlay
  },
  setup() {
    const { isLoading, loadingMessage } = useAppState()
    const auth = useAuth()
    
    // Initialize authentication on app mount
    onMounted(() => {
      try {
        // Safe initialization with error handling
        console.log('Initializing auth...')
        auth.initializeAuth()
        console.log('Auth initialized successfully')
      } catch (error) {
        console.error('Failed to initialize auth:', error)
      }
    })
    
    return {
      isLoading,
      loadingMessage
    }
  }
}
</script>

<style>
/* Import global styles */
@import '@/assets/styles/global.css';
</style>
