<template>
  <div class="subject-management">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">Subject Management</h2>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="fas fa-plus me-2"></i>Add Subject
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Subjects Table -->
    <div v-else class="card">
      <div class="card-header">
        <h5 class="mb-0">All Subjects</h5>
      </div>
      <div class="card-body">
        <div v-if="subjects.length === 0" class="text-center text-muted py-4">
          <i class="fas fa-book fa-3x mb-3 opacity-50"></i>
          <p>No subjects found. Create your first subject to get started.</p>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Chapters</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="subject in subjects" :key="subject.id">
                <td class="fw-semibold">{{ subject.name }}</td>
                <td>{{ subject.description || 'No description' }}</td>
                <td>
                  <span class="badge bg-info">{{ subject.chapters_count }} chapters</span>
                </td>
                <td>
                  <span class="badge" :class="subject.is_active ? 'bg-success' : 'bg-secondary'">
                    {{ subject.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>{{ formatDate(subject.created_at) }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" @click="editSubject(subject)">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-info" @click="viewChapters(subject)">
                      <i class="fas fa-list"></i>
                    </button>
                    <button 
                      class="btn btn-outline-danger" 
                      @click="deleteSubject(subject)"
                      :disabled="subject.chapters_count > 0"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create/Edit Subject Modal -->
    <div class="modal fade" tabindex="-1" ref="subjectModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingSubject ? 'Edit Subject' : 'Create New Subject' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <form @submit.prevent="saveSubject">
            <div class="modal-body">
              <div class="mb-3">
                <label for="subjectName" class="form-label">Subject Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="subjectName"
                  v-model="subjectForm.name"
                  required
                  maxlength="100"
                >
              </div>
              <div class="mb-3">
                <label for="subjectDescription" class="form-label">Description</label>
                <textarea
                  class="form-control"
                  id="subjectDescription"
                  v-model="subjectForm.description"
                  rows="3"
                  maxlength="500"
                ></textarea>
              </div>
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="subjectActive"
                  v-model="subjectForm.is_active"
                >
                <label class="form-check-label" for="subjectActive">
                  Active
                </label>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                {{ editingSubject ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Error/Success Messages -->
    <div v-if="message" class="position-fixed bottom-0 end-0 p-3" style="z-index: 1050">
      <div class="alert" :class="messageType === 'error' ? 'alert-danger' : 'alert-success'" role="alert">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import apiService from '@/services/api'

export default {
  name: 'SubjectManagement',
  setup() {
    const loading = ref(true)
    const saving = ref(false)
    const subjects = ref([])
    const showCreateModal = ref(false)
    const editingSubject = ref(null)
    const message = ref('')
    const messageType = ref('')
    const subjectModal = ref(null)

    const subjectForm = ref({
      name: '',
      description: '',
      is_active: true
    })

    const loadSubjects = async () => {
      try {
        loading.value = true
        const response = await apiService.get('/admin/subjects')
        subjects.value = response.data
      } catch (error) {
        showMessage('Failed to load subjects', 'error')
        console.error('Load subjects error:', error)
      } finally {
        loading.value = false
      }
    }

    const editSubject = (subject) => {
      editingSubject.value = subject
      subjectForm.value = {
        name: subject.name,
        description: subject.description || '',
        is_active: subject.is_active
      }
      showCreateModal.value = true
    }

    const saveSubject = async () => {
      try {
        saving.value = true
        
        if (editingSubject.value) {
          // Update existing subject
          await apiService.put(`/admin/subjects/${editingSubject.value.id}`, subjectForm.value)
          showMessage('Subject updated successfully', 'success')
        } else {
          // Create new subject
          await apiService.post('/admin/subjects', subjectForm.value)
          showMessage('Subject created successfully', 'success')
        }
        
        closeModal()
        await loadSubjects()
      } catch (error) {
        showMessage('Failed to save subject', 'error')
        console.error('Save subject error:', error)
      } finally {
        saving.value = false
      }
    }

    const deleteSubject = async (subject) => {
      if (subject.chapters_count > 0) {
        showMessage('Cannot delete subject with existing chapters', 'error')
        return
      }

      if (confirm(`Are you sure you want to delete "${subject.name}"?`)) {
        try {
          await apiService.delete(`/admin/subjects/${subject.id}`)
          showMessage('Subject deleted successfully', 'success')
          await loadSubjects()
        } catch (error) {
          showMessage('Failed to delete subject', 'error')
          console.error('Delete subject error:', error)
        }
      }
    }

    const viewChapters = (subject) => {
      // Navigate to chapters management for this subject
      // This would be implemented with router navigation
      console.log('View chapters for:', subject.name)
    }

    const closeModal = () => {
      showCreateModal.value = false
      editingSubject.value = null
      subjectForm.value = {
        name: '',
        description: '',
        is_active: true
      }
    }

    const showMessage = (msg, type) => {
      message.value = msg
      messageType.value = type
      setTimeout(() => {
        message.value = ''
      }, 5000)
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    // Watch for modal visibility changes
    const watchModal = async () => {
      await nextTick()
      if (showCreateModal.value && subjectModal.value) {
        const modal = new bootstrap.Modal(subjectModal.value)
        modal.show()
      }
    }

    onMounted(() => {
      loadSubjects()
    })

    return {
      loading,
      saving,
      subjects,
      showCreateModal,
      editingSubject,
      message,
      messageType,
      subjectForm,
      subjectModal,
      loadSubjects,
      editSubject,
      saveSubject,
      deleteSubject,
      viewChapters,
      closeModal,
      formatDate,
      watchModal
    }
  }
}
</script>

<style scoped>
.subject-management {
  padding: 1rem;
}

.opacity-50 {
  opacity: 0.5;
}
</style>
