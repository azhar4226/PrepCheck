<template>
  <div class="user-management">
    <!-- Page Header -->
    <PageHeader
      title="User Management"
      subtitle="Manage users, roles, and permissions across the platform"
      icon="bi bi-people"
    >
      <template #actions>
        <button class="btn btn-outline-primary" @click="refreshUsers">
          <i class="bi bi-arrow-clockwise me-1"></i>Refresh
        </button>
        <button class="btn btn-primary" @click="showCreateUserModal = true">
          <i class="bi bi-plus-circle me-1"></i>Add User
        </button>
      </template>
    </PageHeader>

    <!-- User Statistics -->
    <StatsGrid :stats="userStats" @stat-click="handleStatClick" />

    <!-- User Data Table -->
    <DataTable
      :data="debugUsers"
      :columns="userColumns"
      :filters="userFilters"
      :loading="loading"
      :error="error"
      :show-filters="true"
      :enable-frontend-filtering="false"
      loading-message="Loading users..."
      empty-message="No users found"
      :show-pagination="true"
      :show-actions="true"
      :page-size="10"
      @edit="editUser"
      @delete="deleteUser"
      @filter-change="handleFilterChange"
    >
      <!-- Custom cell templates -->
      <template #cell-full_name="{ item }">
        <div v-if="item" class="d-flex align-items-center">
          <div class="avatar avatar-sm rounded-circle bg-gradient-info me-2">
            <span class="text-white text-xs">{{ getUserInitials(item.full_name) }}</span>
          </div>
          {{ item.full_name }}
        </div>
        <div v-else class="text-muted">
          <em>Invalid user data</em>
        </div>
      </template>

      <template #cell-role="{ item }">
        <div v-if="item" class="form-check form-switch">
          <input 
            class="form-check-input" 
            type="checkbox" 
            :checked="item.is_admin"
            @change="toggleUserRole(item)"
          >
          <label class="form-check-label">
            <span :class="item.is_admin ? 'badge bg-danger' : 'badge bg-secondary'">
              {{ item.is_admin ? 'Admin' : 'User' }}
            </span>
          </label>
        </div>
      </template>

      <template #cell-status="{ item }">
        <div v-if="item" class="form-check form-switch">
          <input 
            class="form-check-input" 
            type="checkbox" 
            :checked="item.is_active"
            @change="toggleUserStatus(item)"
          >
          <label class="form-check-label">
            <span :class="item.is_active ? 'badge bg-success' : 'badge bg-warning'">
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </span>
          </label>
        </div>
      </template>

      <template #cell-last_login="{ value }">
        <small class="text-muted">
          {{ value ? formatDate(value) : 'Never' }}
        </small>
      </template>

      <template #cell-created_at="{ value }">
        <small class="text-muted">
          {{ formatDate(value) }}
        </small>
      </template>

      <template #actions="{ item }">
        <div class="btn-group btn-group-sm">
          <button 
            class="btn btn-outline-info"
            @click="viewUser(item)"
            title="View Details"
          >
            <i class="bi bi-eye"></i>
          </button>
          <button 
            class="btn btn-outline-primary"
            @click="editUser(item)"
            title="Edit User"
          >
            <i class="bi bi-pencil"></i>
          </button>
          <button 
            class="btn btn-outline-danger"
            @click="deleteUser(item)"
            title="Delete User"
            :disabled="item.is_admin"
          >
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </template>
    </DataTable>

    <!-- User Details Modal -->
    <BaseModal
      v-if="showUserModal"
      :title="isViewMode ? 'User Details' : (selectedUser ? 'Edit User' : 'Create User')"
      icon="bi bi-person"
      @close="closeUserModal"
      @confirm="isViewMode ? closeUserModal : saveUser"
      :confirm-disabled="isViewMode ? false : !isUserFormValid"
      :confirm-text="isViewMode ? 'Close' : 'Save'"
      :show-footer="true"
    >
      <UserForm
        v-model="userForm"
        :errors="userFormErrors"
        :is-editing="!!selectedUser"
        :readonly="isViewMode"
      />
      <template #footer v-if="isViewMode">
        <button type="button" class="btn btn-secondary" @click="closeUserModal">
          Close
        </button>
      </template>
    </BaseModal>

    <!-- Delete Confirmation Modal -->
    <BaseModal
      v-if="showDeleteModal"
      title="Delete User"
      icon="bi bi-exclamation-triangle"
      confirm-text="Delete"
      @close="showDeleteModal = false"
      @confirm="confirmDeleteUser"
    >
      <p>Are you sure you want to delete <strong>{{ userToDelete?.full_name }}</strong>?</p>
      <p class="text-muted small">This action cannot be undone.</p>
    </BaseModal>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useNotifications } from '@/composables/useNotifications'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatsGrid from '@/components/ui/StatsGrid.vue'
import DataTable from '@/components/ui/DataTable.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import UserForm from '@/components/forms/UserForm.vue' // Would need to be created
import adminService from '@/services/adminService'
import { formatISTDate, isToday as isTodayIST } from '@/utils/timezone'

export default {
  name: 'UserManagementRefactored',
  components: {
    PageHeader,
    StatsGrid,
    DataTable,
    BaseModal,
    UserForm
  },
  setup() {
    const { success: showSuccess, error: showError } = useNotifications()
    
    // State
    const loading = ref(false)
    const error = ref('')
    const users = ref([])
    const selectedUser = ref(null)
    const userToDelete = ref(null)
    const showUserModal = ref(false)
    const showDeleteModal = ref(false)
    const isViewMode = ref(false)
    const dashboardStats = ref(null)
    
    // Filter state
    const currentFilters = ref({
      search: '',
      role: '',
      status: '',
      page: 1,
      perPage: 20
    })
    
    // Form state
    const userForm = ref({
      full_name: '',
      email: '',
      password: '',
      is_admin: false,
      is_active: true
    })
    const userFormErrors = ref({})

    // Table configuration
    const userColumns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'full_name', label: 'Name', sortable: true },
      { key: 'email', label: 'Email', sortable: true },
      { key: 'role', label: 'Role' },
      { key: 'status', label: 'Status' },
      { key: 'last_login', label: 'Last Login', sortable: true },
      { key: 'created_at', label: 'Created', sortable: true }
    ]

    const userFilters = [
      {
        key: 'role',
        label: 'Role',
        type: 'select',
        placeholder: 'All Roles',
        options: [
          { value: 'admin', label: 'Admin' },
          { value: 'user', label: 'User' }
        ]
      },
      {
        key: 'status',
        label: 'Status',
        type: 'select',
        placeholder: 'All Status',
        options: [
          { value: 'active', label: 'Active' },
          { value: 'inactive', label: 'Inactive' }
        ]
      },
      {
        key: 'search',
        label: 'Search',
        type: 'text',
        placeholder: 'Search users...'
      }
    ]

    // Stats - Use dashboard stats when available, fallback to calculated stats
    const userStats = computed(() => {
      // If we have dashboard stats, use those
      if (dashboardStats.value) {
        const stats = dashboardStats.value
        console.log('UserManagement: Using dashboard stats for cards:', {
          total_users: stats.total_users,
          active_users_all: stats.active_users_all,
          total_admins: stats.total_admins,
          new_users_today: stats.new_users_today
        })
        return [
          {
            key: 'total',
            title: 'Total Users',
            value: stats.total_users || 0,
            icon: 'bi bi-people',
            variant: 'primary'
          },
          {
            key: 'active',
            title: 'Active Users',
            value: stats.active_users_all || 0,
            icon: 'bi bi-person-check',
            variant: 'success'
          },
          {
            key: 'admins',
            title: 'Administrators',
            value: stats.total_admins || 0,
            icon: 'bi bi-shield-check',
            variant: 'warning'
          },
          {
            key: 'new_today',
            title: 'New Today',
            value: stats.new_users_today || 0,
            icon: 'bi bi-person-plus',
            variant: 'info'
          }
        ]
      }
      
      // Fallback to calculating from local user array (for offline scenarios)
      console.log('UserManagement: Using fallback calculated stats from users array, length:', users.value.length)
      return [
        {
          key: 'total',
          title: 'Total Users',
          value: users.value.length,
          icon: 'bi bi-people',
          variant: 'primary'
        },
        {
          key: 'active',
          title: 'Active Users',
          value: users.value.filter(u => u.is_active).length,
          icon: 'bi bi-person-check',
          variant: 'success'
        },
        {
          key: 'admins',
          title: 'Administrators',
          value: users.value.filter(u => u.is_admin).length,
          icon: 'bi bi-shield-check',
          variant: 'warning'
        },
        {
          key: 'new_today',
          title: 'New Today',
          value: users.value.filter(u => isToday(u.created_at)).length,
          icon: 'bi bi-person-plus',
          variant: 'info'
        }
      ]
    })

    // Computed
    const isUserFormValid = computed(() => {
      return userForm.value.full_name && 
             userForm.value.email && 
             (selectedUser.value || userForm.value.password)
    })

    // Methods
    const loadDashboardStats = async () => {
      try {
        console.log('UserManagement: Loading dashboard stats...')
        const data = await adminService.getDashboard()
        console.log('UserManagement: Raw dashboard data:', data)
        dashboardStats.value = data
        console.log('UserManagement: Dashboard stats loaded:', dashboardStats.value)
      } catch (err) {
        console.error('UserManagement: Failed to load dashboard stats:', err)
        // Don't show error for stats as users list is more important
        // Falls back to calculated stats from user array
      }
    }

    const loadUsers = async (filters = null) => {
      try {
        loading.value = true
        error.value = ''
        
        // Use provided filters or current filters
        const activeFilters = filters || currentFilters.value
        
        console.log('🔍 Loading users with filters:', activeFilters)
        
        const response = await adminService.getUsers(
          activeFilters.page || 1,
          activeFilters.perPage || 20,
          activeFilters.search || '',
          'all', // legacy filter parameter
          activeFilters.role || '',
          activeFilters.status || ''
        )
        
        console.log('📥 User response:', response)
        
        if (response?.users) {
          // Filter out any undefined or null users
          const validUsers = response.users.filter(user => user && user.id)
          console.log('✅ Valid users loaded:', validUsers.length)
          users.value = validUsers
        } else if (Array.isArray(response)) {
          // Handle case where response is directly the array of users
          const validUsers = response.filter(user => user && user.id)
          console.log('✅ Valid users loaded (array):', validUsers.length)
          users.value = validUsers
        } else {
          console.error('❌ Invalid response format:', response)
          error.value = 'Invalid response format from server'
          users.value = []
        }
        
      } catch (err) {
        console.error('❌ Failed to load users:', err)
        error.value = err.message || 'Failed to load users'
        showError(error.value)
        users.value = []
      } finally {
        loading.value = false
      }
    }

    const refreshUsers = () => {
      loadUsers()
      loadDashboardStats()
    }

    const handleStatClick = (stat) => {
      // Filter users based on stat clicked
      console.log('Stat clicked:', stat)
    }

    const handleFilterChange = (filters) => {
      // Update current filters
      currentFilters.value = {
        ...currentFilters.value,
        ...filters,
        page: 1 // Reset to first page when filters change
      }
      
      // Reload users with new filters
      loadUsers(currentFilters.value)
    }

    const editUser = (user) => {
      console.log('editUser called with:', user)
      selectedUser.value = user
      userForm.value = { ...user }
      isViewMode.value = false
      showUserModal.value = true
    }

    const viewUser = (user) => {
      console.log('viewUser called with:', user)
      
      // Set the user data for viewing (read-only mode)
      selectedUser.value = user
      userForm.value = { ...user }
      isViewMode.value = true
      showUserModal.value = true
    }

    const deleteUser = (user) => {
      console.log('deleteUser called with:', user)
      userToDelete.value = user
      showDeleteModal.value = true
    }

    const confirmDeleteUser = async () => {
      try {
        await adminService.deleteUser(userToDelete.value.id)
        users.value = users.value.filter(u => u.id !== userToDelete.value.id)
        showSuccess('User deleted successfully')
        showDeleteModal.value = false
        userToDelete.value = null
      } catch (err) {
        showError('Failed to delete user')
      }
    }

    const toggleUserRole = async (user) => {
      try {
        const response = await adminService.updateUser(user.id, {
          is_admin: !user.is_admin
        })
        console.log('toggleUserRole response:', response)
        
        // Reload users to ensure data consistency
        await loadUsers()
        showSuccess(`User role updated successfully`)
      } catch (err) {
        console.error('toggleUserRole error:', err)
        showError('Failed to update user role')
      }
    }

    const toggleUserStatus = async (user) => {
      try {
        const response = await adminService.updateUser(user.id, {
          is_active: !user.is_active
        })
        console.log('toggleUserStatus response:', response)
        
        // Reload users to ensure data consistency
        await loadUsers()
        showSuccess(`User status updated successfully`)
      } catch (err) {
        console.error('toggleUserStatus error:', err)
        showError('Failed to update user status')
      }
    }

    const saveUser = async () => {
      try {
        userFormErrors.value = {}
        
        if (selectedUser.value) {
          // Update existing user
          const response = await adminService.updateUser(selectedUser.value.id, userForm.value)
          console.log('saveUser update response:', response)
          showSuccess('User updated successfully')
        } else {
          // Create new user
          const response = await adminService.createUser(userForm.value)
          console.log('saveUser create response:', response)
          showSuccess('User created successfully')
        }
        
        // Reload users to ensure data consistency
        await loadUsers()
        closeUserModal()
      } catch (err) {
        console.error('saveUser error:', err)
        if (err.response?.data?.errors) {
          userFormErrors.value = err.response.data.errors
        }
        showError('Failed to save user')
      }
    }

    const closeUserModal = () => {
      showUserModal.value = false
      selectedUser.value = null
      isViewMode.value = false
      userForm.value = {
        full_name: '',
        email: '',
        password: '',
        is_admin: false,
        is_active: true
      }
      userFormErrors.value = {}
    }

    // Utility functions
    const getUserInitials = (name) => {
      if (!name) return '?'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return formatISTDate(dateString)
    }

    const isToday = (dateString) => {
      if (!dateString) return false
      return isTodayIST(dateString)
    }

    // Initialize
    onMounted(() => {
      console.log('UserManagement: Component mounted, loading users...')
      loadUsers()
      loadDashboardStats()
    })

    // Watch users array for changes
    watch(users, (newUsers) => {
      console.log('UserManagement: Users array changed:', newUsers)
      console.log('UserManagement: Users array length:', newUsers?.length || 0)
    }, { immediate: true, deep: true })

    // Debug computed for DataTable data
    const debugUsers = computed(() => {
      console.log('UserManagement: debugUsers computed called, users.value:', users.value)
      return users.value
    })

    return {
      // State
      loading,
      error,
      users,
      debugUsers,
      selectedUser,
      userToDelete,
      showUserModal,
      showDeleteModal,
      isViewMode,
      userForm,
      userFormErrors,
      dashboardStats,
      currentFilters,
      
      // Configuration
      userColumns,
      userFilters,
      userStats,
      
      // Computed
      isUserFormValid,
      
      // Methods
      loadUsers,
      refreshUsers,
      handleStatClick,
      handleFilterChange,
      editUser,
      viewUser,
      deleteUser,
      confirmDeleteUser,
      toggleUserRole,
      toggleUserStatus,
      saveUser,
      closeUserModal,
      getUserInitials,
      formatDate
    }
  }
}
</script>

<style scoped>
.user-management {
  padding: var(--spacing-4);
}

.avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: bold;
}

.form-check-input:checked {
  background-color: var(--color-success);
  border-color: var(--color-success);
}

@media (max-width: 768px) {
  .user-management {
    padding: var(--spacing-3);
  }
}
</style>
