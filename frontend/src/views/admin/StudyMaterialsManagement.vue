<template>
  <div class="study-materials-management">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="bi bi-book me-2"></i>Study Materials Management</h2>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="bi bi-plus-lg me-1"></i>Add Material
      </button>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label">Subject</label>
            <select v-model="filters.subject_id" class="form-select" @change="filterBySubject">
              <option value="">All Subjects</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Chapter</label>
            <select v-model="filters.chapter_id" class="form-select" @change="loadStudyMaterials">
              <option value="">All Chapters</option>
              <option v-for="chapter in filteredChapters" :key="chapter.id" :value="chapter.id">
                {{ chapter.name }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Material Type</label>
            <select v-model="filters.material_type" class="form-select" @change="loadStudyMaterials">
              <option value="">All Types</option>
              <option value="text">Text</option>
              <option value="document">Document</option>
              <option value="video">Video</option>
              <option value="audio">Audio</option>
              <option value="link">Link</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Search</label>
            <input 
              v-model="filters.search" 
              type="text" 
              class="form-control" 
              placeholder="Search materials..."
              @input="debounceSearch"
            >
          </div>
        </div>
      </div>
    </div>

    <!-- Study Materials Table -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading study materials...</p>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          <i class="bi bi-exclamation-triangle me-2"></i>
          {{ error }}
        </div>

        <div v-else>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead class="table-light">
                <tr>
                  <th>Title</th>
                  <th>Type</th>
                  <th>Chapter</th>
                  <th>Subject</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="material in studyMaterials" :key="material.id">
                  <td>
                    <div class="material-preview">
                      <div class="material-title fw-bold">{{ material.title }}</div>
                      <small class="text-muted">{{ truncateText(material.description, 60) }}</small>
                    </div>
                  </td>
                  <td>
                    <span 
                      class="badge"
                      :class="{
                        'bg-info': material.material_type === 'text',
                        'bg-success': material.material_type === 'document',
                        'bg-warning': material.material_type === 'video',
                        'bg-secondary': material.material_type === 'audio',
                        'bg-primary': material.material_type === 'link'
                      }"
                    >
                      <i :class="getTypeIcon(material.material_type)" class="me-1"></i>
                      {{ formatType(material.material_type) }}
                    </span>
                  </td>
                  <td>{{ material.chapter_name || 'General' }}</td>
                  <td>{{ material.subject_name || 'N/A' }}</td>
                  <td>
                    <span 
                      class="badge"
                      :class="{
                        'bg-success': material.is_active,
                        'bg-warning': !material.is_active
                      }"
                    >
                      {{ material.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td>
                    <small class="text-muted">
                      {{ formatDate(material.created_at) }}
                    </small>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button 
                        class="btn btn-outline-info"
                        @click="viewMaterial(material)"
                        title="View Details"
                      >
                        <i class="bi bi-eye"></i>
                      </button>
                      <button 
                        class="btn btn-outline-primary"
                        @click="editMaterial(material)"
                        title="Edit Material"
                      >
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button 
                        class="btn btn-outline-success"
                        @click="duplicateMaterial(material)"
                        title="Duplicate Material"
                      >
                        <i class="bi bi-copy"></i>
                      </button>
                      <button 
                        class="btn btn-outline-danger"
                        @click="confirmDelete(material)"
                        title="Delete Material"
                      >
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <nav v-if="totalPages > 1" class="mt-4">
            <ul class="pagination justify-content-center">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button 
                  class="page-link" 
                  @click="changePage(currentPage - 1)"
                  :disabled="currentPage === 1"
                >
                  Previous
                </button>
              </li>
              
              <li 
                v-for="page in visiblePages" 
                :key="page" 
                class="page-item" 
                :class="{ active: page === currentPage }"
              >
                <button class="page-link" @click="changePage(page)">
                  {{ page }}
                </button>
              </li>
              
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button 
                  class="page-link" 
                  @click="changePage(currentPage + 1)"
                  :disabled="currentPage === totalPages"
                >
                  Next
                </button>
              </li>
            </ul>
          </nav>

          <!-- Empty state -->
          <div v-if="studyMaterials.length === 0" class="text-center py-5">
            <i class="bi bi-book display-1 text-muted"></i>
            <h4 class="mt-3 text-muted">No study materials found</h4>
            <p class="text-muted">Create your first study material to get started.</p>
            <button class="btn btn-primary" @click="showCreateModal = true">
              <i class="bi bi-plus-lg me-1"></i>Add Material
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <StudyMaterialModal 
      v-if="showCreateModal || showEditModal"
      :show="showCreateModal || showEditModal"
      :material="editingMaterial"
      :subjects="subjects"
      :chapters="chapters"
      @close="closeModal"
      @save="handleSave"
    />

    <!-- View Modal -->
    <StudyMaterialViewModal 
      ref="viewModal"
      :material="viewingMaterial"
      @edit-material="editMaterial"
    />

    <!-- Delete Confirmation Modal -->
    <div 
      v-if="showDeleteModal" 
      class="modal d-block" 
      style="background-color: rgba(0,0,0,0.5)"
      @click.self="showDeleteModal = false"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this study material?</p>
            <div class="alert alert-warning">
              <strong>{{ deletingMaterial?.title }}</strong><br>
              <small>This action cannot be undone.</small>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">
              Cancel
            </button>
            <button type="button" class="btn btn-danger" @click="deleteMaterial">
              <i class="bi bi-trash me-1"></i>Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import StudyMaterialModal from '@/components/modals/StudyMaterialModal.vue'
import StudyMaterialViewModal from '@/components/modals/StudyMaterialViewModal.vue'

// Reactive state
const loading = ref(false)
const error = ref('')
const studyMaterials = ref([])
const subjects = ref([])
const chapters = ref([])

// Pagination
const currentPage = ref(1)
const totalPages = ref(1)
const perPage = ref(20)

// Modals
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const editingMaterial = ref(null)
const viewingMaterial = ref(null)
const deletingMaterial = ref(null)

// Filters
const filters = reactive({
  subject_id: '',
  chapter_id: '',
  material_type: '',
  search: ''
})

// Computed
const filteredChapters = computed(() => {
  if (!filters.subject_id) return chapters.value
  return chapters.value.filter(chapter => chapter.subject_id == filters.subject_id)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Debounced search
let searchTimeout = null
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadStudyMaterials()
  }, 500)
}

// Load data methods
const loadStudyMaterials = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const params = {
      page: currentPage.value,
      per_page: perPage.value,
      ...filters
    }
    
    const response = await apiService.getStudyMaterials(params)
    
    studyMaterials.value = response.materials || []
    totalPages.value = response.pages || 1
    
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load study materials'
    console.error('Error loading study materials:', err)
  } finally {
    loading.value = false
  }
}

const loadSubjects = async () => {
  try {
    const response = await apiService.get('/api/admin/subjects')
    subjects.value = response || []
  } catch (err) {
    console.error('Error loading subjects:', err)
  }
}

const loadChapters = async () => {
  try {
    const response = await apiService.get('/api/admin/chapters')
    chapters.value = response || []
  } catch (err) {
    console.error('Error loading chapters:', err)
  }
}

// Filter handlers
const filterBySubject = () => {
  filters.chapter_id = ''
  loadStudyMaterials()
}

// Pagination
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadStudyMaterials()
  }
}

// Material actions
const viewModal = ref(null)

const viewMaterial = (material) => {
  viewingMaterial.value = material
  if (viewModal.value) {
    viewModal.value.show()
  }
}

const editMaterial = (material) => {
  editingMaterial.value = { ...material }
  showEditModal.value = true
}

const duplicateMaterial = async (material) => {
  try {
    const duplicateData = {
      ...material,
      title: `${material.title} (Copy)`,
      id: undefined,
      created_at: undefined,
      updated_at: undefined
    }
    
    await apiService.createStudyMaterial(duplicateData)
    await loadStudyMaterials()
    
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to duplicate material'
  }
}

const confirmDelete = (material) => {
  deletingMaterial.value = material
  showDeleteModal.value = true
}

const deleteMaterial = async () => {
  try {
    await apiService.deleteStudyMaterial(deletingMaterial.value.id)
    await loadStudyMaterials()
    showDeleteModal.value = false
    deletingMaterial.value = null
    
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to delete material'
  }
}

// Modal handlers
const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingMaterial.value = null
}

const handleSave = async () => {
  await loadStudyMaterials()
  closeModal()
}

// Utility functions
const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const formatType = (type) => {
  const types = {
    text: 'Text',
    document: 'Document',
    video: 'Video',
    audio: 'Audio',
    link: 'Link'
  }
  return types[type] || type
}

const getTypeIcon = (type) => {
  const icons = {
    text: 'bi-file-text',
    document: 'bi-file-earmark-pdf',
    video: 'bi-play-circle',
    audio: 'bi-music-note',
    link: 'bi-link-45deg'
  }
  return icons[type] || 'bi-file'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

// Initialize
onMounted(async () => {
  await Promise.all([
    loadStudyMaterials(),
    loadSubjects(),
    loadChapters()
  ])
})
</script>

<style scoped>
.material-preview {
  max-width: 300px;
}

.material-title {
  color: #333;
  text-decoration: none;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.table td {
  vertical-align: middle;
}

.pagination {
  margin-bottom: 0;
}

.modal {
  z-index: 1050;
}

@media (max-width: 768px) {
  .table-responsive {
    font-size: 0.875rem;
  }
  
  .btn-group-sm .btn {
    padding: 0.125rem 0.25rem;
    font-size: 0.75rem;
  }
}
</style>
