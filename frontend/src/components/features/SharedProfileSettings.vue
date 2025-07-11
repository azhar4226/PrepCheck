<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <!-- Header -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i :class="headerIcon" class="me-2"></i>{{ headerTitle }}
          </h2>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-secondary" @click="refreshProfile">
              <i class="bi bi-arrow-clockwise me-1"></i>Refresh
            </button>
            <slot name="header-actions"></slot>
          </div>
        </div>

        <!-- Admin Status Banner (only for admin) -->
        <div v-if="isAdmin" class="alert alert-info mb-4">
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
                <div v-if="uploading" class="progress mt-3">
                  <div class="progress-bar" role="progressbar" :style="{ width: uploadProgress + '%' }">
                    {{ uploadProgress }}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Profile Information -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-person me-2"></i>Profile Information</h5>
            <!-- Debug info - remove after testing -->

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
                  <label for="phone" class="form-label">Phone Number</label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    id="phone" 
                    v-model="profile.phone"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="dateOfBirth" class="form-label">Date of Birth</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    id="dateOfBirth" 
                    v-model="profile.date_of_birth"
                  >
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="gender" class="form-label">Gender</label>
                  <select class="form-select" id="gender" v-model="profile.gender" :disabled="isAdmin">
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                    <option value="prefer_not_to_say">Prefer not to say</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="country" class="form-label">Country</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="country" 
                    v-model="profile.country"
                    :disabled="isAdmin"
                  >
                </div>
              </div>

              <!-- Admin-only section -->
              <div v-if="isAdmin" class="row mb-4">
                <div class="col-12">
                  <div class="card bg-light">
                    <div class="card-body">
                      <h6 class="card-title"><i class="bi bi-shield-lock me-2"></i>Administrative Controls</h6>
                      <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        As an administrator, some personal profile fields are restricted. Use the User Management section to make administrative changes.
                      </div>
                      <div class="d-grid gap-2">
                        <router-link to="/admin/users" class="btn btn-primary">
                          <i class="bi bi-people me-2"></i>Manage Users
                        </router-link>
                        <router-link to="/admin/subjects" class="btn btn-secondary">
                          <i class="bi bi-book me-2"></i>Manage Subjects
                        </router-link>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Subject preference (non-admin only) -->
              <div v-if="!isAdmin" class="row mb-3">
                <div class="col-md-6 mb-3">
                  <label for="subject" class="form-label">Subject Preference</label>
                  <select class="form-select" id="subject" v-model="profile.subject_id">
                    <option value="">Select Subject</option>
                    <option v-for="subject in availableSubjects" 
                            :key="subject.id" 
                            :value="subject.id">
                      {{ subject.name }}
                    </option>
                  </select>
                  <div class="form-text text-muted">
                    <i class="bi bi-info-circle me-1"></i>Select your preferred subject for Paper 2.
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="bio" class="form-label">Bio</label>
                <textarea 
                  class="form-control" 
                  id="bio" 
                  rows="3" 
                  v-model="profile.bio"
                  placeholder="Tell us about yourself..."
                ></textarea>
              </div>

              <div class="row mb-3">
                <div class="col-12">
                  <h6 class="mb-3">
                    Notification Preferences
                    <span v-if="isAdmin" class="badge bg-secondary ms-2">Read Only</span>
                  </h6>
                  <div class="form-check form-switch mb-2">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      id="emailNotifications" 
                      v-model="profile.notification_email"
                      :disabled="isAdmin"
                    >
                    <label class="form-check-label" for="emailNotifications">
                      Email Notifications
                    </label>
                  </div>
                  <div class="form-check form-switch">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      id="testReminders" 
                      v-model="profile.notification_test_reminders"
                      :disabled="isAdmin"
                    >
                    <label class="form-check-label" for="testReminders">
                      Test Reminders
                    </label>
                  </div>
                </div>
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

        <!-- Password Change Section -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-shield-lock me-2"></i>Change Password</h5>
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

        <!-- Additional slot for custom content -->
        <slot name="additional-content"></slot>
      </div>
    </div>
    
    <!-- Custom Notification Modal -->
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
import userService from '@/services/userService'
import ugcNetService from '@/services/ugcNetService'
import apiClient from '@/services/apiClient'
import NotificationModal from '@/components/ui/NotificationModal.vue'

export default {
  name: 'SharedProfileSettings',
  components: {
    NotificationModal
  },
  props: {
    isAdmin: {
      type: Boolean,
      required: true
    },
    headerTitle: {
      type: String,
      default: 'Profile Settings'
    },
    headerIcon: {
      type: String,
      default: 'bi bi-person-circle'
    },
    apiEndpoint: {
      type: String,
      default: '/api/user/profile'
    }
  },
  setup(props) {
    const { user } = useAuth()
    
    // Profile data
    const profile = reactive({
      full_name: '',
      email: '',
      phone: '',
      bio: '',
      date_of_birth: '',
      gender: '',
      country: '',
      subject_id: '',
      timezone: 'Asia/Kolkata',
      notification_email: true,
      notification_test_reminders: true,
      theme_preference: 'light',
      profile_picture_url: ''
    })

    // Available subjects for selection
    const availableSubjects = ref([])

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

    // Helper functions for modal
    const showModal = (type, title, message, details = '', options = {}) => {
      modal.type = type
      modal.title = title
      modal.message = message
      modal.details = details
      modal.confirmText = options.confirmText || 'OK'
      modal.cancelText = options.cancelText || 'Cancel'
      modal.onConfirm = options.onConfirm || null
      modal.onCancel = options.onCancel || null
      modal.show = true
    }

    const showSuccess = (message, details = '') => {
      showModal('success', '✅ Success', message, details)
    }

    const showError = (message, details = '') => {
      showModal('error', '❌ Error', message, details)
    }

    const showConfirm = (message, onConfirm, options = {}) => {
      showModal('confirm', options.title || '🤔 Confirm Action', message, options.details || '', {
        confirmText: options.confirmText || 'Yes',
        cancelText: options.cancelText || 'Cancel',
        onConfirm: onConfirm,
        onCancel: options.onCancel || null
      })
    }

    const handleModalConfirm = () => {
      if (modal.onConfirm) {
        modal.onConfirm()
      }
    }

    const handleModalCancel = () => {
      if (modal.onCancel) {
        modal.onCancel()
      }
    }

    // Computed properties
    const profilePictureUrl = computed(() => {
      if (profile.profile_picture_url) {
        // If it's already a full URL, return as is
        if (profile.profile_picture_url.startsWith('http')) {
          return `${profile.profile_picture_url}?t=${profilePictureTimestamp.value}`
        }
        // For development, the uploads need to go through the proxy
        // For production, they should work with relative paths
        // Since we're using Vite proxy, just use the profile_picture_url directly
        return `${profile.profile_picture_url}?t=${profilePictureTimestamp.value}`
      }
      // Return default avatar using UI Avatars service
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.full_name || 'User')}&background=3498db&color=fff&size=120`
    })

    // Helper function to update both local and global user state
    const updateUserState = (updatedUserData) => {
      // Update local profile state
      Object.assign(profile, updatedUserData)
      
      // Update global auth state
      if (user.value) {
        Object.assign(user.value, updatedUserData)
        // Update localStorage
        localStorage.setItem('prepcheck_user', JSON.stringify(user.value))
      }
    }

    // Methods
    const loadProfile = async () => {
      try {
        loading.value = true
        const response = await userService.getProfile()
        
        // Update both local and global user state
        if (response.user) {
          updateUserState(response.user)
        } else {
          // Fallback: just update local profile if response doesn't have user object
          Object.assign(profile, response)
          // Still try to update global state
          if (user.value) {
            Object.assign(user.value, response)
            localStorage.setItem('prepcheck_user', JSON.stringify(user.value))
          }
        }
      } catch (error) {
        console.error('Error loading profile:', error)
        showError('Failed to load profile', error.response?.data?.error || error.message)
      } finally {
        loading.value = false
      }
    }

    const loadSubjects = async () => {
      try {
        // Only load subjects for non-admin users
        if (!props.isAdmin) {
          // Load only Paper 2 subjects (elective subjects) for profile selection
          const response = await userService.getPaper2Subjects()
          availableSubjects.value = response || []
        }
      } catch (error) {
        console.error('Error loading Paper 2 subjects:', error)
      }
    }

    const refreshProfile = async () => {
      try {
        // Reload both profile data and available subjects
        await Promise.all([
          loadProfile(),
          loadSubjects()
        ])
        showSuccess('Profile refreshed successfully!')
      } catch (error) {
        console.error('Error refreshing profile:', error)
        showError('Failed to refresh profile', error.response?.data?.error || error.message)
      }
    }

    const updateProfile = async () => {
      try {
        updating.value = true
        const response = await userService.updateProfile(profile)
        
        // Update both local and global user state
        if (response.user) {
          updateUserState(response.user)
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
        await userService.changePassword({
          current_password: passwordForm.currentPassword,
          new_password: passwordForm.newPassword
        })
        
        // Reset form
        Object.assign(passwordForm, {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        })
        
        showSuccess('Password changed successfully!', 'Your password has been updated.')
      } catch (error) {
        console.error('Error changing password:', error)
        showError('Failed to change password', error.response?.data?.error || error.message)
      } finally {
        changingPassword.value = false
      }
    }

    const triggerFileInput = () => {
      fileInput.value?.click()
    }

    const handleFileSelect = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      // Validate file
      if (file.size > 5 * 1024 * 1024) { // 5MB
        showError('File too large', 'File size must be less than 5MB. Please select a smaller image.')
        return
      }

      // Validate file type
      const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        showError('Invalid file type', 'Please select a PNG, JPG, JPEG, GIF, or WebP image.')
        return
      }

      try {
        uploading.value = true
        uploadProgress.value = 0

        const formData = new FormData()
        formData.append('file', file)

        // Simulate progress (you'd implement real progress tracking)
        const progressInterval = setInterval(() => {
          if (uploadProgress.value < 90) {
            uploadProgress.value += 10
          }
        }, 100)

        const response = await userService.uploadProfilePicture(formData)
        
        clearInterval(progressInterval)
        uploadProgress.value = 100

        // Update both local and global user state with the new profile picture
        if (response.user) {
          console.log('Upload response user data:', response.user)
          updateUserState(response.user)
        } else {
          console.log('Upload response profile_picture_url:', response.profile_picture_url)
          // Fallback to just updating the profile picture URL
          updateUserState({ profile_picture_url: response.profile_picture_url })
        }
        
        // Update cache-busting timestamp to force image reload
        profilePictureTimestamp.value = Date.now()
        console.log('Updated profile picture URL:', profilePictureUrl.value)
        
        // Force page reload for header to update
        window.location.reload()
        
        // Reset file input
        if (fileInput.value) {
          fileInput.value.value = ''
        }
        
        showSuccess('Profile picture uploaded successfully!', 'Your new profile picture is now visible across the application.')
        
      } catch (error) {
        console.error('Error uploading profile picture:', error)
        showError('Failed to upload profile picture', error.response?.data?.error || error.message)
      } finally {
        uploading.value = false
        uploadProgress.value = 0
      }
    }

    const deleteProfilePicture = async () => {
      showConfirm(
        'Are you sure you want to remove your profile picture?',
        async () => {
          try {
            uploading.value = true
            const response = await userService.deleteProfilePicture()
            
            // Update both local and global user state
            if (response.user) {
              updateUserState(response.user)
            } else {
              // Fallback to just updating the profile picture URL
              updateUserState({ profile_picture_url: null })
            }
            
            // Update cache-busting timestamp to force image reload
            profilePictureTimestamp.value = Date.now()
            
            // Force page reload for header to update
            window.location.reload()
            
            showSuccess('Profile picture removed successfully!', 'Your profile picture has been removed and the default avatar is now displayed.')
          } catch (error) {
            console.error('Error deleting profile picture:', error)
            showError('Failed to remove profile picture', error.response?.data?.error || error.message)
          } finally {
            uploading.value = false
          }
        },
        {
          title: '🗑️ Remove Profile Picture',
          confirmText: 'Yes, Remove',
          cancelText: 'Keep Picture'
        }
      )
    }

    const handleImageError = (event) => {
      console.log('Image error for URL:', event.target.src)
      console.log('Profile picture URL from profile:', profile.profile_picture_url)
      // Set a default avatar URL when image fails to load
      event.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.full_name || 'User')}&background=6c757d&color=fff&size=120`
    }

    // Initialize
    onMounted(() => {
      loadProfile()
      if (!props.isAdmin) {
        loadSubjects()
      }
    })

    return {
      profile,
      availableSubjects,
      passwordForm,
      loading,
      updating,
      uploading,
      uploadProgress,
      changingPassword,
      fileInput,
      profilePictureUrl,
      modal,
      loadProfile,
      refreshProfile,
      updateProfile,
      resetForm,
      changePassword,
      triggerFileInput,
      handleFileSelect,
      deleteProfilePicture,
      handleImageError,
      handleModalConfirm,
      handleModalCancel,
      isAdmin: computed(() => props.isAdmin) // Properly expose isAdmin as a computed prop
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
  border: 3px solid #dee2e6;
}

.profile-picture-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
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

.form-check-label {
  cursor: pointer;
}

.btn-group .btn {
  border-radius: 0.375rem;
  margin-right: 0.5rem;
}

.btn-group .btn:last-child {
  margin-right: 0;
}
</style>
