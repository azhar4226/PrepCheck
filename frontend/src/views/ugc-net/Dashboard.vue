<template>
  <div class="ugc-net-dashboard">
    <!-- Header Section -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-8">
                <h2 class="card-title mb-2">
                  <i class="bi bi-mortarboard-fill me-2"></i>
                  UGC NET Preparation
                </h2>
              </div>
              <div class="col-md-4 text-md-end">
                <div class="d-flex flex-column">
                  <small>Last Login: {{ formatDate(new Date()) }}</small>
                  <small>Total Tests: {{ userStats.totalAttempts || 0 }} ({{ userStats.practiceAttempts || 0 }} Practice + {{ userStats.mockAttempts || 0 }} Mock)</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Stats Row -->
    <div class="row mb-4">
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <div class="text-primary mb-2">
              <i class="bi bi-clipboard-check" style="font-size: 2rem;"></i>
            </div>
            <h5 class="card-title">{{ userStats.totalAttempts || 0 }}</h5>
            <p class="text-muted mb-0">Total Tests Taken</p>
          </div>
        </div>
      </div>
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <div class="text-success mb-2">
              <i class="bi bi-trophy" style="font-size: 2rem;"></i>
            </div>
            <h5 class="card-title">{{ userStats.bestScore || 0 }}%</h5>
            <p class="text-muted mb-0">Best Score</p>
          </div>
        </div>
      </div>
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <div class="text-warning mb-2">
              <i class="bi bi-bullseye" style="font-size: 2rem;"></i>
            </div>
            <h5 class="card-title">{{ userStats.averageScore || 0 }}%</h5>
            <p class="text-muted mb-0">Average Score</p>
          </div>
        </div>
      </div>
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <div class="text-info mb-2">
              <i class="bi bi-check-circle" style="font-size: 2rem;"></i>
            </div>
            <h5 class="card-title">{{ userStats.qualifiedTests || 0 }}</h5>
            <p class="text-muted mb-0">Qualified Tests (≥40%)</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Row -->
    <div class="row">
      <!-- Left Column - Subjects & Tests -->
      <div class="col-lg-8">
        <!-- User's Subject and Chapters Section -->
        <div class="card mb-4">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-book me-2"></i>Your Preparation Subject
            </h5>
            <span v-if="userSubject" class="badge bg-primary">{{ userSubject.subject_code }}</span>
          </div>
          <div class="card-body">
            <div v-if="loading.subjects" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading your subject...</span>
              </div>
            </div>
            <div v-else-if="!userSubject" class="text-center py-4 text-muted">
              <i class="bi bi-book display-4 d-block mb-3"></i>
              <p>No subject selected for preparation.</p>
              <p class="small">Please contact admin to set your preparation subject.</p>
            </div>
            <div v-else>
              <!-- Subject Information -->
              <div class="row mb-4">
                <div class="col-12">
                  <div class="card bg-light">
                    <div class="card-body">
                      <h6 class="card-title text-primary">{{ userSubject.name }}</h6>
                      <p class="card-text">{{ userSubject.description }}</p>
                      <button 
                        @click="viewSubjectChapters(userSubject)" 
                        class="btn btn-primary btn-sm"
                        :disabled="loading.chapters"
                      >
                        <i class="bi bi-list me-1"></i>
                        {{ loading.chapters ? 'Loading...' : 'View Chapters' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Chapters for User's Subject -->
              <div v-if="chapters.length > 0" class="row">
                <div class="col-12">
                  <h6 class="mb-3">
                    <i class="bi bi-journal-text me-2"></i>Chapter-wise Topics
                  </h6>
                  <div class="row">
                    <div v-for="chapter in chapters" :key="chapter.id" class="col-md-6 mb-3">
                      <div class="card h-100 border-0 bg-light">
                        <div class="card-body">
                          <h6 class="card-title">{{ chapter.name }}</h6>
                          <p class="card-text small text-muted">{{ chapter.description }}</p>
                          <div class="d-flex justify-content-between align-items-center">
                            <small class="text-success">
                              <i class="bi bi-question-circle me-1"></i>
                              {{ chapter.question_count || 0 }} questions
                            </small>
                            <button 
                              @click="generateTestForSubject(userSubject, chapter)" 
                              class="btn btn-sm btn-outline-success"
                            >
                              <i class="bi bi-play me-1"></i>Practice
                            </button>
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

      <!-- Right Column - Quick Actions & Performance -->
      <div class="col-lg-4">
        <!-- Quick Actions -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-lightning-fill me-2"></i>Quick Actions
            </h5>
          </div>
          <div class="card-body">
            <div class="d-grid gap-2">
              <button @click="generateNewTest" class="btn btn-primary">
                <i class="bi bi-plus-circle me-2"></i>Generate Mock Test
              </button>
              <router-link to="/ugc-net/practice/setup" class="btn btn-outline-primary">
                <i class="bi bi-pencil-square me-2"></i>Practice Test
              </router-link>
              <button @click="viewPerformance" class="btn btn-outline-success">
                <i class="bi bi-graph-up me-2"></i>View Performance
              </button>
              <button @click="$router.push('/ugc-net/syllabus')" class="btn btn-outline-info">
                <i class="bi bi-book me-2"></i>Syllabus Coverage
              </button>
            </div>
          </div>
        </div>

        <!-- Performance Summary -->
        <div class="card performance-summary">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-bar-chart me-2"></i>Performance Summary
            </h5>
          </div>
          <div class="card-body">
            <div v-if="userStats.totalAttempts > 0">
              <div class="mb-3">
                <div class="d-flex justify-content-between">
                  <span>Best Score</span>
                  <span class="fw-bold" :class="userStats.bestScore >= 40 ? 'text-success' : 'text-warning'">{{ userStats.bestScore }}%</span>
                </div>
                <div class="progress mt-1" style="height: 8px;">
                  <div class="progress-bar" 
                       :class="userStats.bestScore >= 40 ? 'bg-success' : 'bg-warning'"
                       :style="{ width: userStats.bestScore + '%' }"></div>
                </div>
              </div>
              <div class="mb-3">
                <div class="d-flex justify-content-between">
                  <span>Average Score</span>
                  <span class="fw-bold" :class="userStats.averageScore >= 40 ? 'text-success' : 'text-primary'">{{ userStats.averageScore }}%</span>
                </div>
                <div class="progress mt-1" style="height: 8px;">
                  <div class="progress-bar" 
                       :class="userStats.averageScore >= 40 ? 'bg-success' : 'bg-primary'"
                       :style="{ width: userStats.averageScore + '%' }"></div>
                </div>
              </div>
              <div class="mb-3">
                <div class="d-flex justify-content-between">
                  <span>Qualification Rate</span>
                  <span class="fw-bold text-info">{{ qualificationRate }}%</span>
                </div>
                <div class="progress mt-1" style="height: 8px;">
                  <div class="progress-bar bg-info" 
                       :style="{ width: qualificationRate + '%' }"></div>
                </div>
                <small class="text-muted">{{ userStats.qualifiedTests }} out of {{ userStats.totalAttempts }} tests qualified</small>
              </div>
              <hr>
              <div class="row text-center">
                <div class="col-6">
                  <div class="text-info">
                    <h6>{{ userStats.practiceAttempts || 0 }}</h6>
                    <small class="text-muted">Practice Tests</small>
                  </div>
                </div>
                <div class="col-6">
                  <div class="text-warning">
                    <h6>{{ userStats.mockAttempts || 0 }}</h6>
                    <small class="text-muted">Mock Tests</small>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-3 text-muted">
              <i class="bi bi-bar-chart display-4 d-block mb-2"></i>
              <p class="mb-0">Take your first test to see performance stats</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <!-- Subject Chapters Modal -->
    <div class="modal fade" id="chaptersModal" tabindex="-1" ref="chaptersModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-book-half me-2"></i>
              {{ selectedSubject?.name }} - Chapters
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="loading.chapters" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading chapters...</span>
              </div>
            </div>
            <div v-else-if="chapters.length === 0" class="text-center py-4 text-muted">
              <p>No chapters available for this subject.</p>
            </div>
            <div v-else class="row">
              <div v-for="chapter in chapters" :key="chapter.id" class="col-md-6 mb-3">
                <div class="card border-0 bg-light h-100">
                  <div class="card-body">
                    <h6 class="card-title">{{ chapter.name }}</h6>
                    <p class="card-text small text-muted">{{ chapter.description }}</p>
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <span class="badge bg-primary">Weightage: {{ chapter.weightage_paper2 }}%</span>
                      </div>
                      <small class="text-success">
                        <i class="bi bi-check-circle me-1"></i>
                        {{ chapter.verified_questions }} questions
                      </small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button 
              @click="generateTestForSubject" 
              class="btn btn-primary"
              :disabled="!selectedSubject"
            >
              <i class="bi bi-plus-circle me-1"></i>Generate Test for {{ selectedSubject?.name }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import api from '@/services/api'
import ugcNetService from '@/services/ugcNetService'
import { Modal } from 'bootstrap'

export default {
  name: 'UGCNetDashboard',
  setup() {
    const router = useRouter()
    const { user } = useAuth()
    
    // Reactive data
    const subjects = ref([])
    const chapters = ref([])
    const stats = ref({
      overview: {
        total_subjects: 0,
        total_questions: 0,
        total_attempts: 0,
        average_score: 0
      },
      user_stats: {
        total_attempts: 0,
        practice_attempts: 0,
        mock_attempts: 0,
        average_score: 0,
        best_score: 0
      },
      subject_distribution: [],
      chapter_distribution: []
    })
    const selectedSubject = ref(null)
    
    // Loading states
    const loading = ref({
      subjects: false,
      chapters: false
    })

    // Computed user's registered subject
    const userSubject = computed(() => {
      if (user.value && user.value.subject_id && subjects.value.length > 0) {
        return subjects.value.find(subject => subject.id === user.value.subject_id)
      }
      return null
    })

    // Computed user stats
    const userStats = computed(() => {
      // If we have user_stats from the statistics API, use that
      if (stats.value && stats.value.user_stats) {
        // Calculate qualified tests from actual user statistics
        const qualifiedTests = Math.round((stats.value.user_stats.total_attempts || 0) * (stats.value.user_stats.qualification_rate || 0) / 100)
        
        return {
          totalAttempts: stats.value.user_stats.total_attempts || 0,
          bestScore: Math.min(Math.round(stats.value.user_stats.best_score || 0), 100),
          averageScore: Math.min(Math.round(stats.value.user_stats.average_score || 0), 100),
          practiceAttempts: stats.value.user_stats.practice_attempts || 0,
          mockAttempts: stats.value.user_stats.mock_attempts || 0,
          qualifiedTests: stats.value.user_stats.qualified_attempts || qualifiedTests || 0
        }
      }
      
      // Fallback: Return default stats when no API data available
      return {
        totalAttempts: 0,
        bestScore: 0,
        averageScore: 0,
        practiceAttempts: 0,
        mockAttempts: 0,
        qualifiedTests: 0
      }
    })

    // Computed qualification rate
    const qualificationRate = computed(() => {
      if (userStats.value.totalAttempts === 0) return 0
      return Math.round((userStats.value.qualifiedTests / userStats.value.totalAttempts) * 100)
    })

    // Methods
    const loadSubjects = async () => {
      loading.value.subjects = true
      try {
        const result = await api.ugcNet.getSubjects()
        if (result.success && result.data) {
          // API returns data directly, not wrapped in .data
          subjects.value = result.data.subjects || []
          
          // Auto-load chapters for user's registered subject
          if (user.value && user.value.subject_id) {
            const userSub = subjects.value.find(subject => subject.id === user.value.subject_id)
            if (userSub) {
              await viewSubjectChapters(userSub)
            }
          }
        } else {
          console.error('Failed to load subjects:', result.error)
          subjects.value = []
        }
      } catch (error) {
        console.error('Failed to load subjects:', error)
        subjects.value = []
      } finally {
        loading.value.subjects = false
      }
    }

    const loadStats = async () => {
      try {
        const result = await api.ugcNet.getStatistics()
        if (result.success && result.data) {
          // API returns data directly, not wrapped in .data
          stats.value = result.data
        } else {
          console.error('Failed to load statistics:', result.error)
          // Set default stats structure to prevent undefined errors
          stats.value = {
            overview: {
              total_subjects: 0,
              total_questions: 0,
              total_attempts: 0,
              average_score: 0
            },
            user_stats: {
              total_attempts: 0,
              practice_attempts: 0,
              mock_attempts: 0,
              average_score: 0,
              best_score: 0
            },
            subject_distribution: [],
            chapter_distribution: []
          }
        }
      } catch (error) {
        console.error('Failed to load statistics:', error)
        // Set default stats structure to prevent undefined errors
        stats.value = {
          overview: {
            total_subjects: 0,
            total_questions: 0,
            total_attempts: 0,
            average_score: 0
          },
          user_stats: {
            total_attempts: 0,
            practice_attempts: 0,
            mock_attempts: 0,
            average_score: 0,
            best_score: 0
          },
          subject_distribution: [],
          chapter_distribution: []
        }
      }
    }

    const viewSubjectChapters = async (subject) => {
      selectedSubject.value = subject
      loading.value.chapters = true
      
      try {
        const result = await api.ugcNet.getSubjectChapters(subject.id)
        if (result.success && result.data) {
          // API returns data directly, check if it has chapters property or is an array
          chapters.value = result.data.chapters || result.data || []
        } else {
          console.error('Failed to load chapters:', result.error)
          chapters.value = []
        }
      } catch (error) {
        console.error('Failed to load chapters:', error)
        chapters.value = []
      } finally {
        loading.value.chapters = false
      }
      
      const modal = new Modal(document.getElementById('chaptersModal'))
      modal.show()
    }

    const generateNewTest = () => {
      router.push('/ugc-net/generate-test')
    }

    const startPractice = () => {
      // Navigate to test generator with practice mode
      router.push('/ugc-net/test-generator?mode=practice')
    }

    const viewPerformance = () => {
      // Scroll to performance summary section
      const performanceSection = document.querySelector('.performance-summary')
      if (performanceSection) {
        performanceSection.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        })
        
        // Add temporary highlight effect
        performanceSection.classList.add('highlighted')
        setTimeout(() => {
          performanceSection.classList.remove('highlighted')
        }, 2000)
      } else {
        // Fallback: scroll to bottom of page where performance section usually is
        window.scrollTo({
          top: document.body.scrollHeight * 0.7,
          behavior: 'smooth'
        })
      }
    }

    const generateTestForSubject = () => {
      const modal = Modal.getInstance(document.getElementById('chaptersModal'))
      modal.hide()
      router.push(`/ugc-net/generate-test?subject=${selectedSubject.value.id}`)
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        // Format for Indian locale with IST timezone
        return date.toLocaleDateString('en-IN', {
          timeZone: 'Asia/Kolkata',
          year: 'numeric',
          month: 'short',
          day: '2-digit'
        })
      } catch (error) {
        return 'Invalid Date'
      }
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

    // Lifecycle
    onMounted(async () => {
      await Promise.all([
        loadSubjects(),
        loadStats()
      ])
    })

    return {
      user,
      subjects,
      chapters,
      stats,
      selectedSubject,
      userSubject,
      loading,
      userStats,
      qualificationRate,
      loadSubjects,
      viewSubjectChapters,
      generateNewTest,
      startPractice,
      viewPerformance,
      generateTestForSubject,
      formatDate,
      formatTimeLimit
    }
  }
}
</script>

<style scoped>
.ugc-net-dashboard {
  padding: 1rem;
}

.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-2px);
}

.performance-summary {
  scroll-margin-top: 20px;
}

.performance-summary:target,
.performance-summary.highlighted {
  box-shadow: 0 0 0 3px rgba(25, 135, 84, 0.25);
  border-color: #198754;
}

.progress {
  border-radius: 10px;
}

.badge {
  font-size: 0.7rem;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}
</style>
