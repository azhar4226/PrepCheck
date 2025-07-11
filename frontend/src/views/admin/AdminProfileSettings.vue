<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <!-- Header -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i class="bi bi-shield-check me-2"></i>Admin Profile Settings
          </h2>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-secondary" @click="refreshProfile">
              <i class="bi bi-arrow-clockwise me-1"></i>Refresh
            </button>
            <router-link to="/admin/users" class="btn btn-outline-primary">
              <i class="bi bi-people me-1"></i>Manage Users
            </router-link>
            <router-link to="/admin/subjects" class="btn btn-outline-primary">
              <i class="bi bi-book me-1"></i>Manage Subjects
            </router-link>
          </div>
        </div>

        <!-- Admin Status Banner -->
        <div class="alert alert-info mb-4">
          <i class="bi bi-info-circle me-2"></i>
          <strong>Administrator Account:</strong> You have full system access and can manage all users, content, and settings.
        </div>

        <!-- Profile Picture Section -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-camera me-2"></i>Profile Picture</h5>
          </div>
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-3 text-center">
                <div class="profile-picture-container">
                  <img 
                    :src="profilePictureUrl" 
                    :alt="profile.full_name"
                    class="profile-picture"
                    @error="handleImageError"
                  >
                  <div class="profile-picture-overlay" @click="triggerFileInput">
                    <i class="bi bi-camera-fill"></i>
                  </div>
                </div>
                <input 
                  ref="fileInput" 
                  type="file" 
                  accept="image/*" 
                  @change="handleFileSelect" 
                  style="display: none"
                >
              </div>
              <div class="col-md-9">
                <h6>Change Profile Picture</h6>
                <p class="text-muted mb-3">Upload a new profile picture. Supported formats: PNG, JPG, JPEG, GIF, WebP. Maximum size: 5MB.</p>
                <div class="btn-group">
                  <button class="btn btn-primary" @click="triggerFileInput" :disabled="uploading">
                    <i class="bi bi-upload me-1"></i>
                    {{ uploading ? 'Uploading...' : 'Upload New Picture' }}
                  </button>
                  <button 
                    class="btn btn-outline-danger" 
                    @click="deleteProfilePicture" 
                    :disabled="!profile.profile_picture_url || uploading"
                  >
                    <i class="bi bi-trash me-1"></i>
                    {{ uploading ? 'Removing...' : 'Remove' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Admin Profile Information -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-person me-2"></i>Admin Information</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="fullName" class="form-label">Full Name</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="fullName" 
                    v-model="profile.full_name" 
                    required 
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email" 
                    v-model="profile.email" 
                    required 
                  >
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="phone" class="form-label">Contact Number</label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    id="phone" 
                    v-model="profile.phone"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="role" class="form-label">Role</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="role" 
                    value="Administrator"
                    disabled
                  >
                </div>
              </div>

              <div class="mb-3">
                <label for="bio" class="form-label">Admin Bio</label>
                <textarea 
                  class="form-control" 
                  id="bio" 
                  rows="3" 
                  v-model="profile.bio"
                  placeholder="Describe your role and responsibilities..."
                ></textarea>
              </div>

              <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary" :disabled="updating">
                  <i class="bi bi-check-circle me-1"></i>
                  {{ updating ? 'Updating...' : 'Update Profile' }}
                </button>
                <button type="button" class="btn btn-outline-secondary" @click="resetForm">
                  <i class="bi bi-arrow-counterclockwise me-1"></i>Reset
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Security Settings -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-shield-lock me-2"></i>Security Settings</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="changePassword">
              <div class="row">
                <div class="col-md-4 mb-3">
                  <label for="currentPassword" class="form-label">Current Password</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="currentPassword" 
                    v-model="passwordForm.currentPassword" 
                    required
                  >
                </div>
                <div class="col-md-4 mb-3">
                  <label for="newPassword" class="form-label">New Password</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="newPassword" 
                    v-model="passwordForm.newPassword" 
                    required
                    minlength="6"
                  >
                </div>
                <div class="col-md-4 mb-3">
                  <label for="confirmPassword" class="form-label">Confirm New Password</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="confirmPassword" 
                    v-model="passwordForm.confirmPassword" 
                    required
                    minlength="6"
                  >
                </div>
              </div>
              <button type="submit" class="btn btn-warning" :disabled="changingPassword">
                <i class="bi bi-key me-1"></i>
                {{ changingPassword ? 'Changing...' : 'Change Password' }}
              </button>
            </form>
          </div>
        </div>

        <!-- Admin Quick Actions -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-lightning-charge me-2"></i>Quick Actions</h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6">
                <router-link to="/admin/users" class="btn btn-outline-primary d-block">
                  <i class="bi bi-people me-2"></i>User Management
                </router-link>
              </div>
              <div class="col-md-6">
                <router-link to="/admin/subjects" class="btn btn-outline-primary d-block">
                  <i class="bi bi-book me-2"></i>Subject Management
                </router-link>
              </div>
              <div class="col-md-6">
                <router-link to="/admin/questions" class="btn btn-outline-primary d-block">
                  <i class="bi bi-question-circle me-2"></i>Question Bank
                </router-link>
              </div>
              <div class="col-md-6">
                <router-link to="/admin/reports" class="btn btn-outline-primary d-block">
                  <i class="bi bi-graph-up me-2"></i>Analytics & Reports
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Notification Modal -->
    <NotificationModal
      :show="modal.show"
      :type="modal.type"
      :title="modal.title"
      :message="modal.message"
      :details="modal.details"
      :confirm-text="modal.confirmText"
      :cancel-text="modal.cancelText"
      @close="modal.show = false"
      @confirm="handleModalConfirm"
      @cancel="handleModalCancel"
    />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth.js'
import adminService from '@/services/adminService'
import NotificationModal from '@/components/ui/NotificationModal.vue'

export default {
  name: 'AdminProfileSettings',
  components: {
    NotificationModal
  },
  setup() {
    const { user } = useAuth()
    
    // Profile data
    const profile = reactive({
      full_name: '',
      email: '',
      phone: '',
      bio: '',
      theme_preference: 'light',
      profile_picture_url: ''
    })

    // Password form
    const passwordForm = reactive({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

    // Loading states
    const loading = ref(false)
    const updating = ref(false)
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const changingPassword = ref(false)

    // File input ref
    const fileInput = ref(null)
    
    // Cache busting timestamp for profile picture
    const profilePictureTimestamp = ref(Date.now())

    // Modal state
    const modal = reactive({
      show: false,
      type: 'success',
      title: '',
      message: '',
      details: '',
      confirmText: 'OK',
      cancelText: 'Cancel',
      onConfirm: null,
      onCancel: null
    })

    // Profile picture URL computed property
    const profilePictureUrl = computed(() => {
      if (profile.profile_picture_url) {
        if (profile.profile_picture_url.startsWith('http')) {
          return `${profile.profile_picture_url}?t=${profilePictureTimestamp.value}`
        }
        return `${profile.profile_picture_url}?t=${profilePictureTimestamp.value}`
      }
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.full_name || 'Admin')}&background=dc3545&color=fff&size=120`
    })

    // Methods
    const loadProfile = async () => {
      try {
        loading.value = true
        const response = await adminService.getProfile()
        if (response.user) {
          Object.assign(profile, response.user)
        } else {
          Object.assign(profile, response)
        }
      } catch (error) {
        console.error('Error loading profile:', error)
        showError('Failed to load profile', error.response?.data?.error || error.message)
      } finally {
        loading.value = false
      }
    }

    const refreshProfile = async () => {
      try {
        await loadProfile()
        showSuccess('Profile refreshed successfully!')
      } catch (error) {
        console.error('Error refreshing profile:', error)
        showError('Failed to refresh profile', error.response?.data?.error || error.message)
      }
    }

    const updateProfile = async () => {
      try {
        updating.value = true
        const response = await userService.updateAdminProfile(profile)
        if (response.user) {
          Object.assign(profile, response.user)
        }
        showSuccess('Profile updated successfully!')
      } catch (error) {
        console.error('Error updating profile:', error)
        showError('Failed to update profile', error.response?.data?.error || error.message)
      } finally {
        updating.value = false
      }
    }

    const resetForm = () => {
      loadProfile()
    }

    const changePassword = async () => {
      if (passwordForm.newPassword !== passwordForm.confirmPassword) {
        showError('Password mismatch', 'New passwords do not match. Please try again.')
        return
      }

      try {
        changingPassword.value = true
        await userService.changeAdminPassword({
          current_password: passwordForm.currentPassword,
          new_password: passwordForm.newPassword
        })
        
        Object.assign(passwordForm, {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        })
        
        showSuccess('Password changed successfully!')
      } catch (error) {
        console.error('Error changing password:', error)
        showError('Failed to change password', error.response?.data?.error || error.message)
      } finally {
        changingPassword.value = false
      }
    }

    // Profile picture methods
    const triggerFileInput = () => {
      fileInput.value?.click()
    }

    const handleFileSelect = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      if (file.size > 5 * 1024 * 1024) {
        showError('File too large', 'File size must be less than 5MB')
        return
      }

      const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        showError('Invalid file type', 'Please select a PNG, JPG, JPEG, GIF, or WebP image')
        return
      }

      try {
        uploading.value = true
        uploadProgress.value = 0

        const formData = new FormData()
        formData.append('file', file)

        const response = await userService.uploadAdminProfilePicture(formData)
        
        if (response.user) {
          Object.assign(profile, response.user)
        } else if (response.profile_picture_url) {
          profile.profile_picture_url = response.profile_picture_url
        }
        
        profilePictureTimestamp.value = Date.now()
        
        if (fileInput.value) {
          fileInput.value.value = ''
        }
        
        showSuccess('Profile picture uploaded successfully!')
      } catch (error) {
        console.error('Error uploading profile picture:', error)
        showError('Failed to upload profile picture', error.response?.data?.error || error.message)
      } finally {
        uploading.value = false
        uploadProgress.value = 0
      }
    }

    const deleteProfilePicture = async () => {
      try {
        uploading.value = true
        await userService.deleteAdminProfilePicture()
        profile.profile_picture_url = null
        profilePictureTimestamp.value = Date.now()
        showSuccess('Profile picture removed successfully!')
      } catch (error) {
        console.error('Error deleting profile picture:', error)
        showError('Failed to remove profile picture', error.response?.data?.error || error.message)
      } finally {
        uploading.value = false
      }
    }

    const handleImageError = (event) => {
      event.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.full_name || 'Admin')}&background=dc3545&color=fff&size=120`
    }

    // Modal methods
    const showSuccess = (message, details = '') => {
      modal.type = 'success'
      modal.title = '✅ Success'
      modal.message = message
      modal.details = details
      modal.show = true
    }

    const showError = (message, details = '') => {
      modal.type = 'error'
      modal.title = '❌ Error'
      modal.message = message
      modal.details = details
      modal.show = true
    }

    const handleModalConfirm = () => {
      if (modal.onConfirm) modal.onConfirm()
      modal.show = false
    }

    const handleModalCancel = () => {
      if (modal.onCancel) modal.onCancel()
      modal.show = false
    }

    // Initialize
    onMounted(() => {
      loadProfile()
    })

    return {
      profile,
      passwordForm,
      loading,
      updating,
      uploading,
      uploadProgress,
      changingPassword,
      fileInput,
      profilePictureUrl,
      modal,
      refreshProfile,
      updateProfile,
      resetForm,
      changePassword,
      triggerFileInput,
      handleFileSelect,
      deleteProfilePicture,
      handleImageError,
      handleModalConfirm,
      handleModalCancel
    }
  }
}
</script>

<style scoped>
.profile-picture-container {
  position: relative;
  display: inline-block;
  margin-bottom: 1rem;
}

.profile-picture {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #dc3545;
}

.profile-picture-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(220, 53, 69, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  cursor: pointer;
  color: white;
  font-size: 1.5rem;
}

.profile-picture-container:hover .profile-picture-overlay {
  opacity: 1;
}

.btn-outline-primary {
  border-color: #dc3545;
  color: #dc3545;
}

.btn-outline-primary:hover {
  background-color: #dc3545;
  color: white;
}

.quick-actions .btn {
  text-align: left;
  padding: 1rem;
  font-size: 1.1rem;
}

.quick-actions .btn i {
  font-size: 1.2rem;
}
</style>
