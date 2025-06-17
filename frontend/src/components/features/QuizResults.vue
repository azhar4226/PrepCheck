<template>
  <div class="quiz-results">
    <!-- Results Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card text-center" :class="headerCardClass">
          <div class="card-body py-5">
            <div class="display-1 mb-3">
              <i :class="resultIcon"></i>
            </div>
            <h1 class="display-4 fw-bold mb-3">{{ resultTitle }}</h1>
            <p class="lead mb-4">{{ resultMessage }}</p>
            
            <div class="row justify-content-center">
              <div class="col-auto">
                <div class="d-flex align-items-center gap-4">
                  <div class="text-center">
                    <div class="display-6 fw-bold">{{ results.score || 0 }}</div>
                    <small>Score</small>
                  </div>
                  <div class="text-center">
                    <div class="display-6 fw-bold">{{ results.total_marks || 0 }}</div>
                    <small>Total</small>
                  </div>
                  <div class="text-center">
                    <div class="display-6 fw-bold">{{ results.percentage || 0 }}%</div>
                    <small>Percentage</small>
                  </div>
                  <div class="text-center">
                    <div class="display-6 fw-bold">{{ formatTime(results.time_taken || 0) }}</div>
                    <small>Time Taken</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Breakdown -->
    <div class="row mb-4">
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-graph-up me-2"></i>Performance Breakdown
            </h5>
          </div>
          <div class="card-body">
            <div class="row mb-4">
              <div class="col-md-6">
                <div class="progress-item mb-3">
                  <div class="d-flex justify-content-between mb-1">
                    <span>Correct Answers</span>
                    <span>{{ results.correct_answers }}/{{ results.total_questions }}</span>
                  </div>
                  <div class="progress">
                    <div 
                      class="progress-bar bg-success" 
                      :style="{ width: (results.correct_answers / results.total_questions) * 100 + '%' }"
                    ></div>
                  </div>
                </div>
                
                <div class="progress-item mb-3">
                  <div class="d-flex justify-content-between mb-1">
                    <span>Incorrect Answers</span>
                    <span>{{ results.incorrect_answers }}/{{ results.total_questions }}</span>
                  </div>
                  <div class="progress">
                    <div 
                      class="progress-bar bg-danger" 
                      :style="{ width: (results.incorrect_answers / results.total_questions) * 100 + '%' }"
                    ></div>
                  </div>
                </div>
                
                <div class="progress-item">
                  <div class="d-flex justify-content-between mb-1">
                    <span>Unanswered</span>
                    <span>{{ results.unanswered }}/{{ results.total_questions }}</span>
                  </div>
                  <div class="progress">
                    <div 
                      class="progress-bar bg-warning" 
                      :style="{ width: (results.unanswered / results.total_questions) * 100 + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="stats-grid">
                  <div class="stat-item">
                    <div class="stat-value text-success">{{ results.correct_answers }}</div>
                    <div class="stat-label">Correct</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value text-danger">{{ results.incorrect_answers }}</div>
                    <div class="stat-label">Incorrect</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value text-warning">{{ results.unanswered }}</div>
                    <div class="stat-label">Skipped</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value text-info">{{ results.accuracy }}%</div>
                    <div class="stat-label">Accuracy</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Actions Panel -->
      <div class="col-lg-4">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-gear me-2"></i>What's Next?
            </h5>
          </div>
          <div class="card-body">
            <div class="d-grid gap-2">
              <button class="btn btn-primary" @click="$emit('retake-quiz')">
                <i class="bi bi-arrow-repeat me-2"></i>Retake Quiz
              </button>
              
              <button class="btn btn-outline-secondary" @click="$emit('view-quizzes')">
                <i class="bi bi-collection me-2"></i>Browse More Quizzes
              </button>
              
              <button class="btn btn-outline-info" @click="shareResults">
                <i class="bi bi-share me-2"></i>Share Results
              </button>
              
              <button class="btn btn-outline-success" @click="downloadCertificate" v-if="results.percentage >= 80">
                <i class="bi bi-award me-2"></i>Download Certificate
              </button>
            </div>
            
            <!-- Improvement Tips -->
            <div class="mt-4" v-if="improvementTips.length > 0">
              <h6 class="text-muted">💡 Tips for Improvement:</h6>
              <ul class="list-unstyled small">
                <li v-for="tip in improvementTips" :key="tip" class="mb-1">
                  <i class="bi bi-lightbulb text-warning me-1"></i>{{ tip }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Question Review -->
    <div class="row" v-if="results.question_details">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-list-check me-2"></i>Question Review
            </h5>
            <button class="btn btn-sm btn-outline-primary" @click="showReview = !showReview">
              {{ showReview ? 'Hide' : 'Show' }} Review
            </button>
          </div>
          
          <div v-show="showReview" class="card-body">
            <div class="accordion" id="questionAccordion">
              <div 
                v-for="(question, index) in results.question_details" 
                :key="question.id"
                class="accordion-item"
              >
                <h2 class="accordion-header">
                  <button 
                    class="accordion-button collapsed d-flex align-items-center" 
                    type="button" 
                    :data-bs-target="'#question-' + question.id"
                    data-bs-toggle="collapse"
                  >
                    <span class="me-3">
                      <i 
                        :class="getQuestionIcon(question.is_correct)" 
                        :style="{ color: getQuestionColor(question.is_correct) }"
                      ></i>
                    </span>
                    <span class="flex-grow-1">
                      Question {{ index + 1 }}: {{ truncateText(question.question_text, 80) }}
                    </span>
                    <span class="badge ms-2" :class="getQuestionBadgeClass(question.is_correct)">
                      {{ getQuestionStatusText(question.is_correct, question.user_answer) }}
                    </span>
                  </button>
                </h2>
                <div 
                  :id="'question-' + question.id" 
                  class="accordion-collapse collapse"
                  data-bs-parent="#questionAccordion"
                >
                  <div class="accordion-body">
                    <div class="row">
                      <div class="col-md-8">
                        <p class="fw-semibold">{{ question.question_text }}</p>
                        
                        <div class="mt-3">
                          <div class="mb-2">
                            <strong class="text-success">Correct Answer:</strong>
                            <span class="ms-2">{{ question.correct_answer }}</span>
                          </div>
                          
                          <div class="mb-2" v-if="question.user_answer">
                            <strong class="text-primary">Your Answer:</strong>
                            <span class="ms-2" :class="{ 'text-success': question.is_correct, 'text-danger': !question.is_correct }">
                              {{ question.user_answer }}
                            </span>
                          </div>
                          
                          <div v-else class="mb-2">
                            <strong class="text-warning">Your Answer:</strong>
                            <span class="ms-2 text-muted">Not answered</span>
                          </div>
                        </div>
                        
                        <div v-if="question.explanation" class="mt-3 p-3 bg-light rounded">
                          <h6 class="text-muted mb-2">
                            <i class="bi bi-info-circle me-1"></i>Explanation:
                          </h6>
                          <p class="mb-0">{{ question.explanation }}</p>
                        </div>
                      </div>
                      
                      <div class="col-md-4">
                        <div class="question-stats">
                          <div class="stat-box text-center p-3 border rounded">
                            <div class="h4 mb-1" :class="{ 'text-success': question.is_correct, 'text-danger': !question.is_correct }">
                              {{ question.points_earned }}/{{ question.points_possible }}
                            </div>
                            <div class="small text-muted">Points</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { formatTime } from '@/services/utils'

export default {
  name: 'QuizResults',
  props: {
    results: {
      type: Object,
      required: true,
      validator(value) {
        // Validate that the results object has required fields
        const requiredFields = ['score', 'total_marks', 'percentage', 'correct_answers', 'incorrect_answers', 'total_questions'];
        const hasRequiredFields = requiredFields.every(field => 
          value && typeof value[field] !== 'undefined' && value[field] !== null
        );
        
        if (!hasRequiredFields) {
          console.error('QuizResults component received invalid props:', value);
          console.error('Missing required fields:', requiredFields.filter(field => !value || typeof value[field] === 'undefined'));
        }
        
        return hasRequiredFields;
      }
    }
  },
  emits: ['retake-quiz', 'view-quizzes'],
  setup(props) {
    const showReview = ref(false)
    
    const headerCardClass = computed(() => {
      const percentage = props.results?.percentage || 0
      if (percentage >= 90) return 'border-success'
      if (percentage >= 80) return 'border-info'
      if (percentage >= 70) return 'border-warning'
      return 'border-danger'
    })
    
    const resultIcon = computed(() => {
      const percentage = props.results?.percentage || 0
      if (percentage >= 90) return 'bi bi-trophy-fill text-warning'
      if (percentage >= 80) return 'bi bi-award-fill text-info'
      if (percentage >= 70) return 'bi bi-check-circle-fill text-success'
      return 'bi bi-x-circle-fill text-danger'
    })
    
    const resultTitle = computed(() => {
      const percentage = props.results?.percentage || 0
      if (percentage >= 90) return 'Outstanding!'
      if (percentage >= 80) return 'Great Job!'
      if (percentage >= 70) return 'Good Work!'
      return 'Keep Practicing!'
    })
    
    const resultMessage = computed(() => {
      const percentage = props.results?.percentage || 0
      if (percentage >= 90) return 'Excellent performance! You\'ve mastered this topic.'
      if (percentage >= 80) return 'Very good! You have a solid understanding.'
      if (percentage >= 70) return 'Not bad! A little more practice will help.'
      return 'Don\'t give up! Review the material and try again.'
    })
    
    const improvementTips = computed(() => {
      const tips = []
      const percentage = props.results?.percentage || 0
      
      if (percentage < 70) {
        tips.push('Review the fundamental concepts')
        tips.push('Take your time reading each question')
        tips.push('Practice more quizzes on this topic')
      } else if (percentage < 80) {
        tips.push('Focus on areas where you made mistakes')
        tips.push('Review explanations for incorrect answers')
      } else if (percentage < 90) {
        tips.push('Pay attention to details in questions')
        tips.push('Double-check your answers before submitting')
      }
      
      if ((props.results?.unanswered || 0) > 0) {
        tips.push('Try to answer all questions next time')
      }
      
      return tips
    })
    
    const getQuestionIcon = (isCorrect) => {
      if (isCorrect === null) return 'bi bi-dash-circle'
      return isCorrect ? 'bi bi-check-circle-fill' : 'bi bi-x-circle-fill'
    }
    
    const getQuestionColor = (isCorrect) => {
      if (isCorrect === null) return '#6c757d'
      return isCorrect ? '#198754' : '#dc3545'
    }
    
    const getQuestionBadgeClass = (isCorrect) => {
      if (isCorrect === null) return 'bg-warning'
      return isCorrect ? 'bg-success' : 'bg-danger'
    }
    
    const getQuestionStatusText = (isCorrect, userAnswer) => {
      if (!userAnswer) return 'Skipped'
      return isCorrect ? 'Correct' : 'Incorrect'
    }
    
    const truncateText = (text, length) => {
      if (text.length <= length) return text
      return text.substring(0, length) + '...'
    }
    
    const shareResults = () => {
      const text = `I just scored ${props.results?.percentage || 0}% on a PrepCheck quiz! 🎯`
      if (navigator.share) {
        navigator.share({
          title: 'My Quiz Results',
          text: text,
          url: window.location.href
        })
      } else {
        navigator.clipboard.writeText(text)
        alert('Results copied to clipboard!')
      }
    }
    
    const downloadCertificate = () => {
      // This would generate and download a certificate
      alert('Certificate download feature coming soon!')
    }
    
    return {
      showReview,
      headerCardClass,
      resultIcon,
      resultTitle,
      resultMessage,
      improvementTips,
      getQuestionIcon,
      getQuestionColor,
      getQuestionBadgeClass,
      getQuestionStatusText,
      truncateText,
      shareResults,
      downloadCertificate,
      formatTime
    }
  }
}
</script>

<style scoped>
.quiz-results {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  background-color: #f8f9fa;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6c757d;
}

.progress-item .progress {
  height: 8px;
}

.accordion-button {
  background-color: #f8f9fa;
}

.accordion-button:not(.collapsed) {
  background-color: #e3f2fd;
  border-color: #b3e5fc;
}

.question-stats .stat-box {
  background-color: #f8f9fa;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .d-flex.align-items-center.gap-4 {
    flex-direction: column;
    gap: 1rem !important;
  }
}
</style>