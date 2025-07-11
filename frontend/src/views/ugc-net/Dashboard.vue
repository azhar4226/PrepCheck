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
                        @click="toggleSubjectChapters(userSubject)" 
                        class="btn btn-primary btn-sm"
                        :disabled="loading.chapters"
                      >
                        <i class="bi bi-list me-1"></i>
                        {{ loading.chapters ? 'Loading...' : (showChapters ? 'Hide Chapters' : 'View Chapters') }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Chapters Section (shown inline when toggled) -->
              <div v-if="showChapters" class="row mb-4">
                <div class="col-12">
                  <div class="card border-primary">
                    <div class="card-header bg-primary text-white">
                      <h6 class="mb-0">
                        <i class="bi bi-book-half me-2"></i>
                        {{ userSubject.name }} - Chapters
                      </h6>
                    </div>
                    <div class="card-body">
                      <div v-if="loading.chapters" class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                          <span class="visually-hidden">Loading chapters...</span>
                        </div>
                      </div>
                      <div v-else-if="chapters.length === 0" class="text-center py-4 text-muted">
                        <i class="bi bi-book display-4 d-block mb-3"></i>
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
                      <div v-if="chapters.length > 0" class="text-center mt-3">
                        <button 
                          @click="generateTestForSubject" 
                          class="btn btn-success"
                          :disabled="!userSubject"
                        >
                          <i class="bi bi-plus-circle me-1"></i>Generate Test for {{ userSubject.name }}
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

      <!-- Right Column - Quick Actions & Performance -->
      <div class="col-lg-4 position-relative">
        <!-- Quick Actions -->
        <div class="card mb-4 position-relative">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-lightning-fill me-2"></i>Quick Actions
            </h5>
            <button
              class="btn btn-light retract-toggle-section ms-2 shadow-sm"
              @click="rightSectionVisible.quickActions = !rightSectionVisible.quickActions"
              style="border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;"
            >
              <i :class="rightSectionVisible.quickActions ? 'bi bi-chevron-up' : 'bi bi-chevron-down'" style="font-size: 1.1rem;"></i>
            </button>
          </div>
          <transition name="slide-fade-vertical">
            <div v-show="rightSectionVisible.quickActions">
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
          </transition>
        </div>
        <!-- Incomplete Tests Section -->
        <div class="card mb-4 position-relative">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-clock-history me-2"></i>Resume Incomplete Tests
            </h5>
            <button
              class="btn btn-light retract-toggle-section ms-2 shadow-sm"
              @click="rightSectionVisible.incompleteTests = !rightSectionVisible.incompleteTests"
              style="border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;"
            >
              <i :class="rightSectionVisible.incompleteTests ? 'bi bi-chevron-up' : 'bi bi-chevron-down'" style="font-size: 1.1rem;"></i>
            </button>
          </div>
          <transition name="slide-fade-vertical">
            <div v-show="rightSectionVisible.incompleteTests">
              <div class="card-body">
                <div v-if="loading.incompleteTests" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading incomplete tests...</span>
                  </div>
                </div>
                <div v-else-if="!incompleteTests ||
                  !Array.isArray(incompleteTests.practice_tests) ||
                  !Array.isArray(incompleteTests.mock_tests) ||
                  (incompleteTests.practice_tests.length === 0 && incompleteTests.mock_tests.length === 0)"
                  class="text-center py-4 text-muted">
                  <i class="bi bi-check-circle display-4 d-block mb-3"></i>
                  <p>No incomplete tests found.</p>
                  <p class="small">All your tests have been completed or you haven't started any tests yet.</p>
                </div>
                <div v-else>
                <!-- Practice Tests -->
                <div v-if="incompleteTests.practice_tests.length > 0" class="mb-3">
                  <h6 class="text-muted mb-2">Practice Tests</h6>
                  <div v-for="test in incompleteTests.practice_tests" :key="test.id" class="incomplete-test-item mb-2">
                    <div class="d-flex justify-content-between align-items-center p-2 border rounded">
                      <div class="flex-grow-1">
                        <div class="fw-semibold">{{ test.title }}</div>
                        <small class="text-muted">
                          {{ test.subject_name }} • {{ test.answered_questions }}/{{ test.total_questions }} answered
                        </small>
                        <div class="progress mt-1" style="height: 4px;">
                          <div class="progress-bar bg-info" :style="{ width: test.progress_percentage + '%' }"></div>
                        </div>
                      </div>
                      <div class="ms-2">
                        <button @click="resumePracticeTest(test.id)" class="btn btn-sm btn-outline-primary">
                          <i class="bi bi-play-circle me-1"></i>Resume
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Mock Tests -->
                <div v-if="incompleteTests.mock_tests.length > 0">
                  <h6 class="text-muted mb-2">Mock Tests</h6>
                  <div v-for="test in incompleteTests.mock_tests" :key="test.id" class="incomplete-test-item mb-2">
                    <div class="d-flex justify-content-between align-items-center p-2 border rounded">
                      <div class="flex-grow-1">
                        <div class="fw-semibold">{{ test.title }}</div>
                        <small class="text-muted">
                          {{ test.subject_name }} • {{ test.answered_questions }}/{{ test.total_questions }} answered
                        </small>
                        <div class="progress mt-1" style="height: 4px;">
                          <div class="progress-bar bg-warning" :style="{ width: test.progress_percentage + '%' }"></div>
                        </div>
                      </div>
                      <div class="ms-2">
                        <button @click="resumeMockTest(test.id)" class="btn btn-sm btn-outline-warning">
                          <i class="bi bi-play-circle me-1"></i>Resume
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                </div>
              </div>
            </div>
          </transition>
        </div>

        <!-- AI Study Recommendations -->
        <div class="card mb-4 position-relative">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-robot me-2"></i>AI Study Recommendations
            </h5>
            <button
              class="btn btn-light retract-toggle-section ms-2 shadow-sm"
              @click="rightSectionVisible.recommendations = !rightSectionVisible.recommendations"
              style="border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;"
            >
              <i :class="rightSectionVisible.recommendations ? 'bi bi-chevron-up' : 'bi bi-chevron-down'" style="font-size: 1.1rem;"></i>
            </button>
          </div>
          <transition name="slide-fade-vertical">
            <div v-show="rightSectionVisible.recommendations">
              <div class="card-body">
                <div v-if="loading.recommendations" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Generating recommendations...</span>
                  </div>
                </div>
                <div v-else-if="studyRecommendations.length === 0" class="text-center py-4 text-muted">
                  <i class="bi bi-lightbulb display-4 d-block mb-3"></i>
                  <p>No recommendations available yet.</p>
                  <button @click="generateRecommendations" class="btn btn-primary btn-sm">
                    <i class="bi bi-magic me-1"></i>Generate Recommendations
                  </button>
                </div>
                <div v-else>
                  <div v-for="(recommendation, index) in studyRecommendations" :key="index" class="mb-3">
                    <div class="card bg-light border-0">
                      <div class="card-body p-3">
                        <div class="d-flex align-items-start">
                          <div class="me-2">
                            <i :class="recommendation.icon" class="text-primary"></i>
                          </div>
                          <div class="flex-grow-1">
                            <h6 class="card-title mb-1">{{ recommendation.title }}</h6>
                            <p class="card-text small mb-2">{{ recommendation.description }}</p>
                            <div class="d-flex align-items-center">
                              <span class="badge me-2" :class="recommendation.priority === 'high' ? 'bg-danger' : recommendation.priority === 'medium' ? 'bg-warning text-dark' : 'bg-success'">
                                {{ recommendation.priority.toUpperCase() }}
                              </span>
                              <small class="text-muted">{{ recommendation.estimatedTime }}</small>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="text-center">
                    <button @click="generateRecommendations" class="btn btn-outline-primary btn-sm">
                      <i class="bi bi-arrow-clockwise me-1"></i>Refresh Recommendations
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </div>

        <!-- Study Plan -->
        <div class="card study-plan position-relative">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-calendar-check me-2"></i>AI Study Plan
            </h5>
            <button
              class="btn btn-light retract-toggle-section ms-2 shadow-sm"
              @click="rightSectionVisible.studyPlan = !rightSectionVisible.studyPlan"
              style="border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;"
            >
              <i :class="rightSectionVisible.studyPlan ? 'bi bi-chevron-up' : 'bi bi-chevron-down'" style="font-size: 1.1rem;"></i>
            </button>
          </div>
          <transition name="slide-fade-vertical">
            <div v-show="rightSectionVisible.studyPlan">
              <div class="card-body">
                <div v-if="loading.studyPlan" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Creating study plan...</span>
                  </div>
                </div>
                <div v-else-if="studyPlan.length === 0" class="text-center py-4 text-muted">
                  <i class="bi bi-calendar display-4 d-block mb-3"></i>
                  <p>No study plan created yet.</p>
                  <button @click="generateStudyPlan" class="btn btn-success btn-sm">
                    <i class="bi bi-plus-circle me-1"></i>Create Study Plan
                  </button>
                </div>
                <div v-else>
                  <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                      <h6 class="text-primary mb-0">{{ studyPlanTitle }}</h6>
                      <span class="badge bg-info">{{ studyPlanDuration }}</span>
                    </div>
                  </div>
                  <div class="study-plan-timeline">
                    <div v-for="(week, index) in studyPlan" :key="index" class="week-item mb-3">
                      <div class="d-flex align-items-center mb-2">
                        <div class="week-indicator me-2">
                          <div class="circle" :class="week.completed ? 'bg-success' : 'bg-primary'">
                            <i :class="week.completed ? 'bi bi-check' : 'bi bi-calendar-week'" class="text-white"></i>
                          </div>
                        </div>
                        <div class="flex-grow-1">
                          <h6 class="mb-0">Week {{ index + 1 }}: {{ week.title }}</h6>
                          <small class="text-muted">{{ week.description }}</small>
                        </div>
                      </div>
                      <div class="week-tasks ms-4">
                        <div v-for="(task, taskIndex) in week.tasks" :key="taskIndex" class="task-item d-flex align-items-center mb-1">
                          <input 
                            type="checkbox" 
                            :checked="task.completed" 
                            @change="toggleTask(index, taskIndex)"
                            class="form-check-input me-2"
                          >
                          <span :class="task.completed ? 'text-decoration-line-through text-muted' : ''">
                            {{ task.title }}
                          </span>
                          <span class="badge bg-light text-dark ms-auto">{{ task.duration }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="text-center mt-3">
                    <button @click="generateStudyPlan" class="btn btn-outline-success btn-sm me-2">
                      <i class="bi bi-arrow-clockwise me-1"></i>Regenerate Plan
                    </button>
                    <button @click="exportStudyPlan" class="btn btn-outline-primary btn-sm">
                      <i class="bi bi-download me-1"></i>Export Plan
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </transition>
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

import { formatISTDate } from '@/utils/timezone'

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
    const showChapters = ref(false)
    const incompleteTests = ref({
      practice_tests: [],
      mock_tests: [],
      total_incomplete: 0
    })
    
    const studyRecommendations = ref([])
    const studyPlan = ref([])
    const studyPlanTitle = ref('')
    const studyPlanDuration = ref('')
    
    // Loading states
    const loading = ref({
      subjects: false,
      chapters: false,
      incompleteTests: false,
      recommendations: false,
      studyPlan: false
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
          showChapters.value = true
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
    }

    // Toggle chapters visibility
    const toggleSubjectChapters = async (subject) => {
      if (showChapters.value) {
        // Hide chapters
        showChapters.value = false
        chapters.value = []
        return
      }

      // Show chapters - load them first
      loading.value.chapters = true
      showChapters.value = true
      
      try {
        const result = await api.ugcNet.getSubjectChapters(subject.id)
        if (result.success && result.data) {
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
    }

    const generateNewTest = () => {
      router.push('/ugc-net/generate-test')
    }

    const startPractice = () => {
      // Navigate to test generator with practice mode
      router.push('/ugc-net/test-generator?mode=practice')
    }

    const viewPerformance = () => {
      // Navigate to a dedicated performance page or scroll to study recommendations
      const studySection = document.querySelector('.study-plan')
      if (studySection) {
        studySection.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        })
        
        // Add temporary highlight effect
        studySection.classList.add('highlighted')
        setTimeout(() => {
          studySection.classList.remove('highlighted')
        }, 2000)
      } else {
        // Fallback: navigate to a performance page
        router.push('/ugc-net/performance')
      }
    }

    const generateTestForSubject = () => {
      router.push(`/ugc-net/generate-test?subject=${selectedSubject.value.id}`)
    }

    const loadIncompleteTests = async () => {
      loading.value.incompleteTests = true
      try {
        const result = await api.ugcNet.getIncompleteTests()
        if (result.success && result.data) {
          incompleteTests.value = result.data
        } else {
          console.error('Failed to load incomplete tests:', result.error)
          incompleteTests.value = { practice_tests: [], mock_tests: [], total_incomplete: 0 }
        }
      } catch (error) {
        console.error('Failed to load incomplete tests:', error)
        incompleteTests.value = { practice_tests: [], mock_tests: [], total_incomplete: 0 }
      } finally {
        loading.value.incompleteTests = false
      }
    }

    const resumePracticeTest = (attemptId) => {
      // Navigate to practice test overview page for resume functionality
      router.push(`/ugc-net/practice/${attemptId}`)
    }

    const resumeMockTest = (attemptId) => {
      // For mock tests, we need to find the test ID first
      // Navigate to mock test taking page
      router.push(`/ugc-net/mock-test/${attemptId}/take`)
    }

    const generateRecommendations = async () => {
      loading.value.recommendations = true
      try {
        // Call the new AI recommendations API
        const result = await api.ugcNet.getAIStudyRecommendations(5)
        
        if (result.success && result.data) {
          studyRecommendations.value = result.data.recommendations || []
        } else {
          console.error('Failed to generate AI recommendations:', result.error)
          // Fallback to mock recommendations if API fails
          studyRecommendations.value = await generateFallbackRecommendations()
        }
      } catch (error) {
        console.error('Error generating AI recommendations:', error)
        // Fallback to mock recommendations if API fails
        studyRecommendations.value = await generateFallbackRecommendations()
      } finally {
        loading.value.recommendations = false
      }
    }

    const generateStudyPlan = async () => {
      loading.value.studyPlan = true
      try {
        // Call the new AI study plan API
        const result = await api.ugcNet.getAIStudyPlan(12)
        
        if (result.success && result.data) {
          studyPlanTitle.value = result.data.title || 'Personalized Study Plan'
          studyPlanDuration.value = result.data.duration || '12 weeks'
          studyPlan.value = result.data.weekly_plan || []
        } else {
          console.error('Failed to generate AI study plan:', result.error)
          // Fallback to mock study plan if API fails
          await generateFallbackStudyPlan()
        }
      } catch (error) {
        console.error('Error generating AI study plan:', error)
        // Fallback to mock study plan if API fails
        await generateFallbackStudyPlan()
      } finally {
        loading.value.studyPlan = false
      }
    }

    const generateFallbackRecommendations = async () => {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const recommendations = []
      
      // Base recommendations on actual user stats
      if (userStats.value.totalAttempts === 0) {
        recommendations.push({
          title: "Start with Practice Tests",
          description: "Begin your preparation with chapter-wise practice tests to identify your strengths and weaknesses.",
          icon: "bi bi-play-circle",
          priority: "high",
          estimatedTime: "2-3 hours/day"
        })
      } else if (userStats.value.averageScore < 40) {
        recommendations.push({
          title: "Focus on Fundamentals",
          description: `Your average score is ${userStats.value.averageScore}%. Strengthen fundamental concepts before advanced topics.`,
          icon: "bi bi-book",
          priority: "high",
          estimatedTime: "3-4 hours/day"
        })
      } else if (userStats.value.averageScore < 60) {
        recommendations.push({
          title: "Bridge Knowledge Gaps",
          description: `Your average score is ${userStats.value.averageScore}%. Focus on specific weak areas to improve consistency.`,
          icon: "bi bi-puzzle",
          priority: "medium",
          estimatedTime: "2-3 hours/day"
        })
      } else {
        recommendations.push({
          title: "Maintain Excellence",
          description: `Great performance with ${userStats.value.averageScore}% average! Focus on advanced topics and speed improvement.`,
          icon: "bi bi-trophy",
          priority: "low",
          estimatedTime: "1-2 hours/day"
        })
      }
      
      if (userSubject.value) {
        recommendations.push({
          title: `Master ${userSubject.value.name} Chapters`,
          description: `Focus on high-weightage chapters in ${userSubject.value.name} for maximum impact on your scores.`,
          icon: "bi bi-bullseye",
          priority: "medium",
          estimatedTime: "1-2 hours/day"
        })
      }
      
      // Add practice pattern recommendations
      if (userStats.value.practiceAttempts < userStats.value.mockAttempts) {
        recommendations.push({
          title: "Increase Practice Tests",
          description: "You have more mock tests than practice tests. Build confidence with more chapter-wise practice.",
          icon: "bi bi-pencil-square",
          priority: "medium",
          estimatedTime: "1 hour/day"
        })
      }
      
      recommendations.push({
        title: "Regular Mock Tests",
        description: "Take full-length mock tests weekly to build exam stamina and time management skills.",
        icon: "bi bi-stopwatch",
        priority: userStats.value.mockAttempts < 5 ? "high" : "medium",
        estimatedTime: "3 hours/week"
      })
      
      recommendations.push({
        title: "Review and Revision",
        description: "Dedicate time for regular revision of completed topics to ensure retention.",
        icon: "bi bi-arrow-repeat",
        priority: "low",
        estimatedTime: "1 hour/day"
      })
      
      return recommendations
    }

    const generateFallbackStudyPlan = async () => {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const subjectName = userSubject.value?.name || 'UGC NET'
      studyPlanTitle.value = `Personalized ${subjectName} Study Plan`
      studyPlanDuration.value = '12 weeks'
      
      // Adjust plan based on user performance
      const userLevel = userStats.value.averageScore < 40 ? 'beginner' : 
                       userStats.value.averageScore < 60 ? 'intermediate' : 'advanced'
      
      const plan = []
      
      if (userLevel === 'beginner') {
        // More foundation weeks for beginners
        plan.push(
          {
            title: "Foundation Building - Week 1",
            description: "Establish strong fundamental understanding",
            completed: false,
            tasks: [
              { title: `Study ${subjectName} syllabus and basic concepts`, completed: false, duration: "4 hours" },
              { title: "Complete introductory practice tests", completed: false, duration: "2 hours" },
              { title: "Create concept notes and summaries", completed: false, duration: "2 hours" },
              { title: "Review weak areas from practice", completed: false, duration: "1 hour" }
            ]
          },
          {
            title: "Foundation Building - Week 2",
            description: "Deepen understanding of core concepts",
            completed: false,
            tasks: [
              { title: "Study fundamental chapters in detail", completed: false, duration: "5 hours" },
              { title: "Complete chapter-wise practice tests", completed: false, duration: "3 hours" },
              { title: "Clarify doubts and misconceptions", completed: false, duration: "1 hour" }
            ]
          }
        )
      }
      
      // Practice weeks
      for (let i = 0; i < 6; i++) {
        const weekNum = plan.length + 1
        plan.push({
          title: `Intensive Practice - Week ${weekNum}`,
          description: "Build speed, accuracy, and confidence through practice",
          completed: false,
          tasks: [
            { title: "Mixed topic practice tests", completed: false, duration: "2 hours" },
            { title: "One full-length mock test", completed: false, duration: "3 hours" },
            { title: "Detailed error analysis", completed: false, duration: "1 hour" },
            { title: "Review incorrect concepts", completed: false, duration: "1 hour" }
          ]
        })
      }
      
      // Revision weeks
      for (let i = 0; i < 4; i++) {
        const weekNum = plan.length + 1
        plan.push({
          title: `Comprehensive Revision - Week ${weekNum}`,
          description: "Consolidate knowledge and boost confidence",
          completed: false,
          tasks: [
            { title: "Quick revision of all topics", completed: false, duration: "2 hours" },
            { title: "Focus on previously weak areas", completed: false, duration: "1.5 hours" },
            { title: "Timed mock test", completed: false, duration: "3 hours" },
            { title: "Final doubt clearing", completed: false, duration: "1 hour" }
          ]
        })
      }
      
      studyPlan.value = plan
    }

    const toggleTask = (weekIndex, taskIndex) => {
      studyPlan.value[weekIndex].tasks[taskIndex].completed = !studyPlan.value[weekIndex].tasks[taskIndex].completed
      
      // Check if all tasks in the week are completed
      const allTasksCompleted = studyPlan.value[weekIndex].tasks.every(task => task.completed)
      studyPlan.value[weekIndex].completed = allTasksCompleted
    }

    const exportStudyPlan = () => {
      // Create a simple text export of the study plan
      let exportText = `${studyPlanTitle.value}\n`
      exportText += `Duration: ${studyPlanDuration.value}\n\n`
      
      studyPlan.value.forEach((week, index) => {
        exportText += `Week ${index + 1}: ${week.title}\n`
        exportText += `${week.description}\n`
        week.tasks.forEach(task => {
          exportText += `  ${task.completed ? '✓' : '○'} ${task.title} (${task.duration})\n`
        })
        exportText += '\n'
      })
      
      // Download as text file
      const blob = new Blob([exportText], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'ugc-net-study-plan.txt'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return formatISTDate(dateString)
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

    const closeChapters = () => {
      chapters.value = []
      selectedSubject.value = null
    }

    // Lifecycle
    onMounted(async () => {
      await Promise.all([
        loadSubjects(),
        loadStats(),
        loadIncompleteTests()
      ])
      
      // Auto-generate recommendations if user has taken tests
      if (userStats.value.totalAttempts > 0) {
        setTimeout(() => {
          generateRecommendations()
        }, 1000) // Small delay to let stats load completely
      }
    })

    const rightSectionVisible = ref({
      quickActions: true,
      incompleteTests: false,
      recommendations: false,
      studyPlan: false
    })

    return {
      user,
      subjects,
      chapters,
      stats,
      selectedSubject,
      showChapters,
      userSubject,
      loading,
      userStats,
      qualificationRate,
      incompleteTests,
      studyRecommendations,
      studyPlan,
      studyPlanTitle,
      studyPlanDuration,
      loadSubjects,
      viewSubjectChapters,
      closeChapters,
      toggleSubjectChapters,
      generateNewTest,
      startPractice,
      viewPerformance,
      generateTestForSubject,
      loadIncompleteTests,
      resumePracticeTest,
      resumeMockTest,
      generateRecommendations,
      generateStudyPlan,
      generateFallbackRecommendations,
      generateFallbackStudyPlan,
      toggleTask,
      exportStudyPlan,
      formatDate,
      formatTimeLimit,
      rightSectionVisible
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

.study-plan {
  scroll-margin-top: 20px;
}

.study-plan:target,
.study-plan.highlighted {
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

/* Study Plan Timeline Styles */
.study-plan-timeline {
  position: relative;
}

.week-item {
  position: relative;
}

.week-indicator .circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.week-tasks {
  border-left: 2px solid #e9ecef;
  padding-left: 1rem;
  margin-left: 1rem;
}

.task-item {
  padding: 0.25rem 0;
}

.task-item:hover {
  background-color: rgba(0, 123, 255, 0.05);
  border-radius: 4px;
  padding-left: 0.5rem;
  transition: all 0.2s ease;
}

.form-check-input:checked {
  background-color: #198754;
  border-color: #198754;
}

/* Recommendation Cards */
.card.bg-light:hover {
  background-color: rgba(0, 123, 255, 0.05) !important;
  transform: translateY(-1px);
}

.badge.bg-danger {
  background-color: #dc3545 !important;
}

.badge.bg-warning {
  background-color: #ffc107 !important;
}

.badge.bg-success {
  background-color: #198754 !important;
}

/* Slide Transition for Sections */
.slide-fade-vertical-enter-active, .slide-fade-vertical-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-fade-vertical-enter-from, .slide-fade-vertical-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
.retract-toggle-section {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  background: #fff;
  border: 1px solid #e9ecef;
  cursor: pointer;
}
</style>
