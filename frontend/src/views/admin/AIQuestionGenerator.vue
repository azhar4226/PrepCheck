<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <!-- Header -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2 class="mb-1">🤖 AI Question Generator</h2>
            <p class="text-muted mb-0">Generate intelligent questions for UGC NET tests using AI technology</p>
          </div>
          <div class="badge bg-primary">
            {{ aiStatus }}
          </div>
        </div>

        <div class="row">
          <!-- Generation Form -->
          <div class="col-lg-5">
            <div class="card shadow-sm h-100">
              <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                  <i class="bi bi-gear me-2"></i>
                  Question Configuration
                </h5>
              </div>
              <div class="card-body">
                <form @submit.prevent="generateQuestions">
                  <!-- Subject Selection -->
                  <div class="mb-3">
                    <label class="form-label fw-bold">Subject</label>
                    <select v-model="form.subject_id" class="form-select" required @change="onSubjectChange">
                      <option value="">Select a subject...</option>
                      <option 
                        v-for="subject in subjects" 
                        :key="subject.id" 
                        :value="subject.id"
                      >
                        {{ subject.name }}
                      </option>
                    </select>
                  </div>

                  <!-- Chapter Selection -->
                  <div class="mb-3">
                    <label class="form-label fw-bold">Chapter</label>
                    <select v-model="form.chapter_id" class="form-select" required :disabled="!form.subject_id || loadingChapters">
                      <option value="">{{ form.subject_id ? 'Select a chapter...' : 'Select a subject first' }}</option>
                      <option 
                        v-for="chapter in chapters" 
                        :key="chapter.id" 
                        :value="chapter.id"
                      >
                        {{ chapter.name }}
                      </option>
                    </select>
                    <div v-if="loadingChapters" class="form-text">
                      <span class="spinner-border spinner-border-sm me-1"></span>
                      Loading chapters...
                    </div>
                  </div>

                  <!-- Topic -->
                  <div class="mb-3">
                    <label class="form-label fw-bold">Question Topic</label>
                    <input 
                      v-model="form.topic" 
                      type="text" 
                      class="form-control" 
                      placeholder="e.g., Python Functions, Machine Learning Basics"
                      required
                    >
                    <div class="form-text">Be specific to get better AI-generated questions</div>
                  </div>

                  <!-- Difficulty -->
                  <div class="mb-3">
                    <label class="form-label fw-bold">Difficulty Level</label>
                    <select v-model="form.difficulty" class="form-select" required>
                      <option value="">Select difficulty...</option>
                      <option value="easy">🟢 Easy - Basic concepts</option>
                      <option value="medium">🟡 Medium - Applied knowledge</option>
                      <option value="hard">🔴 Hard - Advanced concepts</option>
                    </select>
                  </div>

                  <!-- Number of Questions -->
                  <div class="mb-3">
                    <label class="form-label fw-bold">Number of Questions</label>
                    <div class="row">
                      <div class="col-8">
                        <input 
                          v-model="form.num_questions" 
                          type="range" 
                          min="5" 
                          max="20" 
                          class="form-range"
                        >
                      </div>
                      <div class="col-4">
                        <input 
                          v-model="form.num_questions" 
                          type="number" 
                          min="5" 
                          max="20" 
                          class="form-control"
                        >
                      </div>
                    </div>
                    <div class="form-text">Recommended: 10-15 questions</div>
                  </div>

                  <!-- Additional Context -->
                  <div class="mb-4">
                    <label class="form-label fw-bold">Additional Context (Optional)</label>
                    <textarea 
                      v-model="form.context" 
                      class="form-control" 
                      rows="3"
                      placeholder="Provide any specific requirements, focus areas, or learning objectives..."
                    ></textarea>
                  </div>

                  <!-- Verification Settings -->
                  <div class="mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <label class="form-label fw-bold mb-0">🔍 Verification Settings</label>
                      <small class="text-muted">AI Quality Control</small>
                    </div>
                    
                    <!-- Verification Threshold -->
                    <div class="mb-3">
                      <label class="form-label">Confidence Threshold</label>
                      <div class="row">
                        <div class="col-8">
                          <input 
                            v-model="form.verification_threshold" 
                            type="range" 
                            min="0.5" 
                            max="0.95" 
                            step="0.05"
                            class="form-range"
                          >
                        </div>
                        <div class="col-4">
                          <input 
                            v-model="form.verification_threshold" 
                            type="number" 
                            min="0.5" 
                            max="0.95" 
                            step="0.05"
                            class="form-control form-control-sm"
                          >
                        </div>
                      </div>
                      <div class="form-text">Higher values = stricter verification ({{ Math.round(form.verification_threshold * 100) }}%)</div>
                    </div>

                    <!-- Max Retry Attempts -->
                    <div class="mb-3">
                      <label class="form-label">Max Retry Attempts</label>
                      <select v-model="form.max_retry_attempts" class="form-select form-select-sm">
                        <option :value="1">1 attempt</option>
                        <option :value="2">2 attempts</option>
                        <option :value="3">3 attempts (recommended)</option>
                        <option :value="5">5 attempts</option>
                      </select>
                      <div class="form-text">How many times to regenerate if verification fails</div>
                    </div>

                    <!-- Fallback Strategy -->
                    <div class="mb-3">
                      <label class="form-label">Fallback Strategy</label>
                      <select v-model="form.fallback_strategy" class="form-select form-select-sm">
                        <option value="skip">Skip failed questions</option>
                        <option value="manual_review">Mark for manual review</option>
                        <option value="use_anyway">Use anyway (lower quality)</option>
                      </select>
                      <div class="form-text">What to do with questions that fail verification</div>
                    </div>
                  </div>

                  <!-- Generate Button -->
                  <button 
                    type="submit" 
                    class="btn btn-primary btn-lg w-100" 
                    :disabled="generating"
                  >
                    <span v-if="generating">
                      <span class="spinner-border spinner-border-sm me-2"></span>
                      Generating Questions...
                    </span>
                    <span v-else>
                      <i class="bi bi-magic me-2"></i>
                      Generate Questions
                    </span>
                  </button>

                  <div class="text-center mt-3">
                    <small class="text-muted">
                      ⚡ Usually takes 10-30 seconds
                    </small>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- Preview/Results -->
          <div class="col-lg-7">
            <div class="card shadow-sm h-100">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                  <i class="bi bi-eye me-2"></i>
                  Generated Questions Preview
                </h5>
                <div v-if="generatedQuestions">
                  <button 
                    @click="saveQuestions" 
                    class="btn btn-success btn-sm me-2"
                    :disabled="saving"
                  >
                    <span v-if="saving">
                      <span class="spinner-border spinner-border-sm me-1"></span>
                      Saving...
                    </span>
                    <span v-else>
                      <i class="bi bi-check-circle me-1"></i>
                      Save to Question Bank
                    </span>
                  </button>
                  <button @click="regenerateQuestions" class="btn btn-outline-primary btn-sm">
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    Regenerate
                  </button>
                </div>
              </div>
              
              <div class="card-body">
                <!-- No Questions Generated Yet -->
                <div v-if="!generatedQuestions && !generating" class="text-center py-5">
                  <i class="bi bi-lightbulb display-1 text-muted"></i>
                  <h4 class="text-muted mt-3">Ready to Generate</h4>
                  <p class="text-muted">Fill out the form and click "Generate Questions" to create AI-powered questions</p>
                </div>

                <!-- Generating State -->
                <div v-if="generating" class="text-center py-5">
                  <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
                  <h4>AI is Working...</h4>
                  <p class="text-muted">Creating your custom question bank</p>
                  <div class="progress mx-auto" style="width: 300px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         style="width: 75%"></div>
                  </div>
                </div>

                <!-- Generated Questions Display -->
                <div v-if="generatedQuestions && !generating">
                  <!-- Questions Info -->
                  <div class="alert alert-success mb-4">
                    <div class="d-flex align-items-center">
                      <i class="bi bi-check-circle-fill me-2"></i>
                      <div>
                        <strong>Questions Generated Successfully!</strong>
                        <br>
                        <small>{{ generatedQuestions.questions?.length || 0 }} questions created</small>
                      </div>
                    </div>
                  </div>

                  <!-- Questions Header -->
                  <div class="border rounded p-3 mb-4 bg-light">
                    <h4 class="mb-1">{{ generatedQuestions.title || 'Generated Question Bank' }}</h4>
                    <p class="text-muted mb-0">{{ generatedQuestions.description || 'AI-generated practice questions' }}</p>
                  </div>

                  <!-- Questions Preview -->
                  <div class="questions-preview">
                    <div 
                      v-for="(question, index) in generatedQuestions.questions || []" 
                      :key="index"
                      class="card mb-3"
                    >
                      <div class="card-header bg-light">
                        <div class="d-flex justify-content-between">
                          <strong>Question {{ index + 1 }}</strong>
                          <span class="badge bg-primary">{{ question?.marks || 1 }} mark{{ question?.marks !== 1 ? 's' : '' }}</span>
                        </div>
                      </div>
                      <div class="card-body">
                        <h6 class="mb-3">{{ question?.question || '' }}</h6>
                        
                        <!-- Options -->
                        <div class="row">
                          <div 
                            v-for="(option, optionKey) in question?.options || {}" 
                            :key="optionKey"
                            class="col-md-6 mb-2"
                          >
                            <div 
                              class="p-2 border rounded"
                              :class="optionKey === question?.correct_answer ? 'bg-success text-white border-success' : 'bg-white'"
                            >
                              <strong>{{ optionKey }})</strong> {{ option }}
                              <i v-if="optionKey === question?.correct_answer" class="bi bi-check-circle float-end"></i>
                            </div>
                          </div>
                        </div>

                        <!-- Explanation -->
                        <div class="mt-3">
                          <small class="text-muted">
                            <strong>Explanation:</strong> {{ question?.explanation || '' }}
                          </small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Generations -->
        <div class="row mt-4" v-if="recentGenerations.length > 0">
          <div class="col-12">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="bi bi-clock-history me-2"></i>
                  Recent Generations
                </h5>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <table class="table table-hover">
                    <thead>
                      <tr>
                        <th>Topic</th>
                        <th>Difficulty</th>
                        <th>Questions</th>
                        <th>Generated</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="generation in recentGenerations" :key="generation.id">
                        <td>{{ generation.topic }}</td>
                        <td>
                          <span 
                            class="badge"
                            :class="{
                              'bg-success': generation.difficulty === 'easy',
                              'bg-warning': generation.difficulty === 'medium',
                              'bg-danger': generation.difficulty === 'hard'
                            }"
                          >
                            {{ generation.difficulty }}
                          </span>
                        </td>
                        <td>{{ generation.question_count }}</td>
                        <td>{{ formatDate(generation.created_at) }}</td>
                        <td>
                          <span 
                            class="badge"
                            :class="{
                              'bg-success': generation.status === 'saved',
                              'bg-secondary': generation.status === 'draft'
                            }"
                          >
                            {{ generation.status }}
                          </span>
                        </td>
                        <td>
                          <button class="btn btn-sm btn-outline-primary me-1">
                            <i class="bi bi-eye"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-danger">
                            <i class="bi bi-trash"></i>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Verification Status Modal -->
  <div 
    class="modal fade" 
    :class="{ show: showVerificationModal, 'd-block': showVerificationModal }"
    :style="{ display: showVerificationModal ? 'block' : 'none' }"
    tabindex="-1"
  >
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-shield-check me-2"></i>
            AI Question Verification
          </h5>
          <button 
            type="button" 
            class="btn-close" 
            @click="closeVerificationModal"
          ></button>
        </div>
        
        <div class="modal-body">
          <!-- Verification in Progress -->
          <div v-if="verificationStatus && !verificationStatus.ready" class="text-center py-4">
            <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
            <h5>Verifying Questions...</h5>
            <p class="text-muted">{{ verificationProgress?.status || 'Analyzing question quality and accuracy' }}</p>
            
            <!-- Progress Info -->
            <div v-if="verificationProgress" class="mt-4">
              <div class="row text-center">
                <div class="col-4">
                  <div class="card border-primary">
                    <div class="card-body py-2">
                      <h6 class="card-title text-primary mb-1">Current</h6>
                      <span class="h5">{{ verificationProgress.current || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="col-4">
                  <div class="card border-info">
                    <div class="card-body py-2">
                      <h6 class="card-title text-info mb-1">Total</h6>
                      <span class="h5">{{ verificationProgress.total || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="col-4">
                  <div class="card border-success">
                    <div class="card-body py-2">
                      <h6 class="card-title text-success mb-1">Verified</h6>
                      <span class="h5">{{ verificationProgress.verified || 0 }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Progress Bar -->
              <div class="progress mt-3" style="height: 10px;">
                <div 
                  class="progress-bar progress-bar-striped progress-bar-animated"
                  :style="{ width: Math.round((verificationProgress.current / verificationProgress.total) * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>

          <!-- Verification Complete -->
          <div v-if="verificationStatus && verificationStatus.ready">
            <!-- Success Result -->
            <div v-if="verificationStatus.successful" class="text-center py-4">
              <i class="bi bi-check-circle-fill text-success display-1"></i>
              <h4 class="text-success mt-3">Verification Complete!</h4>
              
              <div class="row mt-4">
                <div class="col-3">
                  <div class="card border-success">
                    <div class="card-body text-center py-2">
                      <h6 class="text-success mb-1">Verified</h6>
                      <span class="h4 text-success">{{ verificationProgress?.verified_count || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="card border-danger">
                    <div class="card-body text-center py-2">
                      <h6 class="text-danger mb-1">Failed</h6>
                      <span class="h4 text-danger">{{ verificationProgress?.failed_count || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="card border-warning">
                    <div class="card-body text-center py-2">
                      <h6 class="text-warning mb-1">Review</h6>
                      <span class="h4 text-warning">{{ verificationProgress?.manual_review_count || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="card border-primary">
                    <div class="card-body text-center py-2">
                      <h6 class="text-primary mb-1">Success Rate</h6>
                      <span class="h4 text-primary">{{ Math.round(verificationProgress?.success_rate || 0) }}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Actions for Failed Questions -->
              <div v-if="verificationProgress?.failed_count > 0" class="mt-4">
                <div class="alert alert-warning">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  {{ verificationProgress.failed_count }} questions failed verification.
                </div>
                <button 
                  @click="retryVerification(generatedQuestions?.id)"
                  class="btn btn-warning me-2"
                  :disabled="!generatedQuestions?.id"
                >
                  <i class="bi bi-arrow-clockwise me-1"></i>
                  Retry Failed Questions
                </button>
              </div>
            </div>

            <!-- Error Result -->
            <div v-else class="text-center py-4">
              <i class="bi bi-x-circle-fill text-danger display-1"></i>
              <h4 class="text-danger mt-3">Verification Failed</h4>
              <p class="text-muted">{{ verificationStatus.error || 'Unknown error occurred' }}</p>
              
              <button 
                @click="retryVerification(generatedQuestions?.id)"
                class="btn btn-primary mt-3"
                :disabled="!generatedQuestions?.id"
              >
                <i class="bi bi-arrow-clockwise me-1"></i>
                Retry Verification
              </button>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button 
            type="button" 
            class="btn btn-secondary" 
            @click="closeVerificationModal"
          >
            {{ verificationStatus?.ready ? 'Close' : 'Hide' }}
          </button>
          
          <button 
            v-if="verificationStatus?.ready && verificationStatus.successful && generatedQuestions?.id"
            class="btn btn-primary"
            @click="$router.push(`/admin/question-bank/${generatedQuestions.id}`)"
          >
            <i class="bi bi-eye me-1"></i>
            View Questions
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal backdrop -->
  <div 
    v-if="showVerificationModal" 
    class="modal-backdrop fade show"
    @click="closeVerificationModal"
  ></div>
</template>

<script>
import { useAuth } from '@/composables/useAuth'
import adminService from '@/services/adminService'
import aiService from '@/services/aiService'

export default {
  name: 'AIQuestionGenerator',
  setup() {
    const { user } = useAuth()
    return { user, adminService, aiService }
  },
  data() {
    return {
      form: {
        subject_id: '',
        chapter_id: '',
        topic: '',
        difficulty: '',
        num_questions: 10,
        context: '',
        verification_threshold: 0.7,
        max_retry_attempts: 3,
        fallback_strategy: 'skip'
      },
      subjects: [],
      chapters: [],
      loadingChapters: false,
      generatedQuestions: null,
      generating: false,
      saving: false,
      recentGenerations: [],
      aiStatus: 'Ready',
      // Verification tracking
      verificationTaskId: null,
      verificationStatus: null,
      verificationProgress: null,
      showVerificationModal: false,
      verificationPolling: null
    }
  },
  async mounted() {
    await this.loadSubjects()
    await this.loadRecentGenerations()
    this.checkAIStatus()
  },
  
  beforeDestroy() {
    // Cleanup polling when component is destroyed
    if (this.verificationPolling) {
      clearInterval(this.verificationPolling)
      this.verificationPolling = null
    }
  },
  methods: {
    showToast(message, type = 'info') {
      // Simple notification system
      const alertType = type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'
      console.log(`[${type.toUpperCase()}] ${message}`)
      
      // For now, just use console and alert for critical errors
      if (type === 'error') {
        alert(`Error: ${message}`)
      } else if (type === 'success') {
        console.log(`✅ ${message}`)
      } else {
        console.log(`ℹ️  ${message}`)
      }
    },

    async loadSubjects() {
      try {
        const response = await this.adminService.getSubjects()
        this.subjects = response
      } catch (error) {
        console.error('Failed to load subjects:', error)
        this.showToast('Failed to load subjects: ' + (error.response?.data?.error || error.message), 'error')
      }
    },

    async loadChapters(subjectId) {
      if (!subjectId) {
        this.chapters = []
        return
      }
      
      this.loadingChapters = true
      try {
        const response = await this.adminService.getChapters(subjectId)
        this.chapters = response
      } catch (error) {
        console.error('Failed to load chapters:', error)
        this.showToast('Failed to load chapters: ' + (error.response?.data?.error || error.message), 'error')
        this.chapters = []
      } finally {
        this.loadingChapters = false
      }
    },

    async onSubjectChange() {
      // Reset chapter selection when subject changes
      this.form.chapter_id = ''
      this.chapters = []
      
      if (this.form.subject_id) {
        await this.loadChapters(this.form.subject_id)
      }
    },

    async generateQuestions() {
      this.generating = true
      try {
        const response = await this.aiService.generateQuestions(this.form)
        
        this.generatedQuestions = response.questions
        this.verificationTaskId = response.verification_task_id
        this.aiStatus = 'Generation Complete - Verification Started'
        
        this.showToast('Questions generated! Verification in progress...', 'success')
        
        // Start polling for verification status
        if (this.verificationTaskId) {
          this.showVerificationModal = true
          this.startVerificationPolling()
        }
        
      } catch (error) {
        console.error('Failed to generate questions:', error)
        this.showToast(
          error.response?.data?.error || 'Failed to generate questions', 
          'error'
        )
      } finally {
        this.generating = false
      }
    },

    async startVerificationPolling() {
      if (!this.verificationTaskId) return
      
      this.verificationPolling = setInterval(async () => {
        try {
          const status = await aiService.getVerificationStatus(this.verificationTaskId)
          this.verificationStatus = status
          
          if (status.ready) {
            // Verification complete
            clearInterval(this.verificationPolling)
            this.verificationPolling = null
            
            if (status.successful) {
              const result = status.result
              this.verificationProgress = result
              this.aiStatus = `Verification Complete - ${result.verified_count}/${result.total_questions} verified`
              
              this.showToast(
                `Verification complete! ${result.verified_count} questions verified (${result.success_rate.toFixed(1)}% success rate)`,
                'success'
              )
              
              // Refresh questions data
              await this.loadQuestionVerificationSummary(this.generatedQuestions.id)
              
            } else {
              this.aiStatus = 'Verification Failed'
              this.showToast('Verification failed: ' + (status.error || 'Unknown error'), 'error')
            }
          } else {
            // Update progress
            this.verificationProgress = status.info
            if (status.info && status.info.status) {
              this.aiStatus = status.info.status
            }
          }
        } catch (error) {
          console.error('Failed to get verification status:', error)
          clearInterval(this.verificationPolling)
          this.verificationPolling = null
        }
      }, 2000) // Poll every 2 seconds
    },

    async loadQuestionVerificationSummary(questionId) {
      try {
        const summary = await aiService.getQuestionVerificationSummary(questionId)
        this.verificationProgress = summary
        this.generatedQuestions.verification_summary = summary
      } catch (error) {
        console.error('Failed to load verification summary:', error)
      }
    },

    async retryVerification(questionId) {
      try {
        const response = await aiService.retryVerification({ 
          question_id: questionId,
          verification_threshold: this.form.verification_threshold,
          max_retry_attempts: this.form.max_retry_attempts,
          fallback_strategy: this.form.fallback_strategy
        })
        
        this.verificationTaskId = response.task_id
        this.startVerificationPolling()
        
        this.showToast('Verification retry started...', 'info')
      } catch (error) {
        console.error('Failed to retry verification:', error)
        this.showToast('Failed to retry verification', 'error')
      }
    },

    async manualApproveQuestion(questionId, reason = '') {
      try {
        await aiService.manualApproveQuestion(questionId, reason)
        this.showToast('Question manually approved', 'success')
        
        // Refresh verification summary
        if (this.generatedQuestions && this.generatedQuestions.id) {
          await this.loadQuestionVerificationSummary(this.generatedQuestions.id)
        }
      } catch (error) {
        console.error('Failed to approve question:', error)
        this.showToast('Failed to approve question', 'error')
      }
    },

    closeVerificationModal() {
      this.showVerificationModal = false
      if (this.verificationPolling) {
        clearInterval(this.verificationPolling)
        this.verificationPolling = null
      }
    },

    async saveQuestions() {
      this.saving = true
      try {
        // Save questions to the question bank
        this.aiStatus = 'Questions Saved'
        this.showToast('Questions saved to question bank successfully!', 'success')
        await this.loadRecentGenerations()
      } catch (error) {
        console.error('Failed to save questions:', error)
        this.showToast('Failed to save questions', 'error')
      } finally {
        this.saving = false
      }
    },

    regenerateQuestions() {
      this.generatedQuestions = null
      this.generateQuestions()
    },

    async loadRecentGenerations() {
      try {
        // Mock data for now - implement backend endpoint later
        this.recentGenerations = [
          {
            id: 1,
            topic: 'Python Functions',
            difficulty: 'medium',
            question_count: 10,
            status: 'saved',
            created_at: new Date().toISOString()
          }
        ]
      } catch (error) {
        console.error('Failed to load recent generations:', error)
      }
    },

    checkAIStatus() {
      // Check if AI service is available
      this.aiStatus = 'AI Ready'
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString() + ' ' + 
             new Date(dateString).toLocaleTimeString()
    }
  }
}
</script>

<style scoped>
.questions-preview {
  max-height: 600px;
  overflow-y: auto;
}

.form-range::-webkit-slider-thumb {
  background: #0d6efd;
}

.form-range::-moz-range-thumb {
  background: #0d6efd;
  border: none;
}

.progress-bar-animated {
  animation: progress-bar-stripes 1s linear infinite;
}

.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-2px);
}

.badge {
  font-size: 0.75em;
}
</style>
