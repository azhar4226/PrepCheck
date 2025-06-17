<template>
  <div class="question-management">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="bi bi-question-circle me-2"></i>Question Management</h2>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="bi bi-plus-lg me-1"></i>Add Question
      </button>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label">Quiz</label>
            <select v-model="filters.quiz_id" class="form-select" @change="loadQuestions">
              <option value="">All Quizzes</option>
              <option v-for="quiz in quizzes" :key="quiz.id" :value="quiz.id">
                {{ quiz.title }}
              </option>
            </select>
          </div>
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
            <label class="form-label">Verification Status</label>
            <select v-model="filters.verification_status" class="form-select" @change="loadQuestions">
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="verified">Verified</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Search</label>
            <input 
              v-model="filters.search" 
              type="text" 
              class="form-control" 
              placeholder="Search questions..."
              @input="debounceSearch"
            >
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
                  <th>Quiz</th>
                  <th>Subject</th>
                  <th>Type</th>
                  <th>Marks</th>
                  <th>Status</th>
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
                  <td>{{ question.quiz_title || 'Unassigned' }}</td>
                  <td>{{ question.subject_name || 'N/A' }}</td>
                  <td>
                    <span class="badge bg-info">
                      {{ question.question_type || 'Multiple Choice' }}
                    </span>
                  </td>
                  <td>{{ question.marks || 1 }}</td>
                  <td>
                    <span 
                      class="badge"
                      :class="{
                        'bg-success': question.is_verified,
                        'bg-warning': !question.is_verified
                      }"
                    >
                      {{ question.is_verified ? 'Verified' : 'Pending' }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button 
                        class="btn btn-outline-info"
                        @click="viewQuestion(question)"
                        title="View Details"
                      >
                        <i class="bi bi-eye"></i>
                      </button>
                      <button 
                        class="btn btn-outline-primary"
                        @click="editQuestion(question)"
                        title="Edit Question"
                      >
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button 
                        class="btn btn-outline-success"
                        @click="duplicateQuestion(question)"
                        title="Duplicate Question"
                      >
                        <i class="bi bi-copy"></i>
                      </button>
                      <button 
                        class="btn btn-outline-danger"
                        @click="confirmDelete(question)"
                        title="Delete Question"
                      >
                        <i class="bi bi-trash"></i>
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
              <li 
                v-for="page in totalPages" 
                :key="page" 
                class="page-item" 
                :class="{ active: page === currentPage }"
              >
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

    <!-- Create/Edit Question Modal -->
    <QuestionModal
      v-if="showCreateModal || showEditModal"
      :show="showCreateModal || showEditModal"
      :question="editingQuestion"
      :quizzes="quizzes"
      :subjects="subjects"
      @close="closeModal"
      @save="handleQuestionSave"
    />

    <!-- View Question Modal -->
    <QuestionViewModal
      v-if="showViewModal"
      :show="showViewModal"
      :question="viewingQuestion"
      @close="showViewModal = false"
    />
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import adminService from '@/services/adminService'
import QuestionModal from '@/components/modals/QuestionModal.vue'
import QuestionViewModal from '@/components/modals/QuestionViewModal.vue'

export default {
  name: 'QuestionManagement',
  components: {
    QuestionModal,
    QuestionViewModal
  },
  setup() {
    const { api } = useAuth()
    
    // Reactive state
    const loading = ref(false)
    const error = ref('')
    const questions = ref([])
    const quizzes = ref([])
    const subjects = ref([])
    
    // Pagination
    const currentPage = ref(1)
    const totalPages = ref(1)
    const perPage = ref(20)
    
    // Modals
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showViewModal = ref(false)
    const editingQuestion = ref(null)
    const viewingQuestion = ref(null)
    
    // Filters
    const filters = reactive({
      quiz_id: '',
      subject_id: '',
      verification_status: '',
      search: ''
    })
    
    // Debounced search
    let searchTimeout = null
    const debounceSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        loadQuestions()
      }, 500)
    }
    
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
        
        const response = await api.getQuestions(params)
        
        questions.value = response.questions || []
        totalPages.value = response.total_pages || 1
        
      } catch (err) {
        error.value = err.response?.data?.message || 'Failed to load questions'
        console.error('Error loading questions:', err)
      } finally {
        loading.value = false
      }
    }
    
    const loadQuizzes = async () => {
      try {
        const response = await adminService.getQuizzes()
        quizzes.value = response.quizzes || []
      } catch (err) {
        console.error('Error loading quizzes:', err)
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
    
    // Filter handlers
    const filterBySubject = () => {
      // Reset quiz filter when subject changes
      filters.quiz_id = ''
      
      // Filter quizzes by subject
      if (filters.subject_id) {
        // This would need to be implemented based on quiz-subject relationship
      }
      
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
        
        await api.createQuestion(duplicatedQuestion)
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
        await api.deleteQuestion(questionId)
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
          await api.updateQuestion(editingQuestion.value.id, questionData)
        } else {
          // Create new question
          await api.createQuestion(questionData)
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
    
    // Utility functions
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }
    
    // Watchers
    watch(() => filters.quiz_id, () => {
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
        loadQuizzes(),
        loadSubjects()
      ])
    })
    
    return {
      // State
      loading,
      error,
      questions,
      quizzes,
      subjects,
      currentPage,
      totalPages,
      filters,
      
      // Modals
      showCreateModal,
      showEditModal,
      showViewModal,
      editingQuestion,
      viewingQuestion,
      
      // Methods
      loadQuestions,
      loadQuizzes,
      loadSubjects,
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
