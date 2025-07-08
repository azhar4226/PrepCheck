<template>
  <div class="analytics-dashboard">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">
        <i class="bi bi-bar-chart me-2"></i>
        System Analytics
      </h2>
      <div class="d-flex gap-2">
        <select v-model="selectedPeriod" @change="loadAnalytics" class="form-select" style="width: auto;">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="365">Last year</option>
        </select>
        <button class="btn btn-success" @click="exportUserAnalytics">
          <i class="bi bi-people me-2"></i>Export User Analytics
        </button>
        <button class="btn btn-info" @click="exportQuestionBankAnalytics">
          <i class="bi bi-question-circle me-2"></i>Export Question Bank
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading analytics...</span>
      </div>
    </div>

    <!-- Analytics Content - All in One View -->
    <div v-else-if="analytics" class="analytics-content">
      <!-- System Overview Section -->
      <!-- <div class="analytics-section mb-5">
        <div class="section-header mb-3">
          <h4 class="mb-0">
            <i class="bi bi-speedometer2 me-2"></i>
            System Overview
          </h4>
        </div> -->
      <!-- Key Metrics Cards -->
      <!-- <div class="row mb-4">
        <div class="col-md-3 mb-3">
          <div class="card bg-primary text-white">
            <div class="card-body text-center">
              <i class="bi bi-people display-4 mb-3"></i>
              <h3 class="mb-1">{{ analytics.stats.total_users }}</h3>
              <p class="mb-0">Total Users</p>
              <small class="opacity-75">{{ analytics.stats.active_users }} active</small>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-success text-white">
            <div class="card-body text-center">
              <i class="bi bi-clipboard-check display-4 mb-3"></i>
              <h3 class="mb-1">{{ analytics.stats.total_attempts }}</h3>
              <p class="mb-0">Total Attempts</p>
              <small class="opacity-75">{{ analytics.stats.recent_attempts }} recent</small>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-info text-white">
            <div class="card-body text-center">
              <i class="bi bi-graph-up display-4 mb-3"></i>
              <h3 class="mb-1">{{ analytics.performance.average_percentage }}%</h3>
              <p class="mb-0">Avg Score</p>
              <small class="opacity-75">{{ analytics.performance.pass_rate }}% pass rate</small>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-warning text-white">
            <div class="card-body text-center">
              <i class="bi bi-clock display-4 mb-3"></i>
              <h3 class="mb-1">{{ analytics.performance.average_time_minutes }}</h3>
              <p class="mb-0">Avg Time (min)</p>
              <small class="opacity-75">per test</small>
            </div>
          </div>
        </div>
      </div> -->

      <!-- Charts Section -->
      <div class="row mb-4">
        <!-- Daily Trends Chart -->
        <div class="col-lg-8 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-graph-up me-2"></i>Daily Activity Trends
              </h5>
            </div>
            <div class="card-body">
              <div style="position: relative; height: 300px;">
                <canvas ref="dailyChart"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- User Engagement -->
        <div class="col-lg-4 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-people me-2"></i>User Engagement
              </h5>
            </div>
            <div class="card-body">
              <div class="text-center mb-3">
                <div class="display-6 fw-bold text-success">{{ analytics.engagement.retention_rate }}%</div>
                <small class="text-muted">Retention Rate</small>
              </div>
              
              <div class="row text-center">
                <div class="col-6">
                  <div class="h5 mb-0">{{ analytics.engagement.total_registered }}</div>
                  <small class="text-muted">Registered</small>
                </div>
                <div class="col-6">
                  <div class="h5 mb-0">{{ analytics.engagement.active_users }}</div>
                  <small class="text-muted">Active</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Subject Performance -->
      <div class="row mb-4">
        <div class="col-lg-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-book me-2"></i>Subject Performance
              </h5>
            </div>
            <div class="card-body">
              <div v-if="analytics.subjects.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-book display-4 mb-3 opacity-50"></i>
                <h6 class="text-muted">No Subject Data Available</h6>
                <p class="small">Subject performance data will appear here once users start taking mock tests.</p>
              </div>
              <div v-else>
                <div 
                  v-for="subject in analytics.subjects" 
                  :key="subject.subject"
                  class="mb-3"
                >
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="fw-medium">{{ subject.subject }}</span>
                    <span class="badge bg-primary">{{ subject.attempts }} attempts</span>
                  </div>
                  <div class="progress">
                    <div 
                      class="progress-bar" 
                      :class="getScoreColor(subject.average_percentage)"
                      :style="{ width: subject.average_percentage + '%' }"
                    >
                      {{ subject.average_percentage }}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Performers -->
        <div class="col-lg-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-trophy me-2"></i>Recent Top Performers
              </h5>
            </div>
            <div class="card-body">
              <div v-if="topPerformers.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-trophy display-4 mb-3 opacity-50"></i>
                <h6 class="text-muted">No Top Performers Yet</h6>
                <p class="small">Top performers will appear here when users score 80% or higher on mock tests.</p>
              </div>
              <div v-else>
                <div class="mb-3 d-flex justify-content-between align-items-center">
                  <small class="text-muted">Recent high scorers (80%+ scores)</small>
                  <span class="badge bg-info">{{ topPerformers.length }} performers</span>
                </div>
                <div class="list-group list-group-flush">
                  <div 
                    v-for="(performer, index) in topPerformers.slice(0, 10)" 
                    :key="performer.id"
                    class="list-group-item d-flex justify-content-between align-items-center px-0 py-2"
                  >
                    <div class="d-flex align-items-center">
                      <span 
                        class="badge rounded-pill me-3"
                        :class="index < 3 ? 'bg-warning' : 'bg-secondary'"
                      >
                        {{ index + 1 }}
                      </span>
                      <div class="flex-grow-1">
                        <div class="fw-medium text-truncate" style="max-width: 150px;">
                          {{ performer.user_name || 'Unknown User' }}
                        </div>
                        <small class="text-muted text-truncate d-block" style="max-width: 150px;">
                          {{ performer.test_title || 'Unknown Test' }}
                        </small>
                        <small class="text-muted">
                          {{ formatDate(performer.completed_at) }}
                        </small>
                      </div>
                    </div>
                    <div class="text-end">
                      <span 
                        class="badge fs-6"
                        :class="getScoreColor(performer.percentage)"
                      >
                        {{ performer.percentage }}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>  
    </div>

      <!-- Detailed Analytics Table -->
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">
            <i class="bi bi-table me-2"></i>Detailed Analytics
          </h5>
          <div class="btn-group btn-group-sm">
            <button 
              v-for="tab in analyticsTab" 
              :key="tab.key"
              class="btn btn-outline-primary"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>

        <div class="card-body">

          <!-- Users Tab -->
          <div v-if="activeTab === 'users'" class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Total Attempts</th>
                  <th>Average Score</th>
                  <th>Last Activity</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in detailedUsers" :key="user.id">
                  <td>
                    <div>
                      <div class="fw-medium">{{ user.full_name }}</div>
                      <small class="text-muted">{{ user.email }}</small>
                    </div>
                  </td>
                  <td>{{ user.total_attempts || 0 }}</td>
                  <td>
                    <span class="badge" :class="getScoreColor(user.average_score || 0)">
                      {{ user.average_score || 0 }}%
                    </span>
                  </td>
                  <td>{{ formatDate(user.last_login) }}</td>
                  <td>
                    <button 
                      class="btn btn-sm btn-outline-primary"
                      @click="viewUserAnalytics(user.id)"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Tests Tab -->
          <div v-if="activeTab === 'tests'" class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Test</th>
                  <th>Subject</th>
                  <th>Attempts</th>
                  <th>Average Score</th>
                  <th>Difficulty</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="test in detailedTests" :key="test.id">
                  <td>
                    <div>
                      <div class="fw-medium">{{ test.title }}</div>
                      <small class="text-muted">{{ test.total_questions }} questions</small>
                    </div>
                  </td>
                  <td>{{ test.subject_name }}</td>
                  <td>{{ test.attempts_count || 0 }}</td>
                  <td>
                    <span class="badge" :class="getScoreColor(test.average_score || 0)">
                      {{ test.average_score || 0 }}%
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="getDifficultyColor(test.difficulty)">
                      {{ test.difficulty || 'Medium' }}
                    </span>
                  </td>
                  <td>
                    <button 
                      class="btn btn-sm btn-outline-primary"
                      @click="viewTestAnalytics(test.id)"
                    >
                      Analyze
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

        </div>

      </div>


      <!-- User Analytics Tab -->
      <div class="tab-pane fade" id="user-analytics" role="tabpanel" aria-labelledby="user-analytics-tab">
        <div class="row mb-4">
          <div class="col-12">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="bi bi-person-lines-fill me-2"></i>Individual User Analytics
                </h5>
                <small class="text-muted">Select a user to view detailed performance analytics</small>
              </div>
              <div class="card-body">
                <!-- User Selection -->
                <div class="row mb-4">
                  <div class="col-md-6">
                    <label for="userSelect" class="form-label">Select User:</label>
                    <select 
                      id="userSelect" 
                      v-model="selectedUserId" 
                      @change="loadUserAnalytics" 
                      class="form-select"
                    >
                      <option value="">Choose a user...</option>
                      <option 
                        v-for="user in users" 
                        :key="user.id" 
                        :value="user.id"
                      >
                        {{ user.full_name }} ({{ user.email }})
                      </option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label for="analyticsTimeframe" class="form-label">Timeframe:</label>
                    <select 
                      id="analyticsTimeframe" 
                      v-model="userAnalyticsTimeframe" 
                      @change="loadUserAnalytics" 
                      class="form-select"
                    >
                      <option value="7">Last 7 days</option>
                      <option value="30">Last 30 days</option>
                      <option value="90">Last 90 days</option>
                    </select>
                  </div>
                </div>

                <!-- User Analytics Content -->
                <div v-if="loadingUserAnalytics" class="text-center py-5">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading user analytics...</span>
                  </div>
                </div>

                <div v-else-if="userAnalyticsError" class="alert alert-danger">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  {{ userAnalyticsError }}
                </div>

                <div v-else-if="selectedUserId && userAnalytics" class="user-analytics-content">
                  <!-- User Summary Cards -->
                  <div class="row mb-4">
                    <div class="col-md-3 mb-3">
                      <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                          <i class="bi bi-clipboard-check display-6 mb-2"></i>
                          <h4 class="mb-1">{{ userAnalytics.summary.total_attempts }}</h4>
                          <p class="mb-0 small">Test Attempts</p>
                        </div>
                      </div>
                    </div>

                    <div class="col-md-3 mb-3">
                      <div class="card bg-success text-white">
                        <div class="card-body text-center">
                          <i class="bi bi-trophy display-6 mb-2"></i>
                          <h4 class="mb-1">{{ userAnalytics.summary.average_score }}%</h4>
                          <p class="mb-0 small">Average Score</p>
                        </div>
                      </div>
                    </div>

                    <div class="col-md-3 mb-3">
                      <div class="card bg-info text-white">
                        <div class="card-body text-center">
                          <i class="bi bi-graph-up display-6 mb-2"></i>
                          <h4 class="mb-1">
                            {{ userAnalytics.summary.score_trend > 0 ? '+' : '' }}{{ userAnalytics.summary.score_trend }}%
                          </h4>
                          <p class="mb-0 small">Score Trend</p>
                        </div>
                      </div>
                    </div>

                    <div class="col-md-3 mb-3">
                      <div class="card bg-warning text-white">
                        <div class="card-body text-center">
                          <i class="bi bi-question-circle display-6 mb-2"></i>
                          <h4 class="mb-1">{{ userAnalytics.question_analytics.total_questions_answered }}</h4>
                          <p class="mb-0 small">Questions Answered</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Subject Performance -->
                  <div class="row mb-4" v-if="userAnalytics.subject_performance.length > 0">
                    <div class="col-12">
                      <div class="card">
                        <div class="card-header">
                          <h6 class="mb-0">Subject Performance</h6>
                        </div>
                        <div class="card-body">
                          <div class="row">
                            <div 
                              v-for="subject in userAnalytics.subject_performance" 
                              :key="subject.name"
                              class="col-md-6 col-lg-4 mb-3"
                            >
                              <div class="border rounded p-3">
                                <h6 class="mb-2">{{ subject.name }}</h6>
                                <div class="d-flex justify-content-between mb-2">
                                  <span class="text-muted">Score:</span>
                                  <span class="fw-bold">{{ subject.percentage }}%</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                  <span class="text-muted">Attempts:</span>
                                  <span>{{ subject.attempts }}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Improvement Suggestions -->
                  <div class="row" v-if="userAnalytics.question_analytics.improvement_suggestions.length > 0">
                    <div class="col-12">
                      <div class="card">
                        <div class="card-header">
                          <h6 class="mb-0">
                            <i class="bi bi-lightbulb me-2"></i>Improvement Recommendations
                          </h6>
                        </div>
                        <div class="card-body">
                          <div 
                            v-for="(suggestion, index) in userAnalytics.question_analytics.improvement_suggestions" 
                            :key="index"
                            class="alert mb-3"
                            :class="getSuggestionClass(suggestion.priority)"
                          >
                            <div class="d-flex align-items-start">
                              <i class="bi me-2 mt-1" :class="getSuggestionIcon(suggestion.type)"></i>
                              <div class="flex-grow-1">
                                <div class="fw-bold">{{ formatSuggestionType(suggestion.type) }}</div>
                                <div>{{ suggestion.message }}</div>
                              </div>
                              <span class="badge" :class="getPriorityBadgeClass(suggestion.priority)">
                                {{ suggestion.priority.toUpperCase() }}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-else-if="!selectedUserId" class="text-center py-5 text-muted">
                  <i class="bi bi-person-plus display-4 mb-3"></i>
                  <h5>Select a User</h5>
                  <p>Choose a user from the dropdown above to view their detailed analytics</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Question Bank Tab -->
      <div class="tab-pane fade" id="question-bank" role="tabpanel" aria-labelledby="question-bank-tab">
        <div class="row">
          <div class="col-12">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="bi bi-question-circle me-2"></i>Question Bank Analytics
                </h5>
                <small class="text-muted">Analytics and insights from the AI question bank</small>
              </div>
              <div class="card-body">
                <div class="text-center py-5 text-muted">
                  <i class="bi bi-question-circle display-4 mb-3"></i>
                  <h5>Question Bank Analytics</h5>
                  <p>Detailed question bank analytics will be displayed here</p>
                  <router-link to="/admin/question-bank" class="btn btn-primary">
                    <i class="bi bi-question-circle me-2"></i>Manage Question Bank
                  </router-link>
                </div>
              </div>
            </div>          
          </div>
        </div>
      </div>
    </div>  

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
    </div>
</template>

<script>
import { ref, onMounted, computed, nextTick } from 'vue'
import analyticsService from '@/services/analyticsService'
import adminService from '@/services/adminService'
import apiClient from '@/services/apiClient'
import Chart from 'chart.js/auto'

export default {
  name: 'AnalyticsDashboard',
  setup() {
    const loading = ref(false)
    const error = ref('')
    const analytics = ref(null)
    const selectedPeriod = ref(30)
    const activeTab = ref('users')
    const topPerformers = ref([])
    const detailedUsers = ref([])
    const detailedTests = ref([])
    const dailyChart = ref(null)
    const dailyChartInstance = ref(null)
    
    // User analytics specific data
    const users = ref([])
    const selectedUserId = ref('')
    const userAnalytics = ref(null)
    const userAnalyticsTimeframe = ref(30)
    const loadingUserAnalytics = ref(false)
    const userAnalyticsError = ref('')

    const analyticsTab = [
      { key: 'users', label: 'Users' },
      { key: 'tests', label: 'Tests' }
    ]

    const loadAnalytics = async () => {
      try {
        loading.value = true
        error.value = ''

        const response = await adminService.getDashboard()
        analytics.value = {
          stats: {
            total_users: response.total_users || 0,
            total_attempts: response.total_attempts || 0,
            active_users: response.active_users || 0,
            recent_attempts: response.recent_attempts || 0
          },
          performance: {
            average_percentage: response.average_score || 0,
            pass_rate: response.pass_rate || 0,
            average_time_minutes: response.average_time || 0
          },
          engagement: {
            retention_rate: response.retention_rate || 0,
            total_registered: response.total_users || 0,
            active_users: response.active_users || 0
          },
          subjects: response.subject_stats || []
        }   
        
        // Set top performers from the same response
        topPerformers.value = response.top_performers || []
        
        // Set daily trends data for charts
        const dailyTrends = response.daily_trends || []
        
        // Set sample detailed data for now
        detailedUsers.value = []
        detailedTests.value = []
        
        // Create charts after data is loaded
        await nextTick()
        try {
          createDailyChart(dailyTrends)
        } catch (chartError) {
          console.warn('Chart creation failed:', chartError)
          // Continue without charts
        }

      } catch (err) {
        console.error('Analytics error:', err)
        error.value = err.response?.data?.error || 'Failed to load analytics'
      } finally {
        loading.value = false
      }
    }

    const createDailyChart = (dailyTrendsData = []) => {
      try {
        console.log('Creating daily chart with data:', dailyTrendsData)
        
        // Wait for next tick to ensure DOM is ready, with retry logic
        const attemptChartCreation = (retryCount = 0) => {
          if (!dailyChart.value) {
            if (retryCount < 5) {
              console.log(`Canvas ref not found, retrying... (${retryCount + 1}/5)`)
              setTimeout(() => attemptChartCreation(retryCount + 1), 100)
              return
            } else {
              console.error('Canvas ref not found after 5 retries')
              return
            }
          }
          
          // Destroy existing chart
          if (dailyChartInstance.value) {
            dailyChartInstance.value.destroy()
          }
        
          // Use real data if available, otherwise generate sample data
          let labels = []
          let attempts = []
          let avgScores = []
          
          if (dailyTrendsData && dailyTrendsData.length > 0) {
            // Use real data from backend
            console.log('Using real data for chart')
            labels = dailyTrendsData.map(day => day.date)
            attempts = dailyTrendsData.map(day => day.attempts)
            avgScores = dailyTrendsData.map(day => day.average_score)
          } else {
            // Generate sample data for the last 7 days as fallback
            console.log('Using sample data for chart')
            for (let i = 6; i >= 0; i--) {
              const date = new Date()
              date.setDate(date.getDate() - i)
              labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))
              attempts.push(Math.floor(Math.random() * 20) + 5)
              avgScores.push(Math.floor(Math.random() * 30) + 70)
            }
          }
          
          console.log('Chart data prepared:', { labels, attempts, avgScores })
          
          const ctx = dailyChart.value.getContext('2d')
          console.log('Canvas context:', ctx)
          
          dailyChartInstance.value = new Chart(ctx, {
            type: 'line',
            data: {
              labels: labels,
              datasets: [
                {
                  label: 'Test Attempts',
                  data: attempts,
                  borderColor: '#007bff',
                  backgroundColor: 'rgba(0, 123, 255, 0.1)',
                  borderWidth: 2,
                  tension: 0.1,
                  fill: true
                },
                {
                  label: 'Average Score (%)',
                  data: avgScores,
                  borderColor: '#28a745',
                  backgroundColor: 'rgba(40, 167, 69, 0.1)',
                  borderWidth: 2,
                  tension: 0.1,
                  fill: true,
                  yAxisID: 'y1'
                }
              ]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                title: {
                  display: true,
                  text: 'Daily Activity Trends (Last 7 Days)'
                },
                legend: {
                  display: true,
                  position: 'top'
                }
              },
              scales: {
                x: {
                  display: true,
                  title: {
                    display: true,
                    text: 'Date'
                  }
                },
                y: {
                  type: 'linear',
                  display: true,
                  position: 'left',
                  title: {
                    display: true,
                    text: 'Test Attempts'
                  },
                  beginAtZero: true
                },
                y1: {
                  type: 'linear',
                  display: true,
                  position: 'right',
                  title: {
                    display: true,
                    text: 'Average Score (%)'
                  },
                  beginAtZero: true,
                  max: 100,
                  grid: {
                    drawOnChartArea: false,
                  }
                }
              }
            }
          })
          
          console.log('Chart created successfully:', dailyChartInstance.value)
        }
        
        // Start the chart creation attempt
        nextTick(() => {
          attemptChartCreation()
        })
        
      } catch (error) {
        console.error('Chart creation error:', error)
      }
    }

    const exportAnalytics = async () => {
      try {
        const response = await adminService.exportData('analytics')
        if (response.files_created && response.files_created.length > 0) {
          // Create download links for each file
          const downloadPromises = response.files_created.map(async (filePath) => {
            const filename = filePath.split('/').pop() // Get filename from path
            try {
              const downloadResponse = await adminService.downloadExportFile(filename)
              
              // Create download link
              const blob = new Blob([downloadResponse.data], { 
                type: downloadResponse.headers['content-type'] || 'application/octet-stream' 
              })
              const url = window.URL.createObjectURL(blob)
              const link = document.createElement('a')
              link.href = url
              link.download = filename
              document.body.appendChild(link)
              link.click()
              document.body.removeChild(link)
              window.URL.revokeObjectURL(url)
              
              return filename
            } catch (downloadErr) {
              console.error(`Failed to download ${filename}:`, downloadErr)
              return null
            }
          })
          
          const downloadedFiles = await Promise.all(downloadPromises)
          const successfulDownloads = downloadedFiles.filter(f => f !== null)
          
          if (successfulDownloads.length > 0) {
            alert(`Export completed! Downloaded files: ${successfulDownloads.join(', ')}`)
          } else {
            alert('Export completed but failed to download files. Please check the exports folder.')
          }
        } else if (response.message) {
          alert(response.message)
        } else {
          alert('Export completed successfully!')
        }
      } catch (err) {
        console.error('Export error:', err)
        alert('Failed to export analytics data')
      }
    }

    const refreshAnalytics = async () => {
      await loadAnalytics()
    }

    const viewUserAnalytics = (userId) => {
      // Navigate to detailed user analytics
      window.open(`/admin/analytics/user/${userId}`, '_blank')
    }

    const viewTestAnalytics = (testId) => {
      // Navigate to detailed test analytics
      window.open(`/admin/analytics/test/${testId}`, '_blank')
    }

    const getScoreColor = (percentage) => {
      if (percentage >= 90) return 'bg-success'
      if (percentage >= 80) return 'bg-info'
      if (percentage >= 70) return 'bg-warning'
      return 'bg-danger'
    }

    const getDifficultyColor = (difficulty) => {
      switch (difficulty?.toLowerCase()) {
        case 'easy': return 'bg-success'
        case 'medium': return 'bg-warning'
        case 'hard': return 'bg-danger'
        default: return 'bg-secondary'
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Never'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    // User analytics functions
    const loadUsers = async () => {
      try {
        const response = await adminService.getAllUsers()
        users.value = response.data?.users || response.users || []
      } catch (err) {
        console.error('Failed to load users:', err)
        userAnalyticsError.value = 'Failed to load users'
        users.value = [] // Ensure users is always an array
      }
    }

    const loadUserAnalytics = async () => {
      if (!selectedUserId.value) {
        userAnalytics.value = null
        return
      }

      try {
        loadingUserAnalytics.value = true
        userAnalyticsError.value = ''

        // Admin can view any user's analytics by making a direct API call
        const response = await apiClient.get(`/admin/user/${selectedUserId.value}/analytics`, {
          params: {
            days: userAnalyticsTimeframe.value
          }
        })
        
        userAnalytics.value = response.data
      } catch (err) {
        console.error('Failed to load user analytics:', err)
        userAnalyticsError.value = err.response?.data?.error || 'Failed to load user analytics'
      } finally {
        loadingUserAnalytics.value = false
      }
    }

    // Helper functions for user analytics UI
    const getSuggestionClass = (priority) => {
      const classes = {
        'high': 'alert-danger',
        'medium': 'alert-warning',
        'low': 'alert-info'
      }
      return classes[priority] || 'alert-info'
    }

    const getSuggestionIcon = (type) => {
      const icons = {
        'topic_improvement': 'bi-book',
        'difficulty_adjustment': 'bi-sliders',
        'practice_frequency': 'bi-clock'
      }
      return icons[type] || 'bi-lightbulb'
    }

    const getPriorityBadgeClass = (priority) => {
      const classes = {
        'high': 'bg-danger',
        'medium': 'bg-warning',
        'low': 'bg-info'
      }
      return classes[priority] || 'bg-secondary'
    }

    const formatSuggestionType = (type) => {
      return type.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ')
    }

    // Export functions
    const exportUserAnalytics = async () => {
      try {
        loading.value = true
        console.log('Exporting user analytics...')
        
        const response = await apiClient.post('/api/admin/export/user-analytics', {
          period: selectedPeriod.value,
          format: 'pdf',
          include: ['user_stats', 'performance_data', 'activity_logs']
        }, {
          responseType: 'blob'
        })
        
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `user-analytics-${getCurrentDateString()}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        console.log('User analytics exported successfully')
      } catch (error) {
        console.error('User analytics export failed:', error)
        error.value = 'Failed to export user analytics. Please try again.'
      } finally {
        loading.value = false
      }
    }

    const exportQuestionBankAnalytics = async () => {
      try {
        loading.value = true
        console.log('Exporting question bank analytics...')
        
        const response = await apiClient.post('/api/admin/export/question-bank', {
          period: selectedPeriod.value,
          format: 'pdf',
          include: ['question_stats', 'difficulty_analysis', 'subject_breakdown']
        }, {
          responseType: 'blob'
        })
        
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `question-bank-analytics-${getCurrentDateString()}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        console.log('Question bank analytics exported successfully')
      } catch (error) {
        console.error('Question bank analytics export failed:', error)
        error.value = 'Failed to export question bank analytics. Please try again.'
      } finally {
        loading.value = false
      }
    }

    // Helper function for date formatting
    const getCurrentDateString = () => {
      return new Date().toISOString().split('T')[0] // Returns YYYY-MM-DD
    }

    onMounted(() => {
      loadAnalytics()
      loadUsers()
    })

    return {
      loading,
      error,
      analytics,
      selectedPeriod,
      activeTab,
      analyticsTab,
      topPerformers,
      detailedUsers,
      detailedTests,
      dailyChart,
      // User analytics data
      users,
      selectedUserId,
      userAnalytics,
      userAnalyticsTimeframe,
      loadingUserAnalytics,
      userAnalyticsError,
      // Methods
      loadAnalytics,
      refreshAnalytics,
      exportAnalytics,
      exportUserAnalytics,
      exportQuestionBankAnalytics,
      viewUserAnalytics,
      viewTestAnalytics,
      loadUserAnalytics,
      getSuggestionClass,
      getSuggestionIcon,
      getPriorityBadgeClass,
      formatSuggestionType,
      getScoreColor,
      getDifficultyColor,
      formatDate
    }
  }
}
</script>

<style scoped>
.analytics-dashboard {
  padding: 1rem;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.progress {
  height: 8px;
}

.badge {
  font-size: 0.75em;
}

.opacity-75 {
  opacity: 0.75;
}

.table th {
  border-top: none;
  font-weight: 600;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.btn-group .btn.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: white;
}

.analytics-content {
  max-height: 80vh;
  overflow-y: auto;
}

.analytics-section {
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 2rem;
}

.analytics-section:last-child {
  border-bottom: none;
}

.section-header {
  border-left: 4px solid #007bff;
  padding-left: 1rem;
  background-color: #f8f9fa;
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
}

.section-header h4 {
  color: #495057;
  font-weight: 600;
}
</style>
