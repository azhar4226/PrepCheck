<template>
  <SharedProfileSettings 
    :is-admin="true"
    header-title="Admin Profile Settings"
    header-icon="bi bi-shield-check"
    api-endpoint="/api/admin/profile"
  >
    <template #header-actions>
      <router-link to="/admin/users" class="btn btn-outline-primary">
        <i class="bi bi-people me-1"></i>Manage Users
      </router-link>
    </template>
    
    <template #additional-content>
      <!-- Admin-specific content -->
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0"><i class="bi bi-info-circle-fill me-2"></i>Account Information</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <p><strong>Account Type:</strong> 
                <span class="badge bg-danger">Administrator</span>
              </p>
              <p><strong>Status:</strong> 
                <span class="text-success">Active</span>
              </p>
              <p><strong>Email Verified:</strong> 
                <span class="text-success">Yes</span>
              </p>
            </div>
            <div class="col-md-6">
              <p><strong>Admin Since:</strong> Account Creation</p>
              <p><strong>Last Updated:</strong> Recently</p>
              <p><strong>Last Login:</strong> Current Session</p>
            </div>
          </div>
          
          <!-- Quick Actions -->
          <hr>
          <h6>Quick Actions</h6>
          <div class="btn-group" role="group">
            <router-link to="/admin/dashboard" class="btn btn-outline-primary btn-sm">
              <i class="bi bi-speedometer2 me-1"></i>Dashboard
            </router-link>
            <router-link to="/admin/users" class="btn btn-outline-primary btn-sm">
              <i class="bi bi-people me-1"></i>Users
            </router-link>
            <router-link to="/admin/subjects" class="btn btn-outline-primary btn-sm">
              <i class="bi bi-book me-1"></i>Subjects
            </router-link>
            <router-link to="/admin/ai-question-generator" class="btn btn-outline-primary btn-sm">
              <i class="bi bi-clipboard-check me-1"></i>Question Generator
            </router-link>
          </div>
        </div>
      </div>
    </template>
  </SharedProfileSettings>
</template>

<script>
import SharedProfileSettings from '@/components/features/SharedProfileSettings.vue'

export default {
  name: 'AdminProfileSettings',
  components: {
    SharedProfileSettings
  }
}
</script>

<style scoped>
.badge {
  font-size: 0.75rem;
}
</style>
