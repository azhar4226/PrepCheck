<template>
  <div class="practice-results-container">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading your results...</p>
    </div>

    <!-- Error State -->
    <div v-if="error && !loading" class="error-container">
      <div class="error-content">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Error Loading Results</h3>
        <p>{{ error }}</p>
        <button @click="loadResults" class="btn btn-primary">
          <i class="fas fa-redo"></i>
          Try Again
        </button>
      </div>
    </div>

    <!-- Results Content -->
    <div v-if="results && !loading && !error" class="results-content">
      <!-- Results Header -->
      <div class="results-header">
        <div class="score-card">
          <div class="score-circle" :class="getScoreClass(results.attempt?.percentage || 0)">
            <div class="score-value">{{ results.attempt?.percentage || 0 }}%</div>
            <div class="score-label">Score</div>
          </div>
          
          <div class="score-details">
            <h2>{{ results.attempt?.title || 'Practice Test Results' }}</h2>
            <div class="score-meta">
              <span class="subject">{{ results.subject?.name || results.attempt?.subject_name }}</span>
              <span class="separator">•</span>
              <span class="paper-type">{{ results.attempt?.paper_type?.toUpperCase() || 'PAPER' }}</span>
              <span class="separator">•</span>
              <span class="completed-date">{{ formatDate(results.attempt?.completed_at) }}</span>
            </div>
            
            <div class="score-stats">
              <div class="stat">
                <span class="stat-value">{{ results.attempt?.correct_answers || 0 }}</span>
                <span class="stat-label">Correct</span>
              </div>
              <div class="stat">
                <span class="stat-value">{{ (results.attempt?.total_questions || 0) - (results.attempt?.correct_answers || 0) }}</span>
                <span class="stat-label">Incorrect</span>
              </div>
              <div class="stat">
                <span class="stat-value">{{ formatTime(results.attempt?.time_taken) }}</span>
                <span class="stat-label">Time Taken</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Analysis Grid -->
      <div class="analysis-grid">
        <!-- Chapter Performance -->
        <div class="analysis-card">
          <h3>
            <i class="fas fa-chart-bar"></i>
            Chapter-wise Performance
          </h3>
          <div class="chapter-performance">
            <div 
              v-for="performance in results.chapter_performance" 
              :key="performance.name"
              class="chapter-item"
            >
              <div class="chapter-info">
                <span class="chapter-name">{{ performance.name }}</span>
                <span class="chapter-score">
                  {{ performance.correct }}/{{ performance.total }}
                </span>
              </div>
              <div class="chapter-progress">
                <div 
                  class="progress-bar" 
                  :class="getPerformanceClass(performance.percentage)"
                  :style="{ width: performance.percentage + '%' }"
                ></div>
              </div>
              <div class="chapter-percentage" :class="getPerformanceClass(performance.percentage)">
                {{ performance.percentage }}%
              </div>
            </div>
          </div>
        </div>

        <!-- Strengths & Weaknesses -->
        <div class="analysis-card">
          <h3>
            <i class="fas fa-balance-scale"></i>
            Strengths & Areas for Improvement
          </h3>
          
          <div class="strengths-weaknesses">
            <div class="strengths" v-if="results.attempt?.strengths && results.attempt.strengths.length > 0">
              <h4>
                <i class="fas fa-thumbs-up"></i>
                Strengths
              </h4>
              <div class="tags">
                <span v-for="strength in results.attempt.strengths" :key="strength" class="tag strength-tag">
                  {{ strength }}
                </span>
              </div>
            </div>
            
            <div class="weaknesses" v-if="results.attempt?.weaknesses && results.attempt.weaknesses.length > 0">
              <h4>
                <i class="fas fa-exclamation-circle"></i>
                Areas for Improvement
              </h4>
              <div class="tags">
                <span v-for="weakness in results.attempt.weaknesses" :key="weakness" class="tag weakness-tag">
                  {{ weakness }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Question Results -->
      <div class="question-results-section" v-if="results.question_results && results.question_results.length > 0">
        <h3>
          <i class="fas fa-list-alt"></i>
          Detailed Question Analysis
        </h3>
        
        <div class="question-results">
          <div 
            v-for="(result, index) in results.question_results" 
            :key="result.question_id || index"
            class="question-result-item"
            :class="{ 'correct': result.is_correct, 'incorrect': !result.is_correct }"
          >
            <div class="question-header">
              <span class="question-number">Question {{ index + 1 }}</span>
              <span class="result-badge" :class="{ 'correct': result.is_correct, 'incorrect': !result.is_correct }">
                <i :class="result.is_correct ? 'fas fa-check' : 'fas fa-times'"></i>
                {{ result.is_correct ? 'Correct' : 'Incorrect' }}
              </span>
            </div>
            
            <div class="question-content">
              <div class="answer-comparison">
                <div class="user-answer">
                  <label>Your Answer:</label>
                  <span class="answer-value" :class="{ 'correct': result.is_correct, 'incorrect': !result.is_correct }">
                    {{ result.user_answer || 'Not answered' }}
                  </span>
                </div>
                
                <div class="correct-answer">
                  <label>Correct Answer:</label>
                  <span class="answer-value correct">{{ result.correct_answer }}</span>
                </div>
              </div>
              
              <div v-if="result.explanation" class="explanation">
                <h5><i class="fas fa-info-circle"></i> Explanation</h5>
                <p>{{ result.explanation }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button @click="$router.push('/ugc-net/practice-tests')" class="btn btn-secondary">
          <i class="fas fa-arrow-left"></i>
          Back to Practice Tests
        </button>
        
        <button @click="$router.push('/ugc-net/practice-setup')" class="btn btn-primary">
          <i class="fas fa-plus"></i>
          Take Another Practice Test
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import ugcNetService from '@/services/ugcNetService'

export default {
  name: 'PracticeResults',
  data() {
    return {
      results: null,
      detailedResults: [],
      loading: true,
      error: null
    }
  },
  
  async mounted() {
    await this.loadResults()
  },
  
  methods: {
    async loadResults() {
      try {
        this.loading = true
        const attemptId = this.$route.params.attemptId
        
        const response = await ugcNetService.getPracticeResults(attemptId)
        if (response.success) {
          this.results = response.data
          
          // Load detailed results if available
          if (this.results.detailed_results && this.results.detailed_results.questions) {
            this.detailedResults = this.results.detailed_results.questions
          }
        } else {
          this.error = response.error || 'Failed to load results'
        }
      } catch (err) {
        console.error('Error loading results:', err)
        this.error = 'Failed to load results'
      } finally {
        this.loading = false
      }
    },
    
    getScoreClass(percentage) {
      if (percentage >= 80) return 'excellent'
      if (percentage >= 60) return 'good'
      if (percentage >= 40) return 'average'
      return 'poor'
    },
    
    getPerformanceClass(percentage) {
      if (percentage >= 80) return 'excellent'
      if (percentage >= 60) return 'good'
      if (percentage >= 40) return 'average'
      return 'poor'
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    formatTime(seconds) {
      if (!seconds) return 'N/A'
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}m ${remainingSeconds}s`
    }
  }
}
</script>

<style scoped>
.practice-results-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
}

.error-content {
  background: white;
  padding: 40px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
}

.results-header {
  margin-bottom: 30px;
}

.score-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  display: flex;
  align-items: center;
  gap: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  border: 1px solid #e2e8f0;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border: 4px solid;
}

.score-circle.excellent {
  border-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  color: #065f46;
}

.score-circle.good {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  color: #1e40af;
}

.score-circle.average {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
  color: #92400e;
}

.score-circle.poor {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2, #fecaca);
  color: #991b1b;
}

.score-value {
  font-size: 2rem;
  line-height: 1;
}

.score-label {
  font-size: 0.875rem;
  margin-top: 4px;
  opacity: 0.7;
}

.score-details {
  flex: 1;
}

.score-details h2 {
  margin: 0 0 12px 0;
  color: #1f2937;
  font-size: 1.5rem;
}

.score-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  color: #6b7280;
  font-size: 0.875rem;
}

.separator {
  opacity: 0.5;
}

.score-stats {
  display: flex;
  gap: 30px;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 4px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 30px;
}

.analysis-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
}

.analysis-card h3 {
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2937;
  font-size: 1.125rem;
}

.chapter-performance {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chapter-item {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.chapter-info {
  display: flex;
  flex-direction: column;
}

.chapter-name {
  font-weight: 500;
  color: #1f2937;
}

.chapter-score {
  font-size: 0.875rem;
  color: #6b7280;
}

.chapter-progress {
  width: 60px;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-bar.excellent {
  background: #10b981;
}

.progress-bar.good {
  background: #3b82f6;
}

.progress-bar.average {
  background: #f59e0b;
}

.progress-bar.poor {
  background: #ef4444;
}

.chapter-percentage {
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 40px;
  text-align: right;
}

.strengths-weaknesses {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.strengths h4, .weaknesses h4 {
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.strength-tag {
  background: #dcfce7;
  color: #166534;
}

.weakness-tag {
  background: #fef2f2;
  color: #991b1b;
}

.question-results-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 30px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
}

.question-results-section h3 {
  margin: 0 0 24px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2937;
  font-size: 1.125rem;
}

.question-results {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-result-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.question-result-item.correct {
  border-color: #10b981;
}

.question-result-item.incorrect {
  border-color: #ef4444;
}

.question-header {
  padding: 12px 16px;
  background: #f9fafb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
}

.question-result-item.correct .question-header {
  background: #ecfdf5;
}

.question-result-item.incorrect .question-header {
  background: #fef2f2;
}

.question-number {
  font-weight: 500;
  color: #1f2937;
}

.result-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.result-badge.correct {
  background: #dcfce7;
  color: #166534;
}

.result-badge.incorrect {
  background: #fecaca;
  color: #991b1b;
}

.question-content {
  padding: 16px;
}

.answer-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.user-answer, .correct-answer {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-answer label, .correct-answer label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.answer-value {
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: 500;
}

.answer-value.correct {
  background: #dcfce7;
  color: #166534;
}

.answer-value.incorrect {
  background: #fecaca;
  color: #991b1b;
}

.explanation {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 16px;
}

.explanation h5 {
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #0369a1;
  font-size: 0.875rem;
}

.explanation p {
  margin: 0;
  color: #1e40af;
  line-height: 1.5;
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

@media (max-width: 768px) {
  .score-card {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .analysis-grid {
    grid-template-columns: 1fr;
  }
  
  .answer-comparison {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>
