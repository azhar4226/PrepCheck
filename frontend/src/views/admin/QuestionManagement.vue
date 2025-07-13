<template>
  <div class="question-management">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="bi bi-question-circle me-2"></i>Question Management</h2>
      <div class="action-buttons d-flex gap-2">
        <button class="btn btn-info" @click="openAIGenerateModal">
          <i class="bi bi-robot me-1"></i>Generate by AI
        </button>
        <button class="btn btn-secondary" @click="openImportModal">
          <i class="bi bi-upload me-1"></i>Import CSV
        </button>
        <button class="btn btn-primary" @click="openCreateModal">
          <i class="bi bi-plus-lg me-1"></i>Add Question
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-2">
            <label class="form-label">Subject</label>
            <select v-model="filters.subject_id" class="form-select" @change="filterBySubject">
              <option value="">All Subjects</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Chapter</label>
            <select v-model="filters.chapter_id" class="form-select" @change="loadQuestions">
              <option value="">All Chapters</option>
              <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                {{ chapter.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Source</label>
            <select v-model="filters.source" class="form-select" @change="loadQuestions">
              <option value="">All Sources</option>
              <option value="manual">Manual</option>
              <option value="ai">AI</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Verified</label>
            <select v-model="filters.is_verified" class="form-select" @change="loadQuestions">
              <option value="">All</option>
              <option value="true">Verified</option>
              <option value="false">Unverified</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Verified By</label>
            <select v-model="filters.verification_method" class="form-select" @change="loadQuestions">
              <option value="">All</option>
              <option value="manual">Admin</option>
              <option value="gemini">AI</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Search</label>
            <input v-model="filters.search" type="text" class="form-control" placeholder="Search questions..." @input="debounceSearch">
          </div>
        </div>
      </div>
    </div>

    <!-- Questions Table -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading questions...</p>
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
                  <th>Question</th>
                  <th>Subject</th>
                  <th>Chapter</th>
                  <th>Source</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Verified By</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="question in questions" :key="question.id">
                  <td>
                    <div class="question-preview">
                      <div class="question-text">{{ truncateText(question.question_text, 80) }}</div>
                      <small class="text-muted">Correct: {{ question.correct_option }}</small>
                    </div>
                  </td>
                  <td>{{ question.subject_name || 'N/A' }}</td>
                  <td>{{ question.chapter_name || 'N/A' }}</td>
                  <td>
                    <span class="badge" :class="question.source === 'ai' ? 'bg-info' : 'bg-secondary'">
                      {{ question.source ? question.source.toUpperCase() : 'MANUAL' }}
                    </span>
                  </td>
                  <td>
                    <span class="badge bg-info">
                      {{ question.question_type || 'Multiple Choice' }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="{'bg-success': question.is_verified, 'bg-warning': !question.is_verified}">
                      {{ question.is_verified ? 'Verified' : 'Pending' }}
                    </span>
                  </td>
                  <td>
                    <span v-if="question.is_verified">
                      <span v-if="question.verification_method === 'manual'">Admin</span>
                      <span v-else-if="question.verification_method === 'gemini'">AI</span>
                      <span v-else>{{ question.verified_by_name || question.verified_by_email || 'N/A' }}</span>
                    </span>
                    <span v-else>N/A</span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-info" @click="viewQuestion(question)" title="View Details">
                        <i class="bi bi-eye"></i>
                      </button>
                      <button class="btn btn-outline-primary" @click="editQuestion(question)" title="Edit Question">
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button class="btn btn-outline-danger" @click="confirmDelete(question)" title="Delete Question">
                        <i class="bi bi-trash"></i>
                      </button>
                      <button v-if="!question.is_verified" class="btn btn-outline-success" @click="openVerifyModal(question)" title="Verify Question">
                        <i class="bi bi-shield-check"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="questions.length === 0" class="text-center py-4">
              <i class="bi bi-question-circle text-muted" style="font-size: 3rem;"></i>
              <p class="text-muted mt-2">No questions found matching your criteria</p>
            </div>
          </div>

          <!-- Pagination -->
          <nav v-if="totalPages > 1" class="mt-4">
            <ul class="pagination justify-content-center">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link" @click="changePage(currentPage - 1)">Previous</button>
              </li>
              <li v-for="page in totalPages" :key="page" class="page-item" :class="{ active: page === currentPage }">
                <button class="page-link" @click="changePage(page)">{{ page }}</button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link" @click="changePage(currentPage + 1)">Next</button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- View Question Modal -->
    <QuestionViewModal
      v-if="showViewModal"
      :show="showViewModal"
      :question="viewingQuestion"
      @close="closeAllModals"
    />

    <!-- Edit Question Modal -->
    <QuestionModal
      v-if="showEditModal"
      :show="showEditModal"
      :question="editingQuestion"
      :subjects="subjects"
      :chapters="chapters"
      @close="closeAllModals"
      @save="handleQuestionSave"
    />

    <!-- Create Question Modal -->
    <QuestionModal
      v-if="showCreateModal"
      :show="showCreateModal"
      :question="null"
      :subjects="subjects"
      :chapters="chapters"
      @close="closeAllModals"
      @save="handleQuestionSave"
    />

    <!-- Import Modal -->
    <QuestionBankImportModal
      v-if="showImportModal"
      :show="showImportModal"
      @close="closeAllModals"
      @imported="loadQuestions"
    />

    <!-- AI Generate Modal -->
    <AIQuestionGenerator
      v-if="showAIGenerateModal"
      :show="showAIGenerateModal"
      @close="closeAllModals"
      @generated="loadQuestions"
    />

    <!-- Verify Question Modal -->
    <VerifyQuestionModal
      v-if="showVerifyModal"
      :show="showVerifyModal"
      :question="verifyingQuestion"
      @close="closeAllModals"
      @verify="handleVerify"
    />
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import adminService from '@/services/adminService'
import QuestionModal from '@/components/modals/QuestionModal.vue'
import QuestionViewModal from '@/components/modals/QuestionViewModal.vue'
import QuestionBankImportModal from '@/components/modals/QuestionBankImportModal.vue'
import AIQuestionGenerator from './AIQuestionGenerator.vue'
import VerifyQuestionModal from '@/components/modals/VerifyQuestionModal.vue'

export default {
  name: 'QuestionManagement',
  components: {
    QuestionModal,
    QuestionViewModal,
    QuestionBankImportModal,
    AIQuestionGenerator,
    VerifyQuestionModal
  },
  setup() {
    const { api } = useAuth()
    
    // Reactive state
    const loading = ref(false)
    const error = ref('')
    const questions = ref([])
    const tests = ref([])
    const subjects = ref([])
    const chapters = ref([])
    
    // Pagination
    const currentPage = ref(1)
    const totalPages = ref(1)
    const perPage = ref(10)
    
    // Modals
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showViewModal = ref(false)
    const showImportModal = ref(false)
    const showAIGenerateModal = ref(false)
    const showVerifyModal = ref(false)
    const editingQuestion = ref(null)
    const viewingQuestion = ref(null)
    const verifyingQuestion = ref(null)

    // Filters
    const filters = reactive({
      subject_id: '',
      chapter_id: '',
      source: '',
      is_verified: '',
      verification_method: '',
      search: ''
    })

    // --- URL & Modal State Sync ---
    const MODAL_URLS = {
      ai: '/admin/dashboard?tab=questions&modal=ai-generate',
      import: '/admin/dashboard?tab=questions&modal=import',
      add: '/admin/dashboard?tab=questions&modal=add',
      base: '/admin/dashboard?tab=questions'
    }

    // Open/close modal helpers that update URL
    const openAIGenerateModal = () => {
      showAIGenerateModal.value = true
      showCreateModal.value = false
      showImportModal.value = false
      window.history.pushState({ modal: 'ai-generate' }, '', MODAL_URLS.ai)
    }
    const openImportModal = () => {
      showImportModal.value = true
      showCreateModal.value = false
      showAIGenerateModal.value = false
      window.history.pushState({ modal: 'import' }, '', MODAL_URLS.import)
    }
    const openCreateModal = () => {
      showCreateModal.value = true
      showImportModal.value = false
      showAIGenerateModal.value = false
      window.history.pushState({ modal: 'add' }, '', MODAL_URLS.add)
    }
    // Close all modals and update URL
    const closeAllModals = () => {
      showCreateModal.value = false
      showImportModal.value = false
      showAIGenerateModal.value = false
      showEditModal.value = false
      showViewModal.value = false
      showVerifyModal.value = false
      window.history.replaceState({}, '', MODAL_URLS.base)
    }

    // Listen for browser navigation
    window.addEventListener('popstate', () => {
      const params = new URLSearchParams(window.location.search)
      const modal = params.get('modal')
      if (modal === 'ai-generate') {
        showAIGenerateModal.value = true
        showCreateModal.value = false
        showImportModal.value = false
      } else if (modal === 'import') {
        showImportModal.value = true
        showCreateModal.value = false
        showAIGenerateModal.value = false
      } else if (modal === 'add') {
        showCreateModal.value = true
        showImportModal.value = false
        showAIGenerateModal.value = false
      } else {
        closeAllModals()
      }
    })

    // On mount, sync modal state with URL
    onMounted(() => {
      const params = new URLSearchParams(window.location.search)
      const modal = params.get('modal')
      if (modal === 'ai-generate') openAIGenerateModal()
      else if (modal === 'import') openImportModal()
      else if (modal === 'add') openCreateModal()
    })
    // --- end URL & Modal State Sync ---

    // Load data
    const loadQuestions = async () => {
      try {
        loading.value = true
        error.value = ''
        const params = {
          page: currentPage.value,
          per_page: perPage.value,
          ...filters
        }
        const response = await adminService.getQuestions(params)
        questions.value = response.questions || []
        totalPages.value = response.total_pages || 1
      } catch (err) {
        error.value = err.response?.data?.message || 'Failed to load questions'
        console.error('Error loading questions:', err)
      } finally {
        loading.value = false
      }
    }
    
    const loadTests = async () => {
      try {
        const response = await adminService.getMockTests()
        tests.value = response.tests || []
      } catch (err) {
        console.error('Error loading tests:', err)
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
    
    const loadChapters = async () => {
      if (!filters.subject_id) {
        chapters.value = []
        return
      }
      try {
        const response = await adminService.getChapters(filters.subject_id)
        chapters.value = response || []
      } catch (err) {
        chapters.value = []
      }
    }
    
    // Filter handlers
    const filterBySubject = async () => {
      await loadChapters()
      filters.chapter_id = ''
      loadQuestions()
    }
    
    // CRUD operations
    const viewQuestion = (question) => {
      viewingQuestion.value = question
      showViewModal.value = true
    }
    
    const editQuestion = (question) => {
      editingQuestion.value = { ...question }
      showEditModal.value = true
    }
    
    const duplicateQuestion = async (question) => {
      try {
        const duplicatedQuestion = {
          ...question,
          question_text: `${question.question_text} (Copy)`,
          id: undefined // Remove ID to create new question
        }
        
        await adminService.createQuestion(duplicatedQuestion)
        await loadQuestions()
        
        // Show success message
        alert('Question duplicated successfully!')
        
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to duplicate question')
        console.error('Error duplicating question:', err)
      }
    }
    
    const confirmDelete = (question) => {
      if (confirm(`Are you sure you want to delete this question?\n\n"${question.question_text}"`)) {
        deleteQuestion(question.id)
      }
    }
    
    const deleteQuestion = async (questionId) => {
      try {
        await adminService.deleteQuestion(questionId)
        await loadQuestions()
        
        // Show success message
        alert('Question deleted successfully!')
        
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to delete question')
        console.error('Error deleting question:', err)
      }
    }
    
    const handleQuestionSave = async (questionData) => {
      try {
        if (editingQuestion.value && editingQuestion.value.id) {
          // Update existing question
          await adminService.updateQuestion(editingQuestion.value.id, questionData)
        } else {
          // Create new question
          await adminService.createQuestion(questionData)
        }
        
        await loadQuestions()
        closeModal()
        
        // Show success message
        alert('Question saved successfully!')
        
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to save question')
        console.error('Error saving question:', err)
      }
    }
    
    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingQuestion.value = null
    }
    
    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadQuestions()
      }
    }
    
    // Verify question
    const openVerifyModal = (question) => {
      verifyingQuestion.value = question
      showVerifyModal.value = true
    }
    
    const handleVerify = async (method) => {
      try {
        // method: 'admin' or 'ai'
        const verification_method = method === 'ai' ? 'gemini' : 'manual'
        await adminService.verifyQuestion(verifyingQuestion.value.id, {
          verification_method
        })
        showVerifyModal.value = false
        verifyingQuestion.value = null
        await loadQuestions()
        alert('Question verified successfully!')
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to verify question')
      }
    }
    
    
    // Utility functions
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }
    
    // Debounce search (no-op for now, implement as needed)
    const debounceSearch = () => {
      loadQuestions()
    }
    
    // Watchers
    watch(() => filters.is_verified, (val) => {
      if (val === 'false') {
        filters.verification_method = ''
      }
    })
    watch(() => filters.test_id, () => {
      currentPage.value = 1
      loadQuestions()
    })
    
    watch(() => filters.difficulty, () => {
      currentPage.value = 1
      loadQuestions()
    })
    
    // Initialize
    onMounted(async () => {
      await Promise.all([
        loadQuestions(),
        loadSubjects(),
        loadChapters()
      ])
    })
    
    return {
      // State
      loading,
      error,
      questions,
      tests,
      subjects,
      chapters,
      currentPage,
      totalPages,
      filters,
      
      // Modals
      showCreateModal,
      showEditModal,
      showViewModal,
      showImportModal,
      showAIGenerateModal,
      showVerifyModal,
      editingQuestion,
      viewingQuestion,
      verifyingQuestion,
      openAIGenerateModal,
      openImportModal,
      openCreateModal,
      closeAllModals,
      
      // Methods
      loadQuestions,
      loadTests,
      loadSubjects,
      loadChapters,
      filterBySubject,
      debounceSearch,
      viewQuestion,
      editQuestion,
      duplicateQuestion,
      confirmDelete,
      deleteQuestion,
      handleQuestionSave,
      closeModal,
      changePage,
      openVerifyModal,
      handleVerify,
      truncateText
    }
  }
}
</script>

<style scoped>
.question-management {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.question-preview {
  max-width: 300px;
}

.question-text {
  font-weight: 500;
  line-height: 1.4;
  margin-bottom: 0.25rem;
}

.table td {
  vertical-align: middle;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.page-link {
  cursor: pointer;
}

.page-item.disabled .page-link {
  cursor: not-allowed;
}
</style>
