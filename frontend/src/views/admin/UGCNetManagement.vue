<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <!-- Header -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2 class="mb-1">📋 Mock Test Management</h2>
            <p class="text-muted mb-0">Manage and organize UGC NET mock tests across all subjects</p>
          </div>
          <div class="d-flex gap-2">
            <button 
              class="btn btn-outline-primary"
              @click="loadMockTests"
            >
              <i class="bi bi-arrow-clockwise me-1"></i>
              Refresh
            </button>
            <button 
              class="btn btn-primary"
              @click="showCreateModal = true"
            >
              <i class="bi bi-plus-circle me-1"></i>
              Create Mock Test
            </button>
          </div>
        </div>

        <!-- Filters -->
        <div class="card shadow-sm mb-4">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-3">
                <label class="form-label">Subject Filter</label>
                <select v-model="filters.subject" class="form-select">
                  <option value="">All Subjects</option>
                  <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                    {{ subject.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Difficulty</label>
                <select v-model="filters.difficulty" class="form-select">
                  <option value="">All Difficulties</option>
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Status</label>
                <select v-model="filters.status" class="form-select">
                  <option value="">All Statuses</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="draft">Draft</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Search</label>
                <input 
                  v-model="filters.search" 
                  type="text" 
                  class="form-control" 
                  placeholder="Search mock tests..."
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading mock tests...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger">
          <i class="bi bi-exclamation-triangle me-2"></i>
          {{ error }}
        </div>

        <!-- Mock Tests Table -->
        <div v-else class="card shadow-sm">
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover">
                <thead class="table-dark">
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Subject</th>
                    <th>Paper Type</th>
                    <th>Questions</th>
                    <th>Difficulty</th>
                    <th>Status</th>
                    <th>Attempts</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="mockTest in filteredMockTests" :key="mockTest.id">
                    <td>{{ mockTest.id }}</td>
                    <td>
                      <div class="fw-bold">{{ mockTest.title }}</div>
                      <small class="text-muted">{{ mockTest.description?.substring(0, 50) }}...</small>
                    </td>
                    <td>
                      <span class="badge bg-info">{{ mockTest.subject?.name }}</span>
                    </td>
                    <td>{{ mockTest.paper_type || 'Paper 2' }}</td>
                    <td>
                      <span class="badge bg-secondary">{{ mockTest.total_questions || 0 }}</span>
                    </td>
                    <td>
                      <span 
                        class="badge"
                        :class="{
                          'bg-success': mockTest.difficulty === 'easy',
                          'bg-warning': mockTest.difficulty === 'medium',
                          'bg-danger': mockTest.difficulty === 'hard'
                        }"
                      >
                        {{ mockTest.difficulty }}
                      </span>
                    </td>
                    <td>
                      <span 
                        class="badge"
                        :class="{
                          'bg-success': mockTest.status === 'active',
                          'bg-secondary': mockTest.status === 'inactive',
                          'bg-warning': mockTest.status === 'draft'
                        }"
                      >
                        {{ mockTest.status }}
                      </span>
                    </td>
                    <td>{{ mockTest.attempts_count || 0 }}</td>
                    <td>{{ formatDate(mockTest.created_at) }}</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button 
                          class="btn btn-outline-primary"
                          @click="editMockTest(mockTest)"
                          title="Edit Mock Test"
                        >
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button 
                          class="btn btn-outline-info"
                          @click="viewQuestions(mockTest)"
                          title="Generate Questions"
                        >
                          <i class="bi bi-list"></i>
                        </button>
                        <button 
                          class="btn btn-outline-success"
                          @click="duplicateMockTest(mockTest)"
                          title="Duplicate Mock Test"
                        >
                          <i class="bi bi-copy"></i>
                        </button>
                        <button 
                          class="btn btn-outline-danger"
                          @click="confirmDelete(mockTest)"
                          title="Delete Mock Test"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              
              <div v-if="filteredMockTests.length === 0" class="text-center py-4">
                <i class="bi bi-search text-muted" style="font-size: 3rem;"></i>
                <p class="text-muted mt-2">No mock tests found matching your criteria</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <nav v-if="totalPages > 1" class="mt-4">
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: currentPage <= 1 }">
              <button class="page-link" @click="changePage(currentPage - 1)">Previous</button>
            </li>
            <li 
              v-for="page in visiblePages" 
              :key="page" 
              class="page-item" 
              :class="{ active: page === currentPage }"
            >
              <button class="page-link" @click="changePage(page)">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage >= totalPages }">
              <button class="page-link" @click="changePage(currentPage + 1)">Next</button>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Create/Edit Mock Test Modal -->
    <div 
      class="modal fade" 
      :class="{ show: showCreateModal || showEditModal }" 
      :style="{ display: showCreateModal || showEditModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingMockTest ? 'Edit Mock Test' : 'Create New Mock Test' }}
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="closeModal"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveMockTest">
              <div class="row g-3">
                <div class="col-12">
                  <label class="form-label">Mock Test Title</label>
                  <input 
                    v-model="mockTestForm.title" 
                    type="text" 
                    class="form-control" 
                    required
                  >
                </div>
                
                <div class="col-12">
                  <label class="form-label">Description</label>
                  <textarea 
                    v-model="mockTestForm.description" 
                    class="form-control" 
                    rows="3"
                  ></textarea>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label">Subject</label>
                  <select v-model="mockTestForm.subject_id" class="form-select" required>
                    <option value="">Select Subject</option>
                    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                      {{ subject.name }}
                    </option>
                  </select>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label">Chapter</label>
                  <select v-model="mockTestForm.chapter_id" class="form-select">
                    <option value="">Select Chapter</option>
                    <option 
                      v-for="chapter in availableChapters" 
                      :key="chapter.id" 
                      :value="chapter.id"
                    >
                      {{ chapter.name }}
                    </option>
                  </select>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label">Difficulty</label>
                  <select v-model="mockTestForm.difficulty" class="form-select" required>
                    <option value="">Select Difficulty</option>
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label">Status</label>
                  <select v-model="mockTestForm.status" class="form-select" required>
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label">Time Limit (minutes)</label>
                  <input 
                    v-model="mockTestForm.time_limit" 
                    type="number" 
                    class="form-control" 
                    min="1"
                  >
                </div>
                
                <div class="col-md-6">
                  <label class="form-label">Passing Score (%)</label>
                  <input 
                    v-model="mockTestForm.passing_score" 
                    type="number" 
                    class="form-control" 
                    min="0" 
                    max="100"
                  >
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="saveMockTest"
              :disabled="saving"
            >
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              {{ editingMockTest ? 'Update Mock Test' : 'Create Mock Test' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Backdrop -->
    <div 
      v-if="showCreateModal || showEditModal" 
      class="modal-backdrop fade show"
      @click="closeModal"
    ></div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import adminService from '@/services/adminService'

export default {
  name: 'MockTestManagement',
  setup() {
    const { api } = useAuth()
    
    // Reactive data
    const loading = ref(false)
    const saving = ref(false)
    const error = ref('')
    const mockTests = ref([])
    const subjects = ref([])
    const chapters = ref([])
    const currentPage = ref(1)
    const totalPages = ref(1)
    const itemsPerPage = ref(10)
    
    // Modal states
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const editingMockTest = ref(null)
    
    // Form data
    const mockTestForm = ref({
      title: '',
      description: '',
      subject_id: '',
      chapter_id: '',
      difficulty: '',
      status: 'draft',
      time_limit: null,
      passing_score: null
    })
    
    // Filters
    const filters = ref({
      subject: '',
      difficulty: '',
      status: '',
      search: ''
    })
    
    // Computed properties
    const filteredMockTests = computed(() => {
      let filtered = mockTests.value
      
      if (filters.value.subject) {
        filtered = filtered.filter(mockTest => 
          mockTest.subject_id === parseInt(filters.value.subject)
        )
      }
      
      if (filters.value.difficulty) {
        filtered = filtered.filter(mockTest => 
          mockTest.difficulty === filters.value.difficulty
        )
      }
      
      if (filters.value.status) {
        filtered = filtered.filter(mockTest => 
          mockTest.status === filters.value.status
        )
      }
      
      if (filters.value.search) {
        const search = filters.value.search.toLowerCase()
        filtered = filtered.filter(mockTest => 
          mockTest.title.toLowerCase().includes(search) ||
          mockTest.description?.toLowerCase().includes(search)
        )
      }
      
      return filtered
    })
    
    const availableChapters = computed(() => {
      if (!mockTestForm.value.subject_id) return []
      return chapters.value || []
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
    
    // Methods
    const loadMockTests = async () => {
      try {
        loading.value = true
        error.value = ''
        
        const response = await adminService.getMockTests()
        
        if (response) {
          mockTests.value = response.mockTests || []
          totalPages.value = Math.ceil((response.total || 0) / itemsPerPage.value)
        }
      } catch (err) {
        error.value = err.response?.data?.message || 'Failed to load mock tests'
        console.error('Error loading mock tests:', err)
      } finally {
        loading.value = false
      }
    }
    
    const loadSubjects = async () => {
      try {
        const response = await adminService.getSubjects()
        subjects.value = response || []
      } catch (err) {
        console.error('Error loading subjects:', err)
      }
    }
    
    const loadChapters = async (subjectId = null) => {
      try {
        if (subjectId) {
          const response = await adminService.getChapters(subjectId)
          chapters.value = response || []
        } else {
          chapters.value = []
        }
      } catch (err) {
        console.error('Error loading chapters:', err)
        chapters.value = []
      }
    }
    
    const editMockTest = (mockTest) => {
      editingMockTest.value = mockTest
      mockTestForm.value = {
        title: mockTest.title,
        description: mockTest.description || '',
        subject_id: mockTest.subject_id,
        chapter_id: mockTest.chapter_id,
        difficulty: mockTest.difficulty,
        status: mockTest.status,
        time_limit: mockTest.time_limit,
        passing_score: mockTest.passing_score
      }
      showEditModal.value = true
    }
    
    const saveMockTest = async () => {
      try {
        saving.value = true
        
        if (editingMockTest.value) {
          // Update existing mock test
          await adminService.updateMockTest(editingMockTest.value.id, mockTestForm.value)
          alert('Mock test updated successfully!')
        } else {
          // Create new mock test
          await adminService.createMockTest(mockTestForm.value)
          alert('Mock test created successfully!')
        }
        
        closeModal()
        loadMockTests()
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to save mock test')
        console.error('Error saving mock test:', err)
      } finally {
        saving.value = false
      }
    }
    
    const duplicateMockTest = async (mockTest) => {
      if (!confirm(`Are you sure you want to duplicate "${mockTest.title}"?`)) return
      
      try {
        const response = await apiClient.post(`/api/admin/mock-tests/${mockTest.id}/duplicate`)
        if (response.data.success) {
          loadMockTests()
          alert('Mock test duplicated successfully!')
        }
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to duplicate mock test')
        console.error('Error duplicating mock test:', err)
      }
    }
    
    const confirmDelete = async (mockTest) => {
      if (!confirm(`Are you sure you want to delete "${mockTest.title}"? This action cannot be undone.`)) return
      
      try {
        await adminService.deleteMockTest(mockTest.id)
        loadMockTests()
        alert('Mock test deleted successfully!')
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to delete mock test')
        console.error('Error deleting mock test:', err)
      }
    }
    
    const viewQuestions = (mockTest) => {
      // Navigate to questions management for this mock test
      // This would typically use router.push()
      alert(`Navigate to questions management for mock test: ${mockTest.title}`)
    }
    
    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingMockTest.value = null
      mockTestForm.value = {
        title: '',
        description: '',
        subject_id: '',
        chapter_id: '',
        difficulty: '',
        status: 'draft',
        time_limit: null,
        passing_score: null
      }
    }
    
    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadMockTests()
      }
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }
    
    // Watch for subject changes to clear chapter selection and load chapters
    watch(() => mockTestForm.value.subject_id, (newSubjectId) => {
      mockTestForm.value.chapter_id = ''
      if (newSubjectId) {
        loadChapters(newSubjectId)
      } else {
        chapters.value = []
      }
    })
    
    // Lifecycle
    onMounted(() => {
      loadMockTests()
      loadSubjects()
    })
    
    return {
      // Data
      loading,
      saving,
      error,
      mockTests,
      subjects,
      chapters,
      currentPage,
      totalPages,
      showCreateModal,
      showEditModal,
      editingMockTest,
      mockTestForm,
      filters,
      
      // Computed
      filteredMockTests,
      availableChapters,
      visiblePages,
      
      // Methods
      loadMockTests,
      loadSubjects,
      loadChapters,
      editMockTest,
      saveMockTest,
      duplicateMockTest,
      confirmDelete,
      viewQuestions,
      closeModal,
      changePage,
      formatDate
    }
  }
}
</script>

<style scoped>
.modal {
  background: rgba(0, 0, 0, 0.5);
}

.badge {
  font-size: 0.75em;
}

.table th {
  border-top: none;
  font-weight: 600;
  white-space: nowrap;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}

.table-responsive {
  border-radius: 0.5rem;
}
</style>
