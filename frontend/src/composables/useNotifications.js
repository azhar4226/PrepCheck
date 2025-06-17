// Composable for notification/toast management
import { ref, reactive } from 'vue'

const notifications = ref([])
const config = reactive({
  maxNotifications: 5,
  defaultDuration: 5000,
  position: 'top-right'
})

export function useNotifications() {
  
  const addNotification = (message, type = 'info', options = {}) => {
    const notification = {
      id: Date.now() + Math.random(),
      message,
      type, // success, error, warning, info
      duration: options.duration || config.defaultDuration,
      persistent: options.persistent || false,
      icon: getIcon(type),
      createdAt: new Date()
    }
    
    notifications.value.unshift(notification)
    
    // Remove excess notifications
    if (notifications.value.length > config.maxNotifications) {
      notifications.value = notifications.value.slice(0, config.maxNotifications)
    }
    
    // Auto-remove non-persistent notifications
    if (!notification.persistent) {
      setTimeout(() => {
        removeNotification(notification.id)
      }, notification.duration)
    }
    
    return notification.id
  }
  
  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }
  
  const clearAll = () => {
    notifications.value = []
  }
  
  const getIcon = (type) => {
    const icons = {
      success: 'bi-check-circle-fill',
      error: 'bi-x-circle-fill',
      warning: 'bi-exclamation-triangle-fill',
      info: 'bi-info-circle-fill'
    }
    return icons[type] || icons.info
  }
  
  // Convenience methods
  const success = (message, options) => addNotification(message, 'success', options)
  const error = (message, options) => addNotification(message, 'error', options)
  const warning = (message, options) => addNotification(message, 'warning', options)
  const info = (message, options) => addNotification(message, 'info', options)
  
  return {
    notifications,
    config,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info
  }
}
