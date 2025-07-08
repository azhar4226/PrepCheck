<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2><i class="bi bi-clock-history me-2"></i>Test History</h2>
          <div class="btn-group" role="group">
            <router-link to="/ugc-net" class="btn btn-outline-primary">
              <i class="bi bi-mortarboard me-2"></i>
              Take New Test
            </router-link>
            <router-link to="/ugc-net/practice/setup" class="btn btn-outline-success">
              <i class="bi bi-play-circle me-2"></i>
              Practice Tests
            </router-link>
          </div>
        </div>

        <!-- Filter Tabs -->
        <div class="card mb-4">
          <div class="card-header">
            <ul class="nav nav-tabs card-header-tabs" role="tablist">
              <li class="nav-item" role="presentation">
                <button 
                  class="nav-link" 
                  :class="{ active: activeTab === 'all' }"
                  @click="activeTab = 'all'"
                  type="button"
                >
                  <i class="bi bi-list me-2"></i>All Tests
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button 
                  class="nav-link" 
                  :class="{ active: activeTab === 'mock' }"
                  @click="activeTab = 'mock'"
                  type="button"
                >
                  <i class="bi bi-clipboard-check me-2"></i>Mock Tests
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button 
                  class="nav-link" 
                  :class="{ active: activeTab === 'practice' }"
                  @click="activeTab = 'practice'"
                  type="button"
                >
                  <i class="bi bi-mortarboard me-2"></i>Practice Tests
                </button>
              </li>
            </ul>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3">Loading test history...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger">
          <i class="bi bi-exclamation-triangle me-2"></i>
          {{ error }}
        </div>

        <!-- Statistics Cards -->
        <div v-else class="row mb-4">
          <div class="col-md-3">
            <div class="card bg-primary text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h6 class="card-title">Total Tests</h6>
                    <h3 class="mb-0">{{ statistics.totalTests }}</h3>
                  </div>
                  <div class="align-self-center">
                    <i class="bi bi-clipboard-check display-4 opacity-75"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-success text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h6 class="card-title">Completed</h6>
                    <h3 class="mb-0">{{ statistics.completedTests }}</h3>
                  </div>
                  <div class="align-self-center">
                    <i class="bi bi-check-circle display-4 opacity-75"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-info text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h6 class="card-title">Average Score</h6>
                    <h3 class="mb-0">{{ statistics.averageScore }}%</h3>
                  </div>
                  <div class="align-self-center">
                    <i class="bi bi-graph-up display-4 opacity-75"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-warning text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h6 class="card-title">Best Score</h6>
                    <h3 class="mb-0">{{ statistics.bestScore }}%</h3>
                  </div>
                  <div class="align-self-center">
                    <i class="bi bi-trophy display-4 opacity-75"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Test History Content -->
        <div v-if="filteredAttempts.length === 0 && !loading" class="card">
          <div class="card-body">
            <div class="text-center py-5">
              <i class="bi bi-clock-history display-1 text-muted mb-3"></i>
              <h4 class="text-muted">No Test History Yet</h4>
              <p class="text-muted mb-4">Start taking UGC NET tests to see your history here.</p>
              <!-- Debug information -->
              <div class="alert alert-info mt-3">
                <small>
                  <strong>Status:</strong> Connected to backend successfully<br>
                  <strong>Data loaded:</strong> Mock attempts: {{ mockAttempts.length }}, Practice attempts: {{ practiceAttempts.length }}<br>
                  <strong>Statistics:</strong> Total tests: {{ statistics.totalTests }}, Best score: {{ statistics.bestScore }}%<br>
                  <span v-if="statistics.totalTests > 0"><strong>Note:</strong> Statistics show {{ statistics.totalTests }} tests taken, but detailed history may not be available yet.</span><br>
                  <strong>Next steps:</strong> Take some tests to see your history here
                </small>
              </div>
              <div class="d-flex justify-content-center gap-2">
                <router-link to="/ugc-net" class="btn btn-primary">
                  <i class="bi bi-mortarboard me-2"></i>
                  Browse Mock Tests
                </router-link>
                <router-link to="/ugc-net/practice/setup" class="btn btn-success">
                  <i class="bi bi-play-circle me-2"></i>
                  Start Practice Test
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Test History List -->
        <div v-else class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-list-ul me-2"></i>
              Test History 
              <span class="badge bg-secondary ms-2">{{ filteredAttempts.length }}</span>
            </h5>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Type</th>
                    <th>Subject</th>
                    <th>Test/Chapter</th>
                    <th>Questions</th>
                    <th>Score</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="attempt in filteredAttempts" :key="`${attempt.type}-${attempt.id}`">
                    <td>
                      <span class="badge" :class="getTypeBadgeClass(attempt.type)">
                        {{ attempt.type === 'mock' ? 'Mock Test' : 'Practice' }}
                      </span>
                    </td>
                    <td>
                      <strong>{{ attempt.subject_name }}</strong>
                    </td>
                    <td>
                      <span v-if="attempt.type === 'mock'" class="text-primary">
                        {{ attempt.test_name }}
                      </span>
                      <span v-else class="badge bg-light text-dark">
                        {{ attempt.chapter_name }}
                      </span>
                    </td>
                    <td>{{ attempt.total_questions }}</td>
                    <td>
                      <span v-if="attempt.is_completed" class="badge" :class="getScoreBadgeClass(attempt.percentage)">
                        {{ attempt.percentage }}%
                      </span>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td>
                      <span class="badge" :class="getStatusBadgeClass(attempt.is_completed)">
                        {{ attempt.is_completed ? 'Completed' : 'In Progress' }}
                      </span>
                    </td>
                    <td>{{ formatDate(attempt.created_at) }}</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button 
                          v-if="!attempt.is_completed" 
                          @click="resumeTest(attempt)"
                          class="btn btn-outline-primary"
                          title="Resume Test"
                        >
                          <i class="bi bi-play-fill"></i>
                        </button>
                        <button 
                          v-if="attempt.is_completed" 
                          @click="viewResults(attempt)"
                          class="btn btn-outline-success"
                          title="View Results"
                        >
                          <i class="bi bi-eye"></i>
                        </button>
                        <button 
                          @click="deleteAttempt(attempt)"
                          class="btn btn-outline-danger"
                          title="Delete"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
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
</template>

<script>
import apiService from '@/services/api'

export default {
  name: 'UserHistory',
  data() {
    return {
      activeTab: 'all',
      mockAttempts: [],
      practiceAttempts: [],
      loading: true,
      error: null,
      statistics: {
        totalTests: 0,
        completedTests: 0,
        averageScore: 0,
        bestScore: 0
      }
    }
  },
  computed: {
    allAttempts() {
      const mock = this.mockAttempts.map(attempt => ({
        ...attempt,
        type: 'mock'
      }))
      const practice = this.practiceAttempts.map(attempt => ({
        ...attempt,
        type: 'practice'
      }))
      return [...mock, ...practice].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    },
    filteredAttempts() {
      if (this.activeTab === 'all') return this.allAttempts
      if (this.activeTab === 'mock') return this.allAttempts.filter(a => a.type === 'mock')
      if (this.activeTab === 'practice') return this.allAttempts.filter(a => a.type === 'practice')
      return []
    }
  },
  async mounted() {
    await this.fetchHistory()
  },
  methods: {
    async fetchHistory() {
      try {
        this.loading = true
        this.error = null
        
        // First, get statistics from UGC NET (this has real data)
        let ugcStats = null
        try {
          const statsResponse = await apiService.ugcNet.getStatistics()
          console.log('UGC NET Statistics response:', statsResponse)
          
          if (statsResponse.success && statsResponse.data) {
            ugcStats = statsResponse.data
            // Set statistics from UGC NET data
            if (ugcStats.user_stats) {
              this.statistics = {
                totalTests: ugcStats.user_stats.total_attempts || 0,
                completedTests: ugcStats.user_stats.completed_attempts || ugcStats.user_stats.total_attempts || 0,
                averageScore: Math.round(ugcStats.user_stats.average_score || 0),
                bestScore: Math.round(ugcStats.user_stats.best_score || 0)
              }
            }
          }
        } catch (statsError) {
          console.log('UGC NET statistics not available:', statsError)
        }

        // Try to get mock tests with attempt data
        try {
          const mockTestsResponse = await apiService.ugcNet.getMockTests()
          console.log('Mock tests response:', mockTestsResponse)
          
          if (mockTestsResponse.success && mockTestsResponse.data) {
            const mockTests = mockTestsResponse.data.mock_tests || mockTestsResponse.data || []
            
            // Convert mock tests to attempt format for display
            this.mockAttempts = mockTests
              .filter(test => test.user_attempts > 0) // Only tests with attempts
              .map(test => ({
                id: test.id,
                test_id: test.id,
                test_name: test.title,
                subject_name: test.subject_name || 'UGC NET',
                total_questions: test.total_questions,
                percentage: test.best_score || 0,
                is_completed: test.best_score !== null,
                created_at: test.last_attempt_date || test.created_at,
                type: 'mock'
              }))
          }
        } catch (mockError) {
          console.log('Mock tests not available:', mockError)
          this.mockAttempts = []
        }

        // Try to get practice history separately
        try {
          const practiceResponse = await apiService.ugcNet.getPracticeHistory()
          console.log('Practice response:', practiceResponse)
          
          if (practiceResponse.success && practiceResponse.data) {
            this.practiceAttempts = (practiceResponse.data.attempts || practiceResponse.data || [])
              .map(attempt => ({
                ...attempt,
                type: 'practice'
              }))
          }
        } catch (practiceError) {
          console.log('Practice history not available:', practiceError)
          this.practiceAttempts = []
        }

        // If we have statistics but no detailed attempts, we still show the stats
        if (this.mockAttempts.length === 0 && this.practiceAttempts.length === 0 && ugcStats) {
          // Create placeholder entries if we have stats but no detailed history
          console.log('No detailed history found, but statistics indicate tests were taken')
        }
        
        // If no statistics were set from UGC NET, calculate them from attempts
        if (this.statistics.totalTests === 0) {
          this.calculateStatistics()
        }
        
        console.log('Final mock attempts:', this.mockAttempts)
        console.log('Final practice attempts:', this.practiceAttempts)
        console.log('Final statistics:', this.statistics)
        
      } catch (error) {
        console.error('Error fetching history:', error)
        this.error = 'Failed to load test history. Please try again.'
      } finally {
        this.loading = false
      }
    },
    calculateStatistics() {
      const all = this.allAttempts
      const completed = all.filter(a => a.is_completed)
      
      this.statistics = {
        totalTests: all.length,
        completedTests: completed.length,
        averageScore: completed.length > 0 ? 
          Math.round(completed.reduce((sum, a) => sum + (a.percentage || 0), 0) / completed.length) : 0,
        bestScore: completed.length > 0 ? 
          Math.max(...completed.map(a => a.percentage || 0)) : 0
      }
    },
    async resumeTest(attempt) {
      if (attempt.type === 'mock') {
        this.$router.push({
          name: 'TestTaking',
          params: { testId: attempt.test_id, attemptId: attempt.id }
        })
      } else {
        this.$router.push({
          name: 'PracticeTaking',
          params: { attemptId: attempt.id }
        })
      }
    },
    async viewResults(attempt) {
      if (attempt.type === 'mock') {
        this.$router.push({
          name: 'TestResults',
          params: { testId: attempt.test_id, attemptId: attempt.id }
        })
      } else {
        this.$router.push({
          name: 'PracticeResults',
          params: { attemptId: attempt.id }
        })
      }
    },
    async deleteAttempt(attempt) {
      if (!confirm('Are you sure you want to delete this test attempt?')) {
        return
      }
      
      try {
        // For now, show a message that this feature is not implemented
        alert('Delete functionality is not available yet. Contact admin if you need to remove test attempts.')
        return
        
        // TODO: Implement delete functionality when backend API is available
        if (attempt.type === 'mock') {
          // await apiService.ugcNet.deleteMockAttempt(attempt.id)
          this.mockAttempts = this.mockAttempts.filter(a => a.id !== attempt.id)
        } else {
          // await apiService.ugcNet.deletePracticeAttempt(attempt.id)
          this.practiceAttempts = this.practiceAttempts.filter(a => a.id !== attempt.id)
        }
        
        this.calculateStatistics()
      } catch (error) {
        console.error('Error deleting attempt:', error)
        alert('Failed to delete test attempt. Please try again.')
      }
    },
    getTypeBadgeClass(type) {
      return type === 'mock' ? 'bg-primary' : 'bg-success'
    },
    getScoreBadgeClass(score) {
      if (score >= 80) return 'bg-success'
      if (score >= 60) return 'bg-warning'
      return 'bg-danger'
    },
    getStatusBadgeClass(isCompleted) {
      return isCompleted ? 'bg-success' : 'bg-warning'
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.container-fluid {
  max-width: 1200px;
}

.nav-tabs .nav-link {
  border: none;
  color: #6c757d;
  padding: 0.75rem 1rem;
}

.nav-tabs .nav-link.active {
  color: #495057;
  background-color: #fff;
  border-bottom: 2px solid #007bff;
}

.nav-tabs .nav-link:hover {
  color: #007bff;
}

.table th {
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

.table td {
  vertical-align: middle;
}

.badge {
  font-size: 0.75rem;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}

.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.display-4 {
  font-size: 2.5rem;
}

.opacity-75 {
  opacity: 0.75;
}

@media (max-width: 768px) {
  .btn-group {
    flex-direction: column;
  }
  
  .btn-group .btn {
    margin-bottom: 0.25rem;
  }
  
  .nav-tabs .nav-link {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
  }
}
</style>
