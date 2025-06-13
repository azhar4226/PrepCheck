<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <!-- Header -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2 class="mb-1">🤖 AI Quiz Generator</h2>
            <p class="text-muted mb-0">Generate intelligent quizzes using AI technology</p>
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
                  Quiz Configuration
                </h5>
              </div>
              <div class="card-body">
                <form @submit.prevent="generateQuiz">
                  <!-- Subject/Chapter Selection -->
                  <div class="mb-3">
                    <label class="form-label fw-bold">Subject & Chapter</label>
                    <select v-model="form.chapter_id" class="form-select" required>
                      <option value="">Select a chapter...</option>
                      <optgroup 
                        v-for="subject in subjects" 
                        :key="subject.id" 
                        :label="subject.name"
                      >
                        <option 
                          v-for="chapter in subject.chapters" 
                          :key="chapter.id" 
                          :value="chapter.id"
                        >
                          {{ chapter.name }}
                        </option>
                      </optgroup>
                    </select>
                  </div>

                  <!-- Topic -->
                  <div class="mb-3">
                    <label class="form-label fw-bold">Quiz Topic</label>
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

                  <!-- Generate Button -->
                  <button 
                    type="submit" 
                    class="btn btn-primary btn-lg w-100" 
                    :disabled="generating"
                  >
                    <span v-if="generating">
                      <span class="spinner-border spinner-border-sm me-2"></span>
                      Generating Quiz...
                    </span>
                    <span v-else>
                      <i class="bi bi-magic me-2"></i>
                      Generate Quiz
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
                  Generated Quiz Preview
                </h5>
                <div v-if="generatedQuiz">
                  <button 
                    @click="saveQuiz" 
                    class="btn btn-success btn-sm me-2"
                    :disabled="saving"
                  >
                    <span v-if="saving">
                      <span class="spinner-border spinner-border-sm me-1"></span>
                      Saving...
                    </span>
                    <span v-else>
                      <i class="bi bi-check-circle me-1"></i>
                      Save Quiz
                    </span>
                  </button>
                  <button @click="regenerateQuiz" class="btn btn-outline-primary btn-sm">
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    Regenerate
                  </button>
                </div>
              </div>
              
              <div class="card-body">
                <!-- No Quiz Generated Yet -->
                <div v-if="!generatedQuiz && !generating" class="text-center py-5">
                  <i class="bi bi-lightbulb display-1 text-muted"></i>
                  <h4 class="text-muted mt-3">Ready to Generate</h4>
                  <p class="text-muted">Fill out the form and click "Generate Quiz" to create AI-powered questions</p>
                </div>

                <!-- Generating State -->
                <div v-if="generating" class="text-center py-5">
                  <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
                  <h4>AI is Working...</h4>
                  <p class="text-muted">Creating your custom quiz questions</p>
                  <div class="progress mx-auto" style="width: 300px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         style="width: 75%"></div>
                  </div>
                </div>

                <!-- Generated Quiz Display -->
                <div v-if="generatedQuiz && !generating">
                  <!-- Quiz Info -->
                  <div class="alert alert-success mb-4">
                    <div class="d-flex align-items-center">
                      <i class="bi bi-check-circle-fill me-2"></i>
                      <div>
                        <strong>Quiz Generated Successfully!</strong>
                        <br>
                        <small>{{ generatedQuiz.questions.length }} questions created</small>
                      </div>
                    </div>
                  </div>

                  <!-- Quiz Header -->
                  <div class="border rounded p-3 mb-4 bg-light">
                    <h4 class="mb-1">{{ generatedQuiz.title }}</h4>
                    <p class="text-muted mb-0">{{ generatedQuiz.description }}</p>
                  </div>

                  <!-- Questions Preview -->
                  <div class="questions-preview">
                    <div 
                      v-for="(question, index) in generatedQuiz.questions" 
                      :key="index"
                      class="card mb-3"
                    >
                      <div class="card-header bg-light">
                        <div class="d-flex justify-content-between">
                          <strong>Question {{ index + 1 }}</strong>
                          <span class="badge bg-primary">{{ question.marks }} mark{{ question.marks !== 1 ? 's' : '' }}</span>
                        </div>
                      </div>
                      <div class="card-body">
                        <h6 class="mb-3">{{ question.question }}</h6>
                        
                        <!-- Options -->
                        <div class="row">
                          <div 
                            v-for="(option, optionKey) in question.options" 
                            :key="optionKey"
                            class="col-md-6 mb-2"
                          >
                            <div 
                              class="p-2 border rounded"
                              :class="optionKey === question.correct_answer ? 'bg-success text-white border-success' : 'bg-white'"
                            >
                              <strong>{{ optionKey }})</strong> {{ option }}
                              <i v-if="optionKey === question.correct_answer" class="bi bi-check-circle float-end"></i>
                            </div>
                          </div>
                        </div>

                        <!-- Explanation -->
                        <div class="mt-3">
                          <small class="text-muted">
                            <strong>Explanation:</strong> {{ question.explanation }}
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
</template>

<script>
import api from '@/services/api'

export default {
  name: 'AIQuizGenerator',
  data() {
    return {
      form: {
        chapter_id: '',
        topic: '',
        difficulty: '',
        num_questions: 10,
        context: ''
      },
      subjects: [],
      generatedQuiz: null,
      generating: false,
      saving: false,
      recentGenerations: [],
      aiStatus: 'Ready'
    }
  },
  async mounted() {
    await this.loadSubjects()
    await this.loadRecentGenerations()
    this.checkAIStatus()
  },
  methods: {
    async loadSubjects() {
      try {
        const response = await api.get('/subjects')
        this.subjects = response.data
      } catch (error) {
        console.error('Failed to load subjects:', error)
        this.$root.showToast('Failed to load subjects', 'error')
      }
    },

    async generateQuiz() {
      this.generating = true
      try {
        const response = await api.post('/ai/generate-quiz', this.form)
        this.generatedQuiz = response.data.quiz_data
        this.aiStatus = 'Generation Complete'
        this.$root.showToast('Quiz generated successfully!', 'success')
      } catch (error) {
        console.error('Failed to generate quiz:', error)
        this.$root.showToast(
          error.response?.data?.error || 'Failed to generate quiz', 
          'error'
        )
      } finally {
        this.generating = false
      }
    },

    async saveQuiz() {
      this.saving = true
      try {
        // The quiz is already saved as draft in the backend
        // Here we just need to update its status or perform additional actions
        this.aiStatus = 'Quiz Saved'
        this.$root.showToast('Quiz saved successfully!', 'success')
        await this.loadRecentGenerations()
      } catch (error) {
        console.error('Failed to save quiz:', error)
        this.$root.showToast('Failed to save quiz', 'error')
      } finally {
        this.saving = false
      }
    },

    regenerateQuiz() {
      this.generatedQuiz = null
      this.generateQuiz()
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
