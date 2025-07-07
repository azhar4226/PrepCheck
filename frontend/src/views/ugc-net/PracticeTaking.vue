<template>
  <div class="practice-taking-container">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="text-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3">Loading practice test...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="alert alert-danger" role="alert">
        <h4 class="alert-heading">Error Loading Practice Test</h4>
        <p>{{ error }}</p>
        <hr>
        <div class="d-flex justify-content-between">
          <button class="btn btn-outline-danger" @click="retryLoad">
            <i class="fas fa-redo"></i> Retry
          </button>
          <router-link to="/ugc-net" class="btn btn-secondary">
            <i class="fas fa-arrow-left"></i> Back to Dashboard
          </router-link>
        </div>
      </div>
    </div>

    <!-- Practice Test Interface -->
    <div v-else-if="practiceTest" class="practice-test-interface">
      <!-- Header with Timer and Progress -->
      <div class="test-header bg-white shadow-sm border-bottom sticky-top">
        <div class="container-fluid py-3">
          <div class="row align-items-center">
            <div class="col-md-4">
              <h5 class="mb-0">
                <i class="fas fa-file-alt text-primary"></i>
                {{ practiceTest.title }}
              </h5>
              <small class="text-muted">{{ practiceTest.subject_name }}</small>
            </div>
            <div class="col-md-4 text-center">
              <div class="timer-display">
                <i class="fas fa-clock text-warning"></i>
                <span class="fw-bold" :class="timeWarningClass">{{ formattedTimeLeft }}</span>
              </div>
            </div>
            <div class="col-md-4 text-end">
              <div class="question-progress">
                <span>{{ currentQuestionIndex + 1 }} of {{ totalQuestions }}</span>
                <div class="progress mt-1" style="height: 6px;">
                  <div class="progress-bar" role="progressbar" 
                       :style="{ width: progressPercentage + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Question Navigation -->
      <div class="question-navigation bg-light border-bottom">
        <div class="container-fluid py-2">
          <div class="row">
            <div class="col-12">
              <div class="question-grid">
                <button
                  v-for="(question, index) in questions"
                  :key="question.id"
                  @click="goToQuestion(index)"
                  :class="getQuestionButtonClass(index)"
                  class="question-nav-btn"
                >
                  {{ index + 1 }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Question Content -->
      <div class="question-content">
        <div class="container-fluid py-4">
          <div class="row justify-content-center">
            <div class="col-lg-8">
              <div class="question-card card shadow-sm">
                <div class="card-header">
                  <div class="d-flex justify-content-between align-items-center">
                    <span class="badge bg-secondary">Question {{ currentQuestionIndex + 1 }}</span>
                    <span class="badge bg-info">{{ currentQuestion.difficulty }}</span>
                  </div>
                </div>
                <div class="card-body">
                  <!-- Question Text -->
                  <div class="question-text mb-4">
                    <h6 class="fw-semibold">{{ currentQuestion.question_text }}</h6>
                  </div>

                  <!-- Options -->
                  <div class="options-container">
                    <div class="row">
                      <div class="col-12">
                        <div class="form-check option-item mb-3" 
                             v-for="option in options" 
                             :key="option.key">
                          <input 
                            class="form-check-input" 
                            type="radio" 
                            :name="`question_${currentQuestion.id}`"
                            :id="`option_${currentQuestion.id}_${option.key}`"
                            :value="option.key"
                            v-model="userAnswers[currentQuestion.id]"
                            @change="saveAnswer"
                          >
                          <label 
                            class="form-check-label option-label" 
                            :for="`option_${currentQuestion.id}_${option.key}`"
                          >
                            <span class="option-letter">{{ option.key }}.</span>
                            <span class="option-text">{{ option.text }}</span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Question Meta Info -->
                  <div class="question-meta mt-4 pt-3 border-top">
                    <div class="row">
                      <div class="col-md-6">
                        <small class="text-muted">
                          <i class="fas fa-layer-group"></i>
                          Chapter: {{ currentQuestion.chapter_name || 'General' }}
                        </small>
                      </div>
                      <div class="col-md-6 text-end">
                        <small class="text-muted">
                          <i class="fas fa-award"></i>
                          Marks: {{ currentQuestion.marks || 1 }}
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Navigation Buttons -->
              <div class="navigation-buttons mt-4">
                <div class="row">
                  <div class="col-6">
                    <button 
                      class="btn btn-outline-secondary"
                      @click="previousQuestion"
                      :disabled="currentQuestionIndex === 0"
                    >
                      <i class="fas fa-chevron-left"></i> Previous
                    </button>
                  </div>
                  <div class="col-6 text-end">
                    <button 
                      v-if="currentQuestionIndex < totalQuestions - 1"
                      class="btn btn-primary"
                      @click="nextQuestion"
                    >
                      Next <i class="fas fa-chevron-right"></i>
                    </button>
                    <button 
                      v-else
                      class="btn btn-success"
                      @click="showSubmitModal"
                    >
                      <i class="fas fa-check"></i> Submit Test
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit Confirmation Modal -->
    <div class="modal fade" id="submitModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Submit Practice Test</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="submission-summary">
              <h6>Test Summary</h6>
              <div class="row text-center">
                <div class="col-4">
                  <div class="stat-item">
                    <div class="stat-value text-success">{{ answeredCount }}</div>
                    <div class="stat-label">Answered</div>
                  </div>
                </div>
                <div class="col-4">
                  <div class="stat-item">
                    <div class="stat-value text-warning">{{ unansweredCount }}</div>
                    <div class="stat-label">Unanswered</div>
                  </div>
                </div>
                <div class="col-4">
                  <div class="stat-item">
                    <div class="stat-value text-primary">{{ totalQuestions }}</div>
                    <div class="stat-label">Total</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-3">
              <p class="text-muted">
                Are you sure you want to submit this practice test? 
                You won't be able to change your answers after submission.
              </p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Continue Testing
            </button>
            <button type="button" class="btn btn-success" @click="submitTest" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ submitting ? 'Submitting...' : 'Submit Test' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ugcNetService from '@/services/ugcNetService'
import { Modal } from 'bootstrap'

export default {
  name: 'PracticeTaking',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // State
    const loading = ref(true)
    const error = ref(null)
    const practiceTest = ref(null)
    const questions = ref([])
    const currentQuestionIndex = ref(0)
    const userAnswers = ref({})
    const timeLeft = ref(0)
    const timer = ref(null)
    const submitting = ref(false)
    
    // Computed
    const attemptId = computed(() => route.params.attemptId)
    const totalQuestions = computed(() => questions.value.length)
    const currentQuestion = computed(() => questions.value[currentQuestionIndex.value] || {})
    
    const options = computed(() => {
      const q = currentQuestion.value
      if (!q) return []
      
      return [
        { key: 'A', text: q.option_a },
        { key: 'B', text: q.option_b },
        { key: 'C', text: q.option_c },
        { key: 'D', text: q.option_d }
      ]
    })
    
    const progressPercentage = computed(() => {
      if (totalQuestions.value === 0) return 0
      return ((currentQuestionIndex.value + 1) / totalQuestions.value) * 100
    })
    
    const formattedTimeLeft = computed(() => {
      const hours = Math.floor(timeLeft.value / 3600)
      const minutes = Math.floor((timeLeft.value % 3600) / 60)
      const seconds = timeLeft.value % 60
      
      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      }
      return `${minutes}:${seconds.toString().padStart(2, '0')}`
    })
    
    const timeWarningClass = computed(() => {
      if (timeLeft.value < 300) return 'text-danger' // Less than 5 minutes
      if (timeLeft.value < 600) return 'text-warning' // Less than 10 minutes
      return 'text-success'
    })
    
    const answeredCount = computed(() => {
      return Object.keys(userAnswers.value).length
    })
    
    const unansweredCount = computed(() => {
      return totalQuestions.value - answeredCount.value
    })
    
    // Methods
    const loadPracticeTest = async () => {
      try {
        loading.value = true
        error.value = null
        
        console.log('Loading practice test for attempt:', attemptId.value)
        
        const result = await ugcNetService.getPracticeTest(attemptId.value)
        if (result.success) {
          practiceTest.value = result.data.attempt
          questions.value = result.data.attempt.questions || []
          userAnswers.value = result.data.attempt.answers || {}
          
          // Initialize timer
          if (practiceTest.value.time_limit && practiceTest.value.status === 'in_progress') {
            const startTime = new Date(practiceTest.value.start_time)
            const now = new Date()
            const elapsed = Math.floor((now - startTime) / 1000)
            const totalTime = practiceTest.value.time_limit * 60 // Convert to seconds
            timeLeft.value = Math.max(0, totalTime - elapsed)
            
            if (timeLeft.value > 0) {
              startTimer()
            } else {
              await autoSubmit()
            }
          }
        } else {
          error.value = result.error
        }
      } catch (err) {
        error.value = 'Failed to load practice test'
        console.error('Error loading practice test:', err)
      } finally {
        loading.value = false
      }
    }
    
    const startTimer = () => {
      timer.value = setInterval(() => {
        timeLeft.value--
        if (timeLeft.value <= 0) {
          clearInterval(timer.value)
          autoSubmit()
        }
      }, 1000)
    }
    
    const autoSubmit = async () => {
      console.log('Auto-submitting due to time expiry')
      await submitTest(true)
    }
    
    const saveAnswer = async () => {
      try {
        // Auto-save answers
        await ugcNetService.savePracticeAnswers(attemptId.value, userAnswers.value)
      } catch (err) {
        console.error('Error saving answer:', err)
      }
    }
    
    const goToQuestion = (index) => {
      currentQuestionIndex.value = index
    }
    
    const nextQuestion = () => {
      if (currentQuestionIndex.value < totalQuestions.value - 1) {
        currentQuestionIndex.value++
      }
    }
    
    const previousQuestion = () => {
      if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--
      }
    }
    
    const getQuestionButtonClass = (index) => {
      const baseClass = 'btn btn-sm me-1 mb-1'
      const isAnswered = userAnswers.value[questions.value[index]?.id]
      const isCurrent = index === currentQuestionIndex.value
      
      if (isCurrent) {
        return `${baseClass} btn-primary`
      } else if (isAnswered) {
        return `${baseClass} btn-success`
      } else {
        return `${baseClass} btn-outline-secondary`
      }
    }
    
    const showSubmitModal = () => {
      const modal = new Modal(document.getElementById('submitModal'))
      modal.show()
    }
    
    const submitTest = async (autoSubmit = false) => {
      try {
        submitting.value = true
        
        const result = await ugcNetService.submitPracticeTest(attemptId.value, userAnswers.value)
        
        if (result.success) {
          // Close modal if not auto-submit
          if (!autoSubmit) {
            const modal = Modal.getInstance(document.getElementById('submitModal'))
            if (modal) modal.hide()
          }
          
          // Navigate to results
          router.push({
            name: 'PracticeResults',
            params: { attemptId: attemptId.value }
          })
        } else {
          alert('Failed to submit test: ' + result.error)
        }
      } catch (err) {
        console.error('Error submitting test:', err)
        alert('Failed to submit test')
      } finally {
        submitting.value = false
      }
    }
    
    const retryLoad = () => {
      loadPracticeTest()
    }
    
    // Lifecycle
    onMounted(() => {
      loadPracticeTest()
    })
    
    onUnmounted(() => {
      if (timer.value) {
        clearInterval(timer.value)
      }
    })
    
    return {
      loading,
      error,
      practiceTest,
      questions,
      currentQuestionIndex,
      userAnswers,
      timeLeft,
      submitting,
      totalQuestions,
      currentQuestion,
      options,
      progressPercentage,
      formattedTimeLeft,
      timeWarningClass,
      answeredCount,
      unansweredCount,
      loadPracticeTest,
      saveAnswer,
      goToQuestion,
      nextQuestion,
      previousQuestion,
      getQuestionButtonClass,
      showSubmitModal,
      submitTest,
      retryLoad
    }
  }
}
</script>

<style scoped>
.practice-taking-container {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.test-header {
  z-index: 1000;
}

.timer-display {
  font-size: 1.1rem;
}

.question-navigation {
  max-height: 80px;
  overflow-y: auto;
}

.question-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.question-nav-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  background: white;
  color: #6c757d;
  font-weight: 500;
  transition: all 0.2s;
}

.question-nav-btn:hover {
  border-color: #0d6efd;
  color: #0d6efd;
}

.question-content {
  padding-bottom: 100px;
}

.question-card {
  border: none;
  border-radius: 12px;
}

.question-text {
  line-height: 1.6;
  font-size: 1.05rem;
}

.option-item {
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
}

.option-item:hover {
  border-color: #0d6efd;
  background-color: #f8f9ff;
}

.option-item input[type="radio"]:checked + .option-label {
  color: #0d6efd;
  font-weight: 500;
}

.option-label {
  cursor: pointer;
  width: 100%;
  margin: 0;
  display: flex;
  align-items: center;
}

.option-letter {
  font-weight: 600;
  margin-right: 12px;
  min-width: 20px;
}

.option-text {
  flex: 1;
  line-height: 1.4;
}

.question-meta {
  font-size: 0.9rem;
}

.navigation-buttons {
  position: sticky;
  bottom: 20px;
  z-index: 100;
}

.stat-item {
  padding: 10px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-label {
  font-size: 0.85rem;
  color: #6c757d;
}

.loading-state,
.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  padding: 2rem;
}
</style>
