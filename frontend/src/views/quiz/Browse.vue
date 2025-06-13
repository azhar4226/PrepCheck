<template>
  <div class="container-fluid">
    <!-- Header Section -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="h2 text-primary">
              <i class="bi bi-collection me-2"></i>Browse Quizzes
            </h1>
            <p class="text-muted mb-0">Choose from our collection of practice quizzes</p>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-secondary" @click="refreshQuizzes">
              <i class="bi bi-arrow-clockwise me-1"></i>Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label">Subject</label>
                <select v-model="filters.subject" class="form-select" @change="applyFilters">
                  <option value="">All Subjects</option>
                  <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                    {{ subject.name }}
                  </option>
                </select>
              </div>
              
              <div class="col-md-4">
                <label class="form-label">Chapter</label>
                <select v-model="filters.chapter" class="form-select" @change="applyFilters" :disabled="!filters.subject">
                  <option value="">All Chapters</option>
                  <option v-for="chapter in filteredChapters" :key="chapter.id" :value="chapter.id">
                    {{ chapter.name }}
                  </option>
                </select>
              </div>
              
              <div class="col-md-4">
                <label class="form-label">Difficulty</label>
                <select v-model="filters.difficulty" class="form-select" @change="applyFilters">
                  <option value="">All Levels</option>
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>
            
            <div class="row g-3 mt-2">
              <div class="col-md-6">
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-search"></i></span>
                  <input 
                    type="text" 
                    class="form-control" 
                    placeholder="Search quizzes..." 
                    v-model="filters.search"
                    @input="debouncedSearch"
                  >
                </div>
              </div>
              
              <div class="col-md-6 d-flex align-items-end gap-2">
                <button class="btn btn-outline-secondary" @click="clearFilters">
                  <i class="bi bi-x-circle me-1"></i>Clear Filters
                </button>
                <div class="text-muted">
                  {{ filteredQuizzes.length }} quiz{{ filteredQuizzes.length !== 1 ? 'es' : '' }} found
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quiz Grid -->
    <div class="row">
      <div v-if="loading" class="col-12 text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Loading quizzes...</p>
      </div>
      
      <div v-else-if="filteredQuizzes.length === 0" class="col-12 text-center py-5">
        <i class="bi bi-search display-1 text-muted mb-3"></i>
        <h4 class="text-muted">No quizzes found</h4>
        <p class="text-muted">Try adjusting your filters or search terms.</p>
        <button class="btn btn-primary" @click="clearFilters">
          <i class="bi bi-arrow-clockwise me-2"></i>Reset Filters
        </button>
      </div>
      
      <div v-else class="col-12">
        <div class="row">
          <div 
            v-for="quiz in paginatedQuizzes" 
            :key="quiz.id" 
            class="col-lg-4 col-md-6 mb-4"
          >
            <div class="card h-100 quiz-card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <span class="badge bg-primary">{{ quiz.subject_name }}</span>
                <span class="badge" :class="getDifficultyBadgeClass(quiz.difficulty)">
                  {{ quiz.difficulty }}
                </span>
              </div>
              
              <div class="card-body d-flex flex-column">
                <h5 class="card-title">{{ quiz.title }}</h5>
                <p class="card-text text-muted small mb-2">
                  <i class="bi bi-bookmark me-1"></i>{{ quiz.chapter_name }}
                </p>
                <p class="card-text flex-grow-1">{{ quiz.description }}</p>
                
                <div class="quiz-stats mb-3">
                  <div class="row text-center small">
                    <div class="col-4">
                      <i class="bi bi-question-circle text-primary"></i>
                      <div>{{ quiz.total_questions }}</div>
                      <div class="text-muted">Questions</div>
                    </div>
                    <div class="col-4">
                      <i class="bi bi-clock text-info"></i>
                      <div>{{ quiz.time_limit }}</div>
                      <div class="text-muted">Minutes</div>
                    </div>
                    <div class="col-4">
                      <i class="bi bi-people text-success"></i>
                      <div>{{ quiz.attempts_count || 0 }}</div>
                      <div class="text-muted">Attempts</div>
                    </div>
                  </div>
                </div>
                
                <div class="d-grid">
                  <button 
                    class="btn btn-primary" 
                    @click="startQuiz(quiz)"
                    :disabled="!quiz.is_active"
                  >
                    <i class="bi bi-play-circle me-2"></i>
                    {{ quiz.is_active ? 'Start Quiz' : 'Unavailable' }}
                  </button>
                </div>
              </div>
              
              <div v-if="quiz.last_attempt" class="card-footer bg-light">
                <small class="text-muted">
                  <i class="bi bi-clock-history me-1"></i>
                  Last attempt: {{ formatDate(quiz.last_attempt.completed_at) }}
                  <span class="float-end">
                    Score: {{ quiz.last_attempt.percentage }}%
                  </span>
                </small>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Pagination -->
        <div v-if="totalPages > 1" class="row mt-4">
          <div class="col-12">
            <nav aria-label="Quiz pagination">
              <ul class="pagination justify-content-center">
                <li class="page-item" :class="{ disabled: currentPage === 1 }">
                  <button class="page-link" @click="changePage(currentPage - 1)" :disabled="currentPage === 1">
                    <i class="bi bi-chevron-left"></i>
                  </button>
                </li>
                
                <li 
                  v-for="page in visiblePages" 
                  :key="page" 
                  class="page-item" 
                  :class="{ active: page === currentPage }"
                >
                  <button class="page-link" @click="changePage(page)">{{ page }}</button>
                </li>
                
                <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                  <button class="page-link" @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">
                    <i class="bi bi-chevron-right"></i>
                  </button>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { formatDate, debounce } from '@/services/utils'

export default {
  name: 'QuizBrowse',
  setup() {
    const router = useRouter()
    
    const quizzes = ref([])
    const subjects = ref([])
    const chapters = ref([])
    const loading = ref(true)
    
    const filters = ref({
      subject: '',
      chapter: '',
      difficulty: '',
      search: ''
    })
    
    const currentPage = ref(1)
    const itemsPerPage = 12
    
    const filteredChapters = computed(() => {
      if (!filters.value.subject) return []
      return chapters.value.filter(chapter => chapter.subject_id == filters.value.subject)
    })
    
    const filteredQuizzes = computed(() => {
      let filtered = quizzes.value
      
      if (filters.value.subject) {
        filtered = filtered.filter(quiz => quiz.subject_id == filters.value.subject)
      }
      
      if (filters.value.chapter) {
        filtered = filtered.filter(quiz => quiz.chapter_id == filters.value.chapter)
      }
      
      if (filters.value.difficulty) {
        filtered = filtered.filter(quiz => quiz.difficulty === filters.value.difficulty)
      }
      
      if (filters.value.search) {
        const searchTerm = filters.value.search.toLowerCase()
        filtered = filtered.filter(quiz => 
          quiz.title.toLowerCase().includes(searchTerm) ||
          quiz.description.toLowerCase().includes(searchTerm) ||
          quiz.subject_name.toLowerCase().includes(searchTerm) ||
          quiz.chapter_name.toLowerCase().includes(searchTerm)
        )
      }
      
      return filtered
    })
    
    const totalPages = computed(() => {
      return Math.ceil(filteredQuizzes.value.length / itemsPerPage)
    })
    
    const paginatedQuizzes = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return filteredQuizzes.value.slice(start, end)
    })
    
    const visiblePages = computed(() => {
      const total = totalPages.value
      const current = currentPage.value
      const delta = 2
      
      let start = Math.max(1, current - delta)
      let end = Math.min(total, current + delta)
      
      if (end - start < 4) {
        if (start === 1) {
          end = Math.min(total, start + 4)
        } else {
          start = Math.max(1, end - 4)
        }
      }
      
      const pages = []
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })
    
    const loadQuizzes = async () => {
      try {
        loading.value = true
        const response = await api.get('/quiz/browse')
        quizzes.value = response.data.quizzes
      } catch (error) {
        console.error('Error loading quizzes:', error)
        if (error.response?.status === 401) {
          router.push('/login')
        }
      } finally {
        loading.value = false
      }
    }
    
    const loadSubjects = async () => {
      try {
        const response = await api.get('/quiz/subjects')
        subjects.value = response.data.subjects
      } catch (error) {
        console.error('Error loading subjects:', error)
      }
    }
    
    const loadChapters = async () => {
      try {
        const response = await api.get('/quiz/chapters')
        chapters.value = response.data.chapters
      } catch (error) {
        console.error('Error loading chapters:', error)
      }
    }
    
    const refreshQuizzes = () => {
      loadQuizzes()
    }
    
    const applyFilters = () => {
      currentPage.value = 1
      if (filters.value.subject === '') {
        filters.value.chapter = ''
      }
    }
    
    const clearFilters = () => {
      filters.value = {
        subject: '',
        chapter: '',
        difficulty: '',
        search: ''
      }
      currentPage.value = 1
    }
    
    const debouncedSearch = debounce(() => {
      applyFilters()
    }, 300)
    
    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }
    
    const startQuiz = (quiz) => {
      if (!quiz.is_active) return
      
      router.push({
        name: 'QuizTaking',
        params: { id: quiz.id }
      })
    }
    
    const getDifficultyBadgeClass = (difficulty) => {
      switch (difficulty) {
        case 'easy': return 'bg-success'
        case 'medium': return 'bg-warning'
        case 'hard': return 'bg-danger'
        default: return 'bg-secondary'
      }
    }
    
    // Watch for filter changes to reset pagination
    watch(filteredQuizzes, () => {
      if (currentPage.value > totalPages.value) {
        currentPage.value = 1
      }
    })
    
    onMounted(async () => {
      await Promise.all([
        loadQuizzes(),
        loadSubjects(),
        loadChapters()
      ])
    })
    
    return {
      quizzes,
      subjects,
      filteredChapters,
      loading,
      filters,
      filteredQuizzes,
      paginatedQuizzes,
      currentPage,
      totalPages,
      visiblePages,
      refreshQuizzes,
      applyFilters,
      clearFilters,
      debouncedSearch,
      changePage,
      startQuiz,
      getDifficultyBadgeClass,
      formatDate
    }
  }
}
</script>

<style scoped>
.quiz-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.quiz-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.quiz-stats {
  background-color: #f8f9fa;
  border-radius: 0.375rem;
  padding: 1rem;
}

.pagination .page-link {
  color: #0d6efd;
  border-color: #dee2e6;
}

.pagination .page-item.active .page-link {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.badge {
  font-size: 0.75em;
}

.form-select:focus,
.form-control:focus {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}
</style>