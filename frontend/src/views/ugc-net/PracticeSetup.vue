<template>
  <div class="practice-test-setup">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card bg-gradient-primary text-white">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-8">
                <h2 class="card-title mb-2">
                  <i class="bi bi-play-circle me-2"></i>
                  Practice Test Setup
                </h2>
                <p class="card-text mb-0">
                  Select chapters and configure your practice test for targeted preparation
                </p>
              </div>
              <div class="col-md-4 text-md-end">
                <router-link to="/ugc-net" class="btn btn-outline-light">
                  <i class="bi bi-arrow-left me-1"></i>
                  Back to Dashboard
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Configuration Form -->
    <div class="row">
      <div class="col-lg-8 mx-auto">
        <div class="card shadow">
          <div class="card-body p-4">
            <form @submit.prevent="generatePracticeTest">
              <!-- Paper Type Selection -->
              <div class="mb-4">
                <label class="form-label fw-bold">
                  <i class="bi bi-file-earmark-text me-2"></i>Paper Selection
                </label>
                <div class="row">
                  <div class="col-md-6">
                    <div class="form-check">
                      <input 
                        id="paper1" 
                        v-model="config.paper_type" 
                        value="paper1" 
                        class="form-check-input" 
                        type="radio"
                        @change="onPaperTypeChange"
                      />
                      <label for="paper1" class="form-check-label">
                        <strong>Paper 1</strong> - Teaching and Research Aptitude
                        <div class="small text-muted">General aptitude questions (common for all subjects)</div>
                      </label>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="form-check">
                      <input 
                        id="paper2" 
                        v-model="config.paper_type" 
                        value="paper2" 
                        class="form-check-input" 
                        type="radio"
                        @change="onPaperTypeChange"
                      />
                      <label for="paper2" class="form-check-label">
                        <strong>Paper 2</strong> - Subject-specific Knowledge
                        <div class="small text-muted">Questions from your registered subject</div>
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Subject Selection (only for Paper 2) -->
              <div v-if="config.paper_type === 'paper2'" class="mb-4">
                <label class="form-label fw-bold">
                  <i class="bi bi-book me-2"></i>Subject Selection
                </label>
                <select 
                  v-model="config.subject_id" 
                  class="form-select form-select-lg"
                  required
                  @change="onSubjectChange"
                >
                  <option value="">Select a subject...</option>
                  <option 
                    v-for="subject in subjects" 
                    :key="subject.id" 
                    :value="subject.id"
                  >
                    {{ subject.name }} ({{ subject.subject_code }})
                  </option>
                </select>
                <div v-if="selectedSubject" class="form-text">
                  {{ selectedSubject.description }}
                </div>
              </div>

              <!-- Paper 1 Subject Info (auto-selected) -->
              <div v-else-if="config.paper_type === 'paper1'" class="mb-4">
                <label class="form-label fw-bold">
                  <i class="bi bi-book me-2"></i>Subject
                </label>
                <div class="form-control-plaintext bg-light border rounded p-2">
                  <i class="bi bi-info-circle text-primary me-2"></i>
                  <strong>Teaching and Research Aptitude</strong> - Common for all subjects
                </div>
              </div>

              <!-- Chapter Selection -->
              <div v-if="shouldShowChapterSelection" class="mb-4">
                <label class="form-label fw-bold">
                  <i class="bi bi-list-ul me-2"></i>Chapter Selection
                </label>
                <div v-if="loading.chapters" class="text-center py-3">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading chapters...</span>
                  </div>
                </div>
                <div v-else-if="chapters.length === 0" class="alert alert-warning">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  No chapters available for this {{ config.paper_type === 'paper1' ? 'paper' : 'subject' }}.
                </div>
                <div v-else>
                  <!-- Select All/None Controls -->
                  <div class="row mb-3">
                    <div class="col-md-6">
                      <button 
                        type="button" 
                        @click="selectAllChapters" 
                        class="btn btn-sm btn-outline-primary me-2"
                      >
                        <i class="bi bi-check-all me-1"></i>Select All
                      </button>
                      <button 
                        type="button" 
                        @click="selectNoneChapters" 
                        class="btn btn-sm btn-outline-secondary"
                      >
                        <i class="bi bi-x-square me-1"></i>Select None
                      </button>
                    </div>
                    <div class="col-md-6 text-md-end">
                      <small class="text-muted">
                        {{ selectedChapters.length }} of {{ chapters.length }} chapters selected
                      </small>
                    </div>
                  </div>

                  <!-- Chapter List -->
                  <div class="row">
                    <div v-for="chapter in chapters" :key="chapter.id" class="col-md-6 mb-2">
                      <div class="form-check">
                        <input 
                          :id="`chapter-${chapter.id}`"
                          v-model="config.selected_chapters" 
                          :value="chapter.id"
                          class="form-check-input" 
                          type="checkbox"
                        />
                        <label 
                          :for="`chapter-${chapter.id}`" 
                          class="form-check-label w-100"
                        >
                          <div class="d-flex justify-content-between align-items-start">
                            <div>
                              <strong>{{ chapter.name }}</strong>
                              <div class="small text-muted">{{ chapter.description }}</div>
                            </div>
                            <div class="text-end">
                              <small class="badge bg-light text-dark">
                                {{ chapter.verified_questions || 0 }} questions
                              </small>
                              <div v-if="chapter.weightage" class="small text-primary">
                                {{ chapter.weightage }}% weightage
                              </div>
                            </div>
                          </div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Question Configuration -->
              <div v-if="selectedChapters.length > 0" class="mb-4">
                <label class="form-label fw-bold">
                  <i class="bi bi-gear me-2"></i>Question Configuration
                </label>
                
                <!-- Total Questions and Time -->
                <div class="row mb-3">
                  <div class="col-md-4">
                    <label class="form-label">Total Questions</label>
                    <input 
                      v-model.number="config.total_questions" 
                      type="number" 
                      class="form-control" 
                      min="5" 
                      max="100" 
                      required
                      @input="updateDistribution"
                    />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Time Limit</label>
                    <div class="form-control-plaintext bg-light border rounded p-2">
                      <i class="bi bi-clock text-primary me-2"></i>
                      <strong>{{ calculateTimeLimit(config.total_questions) }}</strong>
                      <div class="small text-muted">1 hour per 50 questions</div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Distribution Mode</label>
                    <select 
                      v-model="config.distribution_mode" 
                      class="form-select"
                      @change="updateDistribution"
                    >
                      <option value="auto">Auto (Equal Distribution)</option>
                      <option value="weightage">Weightage-based</option>
                      <option value="manual">Manual</option>
                    </select>
                  </div>
                </div>

                <!-- Question Distribution Preview -->
                <div class="card bg-light">
                  <div class="card-header">
                    <h6 class="mb-0">Question Distribution Preview</h6>
                  </div>
                  <div class="card-body">
                    <div v-if="config.distribution_mode === 'manual'" class="mb-3">
                      <div v-for="chapter in selectedChapterDetails" :key="chapter.id" class="row mb-2 align-items-center">
                        <div class="col-md-6">
                          <small>{{ chapter.name }}</small>
                        </div>
                        <div class="col-md-3">
                          <input 
                            v-model.number="questionDistribution[chapter.id]" 
                            type="number" 
                            class="form-control form-control-sm" 
                            min="0" 
                            :max="chapter.verified_questions || 0"
                            @input="validateManualDistribution"
                          />
                        </div>
                        <div class="col-md-3">
                          <small class="text-muted">
                            Max: {{ chapter.verified_questions || 0 }}
                          </small>
                        </div>
                      </div>
                      <div class="border-top pt-2 mt-2">
                        <strong>Total: {{ manualTotal }} / {{ config.total_questions }}</strong>
                        <span v-if="manualTotal !== config.total_questions" class="text-danger ms-2">
                          (Adjust to match total)
                        </span>
                      </div>
                    </div>
                    <div v-else>
                      <div v-for="chapter in distributionPreview" :key="chapter.id" class="d-flex justify-content-between align-items-center mb-1">
                        <span>{{ chapter.name }}</span>
                        <span class="badge bg-primary">{{ chapter.questions }} questions</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Difficulty Configuration -->
              <div v-if="selectedChapters.length > 0" class="mb-4">
                <label class="form-label fw-bold">
                  <i class="bi bi-speedometer me-2"></i>Difficulty Distribution
                </label>
                <div class="row">
                  <div class="col-md-4">
                    <label class="form-label">Easy (%)</label>
                    <input 
                      v-model.number="config.difficulty_distribution.easy" 
                      type="number" 
                      class="form-control" 
                      min="0" 
                      max="100"
                      @input="validateDifficultyDistribution"
                    />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Medium (%)</label>
                    <input 
                      v-model.number="config.difficulty_distribution.medium" 
                      type="number" 
                      class="form-control" 
                      min="0" 
                      max="100"
                      @input="validateDifficultyDistribution"
                    />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Hard (%)</label>
                    <input 
                      v-model.number="config.difficulty_distribution.hard" 
                      type="number" 
                      class="form-control" 
                      min="0" 
                      max="100"
                      @input="validateDifficultyDistribution"
                    />
                  </div>
                </div>
                <div class="form-text">
                  Total: {{ difficultyTotal }}% 
                  <span v-if="difficultyTotal !== 100" class="text-danger">
                    (Must equal 100%)
                  </span>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="text-center">
                <button 
                  type="submit" 
                  class="btn btn-primary btn-lg me-3"
                  :disabled="!isFormValid || loading.generate"
                >
                  <span v-if="loading.generate" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-play-fill me-2"></i>
                  Generate Practice Test
                </button>
                <router-link to="/ugc-net" class="btn btn-outline-secondary btn-lg">
                  <i class="bi bi-x-circle me-1"></i>
                  Cancel
                </router-link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import ugcNetService from '@/services/ugcNetService'

export default {
  name: 'PracticeSetup',
  setup() {
    const router = useRouter()
    
    // Reactive data
    const subjects = ref([])
    const chapters = ref([])
    const loading = ref({
      subjects: false,
      chapters: false,
      generate: false
    })
    
    const config = ref({
      paper_type: 'paper2', // Default to Paper 2
      subject_id: '',
      selected_chapters: [],
      total_questions: 20,
      distribution_mode: 'auto',
      difficulty_distribution: {
        easy: 40,
        medium: 45, 
        hard: 15
      }
    })
    
    const questionDistribution = ref({})

    // Computed properties
    const selectedSubject = computed(() => {
      return subjects.value.find(s => s.id === config.value.subject_id)
    })

    const selectedChapters = computed(() => {
      return config.value.selected_chapters
    })

    const selectedChapterDetails = computed(() => {
      return chapters.value.filter(c => selectedChapters.value.includes(c.id))
    })

    // Show chapter selection when Paper 1 is selected OR when Paper 2 with subject selected
    const shouldShowChapterSelection = computed(() => {
      return config.value.paper_type === 'paper1' || 
             (config.value.paper_type === 'paper2' && config.value.subject_id)
    })

    const difficultyTotal = computed(() => {
      const dist = config.value.difficulty_distribution
      return dist.easy + dist.medium + dist.hard
    })

    const manualTotal = computed(() => {
      return Object.values(questionDistribution.value).reduce((sum, val) => sum + (val || 0), 0)
    })

    const distributionPreview = computed(() => {
      if (config.value.distribution_mode === 'manual') {
        return []
      }
      
      const totalQuestions = config.value.total_questions
      const selectedChaps = selectedChapterDetails.value
      
      if (selectedChaps.length === 0) return []
      
      if (config.value.distribution_mode === 'auto') {
        const questionsPerChapter = Math.floor(totalQuestions / selectedChaps.length)
        const remainder = totalQuestions % selectedChaps.length
        
        return selectedChaps.map((chapter, index) => ({
          id: chapter.id,
          name: chapter.name,
          questions: questionsPerChapter + (index < remainder ? 1 : 0)
        }))
      } else if (config.value.distribution_mode === 'weightage') {
        const totalWeightage = selectedChaps.reduce((sum, c) => sum + (c.weightage || 1), 0)
        
        return selectedChaps.map(chapter => {
          const weight = (chapter.weightage || 1) / totalWeightage
          const questions = Math.max(1, Math.round(totalQuestions * weight))
          return {
            id: chapter.id,
            name: chapter.name,
            questions
          }
        })
      }
      
      return []
    })

    const isFormValid = computed(() => {
      const hasValidSubject = config.value.paper_type === 'paper1' || 
                              (config.value.paper_type === 'paper2' && config.value.subject_id)
      
      return config.value.paper_type && 
             hasValidSubject && 
             selectedChapters.value.length > 0 && 
             config.value.total_questions > 0 &&
             difficultyTotal.value === 100 &&
             (config.value.distribution_mode !== 'manual' || manualTotal.value === config.value.total_questions)
    })

    // Methods
    const calculateTimeLimit = (totalQuestions) => {
      if (!totalQuestions || totalQuestions <= 0) return '0 minutes'
      
      // 1 hour (60 minutes) per 50 questions
      const totalMinutes = Math.ceil((totalQuestions / 50) * 60)
      
      if (totalMinutes < 60) {
        return `${totalMinutes} minutes`
      } else {
        const hours = Math.floor(totalMinutes / 60)
        const minutes = totalMinutes % 60
        if (minutes === 0) {
          return `${hours} hour${hours > 1 ? 's' : ''}`
        } else {
          return `${hours} hour${hours > 1 ? 's' : ''} ${minutes} minutes`
        }
      }
    }

    const onPaperTypeChange = () => {
      // Reset chapter and subject selection when changing paper type
      config.value.selected_chapters = []
      chapters.value = []
      
      if (config.value.paper_type === 'paper1') {
        // For Paper 1, auto-load general aptitude chapters
        config.value.subject_id = 1 // Assuming Paper 1 subject has ID 1
        loadChapters(1)
      } else {
        // For Paper 2, reset subject selection
        config.value.subject_id = ''
      }
    }

    const loadSubjects = async () => {
      loading.value.subjects = true
      try {
        const result = await ugcNetService.getSubjects()
        if (result.success) {
          subjects.value = result.data.subjects || []
        } else {
          console.error('Failed to load subjects:', result.error)
        }
      } catch (error) {
        console.error('Error loading subjects:', error)
      } finally {
        loading.value.subjects = false
      }
    }

    const loadChapters = async (subjectId) => {
      loading.value.chapters = true
      try {
        const result = await ugcNetService.getSubjectChapters(subjectId)
        if (result.success) {
          chapters.value = result.data.chapters || []
        } else {
          console.error('Failed to load chapters:', result.error)
          chapters.value = []
        }
      } catch (error) {
        console.error('Error loading chapters:', error)
        chapters.value = []
      } finally {
        loading.value.chapters = false
      }
    }

    const onSubjectChange = () => {
      config.value.selected_chapters = []
      chapters.value = []
      questionDistribution.value = {}
      
      if (config.value.subject_id) {
        loadChapters(config.value.subject_id)
      }
    }

    const selectAllChapters = () => {
      config.value.selected_chapters = chapters.value.map(c => c.id)
      updateDistribution()
    }

    const selectNoneChapters = () => {
      config.value.selected_chapters = []
      questionDistribution.value = {}
    }

    const updateDistribution = () => {
      if (config.value.distribution_mode === 'manual') {
        const questionsPerChapter = Math.floor(config.value.total_questions / selectedChapters.value.length)
        selectedChapters.value.forEach(chapterId => {
          questionDistribution.value[chapterId] = questionsPerChapter
        })
      }
    }

    const validateManualDistribution = () => {
      // Ensure manual distribution doesn't exceed available questions
      selectedChapterDetails.value.forEach(chapter => {
        const current = questionDistribution.value[chapter.id] || 0
        const max = chapter.verified_questions || 0
        if (current > max) {
          questionDistribution.value[chapter.id] = max
        }
      })
    }

    const validateDifficultyDistribution = () => {
      // Auto-adjust to ensure total is 100%
      const dist = config.value.difficulty_distribution
      const total = dist.easy + dist.medium + dist.hard
      
      if (total > 100) {
        // Scale down proportionally
        const factor = 100 / total
        dist.easy = Math.round(dist.easy * factor)
        dist.medium = Math.round(dist.medium * factor)
        dist.hard = 100 - dist.easy - dist.medium
      }
    }

    const generatePracticeTest = async () => {
      loading.value.generate = true
      try {
        // Calculate time limit: 1 hour per 50 questions
        const timeLimit = Math.ceil((config.value.total_questions / 50) * 60) // in minutes
        
        const testConfig = {
          ...config.value,
          time_limit: timeLimit,
          question_distribution: config.value.distribution_mode === 'manual' 
            ? questionDistribution.value 
            : null
        }
        
        const result = await ugcNetService.generatePracticeTest(testConfig)
        if (result.success) {
          // Navigate to practice test taking page
          router.push(`/ugc-net/practice/${result.data.attempt_id}/take`)
        } else {
          alert('Failed to generate practice test: ' + result.error)
        }
      } catch (error) {
        console.error('Error generating practice test:', error)
        alert('Failed to generate practice test. Please try again.')
      } finally {
        loading.value.generate = false
      }
    }

    // Watchers
    watch(selectedChapters, () => {
      updateDistribution()
    })

    // Lifecycle
    onMounted(() => {
      loadSubjects()
    })

    return {
      subjects,
      chapters,
      loading,
      config,
      questionDistribution,
      selectedSubject,
      selectedChapters,
      selectedChapterDetails,
      shouldShowChapterSelection,
      difficultyTotal,
      manualTotal,
      distributionPreview,
      isFormValid,
      calculateTimeLimit,
      onPaperTypeChange,
      onSubjectChange,
      selectAllChapters,
      selectNoneChapters,
      updateDistribution,
      validateManualDistribution,
      validateDifficultyDistribution,
      generatePracticeTest
    }
  }
}
</script>

<style scoped>
.bg-gradient-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
}

.form-check {
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.form-check:hover {
  border-color: #007bff;
  background-color: #f8f9fa;
}

.form-check-input:checked + .form-check-label {
  color: #007bff;
}

.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.btn-lg {
  padding: 0.75rem 2rem;
}
</style>
