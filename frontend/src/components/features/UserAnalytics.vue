<template>
  <div class="user-analytics">
    <!-- Header with filters -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">
        <i class="bi bi-graph-up me-2"></i>My Performance Analytics
      </h3>
      <div class="d-flex gap-2">
        <select v-model="filters.days" @change="loadAnalytics" class="form-select" style="width: auto;">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
        </select>
        <button class="btn btn-outline-primary btn-sm" @click="refreshAnalytics" :disabled="loading">
          <i class="bi bi-arrow-clockwise me-1" :class="{ 'spin': loading }"></i>
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading analytics...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle me-2"></i>
      {{ error }}
    </div>

    <!-- Analytics Content -->
    <div v-else-if="analytics">
      <!-- Summary Cards -->
      <div class="row mb-4">
        <div class="col-md-3 mb-3">
          <div class="card bg-primary text-white">
            <div class="card-body text-center">
              <i class="bi bi-clipboard-check display-6 mb-2"></i>
              <h4 class="mb-1">{{ analytics.summary.total_attempts }}</h4>
              <p class="mb-0 small">Mock Test Attempts</p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-success text-white">
            <div class="card-body text-center">
              <i class="bi bi-trophy display-6 mb-2"></i>
              <h4 class="mb-1">{{ analytics.summary.average_score }}%</h4>
              <p class="mb-0 small">Average Score</p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-info text-white">
            <div class="card-body text-center">
              <i class="bi bi-graph-up display-6 mb-2"></i>
              <h4 class="mb-1">
                {{ analytics.summary.score_trend > 0 ? '+' : '' }}{{ analytics.summary.score_trend }}%
              </h4>
              <p class="mb-0 small">Score Trend</p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card bg-warning text-white">
            <div class="card-body text-center">
              <i class="bi bi-question-circle display-6 mb-2"></i>
              <h4 class="mb-1">{{ questionsAnswered }}</h4>
              <p class="mb-0 small">Questions Answered</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Details -->
      <div class="row mb-4">
        <!-- Daily Performance Chart -->
        <div class="col-lg-8 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-calendar3 me-2"></i>Daily Performance
              </h5>
            </div>
            <div class="card-body">
              <div v-if="analytics.daily_performance.length > 0">
                <canvas ref="dailyChart" style="max-height: 300px;"></canvas>
              </div>
              <div v-else class="text-center py-4 text-muted">
                <i class="bi bi-graph-down display-4 mb-3"></i>
                <p>No UGC NET mock test data available for the selected period.</p>
                <router-link to="/ugc-net" class="btn btn-primary">
                  <i class="bi bi-play-circle me-2"></i>Take Your First UGC NET Mock Test
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Question Analytics -->
        <div class="col-lg-4 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-bullseye me-2"></i>Question Analytics
              </h5>
            </div>
            <div class="card-body">
              <div class="text-center mb-3">
                <div class="h2 text-primary">{{ analytics.question_analytics.accuracy_rate }}%</div>
                <small class="text-muted">Overall Accuracy</small>
              </div>
              
              <div class="mb-3">
                <small class="text-muted d-block">Correct Answers</small>
                <div class="progress" style="height: 8px;">
                  <div 
                    class="progress-bar bg-success" 
                    :style="{ width: analytics.question_analytics.accuracy_rate + '%' }"
                  ></div>
                </div>
                <small class="text-muted">
                  {{ analytics.question_analytics.correct_answers }} / {{ analytics.question_analytics.total_questions_answered }}
                </small>
              </div>

              <!-- Difficulty Breakdown -->
              <div v-if="Object.keys(analytics.question_analytics.question_types_breakdown).length > 0">
                <h6 class="mb-2">By Difficulty</h6>
                <div 
                  v-for="(stats, difficulty) in analytics.question_analytics.question_types_breakdown" 
                  :key="difficulty"
                  class="mb-2"
                >
                  <div class="d-flex justify-content-between">
                    <small>{{ difficulty }}</small>
                    <small>{{ stats.accuracy }}%</small>
                  </div>
                  <div class="progress" style="height: 6px;">
                    <div 
                      class="progress-bar" 
                      :class="getDifficultyColor(difficulty)"
                      :style="{ width: stats.accuracy + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Subject Performance -->
      <div class="row mb-4" v-if="analytics.subject_performance.length > 0">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-book me-2"></i>Subject Performance
              </h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div 
                  v-for="subject in analytics.subject_performance" 
                  :key="subject.name"
                  class="col-md-6 col-lg-4 mb-3"
                >
                  <div class="border rounded p-3">
                    <h6 class="mb-2">{{ subject.name }}</h6>
                    <div class="d-flex justify-content-between mb-2">
                      <span class="text-muted">Score:</span>
                      <span class="fw-bold">{{ subject.percentage }}%</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                      <span class="text-muted">Attempts:</span>
                      <span>{{ subject.attempts }}</span>
                    </div>
                    
                    <!-- Chapter breakdown -->
                    <div v-if="subject.chapters.length > 0" class="mt-3">
                      <small class="text-muted d-block mb-2">Chapters:</small>
                      <div 
                        v-for="chapter in subject.chapters" 
                        :key="chapter.name"
                        class="d-flex justify-content-between small mb-1"
                      >
                        <span>{{ chapter.name }}</span>
                        <span>{{ chapter.percentage }}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Topics Performance -->
      <div class="row mb-4" v-if="hasTopicData">
        <div class="col-lg-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0 text-success">
                <i class="bi bi-trophy me-2"></i>Strongest Topics
              </h5>
            </div>
            <div class="card-body">
              <div v-if="analytics.question_analytics.strongest_topics.length > 0">
                <div 
                  v-for="topic in analytics.question_analytics.strongest_topics" 
                  :key="topic.topic"
                  class="d-flex justify-content-between align-items-center mb-3 p-2 bg-light rounded"
                >
                  <div>
                    <div class="fw-bold">{{ topic.topic }}</div>
                    <small class="text-muted">{{ topic.correct_answers }}/{{ topic.questions_answered }} correct</small>
                  </div>
                  <div class="badge bg-success">{{ topic.accuracy }}%</div>
                </div>
              </div>
              <div v-else class="text-muted text-center py-3">
                <i class="bi bi-trophy display-4 mb-2"></i>
                <p>Complete more UGC NET mock tests to see your strongest topics</p>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0 text-warning">
                <i class="bi bi-exclamation-triangle me-2"></i>Areas for Improvement
              </h5>
            </div>
            <div class="card-body">
              <div v-if="analytics.question_analytics.most_difficult_topics.length > 0">
                <div 
                  v-for="topic in analytics.question_analytics.most_difficult_topics" 
                  :key="topic.topic"
                  class="d-flex justify-content-between align-items-center mb-3 p-2 bg-light rounded"
                >
                  <div>
                    <div class="fw-bold">{{ topic.topic }}</div>
                    <small class="text-muted">{{ topic.correct_answers }}/{{ topic.questions_answered }} correct</small>
                  </div>
                  <div class="badge bg-warning">{{ topic.accuracy }}%</div>
                </div>
              </div>
              <div v-else class="text-muted text-center py-3">
                <i class="bi bi-check-circle display-4 mb-2"></i>
                <p>Great job! No weak areas identified yet.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Improvement Suggestions -->
      <div class="row mb-4" v-if="analytics.question_analytics.improvement_suggestions.length > 0">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-lightbulb me-2"></i>Personalized Recommendations
              </h5>
            </div>
            <div class="card-body">
              <div 
                v-for="(suggestion, index) in analytics.question_analytics.improvement_suggestions" 
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

    <!-- Empty State -->
    <div v-else class="text-center py-5">
      <i class="bi bi-graph-down display-1 text-muted mb-3"></i>
      <h4 class="text-muted">No analytics data available</h4>
      <p class="text-muted mb-4">Start taking UGC NET mock tests to see your performance analytics</p>
      <router-link to="/ugc-net" class="btn btn-primary">
        <i class="bi bi-play-circle me-2"></i>Browse UGC NET Mock Tests
      </router-link>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import ugcNetService from '@/services/ugcNetService'

Chart.register(...registerables)

export default {
  name: 'UserAnalytics',
  data() {
    return {
      analytics: null,
      loading: false,
      error: null,
      filters: {
        days: 30
      },
      dailyChart: null
    }
  },
  computed: {
    hasTopicData() {
      return this.analytics && (
        this.analytics.question_analytics.strongest_topics.length > 0 ||
        this.analytics.question_analytics.most_difficult_topics.length > 0
      )
    },
    questionsAnswered() {
      if (!this.analytics) return 0
      
      // Use the calculated value from summary if available, otherwise use question analytics
      return this.analytics.summary.total_questions_answered || 
             this.analytics.question_analytics.total_questions_answered || 0
    }
  },
  mounted() {
    this.loadAnalytics()
  },
  beforeUnmount() {
    if (this.dailyChart) {
      this.dailyChart.destroy()
    }
  },
  methods: {
    async loadAnalytics() {
      this.loading = true
      this.error = null
      
      try {
        const response = await ugcNetService.getStatistics()
        if (response.success) {
          this.analytics = response.data
        } else {
          throw new Error(response.error || 'Failed to load statistics')
        }
        this.$nextTick(() => {
          this.createDailyChart()
        })
      } catch (error) {
        this.error = error.response?.data?.error || error.message || 'Failed to load analytics'
        console.error('Error loading user analytics:', error)
      } finally {
        this.loading = false
      }
    },
    
    async refreshAnalytics() {
      await this.loadAnalytics()
    },

    createDailyChart() {
      if (!this.analytics?.daily_performance?.length || !this.$refs.dailyChart) {
        return
      }

      // Destroy existing chart
      if (this.dailyChart) {
        this.dailyChart.destroy()
      }

      const ctx = this.$refs.dailyChart.getContext('2d')
      const data = this.analytics.daily_performance

      this.dailyChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.map(d => new Date(d.date).toLocaleDateString()),
          datasets: [
            {
              label: 'Test Attempts',
              data: data.map(d => d.attempts),
              borderColor: '#007bff',
              backgroundColor: 'rgba(0, 123, 255, 0.1)',
              borderWidth: 2,
              fill: true,
              tension: 0.3,
              yAxisID: 'y'
            },
            {
              label: 'Performance (%)',
              data: data.map(d => d.percentage),
              borderColor: '#28a745',
              backgroundColor: 'rgba(40, 167, 69, 0.1)',
              borderWidth: 2,
              fill: false,
              tension: 0.3,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: true,
              position: 'top'
            },
            tooltip: {
              mode: 'index',
              intersect: false
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
                text: 'Performance (%)'
              },
              grid: {
                drawOnChartArea: false
              },
              beginAtZero: true,
              max: 100
            }
          },
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
          }
        }
      })
    },

    getDifficultyColor(difficulty) {
      const colors = {
        'Easy': 'bg-success',
        'Medium': 'bg-warning',
        'Hard': 'bg-danger',
        'Expert': 'bg-dark'
      }
      return colors[difficulty] || 'bg-primary'
    },

    getSuggestionClass(priority) {
      const classes = {
        'high': 'alert-danger',
        'medium': 'alert-warning',
        'low': 'alert-info'
      }
      return classes[priority] || 'alert-info'
    },

    getSuggestionIcon(type) {
      const icons = {
        'topic_improvement': 'bi-book',
        'difficulty_adjustment': 'bi-sliders',
        'practice_frequency': 'bi-clock'
      }
      return icons[type] || 'bi-lightbulb'
    },

    getPriorityBadgeClass(priority) {
      const classes = {
        'high': 'bg-danger',
        'medium': 'bg-warning',
        'low': 'bg-info'
      }
      return classes[priority] || 'bg-secondary'
    },

    formatSuggestionType(type) {
      return type.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ')
    }
  }
}
</script>

<style scoped>
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.progress {
  border-radius: 10px;
}

.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-2px);
}

.alert {
  border-left: 4px solid;
}

.alert-danger {
  border-left-color: #dc3545;
}

.alert-warning {
  border-left-color: #ffc107;
}

.alert-info {
  border-left-color: #17a2b8;
}
</style>
