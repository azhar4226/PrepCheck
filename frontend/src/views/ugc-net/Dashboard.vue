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
                  UGC NET Preparation Dashboard
                </h2>
                <p class="card-text mb-0">
                  Comprehensive preparation platform for UGC NET examinations with weightage-based mock tests
                </p>
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
              <i class="bi bi-journal-text" style="font-size: 2rem;"></i>
            </div>
            <h5 class="card-title">{{ stats.overview?.total_subjects || 0 }}</h5>
            <p class="text-muted mb-0">Available Subjects</p>
          </div>
        </div>
      </div>
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <div class="text-success mb-2">
              <i class="bi bi-question-circle" style="font-size: 2rem;"></i>
            </div>
            <h5 class="card-title">{{ stats.overview?.total_questions || 0 }}</h5>
            <p class="text-muted mb-0">Practice Questions</p>
          </div>
        </div>
      </div>
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <div class="text-warning mb-2">
              <i class="bi bi-clipboard-check" style="font-size: 2rem;"></i>
            </div>
            <h5 class="card-title">{{ mockTests.length }}</h5>
            <p class="text-muted mb-0">Mock Tests</p>
          </div>
        </div>
      </div>
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <div class="text-info mb-2">
              <i class="bi bi-trophy" style="font-size: 2rem;"></i>
            </div>
            <h5 class="card-title">{{ userStats.bestScore || 0 }}%</h5>
            <p class="text-muted mb-0">Best Score</p>
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

        <!-- Recent Mock Tests -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-clipboard-data me-2"></i>Recent Mock Tests
            </h5>
            <div>
              <button @click="generateNewTest" class="btn btn-sm btn-primary me-2">
                <i class="bi bi-plus-circle me-1"></i>Generate Test
              </button>
              <button @click="loadMockTests" class="btn btn-sm btn-outline-secondary">
                <i class="bi bi-arrow-clockwise me-1"></i>Refresh
              </button>
            </div>
          </div>
          <div class="card-body">
            <div v-if="loading.mockTests" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading mock tests...</span>
              </div>
            </div>
            <div v-else-if="mockTests.length === 0" class="text-center py-4 text-muted">
              <i class="bi bi-clipboard-x display-4 d-block mb-3"></i>
              <p>No mock tests available.</p>
              <button @click="generateNewTest" class="btn btn-primary">
                <i class="bi bi-plus-circle me-1"></i>Create First Test
              </button>
            </div>
            <div v-else>
              <div v-for="test in mockTests.slice(0, 5)" :key="test.id" class="mb-3">
                <div class="d-flex justify-content-between align-items-center p-3 border rounded">
                  <div>
                    <h6 class="mb-1">{{ test.title }}</h6>
                    <small class="text-muted">
                      <i class="bi bi-clock me-1"></i>{{ formatTimeLimit(test.time_limit) }}
                      <span class="mx-2">•</span>
                      <i class="bi bi-question-circle me-1"></i>{{ test.total_questions }} questions
                      <span class="mx-2">•</span>
                      <i class="bi bi-calendar me-1"></i>{{ formatDate(test.created_at) }}
                    </small>
                    <!-- Show attempt info if user has attempted -->
                    <div v-if="test.user_attempts > 0" class="mt-1">
                      <small class="text-success">
                        <i class="bi bi-check-circle me-1"></i>
                        {{ test.user_attempts }} attempt{{ test.user_attempts > 1 ? 's' : '' }}
                        <span v-if="test.best_score !== null"> • Best: {{ test.best_score }}%</span>
                        <span v-if="test.last_attempted"> • Last: {{ formatDate(test.last_attempted) }}</span>
                      </small>
                    </div>
                  </div>
                  <div class="d-flex gap-2">
                    <!-- Primary action button based on attempt status -->
                    <button 
                      v-if="test.user_attempts > 0"
                      @click="viewTestResults(test)" 
                      class="btn btn-sm btn-success"
                      title="View your test results and performance"
                    >
                      <i class="bi bi-graph-up me-1"></i>
                      View Results
                    </button>
                    <button 
                      v-else
                      @click="startTest(test)" 
                      class="btn btn-sm btn-primary"
                      :disabled="loading.startTest === test.id"
                      title="Start taking this test"
                    >
                      <span v-if="loading.startTest === test.id" 
                            class="spinner-border spinner-border-sm me-1" 
                            role="status">
                      </span>
                      <i v-else class="bi bi-play-fill me-1"></i>
                      Start Test
                    </button>
                    
                    <!-- Secondary action: Take test again (if attempted) or View info (if not attempted) -->
                    <button 
                      v-if="test.user_attempts > 0"
                      @click="startTest(test)" 
                      class="btn btn-sm btn-outline-primary"
                      :disabled="loading.startTest === test.id"
                      title="Take this test again"
                    >
                      <span v-if="loading.startTest === test.id" 
                            class="spinner-border spinner-border-sm me-1" 
                            role="status">
                      </span>
                      <i v-else class="bi bi-arrow-clockwise me-1"></i>
                      Retake
                    </button>
                    <button 
                      v-else
                      @click="showTestInfo(test)" 
                      class="btn btn-sm btn-outline-secondary"
                      title="View test information and details"
                    >
                      <i class="bi bi-info-circle me-1"></i>
                      Info
                    </button>
                  </div>
                </div>
              </div>
              <div v-if="mockTests.length > 5" class="text-center">
                <button @click="$router.push('/ugc-net/tests')" class="btn btn-outline-primary">
                  View All Tests ({{ mockTests.length }})
                </button>
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
                  <span class="fw-bold text-success">{{ userStats.bestScore }}%</span>
                </div>
                <div class="progress mt-1" style="height: 8px;">
                  <div class="progress-bar bg-success" 
                       :style="{ width: userStats.bestScore + '%' }"></div>
                </div>
              </div>
              <div class="mb-3">
                <div class="d-flex justify-content-between">
                  <span>Average Score</span>
                  <span class="fw-bold text-primary">{{ userStats.averageScore }}%</span>
                </div>
                <div class="progress mt-1" style="height: 8px;">
                  <div class="progress-bar" 
                       :style="{ width: userStats.averageScore + '%' }"></div>
                </div>
              </div>
              <hr>
              <div class="row text-center">
                <div class="col">
                  <div class="text-primary">
                    <h6>{{ userStats.totalAttempts }}</h6>
                    <small class="text-muted">Total Tests</small>
                  </div>
                </div>
                <div class="col">
                  <div class="text-info">
                    <h6>{{ userStats.practiceAttempts || 0 }}</h6>
                    <small class="text-muted">Practice</small>
                  </div>
                </div>
                <div class="col">
                  <div class="text-warning">
                    <h6>{{ userStats.mockAttempts || 0 }}</h6>
                    <small class="text-muted">Mock Tests</small>
                  </div>
                </div>
                <div class="col">
                  <div class="text-success">
                    <h6>{{ userStats.qualifiedTests || 0 }}</h6>
                    <small class="text-muted">Qualified</small>
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
    const mockTests = ref([])
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
      chapters: false,
      mockTests: false,
      startTest: null
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
        return {
          totalAttempts: stats.value.user_stats.total_attempts || 0,
          bestScore: stats.value.user_stats.best_score || 0,
          averageScore: stats.value.user_stats.average_score || 0,
          practiceAttempts: stats.value.user_stats.practice_attempts || 0,
          mockAttempts: stats.value.user_stats.mock_attempts || 0,
          qualifiedTests: mockTests.value.filter(test => test.best_score >= 40).length
        }
      }
      
      // Fallback: Calculate from mock tests only (legacy behavior)
      const attempts = mockTests.value.reduce((acc, test) => {
        return acc + (test.user_attempts || 0)
      }, 0)
      
      // Calculate best and average scores from mock tests
      const scores = mockTests.value
        .filter(test => test.best_score !== null)
        .map(test => test.best_score)
      
      const bestScore = scores.length > 0 ? Math.max(...scores) : 0
      const averageScore = scores.length > 0 ? 
        Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0
      
      return {
        totalAttempts: attempts,
        bestScore,
        averageScore,
        practiceAttempts: 0,
        mockAttempts: attempts,
        qualifiedTests: scores.filter(score => score >= 40).length
      }
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

    const loadMockTests = async () => {
      loading.value.mockTests = true
      try {
        const result = await api.ugcNet.getMockTests()
        if (result.success && result.data) {
          // API returns data directly, not wrapped in .data
          mockTests.value = result.data.mock_tests || []
        } else {
          console.error('Failed to load mock tests:', result.error)
          mockTests.value = []
        }
      } catch (error) {
        console.error('Failed to load mock tests:', error)
        mockTests.value = []
      } finally {
        loading.value.mockTests = false
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

    const startTest = async (test) => {
      loading.value.startTest = test.id
      try {
        const result = await api.ugcNet.startAttempt(test.id)
        if (result.success && result.data) {
          // Check different possible response structures
          const attemptId = result.data.attempt?.id || result.data.id || result.data.attempt_id
          if (attemptId) {
            router.push(`/ugc-net/test/${test.id}/attempt/${attemptId}`)
          } else {
            console.error('No attempt ID found in response:', result.data)
            alert('Failed to start test: No attempt ID received')
          }
        } else {
          console.error('Failed to start test:', result.error)
          alert('Failed to start test: ' + (result.error || 'Unknown error'))
        }
      } catch (error) {
        console.error('Failed to start test:', error)
        alert('Failed to start test: ' + error.message)
      } finally {
        loading.value.startTest = null
      }
    }

    const viewTestDetails = (test) => {
      // If the user has attempted the test, show results
      if (test.user_attempts > 0) {
        viewTestResults(test)
      } else {
        // If not attempted, show test information/preview
        router.push(`/ugc-net/test/${test.id}/preview`)
      }
    }

    const viewTestResults = async (test) => {
      // Debug logging
      console.log('🔍 Dashboard: viewTestResults called with test:', test)
      console.log('🔍 Dashboard: test.id =', test.id)
      console.log('🔍 Dashboard: test.user_attempts =', test.user_attempts)
      
      // Since we know the user has attempts (user_attempts > 0), 
      // navigate to a general results page that can handle finding the latest attempt
      try {
        const route = `/ugc-net/test/${test.id}/results`
        console.log('🔍 Dashboard: Navigating to route:', route)
        // Navigate to test results page - the TestResults component can handle finding the latest attempt
        await router.push(route)
        console.log('✅ Dashboard: Navigation completed')
      } catch (error) {
        console.error('❌ Dashboard: Failed to navigate to test results:', error)
        alert('Failed to view test results')
      }
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
        loadMockTests(),
        loadStats()
      ])
    })

    return {
      user,
      subjects,
      chapters,
      mockTests,
      stats,
      selectedSubject,
      userSubject,
      loading,
      userStats,
      loadSubjects,
      loadMockTests,
      viewSubjectChapters,
      generateNewTest,
      startPractice,
      viewPerformance,
      generateTestForSubject,
      startTest,
      viewTestDetails,
      viewTestResults,
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
