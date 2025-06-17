import { ref, computed } from 'vue'

// Global app state
const isLoading = ref(false)
const loadingMessage = ref('Loading...')

export function useAppState() {
  const setLoading = (loading, message = 'Loading...') => {
    isLoading.value = loading
    loadingMessage.value = message
  }

  const startLoading = (message = 'Loading...') => {
    setLoading(true, message)
  }

  const stopLoading = () => {
    setLoading(false)
  }

  return {
    isLoading: computed(() => isLoading.value),
    loadingMessage: computed(() => loadingMessage.value),
    setLoading,
    startLoading,
    stopLoading
  }
}
