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
                  <div class="btn-group btn-group-sm" role="group" aria-label="Subject Actions">
                    <button class="btn btn-outline-primary d-flex align-items-center" @click="editSubject(subject)" title="Edit Subject">
                      <i class="fas fa-edit me-1"></i> Edit
                    </button>
                    <button class="btn btn-outline-info d-flex align-items-center" @click="manageChapters(subject)" title="Manage Chapters">
                      <i class="fas fa-layer-group me-1"></i> Chapters
                    </button>
                    <button 
                      class="btn btn-outline-danger d-flex align-items-center" 
                      @click="deleteSubject(subject)"
                      :disabled="subject.chapters_count > 0"
                      title="Delete Subject"
                    >
                      <i class="fas fa-trash me-1"></i> Delete
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
    <div 
      v-if="showCreateModal" 
      class="modal d-block" 
      tabindex="-1" 
      style="background-color: rgba(0,0,0,0.5);"
      @click="closeModal"
    >
      <div class="modal-dialog" @click.stop>
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
                <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status"></span>
                {{ editingSubject ? 'Update' : 'Create' }} Subject
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Chapters Management Modal -->
    <div 
      v-if="showChaptersModal" 
      class="modal d-block" 
      tabindex="-1" 
      style="background-color: rgba(0,0,0,0.5);"
      @click="closeChaptersModal"
    >
      <div class="modal-dialog modal-lg" @click.stop>
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              Manage Chapters - {{ selectedSubject?.name }}
            </h5>
            <button type="button" class="btn-close" @click="closeChaptersModal"></button>
          </div>
          <div class="modal-body">
            <!-- Add Chapter Button -->
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="mb-0">Chapters</h6>
              <button class="btn btn-primary btn-sm" @click="openCreateChapterModal">
                <i class="fas fa-plus me-1"></i>Add Chapter
              </button>
            </div>
            
            <!-- Loading State -->
            <div v-if="loadingChapters" class="text-center py-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading chapters...</span>
              </div>
            </div>
            
            <!-- Chapters List -->
            <div v-else-if="chapters.length === 0" class="text-center text-muted py-4">
              <i class="fas fa-folder-open fa-2x mb-3 opacity-50"></i>
              <p>No chapters found. Create the first chapter for this subject.</p>
            </div>
            
            <div v-else class="list-group">
              <div 
                v-for="chapter in chapters" 
                :key="chapter.id"
                class="list-group-item d-flex justify-content-between align-items-center"
              >
                <div>
                  <h6 class="mb-1">{{ chapter.name }}</h6>
                  <p class="mb-1 text-muted small">{{ chapter.description || 'No description' }}</p>
                  <small class="text-muted">
                    {{ chapter.questions_count || 0 }} questions | 
                    <span :class="chapter.is_active ? 'text-success' : 'text-danger'">
                      {{ chapter.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </small>
                </div>
                <div class="btn-group btn-group-sm" role="group" aria-label="Chapter Actions">
                  <button class="btn btn-outline-primary d-flex align-items-center" title="Edit Chapter" @click="editChapter(chapter)">
                    <i class="fas fa-edit me-1"></i> Edit
                  </button>
                  <button class="btn btn-outline-danger d-flex align-items-center" title="Delete Chapter" @click="deleteChapter(chapter)">
                    <i class="fas fa-trash me-1"></i> Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeChaptersModal">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Chapter Modal -->
    <div 
      v-if="showCreateChapterModal" 
      class="modal d-block" 
      tabindex="-1" 
      style="background-color: rgba(0,0,0,0.8);"
      @click="showCreateChapterModal = false"
    >
      <div class="modal-dialog" @click.stop>
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              Add New Chapter to {{ selectedSubject?.name }}
            </h5>
            <button type="button" class="btn-close" @click="showCreateChapterModal = false"></button>
          </div>
          <form @submit.prevent="saveChapter">
            <div class="modal-body">
              <div class="mb-3">
                <label for="chapterName" class="form-label">Chapter Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="chapterName"
                  v-model="chapterForm.name"
                  required
                  maxlength="100"
                >
              </div>
              <div class="mb-3">
                <label for="chapterDescription" class="form-label">Description</label>
                <textarea
                  class="form-control"
                  id="chapterDescription"
                  v-model="chapterForm.description"
                  rows="3"
                  maxlength="500"
                ></textarea>
              </div>
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="chapterActive"
                  v-model="chapterForm.is_active"
                >
                <label class="form-check-label" for="chapterActive">
                  Active
                </label>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showCreateChapterModal = false">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status"></span>
                Create Chapter
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
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import adminService from '@/services/adminService'

export default {
  name: 'SubjectManagement',
  setup() {
    const { api } = useAuth()
    const loading = ref(true)
    const saving = ref(false)
    const subjects = ref([])
    const showCreateModal = ref(false)
    const editingSubject = ref(null)
    const message = ref('')
    const messageType = ref('')
    
    // Chapter management state
    const showChaptersModal = ref(false)
    const selectedSubject = ref(null)
    const chapters = ref([])
    const loadingChapters = ref(false)
    const showCreateChapterModal = ref(false)
    const chapterForm = ref({
      name: '',
      description: '',
      subject_id: null,
      is_active: true
    })

    const subjectForm = ref({
      name: '',
      description: '',
      is_active: true
    })

    const loadSubjects = async () => {
      try {
        loading.value = true
        const response = await adminService.getSubjects()
        subjects.value = response
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
          await api.updateSubject(editingSubject.value.id, subjectForm.value)
          showMessage('Subject updated successfully', 'success')
        } else {
          // Create new subject
          await api.createSubject(subjectForm.value)
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
          await api.deleteSubject(subject.id)
          showMessage('Subject deleted successfully', 'success')
          await loadSubjects()
        } catch (error) {
          showMessage('Failed to delete subject', 'error')
          console.error('Delete subject error:', error)
        }
      }
    }

    const manageChapters = async (subject) => {
      selectedSubject.value = subject
      showChaptersModal.value = true
      await loadChapters(subject.id)
    }

    const loadChapters = async (subjectId) => {
      try {
        loadingChapters.value = true
        const response = await adminService.getChapters(subjectId)
        console.log('Chapters API response:', response)
        if (Array.isArray(response)) {
          chapters.value = response
        } else if (response && Array.isArray(response.chapters)) {
          chapters.value = response.chapters
        } else {
          chapters.value = []
          showMessage('No chapters found or unexpected response format', 'error')
        }
      } catch (error) {
        showMessage('Failed to load chapters', 'error')
        console.error('Load chapters error:', error)
        chapters.value = []
      } finally {
        loadingChapters.value = false
      }
    }

    const openCreateChapterModal = () => {
      chapterForm.value = {
        name: '',
        description: '',
        subject_id: selectedSubject.value.id,
        is_active: true
      }
      showCreateChapterModal.value = true
    }

    const saveChapter = async () => {
      try {
        saving.value = true
        await adminService.createChapter(chapterForm.value)
        showMessage('Chapter created successfully', 'success')
        showCreateChapterModal.value = false
        await loadChapters(selectedSubject.value.id)
        await loadSubjects() // Refresh subject list to update chapter counts
      } catch (error) {
        showMessage('Failed to create chapter', 'error')
        console.error('Save chapter error:', error)
      } finally {
        saving.value = false
      }
    }

    const editChapter = (chapter) => {
      chapterForm.value = {
        name: chapter.name,
        description: chapter.description || '',
        subject_id: chapter.subject_id,
        is_active: chapter.is_active,
        id: chapter.id
      }
      showCreateChapterModal.value = true
    }

    const deleteChapter = async (chapter) => {
      if (confirm(`Are you sure you want to delete chapter "${chapter.name}"?`)) {
        try {
          await adminService.deleteChapter(chapter.id)
          showMessage('Chapter deleted successfully', 'success')
          await loadChapters(selectedSubject.value.id)
          await loadSubjects()
        } catch (error) {
          showMessage('Failed to delete chapter', 'error')
          console.error('Delete chapter error:', error)
        }
      }
    }

    const closeChaptersModal = () => {
      showChaptersModal.value = false
      showCreateChapterModal.value = false
      selectedSubject.value = null
      chapters.value = []
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

    // Watch for showCreateModal changes (no longer needed with v-if approach)

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
      // Chapter management
      showChaptersModal,
      selectedSubject,
      chapters,
      loadingChapters,
      showCreateChapterModal,
      chapterForm,
      // Methods
      loadSubjects,
      editSubject,
      saveSubject,
      deleteSubject,
      manageChapters,
      loadChapters,
      openCreateChapterModal,
      saveChapter,
      closeChaptersModal,
      closeModal,
      formatDate,
      editChapter,
      deleteChapter
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
