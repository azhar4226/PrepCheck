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
                  <select class="form-select" id="gender" v-model="profile.gender">
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
                  >
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="timezone" class="form-label">Timezone</label>
                  <select class="form-select" id="timezone" v-model="profile.timezone">
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Denver">Mountain Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                    <option value="Europe/London">London</option>
                    <option value="Europe/Paris">Paris</option>
                    <option value="Asia/Tokyo">Tokyo</option>
                    <option value="Asia/Shanghai">Shanghai</option>
                    <option value="Australia/Sydney">Sydney</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="theme" class="form-label">Theme Preference</label>
                  <select class="form-select" id="theme" v-model="profile.theme_preference">
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="auto">Auto</option>
                  </select>
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
                  <h6 class="mb-3">Notification Preferences</h6>
                  <div class="form-check form-switch mb-2">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      id="emailNotifications" 
                      v-model="profile.notification_email"
                    >
                    <label class="form-check-label" for="emailNotifications">
                      Email Notifications
                    </label>
                  </div>
                  <div class="form-check form-switch">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      id="quizReminders" 
                      v-model="profile.notification_quiz_reminders"
                    >
                    <label class="form-check-label" for="quizReminders">
                      Quiz Reminders
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
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth.js'
import userService from '@/services/userService'
import apiClient from '@/services/apiClient'

export default {
  name: 'SharedProfileSettings',
  props: {
    isAdmin: {
      type: Boolean,
      default: false
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
      timezone: 'UTC',
      notification_email: true,
      notification_quiz_reminders: true,
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

    // Computed properties
    const profilePictureUrl = computed(() => {
      if (profile.profile_picture_url) {
        // If it's already a full URL, return as is
        if (profile.profile_picture_url.startsWith('http')) {
          return profile.profile_picture_url
        }
        // Otherwise, construct the full URL using the API base URL
        return `${apiClient.baseURL || ''}${profile.profile_picture_url}`
      }
      // Return default avatar using UI Avatars service
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.full_name || 'User')}&background=3498db&color=fff&size=120`
    })

    // Methods
    const loadProfile = async () => {
      try {
        loading.value = true
        const response = await userService.getProfile()
        Object.assign(profile, response.user)
      } catch (error) {
        console.error('Error loading profile:', error)
      } finally {
        loading.value = false
      }
    }

    const refreshProfile = () => {
      loadProfile()
    }

    const updateProfile = async () => {
      try {
        updating.value = true
        const response = await userService.updateProfile(profile)
        Object.assign(profile, response.user)
        // Show success message
      } catch (error) {
        console.error('Error updating profile:', error)
        // Show error message
      } finally {
        updating.value = false
      }
    }

    const resetForm = () => {
      loadProfile()
    }

    const changePassword = async () => {
      if (passwordForm.newPassword !== passwordForm.confirmPassword) {
        alert('New passwords do not match')
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
        
        // Show success message
      } catch (error) {
        console.error('Error changing password:', error)
        // Show error message
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
        alert('File size must be less than 5MB')
        return
      }

      // Validate file type
      const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        alert('Invalid file type. Please select a PNG, JPG, JPEG, GIF, or WebP image.')
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

        profile.profile_picture_url = response.profile_picture_url
        
        // Reset file input
        if (fileInput.value) {
          fileInput.value.value = ''
        }
        
        // Show success message
        alert('Profile picture uploaded successfully!')
        
      } catch (error) {
        console.error('Error uploading profile picture:', error)
        alert('Failed to upload profile picture: ' + (error.response?.data?.error || error.message))
      } finally {
        uploading.value = false
        uploadProgress.value = 0
      }
    }

    const deleteProfilePicture = async () => {
      if (!confirm('Are you sure you want to remove your profile picture?')) {
        return
      }

      try {
        uploading.value = true
        await userService.deleteProfilePicture()
        profile.profile_picture_url = null
        alert('Profile picture removed successfully!')
      } catch (error) {
        console.error('Error deleting profile picture:', error)
        alert('Failed to remove profile picture: ' + (error.response?.data?.error || error.message))
      } finally {
        uploading.value = false
      }
    }

    const handleImageError = (event) => {
      // Set a default avatar URL when image fails to load
      event.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.full_name || 'User')}&background=6c757d&color=fff&size=120`
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
      loadProfile,
      refreshProfile,
      updateProfile,
      resetForm,
      changePassword,
      triggerFileInput,
      handleFileSelect,
      deleteProfilePicture,
      handleImageError
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
