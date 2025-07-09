<template>
  <div class="test-generator">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card bg-gradient-primary text-black">
          <div class="card-body">
            <h2 class="card-title mb-2">
              <i class="bi bi-gear me-2"></i>
              UGC NET Mock Test
            </h2>
            <p class="card-text mb-0">
              Create a mock test (Paper 1 + Paper 2) to simulate actual UGC NET exam
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
                <div class="col-md-12">
                  <label class="form-label">Test Title</label>
                  <input 
                    v-model="form.title" 
                    type="text" 
                    class="form-control"
                    placeholder="Enter test title"
                    required
                  >
                </div>
              </div>

        
              <!-- User Subject Info (Read-only) -->
              <div class="row mb-4">
                <div class="col-md-12">
                  <label class="form-label">Your Registered Subject</label>
                  <div class="form-control-plaintext bg-light border rounded p-2">
                    <span v-if="userSubject">
                      <strong>{{ userSubject.name }}</strong> ({{ userSubject.subject_code }})
                    </span>
                    <span v-else class="text-muted">Loading your subject...</span>
                  </div>
                  <div class="form-text">Paper 2 will be based on this subject. Paper 1 is common for all subjects.</div>
                </div>
              </div>

              <!-- Description -->
              <div class="mb-4">
                <label class="form-label">Description (Optional)</label>
                <textarea 
                  v-model="form.description" 
                  class="form-control" 
                  rows="3"
                  placeholder="Add a description for this mock test..."
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
              <div class="col-4">
                <div class="border rounded p-2">
                  <div class="text-primary">
                    <strong>150</strong>
                  </div>
                  <small class="text-muted">Questions</small>
                </div>
              </div>
              <div class="col-4">
                <div class="border rounded p-2">
                  <div class="text-success">
                    <strong>300</strong>
                  </div>
                  <small class="text-muted">Marks</small>
                </div>
              </div>
              <div class="col-4">
                <div class="border rounded p-2">
                  <div class="text-info">
                    <strong>180</strong>
                  </div>
                  <small class="text-muted">Minutes</small>
                </div>
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
                <li>Mock tests simulate the actual UGC NET exam format</li>
                <li>Paper 1: 50 questions (Teaching & Research Aptitude)</li>
                <li>Paper 2: 100 questions (Your subject-specific questions)</li>
                <li>Each question carries 2 marks (no negative marking)</li>
                <li>Total time: 3 hours for 150 questions</li>
                <li>Questions are randomly selected to ensure fairness</li>
              </ul>
            </div>
            
            <div class="alert alert-warning border-0">
              <h6 class="alert-heading">
                <i class="bi bi-exclamation-triangle me-1"></i>Important
              </h6>
              <p class="mb-0 small">
                Mock tests use your registered subject automatically. Ensure you have registered for the correct subject in your profile before taking mock tests.
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
    const userSubject = ref(null)
    const chapters = ref([])
    const loading = ref(false)
    const generatedTest = ref(null)
    
    // Form data for Mock Test (Fixed configuration)
    const form = ref({
      title: '',
      description: '',
      // Fixed Mock Test configuration - cannot be changed by user
      total_questions: 150, // Paper 1 (50) + Paper 2 (100)
      time_limit: 180, // Fixed 3 hours = 180 minutes
      paper_type: 'mock', // Mock test includes both papers
      // Fixed difficulty distribution as per UGC NET pattern
      easy_percentage: 30,
      medium_percentage: 50,
      hard_percentage: 20,
      weightage_config: null // Will use fixed weightage from backend
    })

    // Computed properties
    const totalDifficultyPercentage = computed(() => {
      return form.value.easy_percentage + form.value.medium_percentage + form.value.hard_percentage
    })

    const totalWeightage = computed(() => {
      return Object.values(form.value.weightage_config).reduce((sum, weight) => sum + (weight || 0), 0)
    })

    const isFormValid = computed(() => {
      return form.value.title && userSubject.value
      // No need to validate time/questions as they are fixed for mock tests
      // User subject is fetched automatically, no selection needed
    })

    // Watch removed as no subject selection needed
    
    // Methods
    const loadUserSubject = async () => {
      try {
        // Get user's registered subject from profile
        const userData = await api.user.getProfile()
        console.log('🔍 User profile data:', userData)
        
        if (userData && userData.subject_id) {
          const subjectId = userData.subject_id
          // Get subject details
          const subjectResult = await api.ugcNet.getSubjects()
          if (subjectResult.success) {
            const subject = subjectResult.data.subjects.find(s => s.id === subjectId)
            if (subject) {
              userSubject.value = subject
              // Set default title
              form.value.title = `${subject.name} Mock Test - ${new Date().toLocaleDateString()}`
            }
          }
        } else {
          console.warn('User has no registered UGC NET subject')
        }
      } catch (error) {
        console.error('Failed to load user subject:', error)
      }
    }
    const loadChapters = async (subjectId) => {
      // For mock tests, we don't need to load chapters for user configuration
      // The backend will use fixed weightage for all chapters
      try {
        console.log('Mock test will use fixed weightage for all chapters of subject:', subjectId)
      } catch (error) {
        console.error('Error:', error)
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
        alert('Please fill all required fields. Make sure you have a registered UGC NET subject.')
        return
      }

      if (!userSubject.value) {
        alert('Please register for a UGC NET subject in your profile before generating mock tests.')
        return
      }

      loading.value = true
      
      try {
        const testConfig = {
          title: form.value.title,
          description: form.value.description,
          subject_id: userSubject.value.id, // Use user's registered subject
          // Fixed Mock Test configuration
          total_questions: form.value.total_questions, // 150 questions (50 Paper 1 + 100 Paper 2)
          time_limit: form.value.time_limit, // 180 minutes (3 hours)
          paper_type: 'mock', // Both Paper 1 and Paper 2
          // Fixed difficulty and weightage - no user customization
          difficulty_distribution: {
            easy: form.value.easy_percentage,
            medium: form.value.medium_percentage,
            hard: form.value.hard_percentage
          },
          // No custom weightage_config - backend will use fixed UGC NET pattern
          use_fixed_weightage: true
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
      await loadUserSubject()
    })

    return {
      subjects,
      userSubject,
      chapters,
      form,
      loading,
      generatedTest,
      totalDifficultyPercentage,
      totalWeightage,
      isFormValid,
      loadUserSubject,
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
