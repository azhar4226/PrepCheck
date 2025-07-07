<template>
  <div class="test-generator">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card bg-gradient-primary text-white">
          <div class="card-body">
            <h2 class="card-title mb-2">
              <i class="bi bi-gear-fill me-2"></i>
              Generate UGC NET Mock Test
            </h2>
            <p class="card-text mb-0">
              Create a customized mock test based on weightage and difficulty preferences
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Form -->
    <div class="row">
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-sliders me-2"></i>Test Configuration
            </h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="generateTest">
              <!-- Basic Settings -->
              <div class="row mb-4">
                <div class="col-md-6">
                  <label class="form-label">Test Title</label>
                  <input 
                    v-model="form.title" 
                    type="text" 
                    class="form-control"
                    placeholder="Enter test title"
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Subject</label>
                  <select v-model="form.subject_id" class="form-select" required>
                    <option value="">Select a subject</option>
                    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                      {{ subject.name }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="row mb-4">
                <div class="col-md-4">
                  <label class="form-label">Total Questions</label>
                  <input 
                    v-model.number="form.total_questions" 
                    type="number" 
                    class="form-control"
                    min="1"
                    max="100"
                    required
                  >
                </div>
                <div class="col-md-4">
                  <label class="form-label">Time Limit (minutes)</label>
                  <input 
                    v-model.number="form.time_limit" 
                    type="number" 
                    class="form-control"
                    min="10"
                    max="300"
                    required
                  >
                </div>
                <div class="col-md-4">
                  <label class="form-label">Paper Type</label>
                  <select v-model="form.paper_type" class="form-select" required>
                    <option value="paper1">Paper 1</option>
                    <option value="paper2">Paper 2</option>
                  </select>
                </div>
              </div>

              <!-- Difficulty Distribution -->
              <div class="mb-4">
                <h6 class="mb-3">
                  <i class="bi bi-bar-chart-steps me-2"></i>Difficulty Distribution
                </h6>
                <div class="row">
                  <div class="col-md-4">
                    <label class="form-label">Easy Questions (%)</label>
                    <input 
                      v-model.number="form.easy_percentage" 
                      type="number" 
                      class="form-control"
                      min="0"
                      max="100"
                      @input="validatePercentages"
                    >
                    <div class="progress mt-2" style="height: 6px;">
                      <div 
                        class="progress-bar bg-success" 
                        :style="{ width: form.easy_percentage + '%' }"
                      ></div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Medium Questions (%)</label>
                    <input 
                      v-model.number="form.medium_percentage" 
                      type="number" 
                      class="form-control"
                      min="0"
                      max="100"
                      @input="validatePercentages"
                    >
                    <div class="progress mt-2" style="height: 6px;">
                      <div 
                        class="progress-bar bg-warning" 
                        :style="{ width: form.medium_percentage + '%' }"
                      ></div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Hard Questions (%)</label>
                    <input 
                      v-model.number="form.hard_percentage" 
                      type="number" 
                      class="form-control"
                      min="0"
                      max="100"
                      @input="validatePercentages"
                    >
                    <div class="progress mt-2" style="height: 6px;">
                      <div 
                        class="progress-bar bg-danger" 
                        :style="{ width: form.hard_percentage + '%' }"
                      ></div>
                    </div>
                  </div>
                </div>
                <small class="text-muted">
                  Total: {{ totalDifficultyPercentage }}% 
                  <span v-if="totalDifficultyPercentage !== 100" class="text-warning">
                    (Should equal 100%)
                  </span>
                </small>
              </div>

              <!-- Weightage Configuration -->
              <div class="mb-4" v-if="chapters.length > 0">
                <h6 class="mb-3">
                  <i class="bi bi-pie-chart me-2"></i>Chapter Weightage Configuration
                </h6>
                <div class="alert alert-info">
                  <i class="bi bi-info-circle me-2"></i>
                  Adjust the weightage for each chapter. Questions will be selected based on these percentages.
                </div>
                <div class="row">
                  <div v-for="chapter in chapters" :key="chapter.id" class="col-md-6 col-lg-4 mb-3">
                    <div class="card border-0 bg-light">
                      <div class="card-body">
                        <h6 class="card-title small">{{ chapter.name }}</h6>
                        <div class="input-group input-group-sm">
                          <input 
                            v-model.number="form.weightage_config[chapter.id]" 
                            type="number" 
                            class="form-control"
                            min="0"
                            max="100"
                            @input="calculateWeightageTotal"
                          >
                          <span class="input-group-text">%</span>
                        </div>
                        <small class="text-muted">
                          Default: {{ chapter.weightage_paper2 }}%
                        </small>
                        <div class="progress mt-1" style="height: 4px;">
                          <div 
                            class="progress-bar" 
                            :style="{ width: (form.weightage_config[chapter.id] || 0) + '%' }"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                  <small class="text-muted">
                    Total Weightage: {{ totalWeightage }}%
                    <span v-if="totalWeightage !== 100" class="text-warning">
                      (Should equal 100%)
                    </span>
                  </small>
                  <button 
                    @click="resetToDefaultWeightage" 
                    type="button" 
                    class="btn btn-sm btn-outline-secondary"
                  >
                    <i class="bi bi-arrow-clockwise me-1"></i>Reset to Default
                  </button>
                </div>
              </div>

              <!-- Description -->
              <div class="mb-4">
                <label class="form-label">Description (Optional)</label>
                <textarea 
                  v-model="form.description" 
                  class="form-control" 
                  rows="3"
                  placeholder="Add a description for this test..."
                ></textarea>
              </div>

              <!-- Form Actions -->
              <div class="d-flex justify-content-between">
                <button 
                  @click="$router.push('/ugc-net')" 
                  type="button" 
                  class="btn btn-outline-secondary"
                >
                  <i class="bi bi-arrow-left me-1"></i>Back to Dashboard
                </button>
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="loading || !isFormValid"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  <i v-else class="bi bi-gear-fill me-1"></i>
                  {{ loading ? 'Generating...' : 'Generate Test' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Right Sidebar - Preview & Tips -->
      <div class="col-lg-4">
        <!-- Test Preview -->
        <div class="card mb-4">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="bi bi-eye me-2"></i>Test Preview
            </h6>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <strong>{{ form.title || 'Untitled Test' }}</strong>
              <div class="text-muted small">{{ form.description || 'No description' }}</div>
            </div>
            <div class="row text-center">
              <div class="col-6">
                <div class="border rounded p-2">
                  <div class="text-primary">
                    <strong>{{ form.total_questions || 0 }}</strong>
                  </div>
                  <small class="text-muted">Questions</small>
                </div>
              </div>
              <div class="col-6">
                <div class="border rounded p-2">
                  <div class="text-info">
                    <strong>{{ form.time_limit || 0 }}</strong>
                  </div>
                  <small class="text-muted">Minutes</small>
                </div>
              </div>
            </div>
            
            <!-- Difficulty Preview -->
            <div class="mt-3" v-if="totalDifficultyPercentage === 100">
              <small class="text-muted d-block mb-2">Difficulty Breakdown:</small>
              <div class="progress" style="height: 20px;">
                <div 
                  class="progress-bar bg-success" 
                  :style="{ width: form.easy_percentage + '%' }"
                >
                  <small v-if="form.easy_percentage > 15">{{ form.easy_percentage }}%</small>
                </div>
                <div 
                  class="progress-bar bg-warning" 
                  :style="{ width: form.medium_percentage + '%' }"
                >
                  <small v-if="form.medium_percentage > 15">{{ form.medium_percentage }}%</small>
                </div>
                <div 
                  class="progress-bar bg-danger" 
                  :style="{ width: form.hard_percentage + '%' }"
                >
                  <small v-if="form.hard_percentage > 15">{{ form.hard_percentage }}%</small>
                </div>
              </div>
              <div class="d-flex justify-content-between text-xs mt-1">
                <small class="text-success">Easy</small>
                <small class="text-warning">Medium</small>
                <small class="text-danger">Hard</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Tips -->
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="bi bi-lightbulb me-2"></i>Tips
            </h6>
          </div>
          <div class="card-body">
            <div class="alert alert-info border-0">
              <h6 class="alert-heading">
                <i class="bi bi-info-circle me-1"></i>Test Generation Tips
              </h6>
              <ul class="mb-0 small">
                <li>Start with 10-15 questions for quick practice</li>
                <li>Use 30-50 questions for full mock tests</li>
                <li>Balance difficulty: 40% easy, 40% medium, 20% hard</li>
                <li>Adjust chapter weightage based on your weak areas</li>
                <li>Allow 1.5-2 minutes per question for timing</li>
              </ul>
            </div>
            
            <div class="alert alert-warning border-0">
              <h6 class="alert-heading">
                <i class="bi bi-exclamation-triangle me-1"></i>Important
              </h6>
              <p class="mb-0 small">
                Ensure sufficient questions are available in the database for your selected configuration.
                The system will inform you if adjustments are needed.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Modal -->
    <div class="modal fade" id="successModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title">
              <i class="bi bi-check-circle me-2"></i>Test Generated Successfully!
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="generatedTest">
            <div class="text-center mb-3">
              <i class="bi bi-clipboard-check display-4 text-success"></i>
            </div>
            <h6 class="text-center">{{ generatedTest.title }}</h6>
            <div class="row text-center mt-3">
              <div class="col-4">
                <strong class="text-primary">{{ generatedTest.total_questions }}</strong>
                <div class="small text-muted">Questions</div>
              </div>
              <div class="col-4">
                <strong class="text-info">{{ generatedTest.time_limit }}</strong>
                <div class="small text-muted">Minutes</div>
              </div>
              <div class="col-4">
                <strong class="text-success">{{ generatedTest.subject_name }}</strong>
                <div class="small text-muted">Subject</div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button 
              @click="startGeneratedTest" 
              class="btn btn-success"
            >
              <i class="bi bi-play-fill me-1"></i>Start Test Now
            </button>
            <button 
              @click="goToDashboard" 
              class="btn btn-outline-primary"
            >
              <i class="bi bi-house me-1"></i>Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'
import { Modal } from 'bootstrap'

export default {
  name: 'TestGenerator',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // Reactive data
    const subjects = ref([])
    const chapters = ref([])
    const loading = ref(false)
    const generatedTest = ref(null)
    
    // Form data
    const form = ref({
      title: '',
      description: '',
      subject_id: '',
      total_questions: 10,
      time_limit: 45,
      paper_type: 'paper2',
      easy_percentage: 40,
      medium_percentage: 40,
      hard_percentage: 20,
      weightage_config: {}
    })

    // Computed properties
    const totalDifficultyPercentage = computed(() => {
      return form.value.easy_percentage + form.value.medium_percentage + form.value.hard_percentage
    })

    const totalWeightage = computed(() => {
      return Object.values(form.value.weightage_config).reduce((sum, weight) => sum + (weight || 0), 0)
    })

    const isFormValid = computed(() => {
      return form.value.title &&
             form.value.subject_id &&
             form.value.total_questions > 0 &&
             form.value.time_limit > 0 &&
             totalDifficultyPercentage.value === 100
    })

    // Watch subject selection to load chapters
    watch(() => form.value.subject_id, async (newSubjectId) => {
      if (newSubjectId) {
        await loadChapters(newSubjectId)
      }
    })

    // Methods
    const loadSubjects = async () => {
      try {
        const result = await api.ugcNet.getSubjects()
        if (result.success) {
          subjects.value = result.data.subjects || []
          
          // Pre-select subject from query params
          const subjectId = route.query.subject
          if (subjectId) {
            form.value.subject_id = parseInt(subjectId)
          }
        }
      } catch (error) {
        console.error('Failed to load subjects:', error)
      }
    }

    const loadChapters = async (subjectId) => {
      try {
        const result = await api.ugcNet.getSubjectChapters(subjectId)
        if (result.success) {
          chapters.value = result.data.chapters || []
          resetToDefaultWeightage()
        }
      } catch (error) {
        console.error('Failed to load chapters:', error)
      }
    }

    const resetToDefaultWeightage = () => {
      form.value.weightage_config = {}
      chapters.value.forEach(chapter => {
        form.value.weightage_config[chapter.id] = chapter.weightage_paper2 || 0
      })
    }

    const validatePercentages = () => {
      // Auto-adjust percentages to ensure they don't exceed 100%
      const total = totalDifficultyPercentage.value
      if (total > 100) {
        const excess = total - 100
        // Proportionally reduce all percentages
        const factor = 100 / total
        form.value.easy_percentage = Math.round(form.value.easy_percentage * factor)
        form.value.medium_percentage = Math.round(form.value.medium_percentage * factor)
        form.value.hard_percentage = Math.round(form.value.hard_percentage * factor)
      }
    }

    const calculateWeightageTotal = () => {
      // This is called when weightage inputs change
      // Could add auto-adjustment logic here if needed
    }

    const generateTest = async () => {
      if (!isFormValid.value) {
        alert('Please fill all required fields and ensure percentages total 100%')
        return
      }

      loading.value = true
      
      try {
        const testConfig = {
          title: form.value.title,
          description: form.value.description,
          subject_id: form.value.subject_id,
          total_questions: form.value.total_questions,
          time_limit: form.value.time_limit,
          paper_type: form.value.paper_type,
          easy_percentage: form.value.easy_percentage,
          medium_percentage: form.value.medium_percentage,
          hard_percentage: form.value.hard_percentage,
          weightage_config: form.value.weightage_config
        }

        const result = await api.ugcNet.generateMockTest(testConfig)
        
        if (result.success) {
          generatedTest.value = result.data.mock_test
          const modal = new Modal(document.getElementById('successModal'))
          modal.show()
        } else {
          alert('Failed to generate test: ' + result.error)
        }
      } catch (error) {
        console.error('Failed to generate test:', error)
        alert('Failed to generate test')
      } finally {
        loading.value = false
      }
    }

    const startGeneratedTest = async () => {
      if (!generatedTest.value) return
      
      try {
        console.log('🔍 TestGenerator: Starting test for ID:', generatedTest.value.id)
        const result = await api.ugcNet.startAttempt(generatedTest.value.id)
        console.log('🔍 TestGenerator: Start attempt result:', result)
        
        if (result.success && result.data && result.data.attempt) {
          const attemptId = result.data.attempt.id
          const route = `/ugc-net/test/${generatedTest.value.id}/attempt/${attemptId}`
          console.log('🔍 TestGenerator: Navigating to:', route)
          router.push(route)
        } else {
          console.error('❌ TestGenerator: Invalid response structure:', result)
          alert('Failed to start test: Invalid response from server')
        }
      } catch (error) {
        console.error('❌ TestGenerator: Failed to start test:', error)
        alert('Failed to start test: ' + error.message)
      }
    }

    const goToDashboard = () => {
      router.push('/ugc-net')
    }

    // Lifecycle
    onMounted(async () => {
      await loadSubjects()
      
      // Set default title based on subject
      if (form.value.subject_id) {
        const subject = subjects.value.find(s => s.id === form.value.subject_id)
        if (subject) {
          form.value.title = `${subject.name} Mock Test`
        }
      }
    })

    return {
      subjects,
      chapters,
      form,
      loading,
      generatedTest,
      totalDifficultyPercentage,
      totalWeightage,
      isFormValid,
      loadSubjects,
      loadChapters,
      resetToDefaultWeightage,
      validatePercentages,
      calculateWeightageTotal,
      generateTest,
      startGeneratedTest,
      goToDashboard
    }
  }
}
</script>

<style scoped>
.test-generator {
  padding: 1rem;
}

.progress {
  border-radius: 10px;
}

.input-group-sm .form-control {
  border-radius: 0.375rem 0 0 0.375rem;
}

.card {
  transition: transform 0.2s ease-in-out;
}

.alert {
  border-radius: 10px;
}

.text-xs {
  font-size: 0.75rem;
}
</style>
