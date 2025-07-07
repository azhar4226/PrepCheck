<template>
  <div class="practice-test-container">
    <!-- Test Header -->
    <div class="test-header" v-if="practiceTest">
      <div class="test-info">
        <h2>{{ practiceTest.title }}</h2>
        <div class="test-meta">
          <span class="subject">{{ practiceTest.subject_name }}</span>
          <span class="separator">•</span>
          <span class="paper-type">{{ practiceTest.paper_type.toUpperCase() }}</span>
          <span class="separator">•</span>
          <span class="questions-count">{{ practiceTest.total_questions }} Questions</span>
        </div>
      </div>
      
      <div class="test-timer" v-if="timeRemaining > 0">
        <div class="timer-display" :class="{ 'warning': timeRemaining < 300 }">
          <i class="fas fa-clock"></i>
          <span class="time">{{ formatTime(timeRemaining) }}</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading practice test...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-container">
      <div class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Error Loading Practice Test</h3>
        <p>{{ error }}</p>
        <button @click="$router.go(-1)" class="btn btn-primary">Go Back</button>
      </div>
    </div>

    <!-- Practice Test Content -->
    <div v-if="practiceTest && !loading && !error" class="test-content">
      <!-- Progress Bar -->
      <div class="progress-container">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: progressPercentage + '%' }"
          ></div>
        </div>
        <span class="progress-text">
          Question {{ currentQuestionIndex + 1 }} of {{ practiceTest.total_questions }}
        </span>
      </div>

      <!-- Question Display -->
      <div class="question-container" v-if="currentQuestion">
        <div class="question-header">
          <span class="question-number">Q{{ currentQuestionIndex + 1 }}</span>
          <span class="question-difficulty" :class="currentQuestion.difficulty">
            {{ currentQuestion.difficulty.toUpperCase() }}
          </span>
          <span class="question-marks">{{ currentQuestion.marks }} mark(s)</span>
        </div>
        
        <div class="question-text" v-html="currentQuestion.question_text"></div>
        
        <div class="options-container">
          <div 
            v-for="option in ['A', 'B', 'C', 'D']" 
            :key="option"
            class="option"
            :class="{ 'selected': answers[currentQuestion.id] === option }"
            @click="selectAnswer(option)"
          >
            <div class="option-marker">{{ option }}</div>
            <div class="option-text" v-html="currentQuestion[`option_${option.toLowerCase()}`]"></div>
          </div>
        </div>
      </div>

      <!-- Navigation Controls -->
      <div class="navigation-container">
        <div class="nav-buttons">
          <button 
            @click="previousQuestion" 
            :disabled="currentQuestionIndex === 0"
            class="btn btn-secondary"
          >
            <i class="fas fa-chevron-left"></i>
            Previous
          </button>
          
          <button 
            @click="nextQuestion" 
            :disabled="currentQuestionIndex === practiceTest.total_questions - 1"
            class="btn btn-secondary"
          >
            Next
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
        
        <div class="action-buttons">
          <button 
            @click="showQuestionPalette = !showQuestionPalette"
            class="btn btn-outline-primary"
          >
            <i class="fas fa-th"></i>
            Questions
          </button>
          
          <button 
            @click="submitTest"
            class="btn btn-success"
            :disabled="submitting"
          >
            <i class="fas fa-check" v-if="!submitting"></i>
            <i class="fas fa-spinner fa-spin" v-else></i>
            {{ submitting ? 'Submitting...' : 'Submit Test' }}
          </button>
        </div>
      </div>

      <!-- Question Palette -->
      <div v-if="showQuestionPalette" class="question-palette-overlay" @click="showQuestionPalette = false">
        <div class="question-palette" @click.stop>
          <div class="palette-header">
            <h3>Questions Overview</h3>
            <button @click="showQuestionPalette = false" class="close-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="palette-grid">
            <div 
              v-for="(question, index) in practiceTest.questions" 
              :key="question.id"
              class="palette-item"
              :class="{ 
                'current': index === currentQuestionIndex,
                'answered': answers[question.id],
                'unanswered': !answers[question.id]
              }"
              @click="goToQuestion(index)"
            >
              {{ index + 1 }}
            </div>
          </div>
          
          <div class="palette-legend">
            <div class="legend-item">
              <div class="legend-color current"></div>
              <span>Current</span>
            </div>
            <div class="legend-item">
              <div class="legend-color answered"></div>
              <span>Answered</span>
            </div>
            <div class="legend-item">
              <div class="legend-color unanswered"></div>
              <span>Unanswered</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit Confirmation Modal -->
    <div v-if="showSubmitModal" class="modal-overlay" @click="showSubmitModal = false">
      <div class="modal-content" @click.stop>
        <h3>Submit Practice Test?</h3>
        <div class="submit-summary">
          <p>You have answered <strong>{{ answeredCount }}</strong> out of <strong>{{ practiceTest.total_questions }}</strong> questions.</p>
          <p v-if="unansweredCount > 0" class="warning">
            <i class="fas fa-exclamation-triangle"></i>
            {{ unansweredCount }} questions remain unanswered.
          </p>
          <p>Are you sure you want to submit the test?</p>
        </div>
        
        <div class="modal-actions">
          <button @click="showSubmitModal = false" class="btn btn-secondary">Cancel</button>
          <button @click="confirmSubmit" class="btn btn-success" :disabled="submitting">
            <i class="fas fa-check" v-if="!submitting"></i>
            <i class="fas fa-spinner fa-spin" v-else></i>
            {{ submitting ? 'Submitting...' : 'Submit Test' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ugcNetService from '@/services/ugcNetService'

export default {
  name: 'PracticeTest',
  data() {
    return {
      practiceTest: null,
      currentQuestionIndex: 0,
      answers: {},
      timeRemaining: 0,
      timer: null,
      loading: true,
      error: null,
      submitting: false,
      showQuestionPalette: false,
      showSubmitModal: false,
      startTime: null
    }
  },
  
  computed: {
    currentQuestion() {
      if (!this.practiceTest || !this.practiceTest.questions) return null
      return this.practiceTest.questions[this.currentQuestionIndex]
    },
    
    progressPercentage() {
      if (!this.practiceTest) return 0
      return ((this.currentQuestionIndex + 1) / this.practiceTest.total_questions) * 100
    },
    
    answeredCount() {
      return Object.keys(this.answers).length
    },
    
    unansweredCount() {
      if (!this.practiceTest) return 0
      return this.practiceTest.total_questions - this.answeredCount
    }
  },
  
  async mounted() {
    await this.loadPracticeTest()
    this.startTimer()
  },
  
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  
  methods: {
    async loadPracticeTest() {
      try {
        this.loading = true
        const attemptId = this.$route.params.attemptId
        
        const response = await ugcNetService.getPracticeTest(attemptId)
        if (response.success) {
          this.practiceTest = response.data
          this.timeRemaining = this.practiceTest.time_limit * 60 // Convert minutes to seconds
          this.startTime = new Date()
          
          // Load existing answers if any
          if (this.practiceTest.answers) {
            this.answers = { ...this.practiceTest.answers }
          }
        } else {
          this.error = response.error || 'Failed to load practice test'
        }
      } catch (error) {
        console.error('Error loading practice test:', error)
        this.error = 'Network error occurred while loading the test'
      } finally {
        this.loading = false
      }
    },
    
    startTimer() {
      this.timer = setInterval(() => {
        if (this.timeRemaining > 0) {
          this.timeRemaining--
        } else {
          this.autoSubmit()
        }
      }, 1000)
    },
    
    formatTime(seconds) {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const remainingSeconds = seconds % 60
      
      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
      }
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    },
    
    selectAnswer(option) {
      if (this.currentQuestion) {
        this.$set(this.answers, this.currentQuestion.id, option)
        
        // Auto-save answers periodically
        this.saveAnswers()
      }
    },
    
    async saveAnswers() {
      try {
        await ugcNetService.savePracticeAnswers(this.practiceTest.id, this.answers)
      } catch (error) {
        console.error('Error saving answers:', error)
      }
    },
    
    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
      }
    },
    
    nextQuestion() {
      if (this.currentQuestionIndex < this.practiceTest.total_questions - 1) {
        this.currentQuestionIndex++
      }
    },
    
    goToQuestion(index) {
      this.currentQuestionIndex = index
      this.showQuestionPalette = false
    },
    
    submitTest() {
      this.showSubmitModal = true
    },
    
    async confirmSubmit() {
      try {
        this.submitting = true
        
        const endTime = new Date()
        const timeTaken = Math.floor((endTime - this.startTime) / 1000)
        
        const response = await ugcNetService.submitPracticeTest(this.practiceTest.id, {
          answers: this.answers,
          time_taken: timeTaken
        })
        
        if (response.success) {
          // Navigate to results page
          this.$router.push({
            name: 'PracticeResults',
            params: { attemptId: this.practiceTest.id }
          })
        } else {
          this.$toast.error(response.error || 'Failed to submit test')
        }
      } catch (error) {
        console.error('Error submitting test:', error)
        this.$toast.error('Network error occurred while submitting')
      } finally {
        this.submitting = false
        this.showSubmitModal = false
      }
    },
    
    async autoSubmit() {
      if (this.timer) {
        clearInterval(this.timer)
      }
      
      this.$toast.warning('Time is up! Auto-submitting test...')
      await this.confirmSubmit()
    }
  }
}
</script>

<style scoped>
.practice-test-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.test-info h2 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.test-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7f8c8d;
  font-size: 14px;
}

.separator {
  color: #bdc3c7;
}

.test-timer .timer-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #ecf0f1;
  border-radius: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.timer-display.warning {
  background: #f39c12;
  color: white;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #ecf0f1;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.error-message i {
  font-size: 48px;
  color: #e74c3c;
  margin-bottom: 20px;
}

.test-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow: hidden;
}

.progress-container {
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #ecf0f1;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: #7f8c8d;
}

.question-container {
  padding: 30px;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.question-number {
  background: #3498db;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: 600;
}

.question-difficulty {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.question-difficulty.easy {
  background: #d5f4e6;
  color: #27ae60;
}

.question-difficulty.medium {
  background: #fef9e7;
  color: #f39c12;
}

.question-difficulty.hard {
  background: #fadbd8;
  color: #e74c3c;
}

.question-marks {
  color: #7f8c8d;
  font-size: 14px;
}

.question-text {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 25px;
  color: #2c3e50;
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 15px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.option:hover {
  border-color: #bdc3c7;
  background: #f8f9fa;
}

.option.selected {
  border-color: #3498db;
  background: #ebf3fd;
}

.option-marker {
  min-width: 24px;
  height: 24px;
  background: #ecf0f1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #7f8c8d;
  margin-top: 2px;
}

.option.selected .option-marker {
  background: #3498db;
  color: white;
}

.option-text {
  flex: 1;
  line-height: 1.5;
  color: #2c3e50;
}

.navigation-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-top: 1px solid #ecf0f1;
  background: #f8f9fa;
}

.nav-buttons, .action-buttons {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

.btn-outline-primary {
  background: transparent;
  color: #3498db;
  border: 2px solid #3498db;
}

.btn-outline-primary:hover {
  background: #3498db;
  color: white;
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #229954;
}

.question-palette-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.question-palette {
  background: white;
  border-radius: 12px;
  padding: 30px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.palette-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.palette-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #7f8c8d;
  padding: 5px;
}

.palette-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.palette-item {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.palette-item.current {
  background: #3498db;
  color: white;
}

.palette-item.answered {
  background: #27ae60;
  color: white;
}

.palette-item.unanswered {
  background: #ecf0f1;
  color: #7f8c8d;
}

.palette-item:hover {
  transform: scale(1.1);
}

.palette-legend {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.legend-color.current {
  background: #3498db;
}

.legend-color.answered {
  background: #27ae60;
}

.legend-color.unanswered {
  background: #ecf0f1;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
}

.modal-content h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
}

.submit-summary {
  margin-bottom: 25px;
}

.submit-summary p {
  margin: 10px 0;
  line-height: 1.5;
}

.submit-summary .warning {
  color: #f39c12;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .practice-test-container {
    padding: 10px;
  }
  
  .test-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .navigation-container {
    flex-direction: column;
    gap: 15px;
  }
  
  .nav-buttons, .action-buttons {
    width: 100%;
    justify-content: center;
  }
  
  .question-container {
    padding: 20px;
  }
  
  .palette-grid {
    grid-template-columns: repeat(auto-fill, minmax(35px, 1fr));
  }
  
  .palette-item {
    width: 35px;
    height: 35px;
  }
}
</style>
