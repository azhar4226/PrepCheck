<template>
  <!-- Main Content -->
  <div class="test-results" v-if="!loading && !error && results">
    <div class="container-fluid">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card bg-success text-white">
            <div class="card-body text-center">
              <h1>TEST RESULTS</h1>
              <h2>Score: {{ results.percentage }}%</h2>
              <p>{{ results.correct_answers }} / {{ results.total_questions }} correct</p>
              <p>Test: {{ mockTest ? mockTest.title : 'Loading...' }}</p>
              <p>Status: {{ results.qualification_status }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions Section -->
      <div class="row">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-header">
              <h5>Performance Analysis</h5>
            </div>
            <div class="card-body">
              <!-- Overall Performance Summary -->
              <div class="row mb-4">
                <div class="col-md-3 text-center">
                  <div class="card bg-primary bg-opacity-10">
                    <div class="card-body">
                      <h4 class="text-primary">{{ results.percentage }}%</h4>
                      <p class="mb-0">Overall Score</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-3 text-center">
                  <div class="card bg-success bg-opacity-10">
                    <div class="card-body">
                      <h4 class="text-success">{{ results.correct_answers }}</h4>
                      <p class="mb-0">Correct</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-3 text-center">
                  <div class="card bg-danger bg-opacity-10">
                    <div class="card-body">
                      <h4 class="text-danger">{{ results.total_questions - results.correct_answers }}</h4>
                      <p class="mb-0">Wrong</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-3 text-center">
                  <div class="card bg-info bg-opacity-10">
                    <div class="card-body">
                      <h4 class="text-info">{{ formatTime(results.time_taken || 0) }}</h4>
                      <p class="mb-0">Time Taken</p>
                      <small class="text-muted">out of {{ formatTimeLimit(results.time_limit) }}</small>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Chapter-wise Performance -->
              <div class="mt-3" v-if="results.chapter_wise_performance && Object.keys(results.chapter_wise_performance).length > 0">
                <h6>Chapter-wise Performance:</h6>
                <div v-for="(performance, chapter) in results.chapter_wise_performance" :key="chapter" class="mb-3">
                  <div class="d-flex justify-content-between mb-1">
                    <span class="fw-medium">{{ chapter }}</span>
                    <span class="badge bg-primary">
                      {{ Math.round((performance.correct || 0) / (performance.total || 1) * 100) }}% 
                      ({{ performance.correct }}/{{ performance.total }})
                    </span>
                  </div>
                  <div class="progress" style="height: 8px;">
                    <div 
                      class="progress-bar" 
                      :class="getProgressBarClass(Math.round((performance.correct || 0) / (performance.total || 1) * 100))"
                      :style="`width: ${Math.round((performance.correct || 0) / (performance.total || 1) * 100)}%`"
                    ></div>
                  </div>
                </div>
              </div>
              
              <!-- Strengths and Weaknesses -->
              <div class="row mt-4" v-if="results.strengths || results.weaknesses">
                <div class="col-md-6" v-if="results.strengths && results.strengths.length > 0">
                  <h6 class="text-success">
                    <i class="bi bi-check-circle me-1"></i>Strengths
                  </h6>
                  <ul class="list-unstyled">
                    <li v-for="strength in results.strengths" :key="strength" class="text-success small">
                      <i class="bi bi-arrow-right me-1"></i>{{ strength }}
                    </li>
                  </ul>
                </div>
                <div class="col-md-6" v-if="results.weaknesses && results.weaknesses.length > 0">
                  <h6 class="text-danger">
                    <i class="bi bi-x-circle me-1"></i>Areas for Improvement
                  </h6>
                  <ul class="list-unstyled">
                    <li v-for="weakness in results.weaknesses" :key="weakness" class="text-danger small">
                      <i class="bi bi-arrow-right me-1"></i>{{ weakness }}
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Analytics Data -->
              <div class="mt-4" v-if="results.analytics">
                <h6>Detailed Analytics</h6>
                <div class="row">
                  <div class="col-md-6" v-if="results.analytics.difficulty_breakdown">
                    <h6 class="small">Difficulty Breakdown:</h6>
                    <div v-for="(count, difficulty) in results.analytics.difficulty_breakdown" :key="difficulty" class="mb-1">
                      <div class="d-flex justify-content-between">
                        <span class="small text-capitalize">{{ difficulty }}:</span>
                        <span class="small">{{ count }} questions</span>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6" v-if="results.analytics.subject_breakdown">
                    <h6 class="small">Subject Breakdown:</h6>
                    <div v-for="(count, subject) in results.analytics.subject_breakdown" :key="subject" class="mb-1">
                      <div class="d-flex justify-content-between">
                        <span class="small">{{ subject }}:</span>
                        <span class="small">{{ count }} questions</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-lg-4">
          <!-- Quick Actions -->
          <div class="card mb-4">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="bi bi-lightning-fill me-2"></i>Result Actions
              </h6>
            </div>
            <div class="card-body">
              <div class="d-grid gap-2">
                <button @click="toggleQuestionWiseResults" class="btn btn-primary">
                  <i class="bi bi-list-check me-2"></i>
                  {{ showQuestionWise ? 'Hide' : 'Show' }} Question-wise Results
                </button>
                <button @click="toggleTestMetadata" class="btn btn-outline-primary">
                  <i class="bi bi-info-circle me-2"></i>
                  {{ showMetadata ? 'Hide' : 'Show' }} Test Metadata
                </button>
                <button @click="$router.push('/ugc-net')" class="btn btn-outline-secondary">
                  <i class="bi bi-house me-2"></i>Back to Dashboard
                </button>
              </div>
            </div>
          </div>

          <!-- Recommendations -->
          <div class="card mb-4" v-if="recommendations.length > 0">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="bi bi-star me-2"></i>Recommendations
              </h6>
            </div>
            <div class="card-body">
              <div v-for="(recommendation, index) in recommendations" :key="index" class="mb-2">
                <div class="d-flex">
                  <div class="flex-shrink-0 me-2">
                    <i class="bi bi-arrow-right-circle text-primary"></i>
                  </div>
                  <div class="flex-grow-1">
                    <p class="mb-0 small">{{ recommendation }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Question-wise Results (toggle) -->
      <div v-if="showQuestionWise" class="row mt-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5>Question-wise Results</h5>
            </div>
            <div class="card-body">
              <div v-if="detailedResults && detailedResults.questions && detailedResults.questions.length > 0">
                <div class="mb-3">
                  <span class="badge bg-success me-2">{{ detailedResults.questions.filter(q => q.is_correct).length }} Correct</span>
                  <span class="badge bg-danger me-2">{{ detailedResults.questions.filter(q => !q.is_correct).length }} Wrong</span>
                  <span class="badge bg-secondary">{{ detailedResults.questions.length }} Total</span>
                </div>
                
                <div class="questions-list">
                  <div v-for="(question, index) in detailedResults.questions.slice(0, 10)" :key="question.id || index" 
                       class="card mb-3 question-item">
                    <div class="card-body">
                      <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0">
                          Question {{ index + 1 }}
                          <span class="badge ms-2" :class="question.is_correct ? 'bg-success' : 'bg-danger'">
                            {{ question.is_correct ? '✓ Correct' : '✗ Wrong' }}
                          </span>
                          <span v-if="question.difficulty" class="badge ms-1" :class="getDifficultyBadgeClass(question.difficulty)">
                            {{ question.difficulty }}
                          </span>
                        </h6>
                        <div class="text-end">
                          <small class="text-muted d-block">{{ question.topic || question.chapter || 'General' }}</small>
                          <small v-if="question.marks" class="text-info">{{ question.marks }} mark{{ question.marks > 1 ? 's' : '' }}</small>
                        </div>
                      </div>
                      
                      <p class="card-text">{{ question.question_text || 'Question text not available' }}</p>
                      
                      <!-- Show options if available -->
                      <div v-if="question.option_a" class="mb-3">
                        <div class="row">
                          <div class="col-md-6">
                            <div class="option-item p-2 rounded mb-1" 
                                 :class="getOptionClass(question, 'A')">
                              <strong>A.</strong> {{ question.option_a }}
                            </div>
                            <div class="option-item p-2 rounded mb-1" 
                                 :class="getOptionClass(question, 'B')">
                              <strong>B.</strong> {{ question.option_b }}
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="option-item p-2 rounded mb-1" 
                                 :class="getOptionClass(question, 'C')">
                              <strong>C.</strong> {{ question.option_c }}
                            </div>
                            <div class="option-item p-2 rounded mb-1" 
                                 :class="getOptionClass(question, 'D')">
                              <strong>D.</strong> {{ question.option_d }}
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div class="row">
                        <div class="col-md-6">
                          <strong>Your Answer:</strong>
                          <div class="p-2 rounded mt-1" :class="question.is_correct ? 'bg-success bg-opacity-10 border border-success' : 'bg-danger bg-opacity-10 border border-danger'">
                            {{ getAnswerText(question, question.user_answer) || 'Not answered' }}
                            <span v-if="!question.user_answer" class="text-muted fst-italic"> (Skipped)</span>
                          </div>
                        </div>
                        <div class="col-md-6">
                          <strong>Correct Answer:</strong>
                          <div class="p-2 rounded mt-1 bg-success bg-opacity-10 border border-success">
                            {{ getAnswerText(question, question.correct_option || question.correct_answer) || 'Not available' }}
                          </div>
                        </div>
                      </div>
                      
                      <!-- Show explanation if available -->
                      <div v-if="question.explanation" class="mt-2">
                        <small class="text-muted">
                          <strong>Explanation:</strong> {{ question.explanation }}
                        </small>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="detailedResults.questions.length > 10" class="text-center mt-3">
                    <small class="text-muted">Showing first 10 questions. Total: {{ detailedResults.questions.length }}</small>
                  </div>
                </div>
              </div>
              <div v-else-if="results.analytics && results.analytics.question_analysis">
                <h6>Question Analysis Summary</h6>
                <div class="row">
                  <div class="col-md-4 text-center">
                    <div class="card bg-success bg-opacity-10">
                      <div class="card-body">
                        <h4 class="text-success">{{ results.correct_answers }}</h4>
                        <p class="mb-0">Correct</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4 text-center">
                    <div class="card bg-danger bg-opacity-10">
                      <div class="card-body">
                        <h4 class="text-danger">{{ results.total_questions - results.correct_answers }}</h4>
                        <p class="mb-0">Wrong</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4 text-center">
                    <div class="card bg-primary bg-opacity-10">
                      <div class="card-body">
                        <h4 class="text-primary">{{ results.percentage }}%</h4>
                        <p class="mb-0">Accuracy</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mt-3">
                  <p class="text-muted">Detailed question-wise breakdown is not available for this attempt.</p>
                </div>
              </div>
              <div v-else>
                <div class="text-center text-muted py-4">
                  <i class="bi bi-info-circle me-2"></i>
                  No detailed question data available for this attempt.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Test Metadata (toggle) -->
      <div v-if="showMetadata" class="row mt-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5>Test Metadata</h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-6">
                  <div class="metadata-section">
                    <h6 class="text-primary">Test Information</h6>
                    <p><strong>Test Title:</strong> {{ results.mock_test_title || mockTest?.title || 'Mock Test' }}</p>
                    <p><strong>Subject:</strong> {{ mockTest?.subject_name || 'General' }}</p>
                    <p><strong>Total Questions:</strong> {{ results.total_questions }}</p>
                    <p><strong>Maximum Marks:</strong> {{ results.total_marks }}</p>
                    <p><strong>Time Limit:</strong> {{ formatTimeLimit(results.time_limit) }}</p>
                    <p v-if="mockTest?.difficulty_level"><strong>Difficulty Level:</strong> 
                      <span class="badge" :class="getDifficultyBadgeClass(mockTest.difficulty_level)">
                        {{ mockTest.difficulty_level }}
                      </span>
                    </p>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="metadata-section">
                    <h6 class="text-success">Your Attempt</h6>
                    <p><strong>Attempt Number:</strong> {{ getAttemptNumber() }}</p>
                    <p><strong>Started At:</strong> {{ formatDate(results.started_at) }}</p>
                    <p><strong>Completed At:</strong> {{ formatDate(results.completed_at) || 'In Progress' }}</p>
                    <p><strong>Time Taken:</strong> {{ formatTime(results.time_taken || 0) }}</p>
                    <p><strong>Completion Status:</strong> 
                      <span class="badge" :class="results.status === 'completed' ? 'bg-success' : 'bg-warning'">
                        {{ results.status === 'completed' ? 'Completed' : 'In Progress' }}
                      </span>
                    </p>
                    <p v-if="results.time_taken && results.time_limit"><strong>Time Efficiency:</strong> 
                      <span class="badge" :class="getTimeEfficiencyBadgeClass()">
                        {{ getTimeEfficiencyText() }}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
              
              <!-- Performance Breakdown -->
              <div class="row mt-3">
                <div class="col-12">
                  <h6 class="text-info">Performance Breakdown</h6>
                  <div class="row">
                    <div class="col-md-3" v-if="results.paper1_score !== null">
                      <div class="text-center p-2 border rounded">
                        <div class="h5 text-primary">{{ results.paper1_score }}</div>
                        <small class="text-muted">Paper 1 Score</small>
                      </div>
                    </div>
                    <div class="col-md-3" v-if="results.paper2_score !== null">
                      <div class="text-center p-2 border rounded">
                        <div class="h5 text-primary">{{ results.paper2_score }}</div>
                        <small class="text-muted">Paper 2 Score</small>
                      </div>
                    </div>
                    <div class="col-md-3">
                      <div class="text-center p-2 border rounded">
                        <div class="h5 text-success">{{ results.score }}</div>
                        <small class="text-muted">Total Score</small>
                      </div>
                    </div>
                    <div class="col-md-3">
                      <div class="text-center p-2 border rounded">
                        <div class="h5 text-info">{{ results.percentage }}%</div>
                        <small class="text-muted">Percentage</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Achievement & Analysis -->
              <div class="row mt-3">
                <div class="col-md-6" v-if="results.qualification_status">
                  <h6 class="text-warning">Qualification Status</h6>
                  <div class="d-flex align-items-center">
                    <span class="badge me-2" :class="getQualificationBadgeClass()">
                      {{ getQualificationDisplayText() }}
                    </span>
                    <small class="text-muted">{{ getQualificationDescription() }}</small>
                  </div>
                </div>
                <div class="col-md-6" v-if="results.predicted_rank">
                  <h6 class="text-secondary">Performance Prediction</h6>
                  <p><strong>Predicted Rank Range:</strong> {{ formatPredictedRank(results.predicted_rank) }}</p>
                  <small class="text-muted">Based on current performance pattern</small>
                </div>
              </div>

              <!-- Additional Insights -->
              <div class="row mt-3" v-if="getPerformanceInsights().length > 0">
                <div class="col-12">
                  <h6 class="text-success">Performance Insights</h6>
                  <div class="row">
                    <div class="col-md-12">
                      <ul class="list-unstyled">
                        <li v-for="insight in getPerformanceInsights()" :key="insight" class="mb-1">
                          <i class="bi bi-lightbulb text-warning me-2"></i>
                          <small>{{ insight }}</small>
                        </li>
                      </ul>
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

  <!-- Loading State -->
  <div v-else-if="loading" class="d-flex justify-content-center align-items-center" style="min-height: 50vh;">
    <div class="text-center">
      <div class="spinner-border text-primary mb-3" role="status">
        <span class="visually-hidden">Loading results...</span>
      </div>
      <p class="text-muted">Loading your test results...</p>
    </div>
  </div>
  
  <!-- Error State -->
  <div v-else-if="error" class="d-flex justify-content-center align-items-center" style="min-height: 50vh;">
    <div class="text-center">
      <div class="text-danger mb-3">
        <i class="bi bi-exclamation-triangle-fill" style="font-size: 3rem;"></i>
      </div>
      <h4 class="text-danger">Error Loading Results</h4>
      <p class="text-muted">{{ error }}</p>
      <button @click="loadResults" class="btn btn-primary me-2">Retry</button>
      <router-link to="/ugc-net" class="btn btn-outline-secondary">Back to Dashboard</router-link>
    </div>
  </div>
  
  <!-- No Results State -->
  <div v-else class="d-flex justify-content-center align-items-center" style="min-height: 50vh;">
    <div class="text-center">
      <div class="text-muted mb-3">
        <i class="bi bi-inbox" style="font-size: 3rem;"></i>
      </div>
      <h4 class="text-muted">No Results Found</h4>
      <p class="text-muted">Unable to load test results.</p>
      <router-link to="/ugc-net" class="btn btn-primary">Back to Dashboard</router-link>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'
import { useAppState } from '@/composables/useAppState'
import { formatISTDateTime } from '@/utils/timezone'

export default {
  name: 'TestResults',
  props: {
    testId: {
      type: [String, Number],
      default: null
    },
    attemptId: {
      type: [String, Number], 
      default: null
    },
    findLatest: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const router = useRouter()
    const route = useRoute()
    const { stopLoading } = useAppState()
    
    // Reactive data
    const mockTest = ref(null)
    const results = ref(null)
    const detailedResults = ref(null)
    const showQuestionWise = ref(false)
    const showMetadata = ref(false)
    const loading = ref(true)
    const error = ref(null)
    
    // Computed properties
    const userToken = computed(() => {
      if (typeof window !== 'undefined' && window.localStorage) {
        return localStorage.getItem('prepcheck_token')
      }
      return null
    })
    
    const recommendations = computed(() => {
      if (!results.value) return []
      
      const recs = []
      
      if (results.value.percentage < 40) {
        recs.push('Focus on fundamental concepts to improve overall understanding')
        recs.push('Practice more questions from weak chapters')
        recs.push('Review incorrect answers to identify knowledge gaps')
      } else if (results.value.percentage < 60) {
        recs.push('Good foundation! Work on advanced topics for better scores')
        recs.push('Time management could be improved')
      } else {
        recs.push('Excellent performance! Keep practicing to maintain consistency')
        recs.push('Consider helping others to reinforce your knowledge')
      }
      
      return recs
    })

    // Methods
    const loadResults = async () => {
      // Get testId and attemptId from props first, then fall back to route params
      const testId = props.testId || route.params.testId
      const attemptId = props.attemptId || route.params.attemptId
      const findLatest = props.findLatest || route.params.findLatest
      
      console.log('🔍 TestResults: Loading results with:', { testId, attemptId, findLatest })
      
      if (!testId) {
        console.error('❌ TestResults: No testId provided')
        error.value = 'Invalid test ID. Redirecting to dashboard.'
        setTimeout(() => router.push('/ugc-net'), 2000)
        loading.value = false
        return
      }
      
      loading.value = true
      error.value = null
      
      try {
        // Load test details
        console.log('🔍 TestResults: Loading test details for testId:', testId)
        const testResult = await api.ugcNet.getMockTestDetails(testId)
        console.log('🔍 TestResults: Test details response:', testResult)
        if (testResult.success) {
          mockTest.value = testResult.data
          console.log('✅ TestResults: Test details loaded:', testResult.data)
        } else {
          console.error('❌ TestResults: Failed to load test details:', testResult.error)
        }
        
        let finalAttemptId = attemptId
        
        // Always load user attempts to get attempt count and order
        console.log('🔍 TestResults: Loading user attempts for testId:', testId)
        const attemptsResult = await api.ugcNet.getUserAttempts(testId)
        console.log('🔍 TestResults: User attempts response:', attemptsResult)
        
        // Debug: Log the actual error details
        if (!attemptsResult.success) {
          console.error('❌ TestResults: User attempts failed:', {
            error: attemptsResult.error,
            status: attemptsResult.status,
            response: attemptsResult.response
          })
        }
        
        // Store user attempts in mockTest for attempt number calculation
        if (attemptsResult.success && attemptsResult.data.attempts) {
          if (mockTest.value) {
            mockTest.value.user_attempts = attemptsResult.data.attempts
          }
        }
        
        // If no attemptId provided or findLatest is true, get the latest attempt
        if (!attemptId || findLatest) {
          console.log('🔍 TestResults: Finding latest attempt for testId:', testId)
          if (attemptsResult.success && attemptsResult.data.attempts && attemptsResult.data.attempts.length > 0) {
            // Get the most recent completed attempt
            const completedAttempts = attemptsResult.data.attempts.filter(a => a.status === 'completed')
            console.log('🔍 TestResults: Completed attempts:', completedAttempts)
            if (completedAttempts.length > 0) {
              finalAttemptId = completedAttempts[0].id
              console.log('✅ TestResults: Found latest attempt:', finalAttemptId)
              // Update the route to reflect the actual attemptId
              router.replace(`/ugc-net/test/${testId}/attempt/${finalAttemptId}/results`)
            } else {
              error.value = 'No completed attempts found for this test'
              console.error('❌ TestResults: No completed attempts found')
              loading.value = false
              return
            }
          } else {
            error.value = 'No attempts found for this test'
            console.error('❌ TestResults: No attempts found:', attemptsResult)
            loading.value = false
            return
          }
        } else {
          // When attemptId is provided, just use it as finalAttemptId
          finalAttemptId = attemptId
        }
        
        // Load attempt results
        console.log('🔍 TestResults: Loading attempt results for:', { testId, attemptId: finalAttemptId })
        const resultsResponse = await api.ugcNet.getAttemptResults(testId, finalAttemptId, true) // Include solutions
        console.log('🔍 TestResults: Raw API response:', resultsResponse)
        if (resultsResponse.success) {
          console.log('🔍 TestResults: Response data:', resultsResponse.data)
          console.log('🔍 TestResults: Response data type:', typeof resultsResponse.data)
          console.log('🔍 TestResults: Response data keys:', Object.keys(resultsResponse.data || {}))
          
          results.value = resultsResponse.data  // Backend returns attempt data directly
          
          // Handle detailed results - check for questions_with_results from backend
          console.log('🔍 TestResults: Checking detailed results...')
          console.log('🔍 TestResults: Has questions_with_results?', !!resultsResponse.data.questions_with_results)
          console.log('🔍 TestResults: Has detailed_results?', !!resultsResponse.data.detailed_results)
          console.log('🔍 TestResults: All response keys:', Object.keys(resultsResponse.data || {}))
          
          if (resultsResponse.data.questions_with_results) {
            detailedResults.value = {
              questions: resultsResponse.data.questions_with_results
            }
            console.log('✅ TestResults: Detailed results loaded from questions_with_results:', detailedResults.value.questions.length, 'questions')
            console.log('🔍 TestResults: Sample question structure:', detailedResults.value.questions[0])
          } else if (resultsResponse.data.detailed_results) {
            detailedResults.value = resultsResponse.data.detailed_results
            console.log('✅ TestResults: Detailed results loaded from detailed_results:', detailedResults.value)
          } else {
            detailedResults.value = null
            console.log('⚠️ TestResults: No detailed results available')
            console.log('🔍 TestResults: This might be because:')
            console.log('  - The attempt has no detailed_results field in the database')
            console.log('  - The backend failed to process the detailed results')
            console.log('  - The include_solutions parameter is not working correctly')
          }
          
          console.log('🔍 TestResults: Results value set to:', results.value)
          console.log('🔍 TestResults: Results value type:', typeof results.value)
          console.log('✅ TestResults: Results loaded successfully')
        } else {
          console.error('❌ TestResults: Failed to load results:', resultsResponse.error)
          console.error('❌ TestResults: Results API error details:', {
            error: resultsResponse.error,
            status: resultsResponse.status,
            response: resultsResponse.response
          })
          error.value = 'Failed to load results: ' + resultsResponse.error
        }
      } catch (error) {
        console.error('❌ TestResults: Failed to load results:', error)
        error.value = 'Failed to load results: ' + error.message
      } finally {
        loading.value = false
      }
    }

    const toggleQuestionWiseResults = () => {
      showQuestionWise.value = !showQuestionWise.value
    }

    const toggleTestMetadata = () => {
      showMetadata.value = !showMetadata.value
    }

    const formatTime = (seconds) => {
      if (!seconds || seconds === 0) return '0 min 0 sec'
      
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const remainingSeconds = seconds % 60
      
      let timeString = ''
      
      if (hours > 0) {
        timeString += `${hours} hr${hours > 1 ? 's' : ''} `
      }
      if (minutes > 0) {
        timeString += `${minutes} min${minutes > 1 ? 's' : ''} `
      }
      if (remainingSeconds > 0 || (hours === 0 && minutes === 0)) {
        timeString += `${remainingSeconds} sec${remainingSeconds > 1 ? 's' : ''}`
      }
      
      return timeString.trim()
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return formatISTDateTime(dateString)
    }

    const formatTimeLimit = (minutes) => {
      if (!minutes || minutes === 0) return 'No limit'
      
      const hours = Math.floor(minutes / 60)
      const remainingMinutes = minutes % 60
      
      if (hours > 0) {
        return remainingMinutes > 0 
          ? `${hours} hr${hours > 1 ? 's' : ''} ${remainingMinutes} min${remainingMinutes > 1 ? 's' : ''}`
          : `${hours} hr${hours > 1 ? 's' : ''}`
      } else {
        return `${minutes} min${minutes > 1 ? 's' : ''}`
      }
    }

    const getProgressBarClass = (percentage) => {
      if (percentage >= 75) return 'bg-success'
      if (percentage >= 50) return 'bg-warning'
      return 'bg-danger'
    }

    const getQualificationBadgeClass = () => {
      if (!results.value) return 'bg-secondary'
      
      const status = results.value.qualification_status
      if (status === 'qualified') return 'bg-success'
      if (status === 'borderline') return 'bg-warning'
      return 'bg-danger'
    }

    const getDifficultyBadgeClass = (difficulty) => {
      switch (difficulty?.toLowerCase()) {
        case 'easy': return 'bg-success'
        case 'medium': return 'bg-warning'
        case 'hard': return 'bg-danger'
        default: return 'bg-secondary'
      }
    }

    const getAttemptNumber = () => {
      // Calculate attempt number based on current attempt and available attempts
      if (mockTest.value?.user_attempts && Array.isArray(mockTest.value.user_attempts)) {
        // Find current attempt in the list and return its position
        const currentAttemptId = results.value?.id
        if (currentAttemptId) {
          // Sort attempts by created_at or started_at to get chronological order
          const sortedAttempts = [...mockTest.value.user_attempts].sort((a, b) => {
            const aTime = new Date(a.created_at || a.started_at || 0)
            const bTime = new Date(b.created_at || b.started_at || 0)
            return aTime - bTime
          })
          
          const attemptIndex = sortedAttempts.findIndex(attempt => attempt.id === currentAttemptId)
          if (attemptIndex >= 0) {
            return `#${attemptIndex + 1}`
          }
        }
        
        // If we can't find the specific attempt, just show the total count
        return `#${mockTest.value.user_attempts.length}`
      } else if (typeof mockTest.value?.user_attempts === 'number') {
        // If it's just a count, show the count
        return `#${mockTest.value.user_attempts}`
      } else if (results.value?.attempt_number) {
        // If the backend provides attempt_number directly
        return `#${results.value.attempt_number}`
      }
      return '#1' // Default to first attempt
    }

    const getTimeEfficiencyText = () => {
      if (!results.value?.time_limit) return 'N/A'
      
      // Calculate time taken from start and end times if time_taken is null
      let timeTakenSeconds = results.value.time_taken
      
      if (!timeTakenSeconds && results.value.start_time && results.value.end_time) {
        const startTime = new Date(results.value.start_time)
        const endTime = new Date(results.value.end_time)
        timeTakenSeconds = Math.floor((endTime - startTime) / 1000)
      }
      
      if (!timeTakenSeconds || timeTakenSeconds <= 0) return 'N/A'
      
      const timeUsedPercentage = (timeTakenSeconds / (results.value.time_limit * 60)) * 100
      
      if (timeUsedPercentage < 50) return 'Very Fast'
      if (timeUsedPercentage < 75) return 'Good Pace'
      if (timeUsedPercentage < 90) return 'Steady'
      if (timeUsedPercentage < 100) return 'Almost Full Time'
      return 'Overtime'
    }

    const getTimeEfficiencyBadgeClass = () => {
      if (!results.value?.time_limit) return 'bg-secondary'
      
      // Calculate time taken from start and end times if time_taken is null
      let timeTakenSeconds = results.value.time_taken
      
      if (!timeTakenSeconds && results.value.start_time && results.value.end_time) {
        const startTime = new Date(results.value.start_time)
        const endTime = new Date(results.value.end_time)
        timeTakenSeconds = Math.floor((endTime - startTime) / 1000)
      }
      
      if (!timeTakenSeconds || timeTakenSeconds <= 0) return 'bg-secondary'
      
      const timeUsedPercentage = (timeTakenSeconds / (results.value.time_limit * 60)) * 100
      
      if (timeUsedPercentage < 50) return 'bg-primary'
      if (timeUsedPercentage < 75) return 'bg-success'
      if (timeUsedPercentage < 90) return 'bg-info'
      if (timeUsedPercentage < 100) return 'bg-warning'
      return 'bg-danger'
    }

    const getQualificationDisplayText = () => {
      if (!results.value?.qualification_status) return 'Unknown'
      
      const status = results.value.qualification_status.toLowerCase()
      switch (status) {
        case 'qualified': return 'QUALIFIED ✓'
        case 'not_qualified': return 'NOT QUALIFIED'
        case 'borderline': return 'BORDERLINE'
        default: return results.value.qualification_status.toUpperCase()
      }
    }

    const getQualificationDescription = () => {
      if (!results.value?.qualification_status) return ''
      
      const status = results.value.qualification_status.toLowerCase()
      const percentage = results.value.percentage
      
      switch (status) {
        case 'qualified': return `Excellent! You've achieved the qualifying percentage.`
        case 'not_qualified': return `Keep practicing! You need ${40 - percentage}% more to qualify.`
        case 'borderline': return `Close! Just a bit more effort needed.`
        default: return ''
      }
    }

    const formatPredictedRank = (rank) => {
      if (!rank) return 'Not available'
      
      // If it's a number, format it nicely
      if (typeof rank === 'number') {
        const lower = Math.max(1, rank - 500)
        const upper = rank + 500
        return `${lower.toLocaleString()} - ${upper.toLocaleString()}`
      }
      
      return rank.toString()
    }

    const getPerformanceInsights = () => {
      if (!results.value) return []
      
      const insights = []
      const percentage = results.value.percentage
      const timeUsedPercentage = results.value.time_taken ? 
        (results.value.time_taken / (results.value.time_limit * 60)) * 100 : 0
      
      // Accuracy insights
      if (percentage >= 80) {
        insights.push('Outstanding accuracy! You have excellent command over the subject.')
      } else if (percentage >= 60) {
        insights.push('Good performance! Focus on weak areas to improve further.')
      } else if (percentage >= 40) {
        insights.push('Qualifying score achieved. Work on accuracy for better ranks.')
      } else {
        insights.push('Need more practice. Focus on fundamental concepts.')
      }
      
      // Time management insights
      if (timeUsedPercentage < 50) {
        insights.push('Excellent time management! You finished much ahead of time.')
      } else if (timeUsedPercentage < 75) {
        insights.push('Good time management with room for double-checking answers.')
      } else if (timeUsedPercentage > 95) {
        insights.push('Consider practicing time management for better speed.')
      }
      
      // Chapter performance insights
      if (results.value.chapter_wise_performance) {
        const chapterPerformances = Object.values(results.value.chapter_wise_performance)
        const avgChapterPerformance = chapterPerformances.reduce((acc, perf) => 
          acc + ((perf.correct || 0) / (perf.total || 1)), 0) / chapterPerformances.length * 100
        
        if (avgChapterPerformance > percentage + 10) {
          insights.push('Strong conceptual understanding across different topics.')
        }
      }
      
      return insights
    }

    const getOptionClass = (question, option) => {
      const correctOption = question.correct_option || question.correct_answer
      const userAnswer = question.user_answer
      
      if (correctOption === option) {
        return 'bg-success bg-opacity-10 border border-success' // Correct answer
      } else if (userAnswer === option && userAnswer !== correctOption) {
        return 'bg-danger bg-opacity-10 border border-danger' // Wrong user selection
      } else {
        return 'bg-light border' // Normal option
      }
    }

    const getAnswerText = (question, answer) => {
      if (!answer) return ''
      
      // If answer is A, B, C, D, convert to the actual option text
      switch (answer.toUpperCase()) {
        case 'A':
          return `A. ${question.option_a || ''}`
        case 'B':
          return `B. ${question.option_b || ''}`
        case 'C':
          return `C. ${question.option_c || ''}`
        case 'D':
          return `D. ${question.option_d || ''}`
        default:
          return answer // Return as-is if it's not A/B/C/D
      }
    }

    // Debug function to check for blocking elements
    const debugInteractionIssues = () => {
      console.log('🔍 Debugging interaction issues...')
      
      // Check for loading overlays
      const loadingOverlays = document.querySelectorAll('.loading-overlay')
      console.log('Loading overlays found:', loadingOverlays.length)
      loadingOverlays.forEach((overlay, index) => {
        console.log(`Overlay ${index}:`, {
          visible: overlay.style.display !== 'none',
          zIndex: overlay.style.zIndex || getComputedStyle(overlay).zIndex,
          opacity: getComputedStyle(overlay).opacity
        })
      })
      
      // Check for modal backdrops
      const modalBackdrops = document.querySelectorAll('.modal-backdrop, .backdrop')
      console.log('Modal backdrops found:', modalBackdrops.length)
      
      // Check body classes that might affect interaction
      console.log('Body classes:', document.body.className)
      
      // Check for elements with high z-index
      const allElements = document.querySelectorAll('*')
      const highZIndexElements = Array.from(allElements).filter(el => {
        const zIndex = getComputedStyle(el).zIndex
        return zIndex && parseInt(zIndex) > 1000
      })
      console.log('High z-index elements:', highZIndexElements.length)
      
      return {
        loadingOverlays: loadingOverlays.length,
        modalBackdrops: modalBackdrops.length,
        highZIndexElements: highZIndexElements.length
      }
    }

    // Expose debug function globally for console access
    if (typeof window !== 'undefined') {
      window.debugTestResults = debugInteractionIssues
    }

    // Lifecycle
    onMounted(() => {
      console.log('🔍 TestResults: Component mounted')
      console.log('🔍 TestResults: Route params:', route.params)
      console.log('🔍 TestResults: Props:', props)
      
      // Ensure global loading overlay is hidden
      stopLoading()
      
      loading.value = true
      error.value = null
      loadResults()
    })

    return {
      mockTest,
      results,
      detailedResults,
      showQuestionWise,
      showMetadata,
      loading,
      error,
      userToken,
      recommendations,
      testId: props.testId || route.params.testId,
      attemptId: props.attemptId || route.params.attemptId,
      findLatest: props.findLatest,
      toggleQuestionWiseResults,
      toggleTestMetadata,
      formatTime,
      formatDate,
      formatTimeLimit,
      getProgressBarClass,
      getQualificationBadgeClass,
      getDifficultyBadgeClass,
      getAttemptNumber,
      getTimeEfficiencyText,
      getTimeEfficiencyBadgeClass,
      getOptionClass,
      getAnswerText,
      loadResults,
      getQualificationDisplayText,
      getQualificationDescription,
      formatPredictedRank,
      getPerformanceInsights,
      getOptionClass,
      getAnswerText
    }
  }
}
</script>

<style scoped>
.test-results {
  padding: 1rem;
  position: relative;
  z-index: 1;
  background-color: #ffffff;
  min-height: 100vh;
}

.card {
  transition: transform 0.2s ease-in-out;
  position: relative;
  z-index: 2;
}

.card:hover {
  transform: translateY(-2px);
}

.recommendation-item {
  border-left: 3px solid #0d6efd;
  padding-left: 1rem;
}

.question-item {
  background-color: #f8f9fa;
  position: relative;
  z-index: 2;
}

.metadata-section {
  border: 1px solid #e9ecef;
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.progress {
  border-radius: 10px;
}

/* Ensure buttons are clickable */
.btn {
  position: relative;
  z-index: 10;
  pointer-events: auto;
}

/* Ensure form elements are interactive */
input, button, select, textarea {
  pointer-events: auto;
}

/* Remove any potential blur effects */
* {
  backdrop-filter: none !important;
  filter: none !important;
}

@media (max-width: 768px) {
  .test-results {
    padding: 0.5rem;
  }
  
  .col-md-3, .col-md-4, .col-md-6 {
    margin-bottom: 1rem;
  }
}
</style>
