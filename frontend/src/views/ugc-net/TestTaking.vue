<template>
  <div class="test-taking-container">
    <!-- Loading state -->
    <div v-if="!attempt || !mockTest" class="loading-container d-flex justify-content-center align-items-center" style="height: 100vh;">
      <div class="text-center">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted">Loading test...</p>
      </div>
    </div>

    <!-- Test content -->
    <div v-else>
      <!-- Test Header -->
      <div class="test-header bg-dark text-white position-sticky top-0" style="z-index: 1000;">
        <div class="container-fluid">
          <div class="row align-items-center py-3">
            <div class="col-md-4">
              <h5 class="mb-0">{{ mockTest.title }}</h5>
              <small class="text-muted">{{ mockTest.subject_name }}</small>
            </div>
          <div class="col-md-4 text-center">
            <div class="timer-display">
              <div class="time-remaining" :class="{ 'text-danger': timeRemaining < 300 }">
                <i class="bi bi-clock me-2"></i>
                {{ formatTime(timeRemaining) }}
              </div>
              <div class="progress mt-1" style="height: 4px;">
                <div 
                  class="progress-bar" 
                  :class="timeRemaining < 300 ? 'bg-danger' : 'bg-success'"
                  :style="{ width: timeProgress + '%' }"
                ></div>
              </div>
            </div>
          </div>
          <div class="col-md-4 text-md-end">
            <div class="question-progress">
              <span class="fw-bold">{{ currentQuestionIndex + 1 }} / {{ questions.length }}</span>
              <div class="small text-muted">Questions</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container-fluid py-4">
      <div class="row">
        <!-- Questions Panel -->
        <div class="col-lg-9">
          <div class="question-panel">
            <!-- Question Navigator -->
            <div class="card mb-4">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h6 class="mb-0">Question Navigator</h6>
                  <div class="legend small">
                    <span class="badge bg-success me-2">Answered</span>
                    <span class="badge bg-warning me-2">Marked</span>
                    <span class="badge bg-light text-dark">Not Visited</span>
                  </div>
                </div>
                <div class="question-grid">
                  <button
                    v-for="(question, index) in questions"
                    :key="question.id"
                    @click="goToQuestion(index)"
                    class="question-nav-btn"
                    :class="getQuestionNavClass(index)"
                  >
                    {{ index + 1 }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Current Question -->
            <div class="card" v-if="currentQuestion">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                  Question {{ currentQuestionIndex + 1 }}
                  <span class="badge bg-primary ms-2">{{ currentQuestion.marks || 1 }} mark{{ (currentQuestion.marks || 1) > 1 ? 's' : '' }}</span>
                </h5>
                <button 
                  @click="toggleBookmark(currentQuestionIndex)"
                  class="btn btn-outline-warning btn-sm"
                  :class="{ 'active': questionStates[currentQuestionIndex]?.bookmarked }"
                >
                  <i class="bi" :class="questionStates[currentQuestionIndex]?.bookmarked ? 'bi-bookmark-fill' : 'bi-bookmark'"></i>
                  {{ questionStates[currentQuestionIndex]?.bookmarked ? 'Bookmarked' : 'Bookmark' }}
                </button>
              </div>
              <div class="card-body">
                <!-- Question Text -->
                <div class="question-text mb-4">
                  <div v-html="currentQuestion.question_text"></div>
                </div>

                <!-- Options -->
                <div class="options">
                  <div 
                    v-for="option in questionOptions" 
                    :key="option.key" 
                    class="option-item mb-3"
                  >
                    <div class="form-check">
                      <input 
                        :id="`option-${currentQuestionIndex}-${option.key}`"
                        v-model="answers[currentQuestion.id]"
                        :value="option.key"
                        class="form-check-input"
                        type="radio"
                        :name="`question-${currentQuestion.id}`"
                        @change="updateQuestionState(currentQuestionIndex)"
                      >
                      <label 
                        :for="`option-${currentQuestionIndex}-${option.key}`"
                        class="form-check-label w-100 p-3 border rounded option-label"
                      >
                        <strong>{{ option.key }}.</strong> {{ option.text }}
                      </label>
                    </div>
                  </div>
                </div>

                <!-- Question Actions -->
                <div class="d-flex justify-content-between mt-4">
                  <div>
                    <button 
                      @click="clearAnswer(currentQuestionIndex)"
                      class="btn btn-outline-secondary me-2"
                      :disabled="!answers[currentQuestion.id]"
                    >
                      <i class="bi bi-eraser me-1"></i>Clear Answer
                    </button>
                    <button 
                      @click="toggleBookmark(currentQuestionIndex)"
                      class="btn btn-outline-warning"
                      :class="{ 'active': questionStates[currentQuestionIndex]?.bookmarked }"
                    >
                      <i class="bi" :class="questionStates[currentQuestionIndex]?.bookmarked ? 'bi-bookmark-fill' : 'bi-bookmark'"></i>
                      {{ questionStates[currentQuestionIndex]?.bookmarked ? 'Remove Bookmark' : 'Bookmark' }}
                    </button>
                  </div>
                  <div>
                    <button 
                      @click="previousQuestion"
                      class="btn btn-outline-primary me-2"
                      :disabled="currentQuestionIndex === 0"
                    >
                      <i class="bi bi-arrow-left me-1"></i>Previous
                    </button>
                    <button 
                      @click="nextQuestion"
                      class="btn btn-outline-primary"
                      :disabled="currentQuestionIndex === questions.length - 1"
                    >
                      Next<i class="bi bi-arrow-right ms-1"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="col-lg-3">
          <!-- Test Summary -->
          <div class="card mb-4 position-sticky" style="top: 100px;">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="bi bi-list-check me-2"></i>Test Summary
              </h6>
            </div>
            <div class="card-body">
              <div class="summary-stats">
                <div class="stat-item d-flex justify-content-between mb-2">
                  <span>Total Questions:</span>
                  <strong>{{ questions.length }}</strong>
                </div>
                <div class="stat-item d-flex justify-content-between mb-2">
                  <span>Answered:</span>
                  <strong class="text-success">{{ answeredCount }}</strong>
                </div>
                <div class="stat-item d-flex justify-content-between mb-2">
                  <span>Bookmarked:</span>
                  <strong class="text-warning">{{ bookmarkedCount }}</strong>
                </div>
                <div class="stat-item d-flex justify-content-between mb-3">
                  <span>Remaining:</span>
                  <strong class="text-danger">{{ questions.length - answeredCount }}</strong>
                </div>
                
                <!-- Progress Bar -->
                <div class="progress mb-3" style="height: 10px;">
                  <div 
                    class="progress-bar bg-success" 
                    :style="{ width: (answeredCount / questions.length * 100) + '%' }"
                  ></div>
                </div>
                
                <div class="text-center small text-muted">
                  {{ Math.round(answeredCount / questions.length * 100) }}% Completed
                </div>
              </div>

              <hr>

              <!-- Quick Actions -->
              <div class="d-grid gap-2">
                <button @click="reviewBookmarked" class="btn btn-outline-warning btn-sm">
                  <i class="bi bi-bookmark me-1"></i>Review Bookmarked
                </button>
                <button @click="reviewUnanswered" class="btn btn-outline-danger btn-sm">
                  <i class="bi bi-question-circle me-1"></i>Review Unanswered
                </button>
                <button @click="showSubmitModal" class="btn btn-success">
                  <i class="bi bi-check-circle me-1"></i>Submit Test
                </button>
              </div>
            </div>
          </div>

          <!-- Instructions -->
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="bi bi-info-circle me-2"></i>Instructions
              </h6>
            </div>
            <div class="card-body">
              <ul class="list-unstyled small">
                <li class="mb-2">
                  <i class="bi bi-check-circle text-success me-2"></i>
                  Click on question numbers to navigate
                </li>
                <li class="mb-2">
                  <i class="bi bi-bookmark text-warning me-2"></i>
                  Bookmark questions for later review
                </li>
                <li class="mb-2">
                  <i class="bi bi-clock text-info me-2"></i>
                  Keep an eye on the timer
                </li>
                <li class="mb-2">
                  <i class="bi bi-save text-primary me-2"></i>
                  Answers are saved automatically
                </li>
                <li class="mb-0">
                  <i class="bi bi-exclamation-triangle text-danger me-2"></i>
                  Submit before time runs out
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit Confirmation Modal -->
    <div class="modal fade" id="submitModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-warning text-dark">
            <h5 class="modal-title">
              <i class="bi bi-exclamation-triangle me-2"></i>Submit Test?
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info">
              <h6 class="alert-heading">Test Summary</h6>
              <div class="row">
                <div class="col-6">
                  <strong>Total Questions:</strong> {{ questions.length }}<br>
                  <strong>Answered:</strong> {{ answeredCount }}<br>
                  <strong>Bookmarked:</strong> {{ bookmarkedCount }}
                </div>
                <div class="col-6">
                  <strong>Time Remaining:</strong> {{ formatTime(timeRemaining) }}<br>
                  <strong>Unanswered:</strong> {{ questions.length - answeredCount }}
                </div>
              </div>
            </div>
            
            <div v-if="questions.length - answeredCount > 0" class="alert alert-warning">
              <i class="bi bi-exclamation-triangle me-2"></i>
              You have {{ questions.length - answeredCount }} unanswered questions. 
              Are you sure you want to submit?
            </div>
            
            <p class="mb-0">
              Once submitted, you cannot make any changes to your answers. 
              Click "Submit" to proceed or "Cancel" to continue the test.
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="bi bi-arrow-left me-1"></i>Cancel
            </button>
            <button @click="submitTest" class="btn btn-success" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <i v-else class="bi bi-check-circle me-1"></i>
              {{ submitting ? 'Submitting...' : 'Submit Test' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- End test content div -->
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'
import { Modal } from 'bootstrap'

export default {
  name: 'TestTaking',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // Reactive data
    const mockTest = ref(null)
    const attempt = ref(null)
    const questions = ref([])
    const answers = ref({})
    const questionStates = ref({})
    const currentQuestionIndex = ref(0)
    const timeRemaining = ref(0)
    const submitting = ref(false)
    
    // Timer
    let timer = null
    
    // Computed properties
    const currentQuestion = computed(() => {
      return questions.value[currentQuestionIndex.value]
    })
    
    const questionOptions = computed(() => {
      if (!currentQuestion.value) return []
      return [
        { key: 'A', text: currentQuestion.value.option_a },
        { key: 'B', text: currentQuestion.value.option_b },
        { key: 'C', text: currentQuestion.value.option_c },
        { key: 'D', text: currentQuestion.value.option_d }
      ]
    })
    
    const answeredCount = computed(() => {
      return Object.keys(answers.value).length
    })
    
    const bookmarkedCount = computed(() => {
      return Object.values(questionStates.value).filter(state => state?.bookmarked).length
    })
    
    const timeProgress = computed(() => {
      if (!attempt.value) return 0
      const totalTime = attempt.value.time_limit * 60 // Convert to seconds
      return Math.max(0, (timeRemaining.value / totalTime) * 100)
    })

    // Methods
    const loadAttempt = async () => {
      console.log('🔍 TestTaking: loadAttempt started')
      const testId = route.params.testId
      const attemptId = route.params.attemptId
      
      console.log('🔍 TestTaking: Route params:', { testId, attemptId })
      
      // Add timeout to prevent hanging
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 30000) // 30 second timeout
      })
      
      try {
        console.log('🔍 TestTaking: Loading test details...')
        // Get test details first
        const testResult = await Promise.race([
          api.ugcNet.getMockTestDetails(testId),
          timeoutPromise
        ])
        console.log('🔍 TestTaking: Test details result:', testResult)
        if (testResult.success) {
          mockTest.value = testResult.data
          console.log('🔍 TestTaking: Mock test loaded:', mockTest.value)
        } else {
          console.error('❌ TestTaking: Failed to load test details:', testResult.error)
          alert('Failed to load test details')
          router.push('/ugc-net')
          return
        }
        
        console.log('🔍 TestTaking: Starting/resuming attempt...')
        // Start or resume attempt
        const attemptResult = await Promise.race([
          api.ugcNet.startAttempt(testId),
          timeoutPromise
        ])
        console.log('🔍 TestTaking: Attempt result:', attemptResult)
        if (attemptResult.success) {
          attempt.value = attemptResult.data.attempt
          questions.value = attemptResult.data.attempt.questions || []
          console.log('🔍 TestTaking: Questions loaded:', questions.value.length)
          
          // If the attempt is already completed, redirect to results
          if (attempt.value.status === 'completed') {
            console.log('🔍 TestTaking: Attempt already completed, redirecting to results...')
            router.push(`/ugc-net/test/${route.params.testId}/attempt/${route.params.attemptId}/results`)
            return
          }
          
          console.log('🔍 TestTaking: Initializing question states...')
          // Initialize question states
          questions.value.forEach((_, index) => {
            questionStates.value[index] = {
              visited: index === 0,
              bookmarked: false
            }
          })
          console.log('🔍 TestTaking: Question states initialized:', Object.keys(questionStates.value).length)
          
          console.log('🔍 TestTaking: Calculating time remaining...')
          // Calculate time remaining
          // Backend now returns UTC timestamps with 'Z' suffix
          const startTime = new Date(attempt.value.start_time)
          const timeLimit = attempt.value.time_limit * 60 * 1000 // Convert to milliseconds
          const elapsed = Date.now() - startTime.getTime()
          timeRemaining.value = Math.max(0, Math.floor((timeLimit - elapsed) / 1000))
          
          // Debug logging
          console.log('🔍 TestTaking: Time calculation debug:')
          console.log('  - Raw start time:', attempt.value.start_time)
          console.log('  - Start time (parsed):', startTime)
          console.log('  - Start time UTC:', startTime.toISOString())
          console.log('  - Current time:', new Date())
          console.log('  - Current time UTC:', new Date().toISOString())
          console.log('  - Time limit (minutes):', attempt.value.time_limit)
          console.log('  - Time limit (ms):', timeLimit)
          console.log('  - Elapsed (ms):', elapsed)
          console.log('  - Time remaining (seconds):', timeRemaining.value)
          
          // If time has expired, auto-submit the test instead of redirecting to results
          if (timeRemaining.value <= 0) {
            console.log('⚠️ TestTaking: Time has expired, auto-submitting test...')
            timeRemaining.value = 0
            submitTest(true) // Auto-submit due to time expiry
            return
          }
          
          console.log('🔍 TestTaking: Starting timer...')
          // Start timer
          startTimer()
          console.log('🔍 TestTaking: loadAttempt completed successfully')
        } else {
          console.error('❌ TestTaking: Failed to start attempt:', attemptResult.error)
          alert('Failed to start test attempt')
          router.push('/ugc-net')
        }
      } catch (error) {
        console.error('❌ TestTaking: Exception in loadAttempt:', error)
        alert('Failed to load test. Redirecting to dashboard.')
        router.push('/ugc-net')
      }
    }

    const startTimer = () => {
      timer = setInterval(() => {
        // Check if timer still exists (component not unmounted)
        if (!timer) return
        
        if (timeRemaining.value > 0) {
          timeRemaining.value--
        } else {
          // Time's up - auto submit
          clearInterval(timer)
          timer = null
          submitTest(true)
        }
      }, 1000)
    }

    const formatTime = (seconds) => {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      
      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
      } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`
      }
    }

    const goToQuestion = (index) => {
      currentQuestionIndex.value = index
      questionStates.value[index] = {
        ...questionStates.value[index],
        visited: true
      }
    }

    const nextQuestion = () => {
      if (currentQuestionIndex.value < questions.value.length - 1) {
        goToQuestion(currentQuestionIndex.value + 1)
      }
    }

    const previousQuestion = () => {
      if (currentQuestionIndex.value > 0) {
        goToQuestion(currentQuestionIndex.value - 1)
      }
    }

    const updateQuestionState = (index) => {
      questionStates.value[index] = {
        ...questionStates.value[index],
        answered: true
      }
    }

    const clearAnswer = (index) => {
      const question = questions.value[index]
      if (question) {
        delete answers.value[question.id]
        questionStates.value[index] = {
          ...questionStates.value[index],
          answered: false
        }
      }
    }

    const toggleBookmark = (index) => {
      questionStates.value[index] = {
        ...questionStates.value[index],
        bookmarked: !questionStates.value[index]?.bookmarked
      }
    }

    const getQuestionNavClass = (index) => {
      const state = questionStates.value[index] || {}
      const isAnswered = answers.value[questions.value[index]?.id]
      
      if (index === currentQuestionIndex.value) return 'btn-primary'
      if (isAnswered) return 'btn-success'
      if (state.bookmarked) return 'btn-warning'
      if (state.visited) return 'btn-outline-secondary'
      return 'btn-outline-light text-dark'
    }

    const reviewBookmarked = () => {
      const bookmarkedIndexes = Object.entries(questionStates.value)
        .filter(([_, state]) => state?.bookmarked)
        .map(([index, _]) => parseInt(index))
      
      if (bookmarkedIndexes.length > 0) {
        goToQuestion(bookmarkedIndexes[0])
      }
    }

    const reviewUnanswered = () => {
      const unansweredIndex = questions.value.findIndex((question, index) => {
        return !answers.value[question.id]
      })
      
      if (unansweredIndex !== -1) {
        goToQuestion(unansweredIndex)
      }
    }

    const showSubmitModal = () => {
      const modal = new Modal(document.getElementById('submitModal'))
      modal.show()
    }

    const submitTest = async (autoSubmit = false) => {
      if (!autoSubmit) {
        const modal = Modal.getInstance(document.getElementById('submitModal'))
        if (modal) modal.hide()
      }
      
      submitting.value = true
      
      try {
        const testId = route.params.testId
        const attemptId = route.params.attemptId
        
        console.log('🔄 Submitting test:', {
          testId,
          attemptId,
          answers: answers.value,
          routeParams: route.params
        })
        
        // Validate required parameters
        if (!testId) {
          throw new Error('Test ID is missing from route parameters')
        }
        if (!attemptId) {
          throw new Error('Attempt ID is missing from route parameters')
        }
        
        // Clear timer
        if (timer) {
          clearInterval(timer)
          timer = null
        }
        
        const result = await api.ugcNet.submitAttempt(testId, attemptId, answers.value)
        
        console.log('📤 Submit result:', result)
        
        if (result.success) {
          // Redirect to results - include both testId and attemptId
          router.push(`/ugc-net/results/${testId}/${attemptId}`)
        } else {
          console.error('Submit failed:', result.error)
          alert('Failed to submit test: ' + (result.error || 'Unknown error'))
          submitting.value = false
        }
      } catch (error) {
        console.error('Failed to submit test:', error)
        console.error('Error details:', {
          message: error.message,
          response: error.response?.data,
          stack: error.stack
        })
        alert('Failed to submit test: ' + (error.message || 'Unknown error'))
        submitting.value = false
      }
    }

    // Lifecycle
    onMounted(() => {
      // Load the attempt data
      loadAttempt()
      
      // Prevent page refresh/close without warning
      const handleBeforeUnload = (e) => {
        e.preventDefault()
        e.returnValue = ''
      }
      
      window.addEventListener('beforeunload', handleBeforeUnload)
      
      // Cleanup function for unmount
      return () => {
        window.removeEventListener('beforeunload', handleBeforeUnload)
      }
    })

    onUnmounted(() => {
      // Clear timer
      if (timer) {
        clearInterval(timer)
        timer = null
      }
      
      // Remove beforeunload listener
      window.removeEventListener('beforeunload', () => {})
    })

    onBeforeUnmount(() => {
      // Clear timer
      if (timer) {
        clearInterval(timer)
        timer = null
      }
    })

    return {
      mockTest,
      attempt,
      questions,
      answers,
      questionStates,
      currentQuestionIndex,
      timeRemaining,
      submitting,
      currentQuestion,
      questionOptions,
      answeredCount,
      bookmarkedCount,
      timeProgress,
      formatTime,
      goToQuestion,
      nextQuestion,
      previousQuestion,
      updateQuestionState,
      clearAnswer,
      toggleBookmark,
      getQuestionNavClass,
      reviewBookmarked,
      reviewUnanswered,
      showSubmitModal,
      submitTest
    }
  }
}
</script>

<style scoped>
.test-taking-container {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.test-header {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.timer-display {
  text-align: center;
}

.time-remaining {
  font-size: 1.1rem;
  font-weight: bold;
}

.question-progress {
  text-align: right;
}

.question-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.question-nav-btn {
  width: 50px;
  height: 50px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
}

.question-nav-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.question-text {
  font-size: 1.1rem;
  line-height: 1.6;
}

.option-label {
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 0;
}

.option-label:hover {
  background-color: #f8f9fa;
  border-color: #0d6efd !important;
}

.form-check-input:checked + .option-label {
  background-color: #e7f3ff;
  border-color: #0d6efd !important;
}

.summary-stats {
  font-size: 0.9rem;
}

.legend .badge {
  font-size: 0.7rem;
}

@media (max-width: 768px) {
  .test-header .row {
    text-align: center;
  }
  
  .question-grid {
    grid-template-columns: repeat(auto-fill, minmax(45px, 1fr));
  }
  
  .question-nav-btn {
    width: 45px;
    height: 45px;
  }
}
</style>
