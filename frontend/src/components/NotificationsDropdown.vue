<template>
  <div class="notifications-dropdown">
    <!-- Notification Bell -->
    <div class="dropdown">
      <button 
        class="btn btn-outline-primary position-relative"
        type="button"
        data-bs-toggle="dropdown"
        @click="loadNotifications"
      >
        <i class="bi bi-bell"></i>
        <span 
          v-if="unreadCount > 0" 
          class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
        >
          {{ unreadCount > 99 ? '99+' : unreadCount }}
        </span>
      </button>

      <div class="dropdown-menu dropdown-menu-end notification-dropdown">
        <!-- Header -->
        <div class="dropdown-header d-flex justify-content-between align-items-center">
          <span>Notifications</span>
          <button 
            v-if="unreadCount > 0"
            class="btn btn-sm btn-outline-primary"
            @click="markAllAsRead"
          >
            Mark All Read
          </button>
        </div>

        <div class="dropdown-divider"></div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border spinner-border-sm" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <!-- Notifications List -->
        <div v-else-if="notifications.length > 0" class="notification-list">
          <div 
            v-for="notification in notifications" 
            :key="notification.id"
            class="dropdown-item notification-item"
            :class="{ 'unread': !notification.read }"
            @click="markAsRead(notification.id)"
          >
            <div class="d-flex">
              <div class="notification-icon me-3">
                <i 
                  class="notification-type-icon"
                  :class="getNotificationIcon(notification.type)"
                ></i>
              </div>
              <div class="flex-grow-1">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-message">{{ notification.message }}</div>
                <small class="notification-time text-muted">
                  {{ formatTime(notification.created_at) }}
                </small>
              </div>
              <div v-if="!notification.read" class="unread-indicator"></div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-4 text-muted">
          <i class="bi bi-bell-slash display-6 mb-2"></i>
          <p class="mb-0">No notifications</p>
        </div>

        <div class="dropdown-divider"></div>

        <!-- Footer -->
        <div class="dropdown-footer text-center">
          <router-link to="/notifications" class="btn btn-sm btn-primary">
            View All Notifications
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'

export default {
  name: 'NotificationsDropdown',
  setup() {
    const loading = ref(false)
    const notifications = ref([])
    const unreadCount = ref(0)

    const loadNotifications = async () => {
      try {
        loading.value = true
        const response = await api.get('/notifications?limit=10')
        notifications.value = response.data.notifications
        unreadCount.value = response.data.unread_count
      } catch (error) {
        console.error('Failed to load notifications:', error)
      } finally {
        loading.value = false
      }
    }

    const markAsRead = async (notificationId) => {
      try {
        await api.post(`/notifications/${notificationId}/read`)
        
        // Update local state
        const notification = notifications.value.find(n => n.id === notificationId)
        if (notification && !notification.read) {
          notification.read = true
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
      } catch (error) {
        console.error('Failed to mark notification as read:', error)
      }
    }

    const markAllAsRead = async () => {
      try {
        await api.post('/notifications/mark-all-read')
        
        // Update local state
        notifications.value.forEach(notification => {
          notification.read = true
        })
        unreadCount.value = 0
      } catch (error) {
        console.error('Failed to mark all notifications as read:', error)
      }
    }

    const getNotificationIcon = (type) => {
      switch (type) {
        case 'success':
          return 'bi bi-check-circle-fill text-success'
        case 'warning':
          return 'bi bi-exclamation-triangle-fill text-warning'
        case 'error':
          return 'bi bi-x-circle-fill text-danger'
        case 'info':
        default:
          return 'bi bi-info-circle-fill text-info'
      }
    }

    const formatTime = (dateString) => {
      const date = new Date(dateString)
      const now = new Date()
      const diffInMinutes = Math.floor((now - date) / (1000 * 60))

      if (diffInMinutes < 1) {
        return 'Just now'
      } else if (diffInMinutes < 60) {
        return `${diffInMinutes}m ago`
      } else if (diffInMinutes < 1440) {
        const hours = Math.floor(diffInMinutes / 60)
        return `${hours}h ago`
      } else {
        const days = Math.floor(diffInMinutes / 1440)
        return `${days}d ago`
      }
    }

    // Auto-refresh notifications every 30 seconds
    const startAutoRefresh = () => {
      setInterval(() => {
        loadNotifications()
      }, 30000)
    }

    onMounted(() => {
      loadNotifications()
      startAutoRefresh()
    })

    return {
      loading,
      notifications,
      unreadCount,
      loadNotifications,
      markAsRead,
      markAllAsRead,
      getNotificationIcon,
      formatTime
    }
  }
}
</script>

<style scoped>
.notification-dropdown {
  width: 350px;
  max-height: 400px;
  overflow-y: auto;
}

.dropdown-header {
  font-weight: 600;
  padding: 0.75rem 1rem;
}

.dropdown-footer {
  padding: 0.75rem 1rem;
}

.notification-list {
  max-height: 300px;
  overflow-y: auto;
}

.notification-item {
  padding: 0.75rem 1rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: #f8f9fa;
}

.notification-item.unread {
  background-color: #e3f2fd;
  border-left: 3px solid #2196f3;
}

.notification-icon {
  width: 24px;
  text-align: center;
}

.notification-type-icon {
  font-size: 1.25rem;
}

.notification-title {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.notification-message {
  font-size: 0.8rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.notification-time {
  font-size: 0.75rem;
}

.unread-indicator {
  width: 8px;
  height: 8px;
  background-color: #2196f3;
  border-radius: 50%;
  margin-top: 0.25rem;
}

.badge {
  font-size: 0.6rem;
}

/* Custom scrollbar for notification list */
.notification-list::-webkit-scrollbar {
  width: 4px;
}

.notification-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.notification-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.notification-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
