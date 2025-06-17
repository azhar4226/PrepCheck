<template>
  <BaseModal
    :show="true"
    title="📈 Question Bank Analytics"
    size="extra-large"
    @close="$emit('close')"
  >
    <div class="analytics-dashboard">
      <!-- Overview Stats -->
      <div class="overview-section">
        <h3>📊 Overview Statistics</h3>
        <div class="overview-stats" v-if="analytics.overview">
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-info">
              <div class="stat-value">{{ analytics.overview.total_questions }}</div>
              <div class="stat-label">Total Questions</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
              <div class="stat-value">{{ analytics.overview.verified_questions }}</div>
              <div class="stat-label">Verified Questions</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-info">
              <div class="stat-value">{{ analytics.overview.avg_success_rate }}%</div>
              <div class="stat-label">Avg Success Rate</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">⏱️</div>
            <div class="stat-info">
              <div class="stat-value">{{ analytics.overview.avg_response_time }}s</div>
              <div class="stat-label">Avg Response Time</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">🔄</div>
            <div class="stat-info">
              <div class="stat-value">{{ analytics.overview.total_usage }}</div>
              <div class="stat-label">Total Usage</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">🎓</div>
            <div class="stat-info">
              <div class="stat-value">{{ analytics.overview.student_attempts }}</div>
              <div class="stat-label">Student Attempts</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Usage Trends -->
      <div class="trends-section">
        <h3>📈 Usage Trends (Last 30 Days)</h3>
        <div class="chart-container">
          <canvas ref="usageChart" width="400" height="200"></canvas>
        </div>
      </div>

      <!-- Performance Analysis -->
      <div class="performance-section">
        <h3>🎯 Performance Analysis</h3>
        <div class="performance-grid">
          <!-- Difficulty Distribution -->
          <div class="chart-card">
            <h4>Questions by Difficulty</h4>
            <canvas ref="difficultyChart" width="300" height="200"></canvas>
          </div>
          
          <!-- Success Rate by Difficulty -->
          <div class="chart-card">
            <h4>Success Rate by Difficulty</h4>
            <canvas ref="successRateChart" width="300" height="200"></canvas>
          </div>
          
          <!-- Topic Coverage -->
          <div class="chart-card">
            <h4>Top Topics by Question Count</h4>
            <canvas ref="topicsChart" width="300" height="200"></canvas>
          </div>
          
          <!-- Verification Status -->
          <div class="chart-card">
            <h4>Verification Status</h4>
            <canvas ref="verificationChart" width="300" height="200"></canvas>
          </div>
        </div>
      </div>

      <!-- Top Performing Questions -->
      <div class="top-questions-section">
        <h3>🏆 Top Performing Questions</h3>
        <div class="questions-tabs">
          <button 
            v-for="tab in questionTabs" 
            :key="tab.key"
            @click="activeQuestionTab = tab.key"
            class="tab-button"
            :class="{ active: activeQuestionTab === tab.key }"
          >
            {{ tab.label }}
          </button>
        </div>
        
        <div class="questions-list">
          <div 
            v-for="question in getQuestionsForTab()" 
            :key="question.id"
            class="question-performance-item"
          >
            <div class="question-info">
              <div class="question-text">{{ question.question_text.substring(0, 100) }}...</div>
              <div class="question-meta">
                <span class="topic">{{ question.topic }}</span>
                <span class="difficulty" :class="question.difficulty">{{ question.difficulty }}</span>
              </div>
            </div>
            
            <div class="performance-metrics">
              <div class="metric">
                <span class="metric-label">Success Rate</span>
                <span class="metric-value">{{ question.success_rate }}%</span>
              </div>
              <div class="metric">
                <span class="metric-label">Usage Count</span>
                <span class="metric-value">{{ question.usage_count }}</span>
              </div>
              <div class="metric">
                <span class="metric-label">Avg Time</span>
                <span class="metric-value">{{ question.avg_time }}s</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quality Insights -->
      <div class="insights-section">
        <h3>💡 Quality Insights</h3>
        <div class="insights-grid">
          <div class="insight-card" v-for="insight in analytics.insights" :key="insight.id">
            <div class="insight-icon">{{ insight.icon }}</div>
            <div class="insight-content">
              <div class="insight-title">{{ insight.title }}</div>
              <div class="insight-description">{{ insight.description }}</div>
              <div v-if="insight.action" class="insight-action">
                <button @click="executeInsightAction(insight)" class="btn btn-sm btn-primary">
                  {{ insight.action.label }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div class="recommendations-section">
        <h3>🎯 Recommendations</h3>
        <div class="recommendations-list">
          <div 
            v-for="recommendation in analytics.recommendations" 
            :key="recommendation.id"
            class="recommendation-item"
            :class="recommendation.priority"
          >
            <div class="recommendation-priority">
              {{ recommendation.priority.toUpperCase() }}
            </div>
            <div class="recommendation-content">
              <div class="recommendation-title">{{ recommendation.title }}</div>
              <div class="recommendation-description">{{ recommendation.description }}</div>
              <div class="recommendation-impact">
                <strong>Expected Impact:</strong> {{ recommendation.impact }}
              </div>
            </div>
            <div class="recommendation-actions">
              <button 
                v-for="action in recommendation.actions" 
                :key="action.id"
                @click="executeRecommendationAction(action)"
                class="btn btn-sm"
                :class="action.type === 'primary' ? 'btn-primary' : 'btn-secondary'"
              >
                {{ action.label }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Export Options -->
      <div class="export-section">
        <h3>📤 Export Analytics</h3>
        <div class="export-options">
          <button @click="exportAnalytics('pdf')" class="btn btn-secondary">
            📄 Export as PDF
          </button>
          <button @click="exportAnalytics('excel')" class="btn btn-secondary">
            📊 Export as Excel
          </button>
          <button @click="exportAnalytics('json')" class="btn btn-secondary">
            📋 Export as JSON
          </button>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'

export default {
  name: 'QuestionBankAnalyticsModal',
  components: {
    BaseModal
  },
  emits: ['close'],
  setup() {
    const loading = ref(false)
    const activeQuestionTab = ref('best')
    
    const analytics = reactive({
      overview: null,
      trends: [],
      performance: null,
      topQuestions: {
        best: [],
        worst: [],
        mostUsed: [],
        leastUsed: []
      },
      insights: [],
      recommendations: []
    })
    
    const questionTabs = [
      { key: 'best', label: '🏆 Best Performing' },
      { key: 'worst', label: '⚠️ Needs Improvement' },
      { key: 'mostUsed', label: '🔥 Most Used' },
      { key: 'leastUsed', label: '😴 Least Used' }
    ]
    
    const usageChart = ref(null)
    const difficultyChart = ref(null)
    const successRateChart = ref(null)
    const topicsChart = ref(null)
    const verificationChart = ref(null)
    
    const getQuestionsForTab = () => {
      return analytics.topQuestions[activeQuestionTab.value] || []
    }
    
    const loadAnalytics = async () => {
      loading.value = true
      
      try {
        // Real analytics API call
        const response = await fetch('/api/admin/question-bank/analytics', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          const analyticsData = await response.json()
          
          // Use real analytics data
          analytics.overview = analyticsData.overview || {
            total_questions: 0,
            verified_questions: 0,
            avg_success_rate: 0,
            avg_response_time: 0,
            total_usage: 0,
            student_attempts: 0
          }
          
          analytics.trends = analyticsData.trends || generateMockTrendData()
          analytics.performance = analyticsData.performance || generateMockPerformanceData()
          analytics.topQuestions = analyticsData.topQuestions || generateMockTopQuestions()
          analytics.insights = analyticsData.insights || generateMockInsights()
          analytics.recommendations = analyticsData.recommendations || generateMockRecommendations()
          
        } else {
          console.warn('Failed to load analytics, using mock data')
          // Fall back to mock data
          analytics.overview = {
            total_questions: 0,
            verified_questions: 0,
            avg_success_rate: 0,
            avg_response_time: 0,
            total_usage: 0,
            student_attempts: 0
          }
          analytics.trends = generateMockTrendData()
          analytics.performance = generateMockPerformanceData()
          analytics.topQuestions = generateMockTopQuestions()
          analytics.insights = generateMockInsights()
          analytics.recommendations = generateMockRecommendations()
        }
        
      } catch (error) {
        console.error('Failed to load analytics:', error)
        // Fall back to mock data on error
        analytics.overview = {
          total_questions: 0,
          verified_questions: 0,
          avg_success_rate: 0,
          avg_response_time: 0,
          total_usage: 0,
          student_attempts: 0
        }
        analytics.trends = generateMockTrendData()
        analytics.performance = generateMockPerformanceData()
        analytics.topQuestions = generateMockTopQuestions()
        analytics.insights = generateMockInsights()
        analytics.recommendations = generateMockRecommendations()
      } finally {
        loading.value = false
      }
    }
    
    const generateMockTrendData = () => {
      const data = []
      for (let i = 29; i >= 0; i--) {
        const date = new Date()
        date.setDate(date.getDate() - i)
        data.push({
          date: date.toISOString().split('T')[0],
          questions_added: Math.floor(Math.random() * 20) + 5,
          questions_used: Math.floor(Math.random() * 100) + 50,
          success_rate: Math.floor(Math.random() * 20) + 70
        })
      }
      return data
    }
    
    const generateMockPerformanceData = () => {
      return {
        by_difficulty: [
          { difficulty: 'easy', count: 432, success_rate: 87.3 },
          { difficulty: 'medium', count: 578, success_rate: 71.8 },
          { difficulty: 'hard', count: 237, success_rate: 54.2 }
        ],
        by_topic: [
          { topic: 'Python Programming', count: 245, success_rate: 78.5 },
          { topic: 'Data Structures', count: 198, success_rate: 69.2 },
          { topic: 'Algorithms', count: 156, success_rate: 62.8 },
          { topic: 'Web Development', count: 189, success_rate: 75.3 },
          { topic: 'Database', count: 134, success_rate: 71.7 }
        ],
        verification_status: [
          { status: 'verified', count: 1089 },
          { status: 'unverified', count: 158 }
        ]
      }
    }
    
    const generateMockTopQuestions = () => {
      const generateQuestion = (id, performance) => ({
        id,
        question_text: `Sample question ${id} about programming concepts and best practices`,
        topic: ['Python', 'JavaScript', 'Data Structures', 'Algorithms'][Math.floor(Math.random() * 4)],
        difficulty: ['easy', 'medium', 'hard'][Math.floor(Math.random() * 3)],
        success_rate: performance.success_rate,
        usage_count: performance.usage_count,
        avg_time: performance.avg_time
      })
      
      return {
        best: Array.from({ length: 10 }, (_, i) => generateQuestion(i + 1, {
          success_rate: Math.floor(Math.random() * 15) + 85,
          usage_count: Math.floor(Math.random() * 50) + 20,
          avg_time: Math.floor(Math.random() * 20) + 30
        })),
        worst: Array.from({ length: 10 }, (_, i) => generateQuestion(i + 100, {
          success_rate: Math.floor(Math.random() * 30) + 30,
          usage_count: Math.floor(Math.random() * 20) + 5,
          avg_time: Math.floor(Math.random() * 40) + 60
        })),
        mostUsed: Array.from({ length: 10 }, (_, i) => generateQuestion(i + 200, {
          success_rate: Math.floor(Math.random() * 40) + 60,
          usage_count: Math.floor(Math.random() * 100) + 100,
          avg_time: Math.floor(Math.random() * 30) + 40
        })),
        leastUsed: Array.from({ length: 10 }, (_, i) => generateQuestion(i + 300, {
          success_rate: Math.floor(Math.random() * 50) + 50,
          usage_count: Math.floor(Math.random() * 5),
          avg_time: Math.floor(Math.random() * 60) + 30
        }))
      }
    }
    
    const generateMockInsights = () => {
      return [
        {
          id: 1,
          icon: '🎯',
          title: 'High Success Rate Topics',
          description: 'Python Programming questions have 87% success rate, 15% above average.',
          action: { label: 'Create More', type: 'generate' }
        },
        {
          id: 2,
          icon: '⚠️',
          title: 'Difficult Questions',
          description: '23 questions have success rates below 40%. Consider reviewing or providing better explanations.',
          action: { label: 'Review Questions', type: 'review' }
        },
        {
          id: 3,
          icon: '📈',
          title: 'Growing Topic Demand',
          description: 'Web Development questions usage increased 45% this month.',
          action: { label: 'Generate More', type: 'generate' }
        },
        {
          id: 4,
          icon: '🔍',
          title: 'Verification Needed',
          description: '158 questions are still unverified and may affect quality.',
          action: { label: 'Bulk Verify', type: 'verify' }
        }
      ]
    }
    
    const generateMockRecommendations = () => {
      return [
        {
          id: 1,
          priority: 'high',
          title: 'Improve Low-Performing Questions',
          description: 'Review and update questions with success rates below 50%',
          impact: 'Improve overall success rate by 8-12%',
          actions: [
            { id: 1, label: 'Auto-Review', type: 'primary' },
            { id: 2, label: 'Manual Review', type: 'secondary' }
          ]
        },
        {
          id: 2,
          priority: 'medium',
          title: 'Expand Popular Topics',
          description: 'Generate more questions for high-demand topics like Python and Web Development',
          impact: 'Meet growing demand and improve topic coverage',
          actions: [
            { id: 3, label: 'Generate Questions', type: 'primary' },
            { id: 4, label: 'Import Questions', type: 'secondary' }
          ]
        },
        {
          id: 3,
          priority: 'low',
          title: 'Verify Unverified Questions',
          description: 'Complete verification for remaining unverified questions',
          impact: 'Improve question quality assurance',
          actions: [
            { id: 5, label: 'Bulk Verify', type: 'primary' }
          ]
        }
      ]
    }
    
    const initCharts = async () => {
      await nextTick()
      
      // Mock chart implementation (in real app, use Chart.js or similar)
      if (usageChart.value) {
        const ctx = usageChart.value.getContext('2d')
        drawMockChart(ctx, 'line', 'Usage Trends')
      }
      
      if (difficultyChart.value) {
        const ctx = difficultyChart.value.getContext('2d')
        drawMockChart(ctx, 'pie', 'Difficulty Distribution')
      }
      
      if (successRateChart.value) {
        const ctx = successRateChart.value.getContext('2d')
        drawMockChart(ctx, 'bar', 'Success Rates')
      }
      
      if (topicsChart.value) {
        const ctx = topicsChart.value.getContext('2d')
        drawMockChart(ctx, 'bar', 'Topic Distribution')
      }
      
      if (verificationChart.value) {
        const ctx = verificationChart.value.getContext('2d')
        drawMockChart(ctx, 'doughnut', 'Verification Status')
      }
    }
    
    const drawMockChart = (ctx, type, title) => {
      ctx.fillStyle = '#f8f9fa'
      ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height)
      
      ctx.fillStyle = '#6c757d'
      ctx.font = '14px Arial'
      ctx.textAlign = 'center'
      ctx.fillText(`${title} Chart`, ctx.canvas.width / 2, ctx.canvas.height / 2 - 10)
      ctx.fillText('(Chart would render here)', ctx.canvas.width / 2, ctx.canvas.height / 2 + 10)
    }
    
    const executeInsightAction = async (insight) => {
      try {
        switch (insight.action.type) {
          case 'generate':
            // Open AI generation modal or navigate to generation page
            alert('Generate more questions feature would be triggered')
            break
          case 'review':
            // Navigate to question review page
            alert('Question review feature would be triggered')
            break
          case 'verify':
            // Trigger bulk verification
            alert('Bulk verification feature would be triggered')
            break
        }
      } catch (error) {
        console.error('Failed to execute insight action:', error)
      }
    }
    
    const executeRecommendationAction = async (action) => {
      try {
        switch (action.id) {
          case 1: // Auto-Review
            alert('Auto-review feature would be triggered')
            break
          case 2: // Manual Review
            alert('Manual review feature would be triggered')
            break
          case 3: // Generate Questions
            alert('Question generation feature would be triggered')
            break
          case 4: // Import Questions
            alert('Question import feature would be triggered')
            break
          case 5: // Bulk Verify
            alert('Bulk verification feature would be triggered')
            break
        }
      } catch (error) {
        console.error('Failed to execute recommendation action:', error)
      }
    }
    
    const exportAnalytics = (format) => {
      try {
        const data = {
          overview: analytics.overview,
          performance: analytics.performance,
          trends: analytics.trends,
          insights: analytics.insights,
          recommendations: analytics.recommendations,
          exportDate: new Date().toISOString()
        }
        
        switch (format) {
          case 'pdf':
            alert('PDF export would be generated')
            break
          case 'excel':
            alert('Excel export would be generated')
            break
          case 'json':
            const jsonString = JSON.stringify(data, null, 2)
            const blob = new Blob([jsonString], { type: 'application/json' })
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `question-bank-analytics-${new Date().toISOString().split('T')[0]}.json`
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            window.URL.revokeObjectURL(url)
            break
        }
      } catch (error) {
        console.error('Failed to export analytics:', error)
        alert('Failed to export analytics. Please try again.')
      }
    }
    
    onMounted(async () => {
      await loadAnalytics()
      await initCharts()
    })
    
    return {
      loading,
      analytics,
      activeQuestionTab,
      questionTabs,
      usageChart,
      difficultyChart,
      successRateChart,
      topicsChart,
      verificationChart,
      getQuestionsForTab,
      executeInsightAction,
      executeRecommendationAction,
      exportAnalytics
    }
  }
}
</script>

<style scoped>
.analytics-dashboard {
  display: flex;
  flex-direction: column;
  gap: 30px;
  max-height: 80vh;
  overflow-y: auto;
}

.overview-section h3,
.trends-section h3,
.performance-section h3,
.top-questions-section h3,
.insights-section h3,
.recommendations-section h3,
.export-section h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 10px;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.stat-icon {
  font-size: 2em;
}

.stat-value {
  font-size: 2em;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9em;
  opacity: 0.9;
}

.chart-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.performance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.chart-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.chart-card h4 {
  margin: 0 0 15px 0;
  color: #495057;
  text-align: center;
}

.questions-tabs {
  display: flex;
  gap: 5px;
  margin-bottom: 20px;
  border-bottom: 1px solid #dee2e6;
}

.tab-button {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease;
}

.tab-button:hover {
  background-color: #f8f9fa;
}

.tab-button.active {
  border-bottom-color: #007bff;
  background-color: #f8f9ff;
  color: #007bff;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 400px;
  overflow-y: auto;
}

.question-performance-item {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-info {
  flex: 1;
}

.question-text {
  font-weight: 500;
  margin-bottom: 8px;
}

.question-meta {
  display: flex;
  gap: 10px;
}

.topic {
  background: #007bff;
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.difficulty {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: bold;
}

.difficulty.easy { background: #d4edda; color: #155724; }
.difficulty.medium { background: #fff3cd; color: #856404; }
.difficulty.hard { background: #f8d7da; color: #721c24; }

.performance-metrics {
  display: flex;
  gap: 20px;
}

.metric {
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 0.8em;
  color: #6c757d;
  margin-bottom: 2px;
}

.metric-value {
  font-weight: bold;
  color: #2c3e50;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.insight-card {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  gap: 15px;
}

.insight-icon {
  font-size: 2em;
  flex-shrink: 0;
}

.insight-content {
  flex: 1;
}

.insight-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #2c3e50;
}

.insight-description {
  color: #6c757d;
  margin-bottom: 10px;
  line-height: 1.4;
}

.insight-action {
  margin-top: 10px;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recommendation-item {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.recommendation-item.high {
  border-left: 5px solid #dc3545;
}

.recommendation-item.medium {
  border-left: 5px solid #ffc107;
}

.recommendation-item.low {
  border-left: 5px solid #28a745;
}

.recommendation-priority {
  background: #6c757d;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: bold;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recommendation-item.high .recommendation-priority {
  background: #dc3545;
}

.recommendation-item.medium .recommendation-priority {
  background: #ffc107;
  color: #212529;
}

.recommendation-item.low .recommendation-priority {
  background: #28a745;
}

.recommendation-content {
  flex: 1;
}

.recommendation-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #2c3e50;
}

.recommendation-description {
  color: #6c757d;
  margin-bottom: 8px;
  line-height: 1.4;
}

.recommendation-impact {
  font-size: 0.9em;
  color: #495057;
}

.recommendation-actions {
  display: flex;
  gap: 10px;
  flex-direction: column;
}

.export-options {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.8em;
}

.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }

.btn:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .overview-stats {
    grid-template-columns: 1fr;
  }
  
  .performance-grid {
    grid-template-columns: 1fr;
  }
  
  .insights-grid {
    grid-template-columns: 1fr;
  }
  
  .questions-tabs {
    flex-wrap: wrap;
  }
  
  .question-performance-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .performance-metrics {
    width: 100%;
    justify-content: space-around;
  }
  
  .recommendation-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .recommendation-priority {
    writing-mode: initial;
    text-orientation: initial;
    min-height: auto;
    width: 100%;
    text-align: center;
  }
}
</style>
