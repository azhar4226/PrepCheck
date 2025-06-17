// Composable for modal management
import { ref, nextTick } from 'vue'

export function useModal() {
  const isOpen = ref(false)
  const data = ref(null)
  const loading = ref(false)
  
  const open = (initialData = null) => {
    data.value = initialData
    isOpen.value = true
    
    // Focus management
    nextTick(() => {
      const modal = document.querySelector('.modal[style*="display: block"]')
      const firstInput = modal?.querySelector('input, select, textarea, button')
      firstInput?.focus()
    })
  }
  
  const close = () => {
    isOpen.value = false
    data.value = null
    loading.value = false
  }
  
  const confirm = async (callback) => {
    try {
      loading.value = true
      await callback(data.value)
      close()
      return true
    } catch (error) {
      console.error('Modal action failed:', error)
      return false
    } finally {
      loading.value = false
    }
  }
  
  return {
    isOpen,
    data,
    loading,
    open,
    close,
    confirm
  }
}
