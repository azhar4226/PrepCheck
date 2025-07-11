<template>
  <div class="user-analytics-page">
    <!-- Performance Overview Cards -->
    <div v-if="!loading && hasData" class="row g-4 mb-4">
      <div class="col-md-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <h5 class="card-title text-primary">Overall Score</h5>
            <h2 class="mb-0">{{ analyticsData.snapshot.overall_average_score.toFixed(1) }}%</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <h5 class="card-title text-success">Accuracy Rate</h5>
            <h2 class="mb-0">{{ analyticsData.snapshot.overall_accuracy.toFixed(1) }}%</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <h5 class="card-title text-info">Tests Taken</h5>
            <h2 class="mb-0">{{ analyticsData.snapshot.total_tests_taken }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <h5 class="card-title text-warning">Time Studied</h5>
            <h2 class="mb-0">{{ formatTime(analyticsData.snapshot.total_time_studied) }}</h2>
          </div>
        </div>
      </div>
    </div>
    <!-- Header & Export -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">My Performance Analytics</h3>
      <button class="btn btn-primary" @click="exportAnalyticsPDF" :disabled="loading">
        <i class="bi bi-download me-1"></i> Export as PDF
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Filters for Performance Over Time: always visible except when loading -->
    <div v-if="!loading" class="row mb-3">
      <div class="col-md-3 mb-2">
        <select v-model="selectedTestType" class="form-select">
          <option value="all">All Tests</option>
          <option value="mock">Mock Tests</option>
          <option value="practice">Practice Tests</option>
        </select>
      </div>
      <div class="col-md-3 mb-2">
        <select v-model="selectedSubject" class="form-select">
          <option value="all">All Subjects</option>
          <option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.name }}</option>
        </select>
      </div>
      <div class="col-md-3 mb-2">
        <select v-model="selectedTimeRange" class="form-select">
          <option value="30">Last 30 days</option>
          <option value="90">Last 3 months</option>
          <option value="all">All time</option>
        </select>
      </div>
      <div class="col-md-3 mb-2">
        <button class="btn btn-outline-primary w-100" @click="refreshAnalytics" :disabled="loading">Apply Filters</button>
      </div>
    </div>

    <!-- No Data Message - Only show when actually no data -->
    <div v-if="!loading && hasNoData" class="text-center py-5">
      <i class="bi bi-bar-chart-line display-1 text-muted"></i>
      <h3 class="mt-3 text-muted">No Analytics Data Available</h3>
      <p class="text-muted">Complete some tests to see your performance analytics here.</p>
    </div>

    <!-- Performance Charts -->
    <div v-if="!loading && hasData" class="row g-4">
      <!-- Performance Over Time -->
      <div class="col-md-8">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Performance Over Time</h5>
            <line-chart
              :chart-data="performanceChartData"
              :options="performanceChartOptions"
            />
          </div>
        </div>
      </div>

      <!-- Accuracy by Difficulty -->
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Accuracy by Difficulty</h5>
            <doughnut-chart
              :chart-data="accuracyChartData"
              :options="accuracyChartOptions"
            />
          </div>
        </div>
      </div>

      <!-- Strengths -->
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title text-success">
              <i class="bi bi-arrow-up-circle me-2"></i>Strengths
            </h5>
            <div class="list-group">
              <div v-for="(strength, index) in analyticsData.strengths" :key="index" class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                  <span>{{ strength.topic }}</span>
                  <span class="badge bg-success">{{ strength.score.toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Weaknesses -->
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title text-danger">
              <i class="bi bi-arrow-down-circle me-2"></i>Areas for Improvement
            </h5>
            <div class="list-group">
              <div v-for="(weakness, index) in analyticsData.weaknesses" :key="index" class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                  <span>{{ weakness.topic }}</span>
                  <span class="badge bg-danger">{{ weakness.score.toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Paper Performance -->
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Paper-wise Performance</h5>
            <div class="row">
              <div class="col-md-6" v-for="(score, paper) in analyticsData.performance_by_paper" :key="paper">
                <div class="mb-3">
                  <label class="form-label">{{ paper }}</label>
                  <div class="progress">
                    <div 
                      class="progress-bar" 
                      role="progressbar" 
                      :style="{ width: score + '%' }"
                      :class="{
                        'bg-danger': score < 40,
                        'bg-warning': score >= 40 && score < 60,
                        'bg-success': score >= 60
                      }"
                    >
                      {{ score.toFixed(1) }}%
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
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { Line as LineChart, Doughnut as DoughnutChart } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement } from 'chart.js'
import analyticsService from '@/services/analyticsService'
import ugcNetService from '@/services/ugcNetService'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement)

export default {
  name: 'UserAnalytics',
  components: {
    LineChart,
    DoughnutChart
  },
  setup() {
    const loading = ref(false)
    const analyticsData = ref(null)
    const selectedTestType = ref('all')
    const selectedSubject = ref('all')
    const selectedTimeRange = ref('30')
    const subjects = ref([])

    const performanceChartData = computed(() => {
      if (!analyticsData.value?.performance_over_time) return null
      
      return {
        labels: analyticsData.value.performance_over_time.map(p => p.date),
        datasets: [{
          label: 'Score',
          data: analyticsData.value.performance_over_time.map(p => p.score),
          borderColor: '#0d6efd',
          tension: 0.1
        }]
      }
    })

    const accuracyChartData = computed(() => {
      if (!analyticsData.value?.accuracy_by_difficulty) return null

      const data = analyticsData.value.accuracy_by_difficulty
      return {
        labels: Object.keys(data),
        datasets: [{
          data: Object.values(data),
          backgroundColor: ['#28a745', '#ffc107', '#dc3545']
        }]
      }
    })

    const performanceChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: 'Score (%)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Date'
          }
        }
      }
    }

    const accuracyChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }

    const hasData = computed(() => {
      return analyticsData.value && analyticsData.value.snapshot?.total_tests_taken > 0
    })

    const hasNoData = computed(() => {
      return !loading.value && (!analyticsData.value || analyticsData.value.snapshot?.total_tests_taken === 0)
    })

    const fetchData = async () => {
      loading.value = true
      try {
        const params = {
          days: selectedTimeRange.value === 'all' ? 'all' : parseInt(selectedTimeRange.value),
          subject_id: selectedSubject.value === 'all' ? null : selectedSubject.value,
          test_type: selectedTestType.value
        }
        const response = await analyticsService.getUserAnalytics(params)
        analyticsData.value = response
      } catch (error) {
        console.error('Error fetching analytics:', error)
        analyticsData.value = null
      } finally {
        loading.value = false
      }
    }

    const loadSubjects = async () => {
      try {
        const result = await ugcNetService.getSubjects()
        if (result.success && result.data) {
          subjects.value = result.data.subjects || []
        } else {
          console.error('Failed to load subjects:', result.error)
          subjects.value = []
        }
      } catch (error) {
        console.error('Error loading subjects:', error)
        subjects.value = []
      }
    }

    const refreshAnalytics = async () => {
      await fetchData()
    }

    const exportAnalyticsPDF = async () => {
      try {
        const data = await analyticsService.exportAnalytics('pdf')
        const url = window.URL.createObjectURL(new Blob([data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'analytics.pdf')
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        console.error('Error exporting analytics:', error)
      }
    }

    const formatTime = (seconds) => {
      if (!seconds) return '0h 0m'
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      return `${hours}h ${minutes}m`
    }

    onMounted(async () => {
      await loadSubjects()
      await fetchData()
    })

    return {
      loading,
      analyticsData,
      selectedTestType,
      selectedSubject,
      selectedTimeRange,
      subjects,
      hasData,
      hasNoData,
      refreshAnalytics,
      exportAnalyticsPDF,
      formatTime,
      performanceChartData,
      accuracyChartData,
      performanceChartOptions,
      accuracyChartOptions
    }
  }
}
</script>

<style scoped>
.user-analytics-page {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { 
    opacity: 0; 
    transform: translateY(10px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transition: box-shadow 0.15s ease-in-out;
}

.card:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.progress {
  height: 25px;
}

.progress-bar {
  line-height: 25px;
}

.list-group-item {
  border-left: none;
  border-right: none;
}

.list-group-item:first-child {
  border-top: none;
}

.list-group-item:last-child {
  border-bottom: none;
}
</style>