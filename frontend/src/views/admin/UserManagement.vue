<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-people me-2"></i>
              User Management
            </h5>
            <button 
              class="btn btn-primary btn-sm"
              @click="loadUsers"
            >
              <i class="bi bi-arrow-clockwise me-1"></i>
              Refresh
            </button>
          </div>
          
          <div class="card-body">
            <!-- Loading State -->
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2 text-muted">Loading users...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="alert alert-danger">
              <i class="bi bi-exclamation-triangle me-2"></i>
              {{ error }}
            </div>

            <!-- Users Table -->
            <div v-else>
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-dark">
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="user in users" :key="user.id">
                      <td>{{ user.id }}</td>
                      <td>{{ user.name }}</td>
                      <td>{{ user.email }}</td>
                      <td>
                        <span :class="user.role === 'admin' ? 'badge bg-danger' : 'badge bg-secondary'">
                          {{ user.role || 'user' }}
                        </span>
                      </td>
                      <td>
                        <span :class="user.is_active ? 'badge bg-success' : 'badge bg-warning'">
                          {{ user.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <button class="btn btn-sm btn-outline-primary me-1">Edit</button>
                        <button class="btn btn-sm btn-outline-danger">Delete</button>
                      </td>
                    </tr>
                    <tr v-if="users.length === 0">
                      <td colspan="6" class="text-center text-muted py-4">
                        No users found
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'

export default {
  name: 'UserManagement',
  setup() {
    const { makeAuthenticatedRequest } = useAuth()
    
    const users = ref([])
    const loading = ref(false)
    const error = ref('')

    const loadUsers = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await makeAuthenticatedRequest('/api/admin/users')
        if (response.ok) {
          const data = await response.json()
          users.value = data.users || []
        } else {
          throw new Error('Failed to load users')
        }
      } catch (err) {
        error.value = err.message
        console.error('Error loading users:', err)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadUsers()
    })

    return {
      users,
      loading,
      error,
      loadUsers
    }
  }
}
</script>
