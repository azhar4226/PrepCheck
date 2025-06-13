<template>
  <div class="container-fluid">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading quiz...</span>
      </div>
      <p class="mt-2">Loading quiz...</p>
    </div>

    <!-- Quiz Interface -->
    <div v-else-if="quiz && !showResults" class="quiz-interface">
      <!-- Quiz Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <div class="row align-items-center">
                <div class="col-md-8">
                  <h3 class="card-title mb-1">{{ quiz.title }}</h3>
                  <p class="card-text mb-0">
                    <i class="bi bi-bookmark me-2"></i>{{ quiz.subject_name }} • {{ quiz.chapter_name }}
                  </p>
                </div>
                <div class="col-md-4 text-md-end">
                  <div class="d-flex justify-content-md-end align-items-center gap-3">
                    <div class="text-center">
                      <div class="h4 mb-0">{{ currentQuestionIndex + 1 }}/{{ quiz.questions.length }}</div>
                      <small>Question</small>
                    </div>
                    <div class="text-center">
                      <div class="h4 mb-0" :class="{ 'text-warning': timeRemaining < 300 }">
                        {{ formatTime(timeRemaining) }}
                      </div>
                      <small>Time Left</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="progress" style="height: 10px;">
            <div 
              class="progress-bar" 
              role="progressbar" 
              :style="{ width: progressPercentage + '%' }"
              :aria-valuenow="progressPercentage" 
              aria-valuemin="0" 
              aria-valuemax="100"
            ></div>
          </div>
        </div>
      </div>

      <!-- Question Card -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Question {{ currentQuestionIndex + 1 }}</h5>
              <span class="badge bg-secondary">{{ currentQuestion.question_type }}</span>
            </div>
            <div class="card-body">
              <div class="question-content mb-4">
                <p class="h6">{{ currentQuestion.question_text }}</p>
                
                <!-- Multiple Choice Options -->
                <div v-if="currentQuestion.question_type === 'multiple_choice'" class="mt-4">
                  <div 
                    v-for="(option, index) in currentQuestion.options" 
                    :key="index"
                    class="form-check mb-3"
                  >
                    <input 
                      class="form-check-input" 
                      type="radio" 
                      :name="'question_' + currentQuestion.id"
                      :id="'option_' + index"
                      :value="option"
                      v-model="answers[currentQuestion.id]"
                    >
                    <label class="form-check-label" :for="'option_' + index">
                      {{ option }}
                    </label>
                  </div>
                </div>

                <!-- True/False Options -->
                <div v-else-if="currentQuestion.question_type === 'true_false'" class="mt-4">
                  <div class="form-check mb-3">
                    <input 
                      class="form-check-input" 
                      type="radio" 
                      :name="'question_' + currentQuestion.id"
                      id="true_option"
                      value="True"
                      v-model="answers[currentQuestion.id]"
                    >
                    <label class="form-check-label" for="true_option">
                      True
                    </label>
                  </div>
                  <div class="form-check mb-3">
                    <input 
                      class="form-check-input" 
                      type="radio" 
                      :name="'question_' + currentQuestion.id"
                      id="false_option"
                      value="False"
                      v-model="answers[currentQuestion.id]"
                    >
                    <label class="form-check-label" for="false_option">
                      False
                    </label>
                  </div>
                </div>

                <!-- Short Answer -->
                <div v-else-if="currentQuestion.question_type === 'short_answer'" class="mt-4">
                  <textarea 
                    class="form-control" 
                    rows="4" 
                    placeholder="Enter your answer..."
                    v-model="answers[currentQuestion.id]"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <button 
              class="btn btn-outline-secondary"
              @click="previousQuestion"
              :disabled="currentQuestionIndex === 0"
            >
              <i class="bi bi-chevron-left me-2"></i>Previous
            </button>

            <div class="d-flex gap-2">
              <button class="btn btn-outline-primary" @click="saveProgress">
                <i class="bi bi-save me-2"></i>Save Progress
              </button>
              
              <button 
                v-if="currentQuestionIndex === quiz.questions.length - 1"
                class="btn btn-success"
                @click="showSubmitModal = true"
              >
                <i class="bi bi-check-circle me-2"></i>Submit Quiz
              </button>
              
              <button 
                v-else
                class="btn btn-primary"
                @click="nextQuestion"
              >
                Next<i class="bi bi-chevron-right ms-2"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Question Navigation Grid -->
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">Question Navigation</h6>
            </div>
            <div class="card-body">
              <div class="question-grid">
                <button
                  v-for="(question, index) in quiz.questions"
                  :key="question.id"
                  class="btn btn-sm question-nav-btn"
                  :class="getQuestionNavClass(index)"
                  @click="goToQuestion(index)"
                >
                  {{ index + 1 }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quiz Results -->
    <QuizResults 
      v-if="showResults && results"
      :results="results"
      @retake-quiz="retakeQuiz"
      @view-quizzes="$router.push('/quizzes')"
    />

    <!-- Submit Confirmation Modal -->
    <div 
      v-if="showSubmitModal" 
      class="modal fade show d-block" 
      tabindex="-1" 
      style="background-color: rgba(0,0,0,0.5);"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Submit Quiz</h5>
            <button type="button" class="btn-close" @click="showSubmitModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to submit this quiz?</p>
            <div class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              <strong>Answered:</strong> {{ answeredCount }}/{{ quiz.questions.length }} questions<br>
              <strong>Unanswered:</strong> {{ unansweredCount }} questions
            </div>
            <p class="text-muted small">
              Once submitted, you cannot change your answers.
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showSubmitModal = false">
              Cancel
            </button>
            <button type="button" class="btn btn-success" @click="submitQuiz" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
              Submit Quiz
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Auto-save indicator -->
    <div v-if="autoSaving" class="position-fixed bottom-0 end-0 m-3">
      <div class="toast show" role="alert">
        <div class="toast-body">
          <i class="bi bi-cloud-upload me-2"></i>Auto-saving...
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import { formatTime } from '@/services/utils'
import QuizResults from '@/components/QuizResults.vue'

export default {
  name: 'QuizTaking',
  components: {
    QuizResults
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const quiz = ref(null)
    const answers = ref({})
    const currentQuestionIndex = ref(0)
    const timeRemaining = ref(0)
    const loading = ref(true)
    const showResults = ref(false)
    const results = ref(null)
    const showSubmitModal = ref(false)
    const submitting = ref(false)
    const autoSaving = ref(false)
    
    let timer = null
    let autoSaveTimer = null
    
    const currentQuestion = computed(() => {
      return quiz.value?.questions[currentQuestionIndex.value]
    })
    
    const progressPercentage = computed(() => {
      if (!quiz.value) return 0
      return ((currentQuestionIndex.value + 1) / quiz.value.questions.length) * 100
    })
    
    const answeredCount = computed(() => {
      return Object.keys(answers.value).filter(key => answers.value[key]).length
    })
    
    const unansweredCount = computed(() => {
      if (!quiz.value) return 0
      return quiz.value.questions.length - answeredCount.value
    })
    
    const startQuiz = async () => {
      try {
        loading.value = true
        const response = await api.post(`/quiz/${route.params.id}/start`)
        
        quiz.value = response.data.quiz
        timeRemaining.value = response.data.time_remaining
        
        // Initialize answers object
        quiz.value.questions.forEach(question => {
          answers.value[question.id] = ''
        })
        
        // Load any existing progress
        if (response.data.saved_answers) {
          Object.assign(answers.value, response.data.saved_answers)
        }
        
        // Start timer
        startTimer()
        
        // Start auto-save
        startAutoSave()
        
      } catch (error) {
        console.error('Error starting quiz:', error)
        if (error.response?.status === 401) {
          router.push('/login')
        } else {
          router.push('/quizzes')
        }
      } finally {
        loading.value = false
      }
    }
    
    const startTimer = () => {
      timer = setInterval(() => {
        if (timeRemaining.value > 0) {
          timeRemaining.value--
        } else {
          // Time's up - auto submit
          submitQuiz()
        }
      }, 1000)
    }
    
    const startAutoSave = () => {
      autoSaveTimer = setInterval(() => {
        saveProgress(true)
      }, 30000) // Auto-save every 30 seconds
    }
    
    const saveProgress = async (isAutoSave = false) => {
      try {
        if (isAutoSave) {
          autoSaving.value = true
        }
        
        await api.put(`/quiz/${route.params.id}/save`, {
          answers: answers.value,
          current_question: currentQuestionIndex.value
        })
        
        if (isAutoSave) {
          setTimeout(() => {
            autoSaving.value = false
          }, 1000)
        }
        
      } catch (error) {
        console.error('Error saving progress:', error)
      }
    }
    
    const submitQuiz = async () => {
      try {
        submitting.value = true
        showSubmitModal.value = false
        
        const response = await api.post(`/quiz/${route.params.id}/submit`, {
          answers: answers.value
        })
        
        results.value = response.data
        showResults.value = true
        
        // Stop timers
        if (timer) clearInterval(timer)
        if (autoSaveTimer) clearInterval(autoSaveTimer)
        
      } catch (error) {
        console.error('Error submitting quiz:', error)
        submitting.value = false
      }
    }
    
    const nextQuestion = () => {
      if (currentQuestionIndex.value < quiz.value.questions.length - 1) {
        currentQuestionIndex.value++
      }
    }
    
    const previousQuestion = () => {
      if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--
      }
    }
    
    const goToQuestion = (index) => {
      currentQuestionIndex.value = index
    }
    
    const getQuestionNavClass = (index) => {
      const questionId = quiz.value.questions[index].id
      const isAnswered = answers.value[questionId] && answers.value[questionId].trim()
      const isCurrent = index === currentQuestionIndex.value
      
      if (isCurrent) {
        return 'btn-primary'
      } else if (isAnswered) {
        return 'btn-success'
      } else {
        return 'btn-outline-secondary'
      }
    }
    
    const retakeQuiz = () => {
      showResults.value = false
      results.value = null
      currentQuestionIndex.value = 0
      answers.value = {}
      
      // Reinitialize answers
      quiz.value.questions.forEach(question => {
        answers.value[question.id] = ''
      })
      
      startQuiz()
    }
    
    // Auto-save when answers change
    watch(answers, () => {
      // Debounced auto-save on answer change
      if (autoSaveTimer) {
        clearTimeout(autoSaveTimer)
      }
      autoSaveTimer = setTimeout(() => {
        saveProgress(true)
      }, 2000)
    }, { deep: true })
    
    // Cleanup on component unmount
    onUnmounted(() => {
      if (timer) clearInterval(timer)
      if (autoSaveTimer) clearInterval(autoSaveTimer)
    })
    
    // Prevent accidental page close
    const handleBeforeUnload = (e) => {
      if (!showResults.value) {
        e.preventDefault()
        e.returnValue = ''
      }
    }
    
    onMounted(() => {
      startQuiz()
      window.addEventListener('beforeunload', handleBeforeUnload)
    })
    
    onUnmounted(() => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    })
    
    return {
      quiz,
      answers,
      currentQuestionIndex,
      currentQuestion,
      timeRemaining,
      loading,
      showResults,
      results,
      showSubmitModal,
      submitting,
      autoSaving,
      progressPercentage,
      answeredCount,
      unansweredCount,
      saveProgress,
      submitQuiz,
      nextQuestion,
      previousQuestion,
      goToQuestion,
      getQuestionNavClass,
      retakeQuiz,
      formatTime
    }
  }
}
</script>

<style scoped>
.quiz-interface {
  max-width: 1200px;
  margin: 0 auto;
}

.question-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
  gap: 0.5rem;
}

.question-nav-btn {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.form-check-label {
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: background-color 0.15s ease-in-out;
}

.form-check-label:hover {
  background-color: #f8f9fa;
}

.modal {
  z-index: 1055;
}

.toast {
  min-width: 200px;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.progress-bar {
  transition: width 0.3s ease;
}

.text-warning {
  color: #ffc107 !important;
}

@media (max-width: 768px) {
  .question-grid {
    grid-template-columns: repeat(auto-fill, minmax(35px, 1fr));
  }
}
</style>