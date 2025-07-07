<template>
  <div class="notifications-page">
    <div class="container">
      <h1 class="title">Notifications</h1>
      
      <div v-if="loading" class="has-text-centered">
        <div class="loader"></div>
        <p>Loading notifications...</p>
      </div>
      
      <div v-else-if="notifications.length === 0" class="has-text-centered">
        <div class="notification is-light">
          <span class="icon">
            <i class="fas fa-bell"></i>
          </span>
          <p>No notifications yet</p>
        </div>
      </div>
      
      <div v-else class="notifications-list">
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          class="notification"
          :class="{ 'is-light': notification.read }"
        >
          <button 
            v-if="!notification.read"
            class="delete is-small"
            @click="markAsRead(notification.id)"
          ></button>
          
          <div class="notification-content">
            <h5 class="title is-6">{{ notification.title }}</h5>
            <p class="content">{{ notification.message }}</p>
            <p class="has-text-grey is-size-7">
              {{ formatDate(notification.created_at) }}
            </p>
          </div>
        </div>
      </div>
      
      <div v-if="notifications.length > 0" class="has-text-centered mt-4">
        <button 
          class="button is-light"
          @click="markAllAsRead"
          :disabled="!hasUnreadNotifications"
        >
          Mark All as Read
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import notificationsService from '@/services/notificationsService'

const notifications = ref([])
const loading = ref(false)

const hasUnreadNotifications = computed(() => {
  return notifications.value.some(n => !n.read)
})

const loadNotifications = async () => {
  try {
    loading.value = true
    const response = await notificationsService.getNotifications()
    notifications.value = response.notifications || []
  } catch (error) {
    console.error('Failed to load notifications:', error)
  } finally {
    loading.value = false
  }
}

const markAsRead = async (notificationId) => {
  try {
    await notificationsService.markAsRead(notificationId)
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.read = true
    }
  } catch (error) {
    console.error('Failed to mark notification as read:', error)
  }
}

const markAllAsRead = async () => {
  try {
    await notificationsService.markAllAsRead()
    notifications.value.forEach(n => n.read = true)
  } catch (error) {
    console.error('Failed to mark all notifications as read:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

onMounted(() => {
  loadNotifications()
})
</script>

<style scoped>
.notifications-page {
  padding: 2rem;
}

.notifications-list {
  max-width: 800px;
  margin: 0 auto;
}

.notification {
  margin-bottom: 1rem;
  position: relative;
}

.notification-content {
  padding-left: 0.5rem;
}

.loader {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
