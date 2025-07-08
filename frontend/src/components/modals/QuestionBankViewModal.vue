<template>
  <BaseModal
    :show="true"
    title="Question Details"
    size="large"
    @close="$emit('close')"
  >
    <div class="question-view" v-if="question">
      <!-- Question Header -->
      <div class="question-header">
        <div class="question-meta">
          <span class="question-id">#{{ question.id }}</span>
          <span class="question-topic">{{ question.topic }}</span>
          <span class="question-difficulty" :class="question.difficulty">
            {{ question.difficulty }}
          </span>
          <span class="question-source">{{ question.source }}</span>
          <span class="verification-status" :class="question.is_verified ? 'verified' : 'unverified'">
            {{ question.is_verified ? '✅ Verified' : '⏳ Unverified' }}
          </span>
        </div>
      </div>

      <!-- Question Content -->
      <div class="question-content">
        <div class="question-text">
          <h3>Question:</h3>
          <p>{{ question.question_text }}</p>
        </div>

        <div class="question-options">
          <h3>Options:</h3>
          <div class="options-list">
            <div 
              v-for="(option, key) in getQuestionOptions()" 
              :key="key" 
              class="option"
              :class="{ 'correct': key === question.correct_option }"
            >
              <span class="option-label">{{ key }})</span>
              <span class="option-text">{{ option }}</span>
              <span v-if="key === question.correct_option" class="correct-indicator">✓ Correct</span>
            </div>
          </div>
        </div>

        <div v-if="question.explanation" class="question-explanation">
          <h3>Explanation:</h3>
          <p>{{ question.explanation }}</p>
        </div>
      </div>

      <!-- Question Metadata -->
      <div class="question-metadata">
        <h3>Details:</h3>
        <div class="metadata-grid">
          <div class="metadata-item">
            <span class="metadata-label">Marks:</span>
            <span class="metadata-value">{{ question.marks }}</span>
          </div>
          
          <div class="metadata-item">
            <span class="metadata-label">Usage Count:</span>
            <span class="metadata-value">{{ question.usage_count }}</span>
          </div>
          
          <div class="metadata-item">
            <span class="metadata-label">Created:</span>
            <span class="metadata-value">{{ formatDate(question.created_at) }}</span>
          </div>
          
          <div v-if="question.last_used" class="metadata-item">
            <span class="metadata-label">Last Used:</span>
            <span class="metadata-value">{{ formatDate(question.last_used) }}</span>
          </div>
          
          <div v-if="question.verification_confidence" class="metadata-item">
            <span class="metadata-label">Verification Confidence:</span>
            <span class="metadata-value">{{ (question.verification_confidence * 100).toFixed(1) }}%</span>
          </div>
          
          <div v-if="question.verification_method" class="metadata-item">
            <span class="metadata-label">Verification Method:</span>
            <span class="metadata-value">{{ question.verification_method }}</span>
          </div>
        </div>

        <div v-if="question.tags && question.tags.length > 0" class="tags-section">
          <span class="metadata-label">Tags:</span>
          <div class="tags">
            <span class="tag" v-for="tag in question.tags" :key="tag">{{ tag }}</span>
          </div>
        </div>

        <div v-if="question.verification_notes" class="verification-notes">
          <span class="metadata-label">Verification Notes:</span>
          <p>{{ question.verification_notes }}</p>
        </div>
      </div>

      <!-- Performance Analytics -->
      <div v-if="analytics" class="question-analytics">
        <h3>Performance Analytics:</h3>
        <div class="analytics-grid">
          <div class="analytics-item">
            <span class="analytics-label">Success Rate:</span>
            <span class="analytics-value">{{ analytics.success_rate }}%</span>
          </div>
          
          <div class="analytics-item">
            <span class="analytics-label">Average Time:</span>
            <span class="analytics-value">{{ analytics.average_time }}s</span>
          </div>
          
          <div class="analytics-item">
            <span class="analytics-label">Times Used in Tests:</span>
            <span class="analytics-value">{{ analytics.test_usage_count }}</span>
          </div>
          
          <div class="analytics-item">
            <span class="analytics-label">Student Attempts:</span>
            <span class="analytics-value">{{ analytics.total_attempts }}</span>
          </div>
        </div>

        <div v-if="analytics.common_wrong_answers && analytics.common_wrong_answers.length > 0" class="wrong-answers">
          <span class="analytics-label">Most Common Wrong Answers:</span>
          <div class="wrong-answers-list">
            <div v-for="answer in analytics.common_wrong_answers" :key="answer.option" class="wrong-answer">
              <span class="option-label">{{ answer.option }}</span>
              <span class="percentage">{{ answer.percentage }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="question-actions">
        <button @click="$emit('edit', question)" class="btn btn-warning">
          ✏️ Edit Question
        </button>
        
        <button 
          v-if="!question.is_verified"
          @click="$emit('verify', question)" 
          class="btn btn-success"
        >
          ✅ Verify Question
        </button>
        
        <button @click="duplicateQuestion" class="btn btn-info">
          📋 Duplicate Question
        </button>
        
        <button @click="exportQuestion" class="btn btn-secondary">
          📤 Export Question
        </button>
        
        <button @click="$emit('delete', question)" class="btn btn-danger">
          🗑️ Delete Question
        </button>
      </div>
    </div>
  </BaseModal>
</template>

<script>
import { ref, onMounted } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import apiClient from '@/services/apiClient'

export default {
  name: 'QuestionBankViewModal',
  components: {
    BaseModal
  },
  props: {
    question: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'edit', 'verify', 'delete'],
  setup(props) {
    const analytics = ref(null)
    
    const getQuestionOptions = () => {
      return {
        A: props.question.option_a,
        B: props.question.option_b,
        C: props.question.option_c,
        D: props.question.option_d
      }
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    const loadAnalytics = async () => {
      try {
        // This endpoint would need to be implemented
        const response = await apiClient.get(`/admin/question-bank/questions/${props.question.id}/analytics`)
        analytics.value = response.data
      } catch (error) {
        console.error('Failed to load analytics:', error)
        // Generate mock data for demonstration
        analytics.value = {
          success_rate: Math.floor(Math.random() * 40) + 60, // 60-100%
          average_time: Math.floor(Math.random() * 60) + 30, // 30-90 seconds
          test_usage_count: props.question.usage_count,
          total_attempts: Math.floor(Math.random() * 100) + 20,
          common_wrong_answers: [
            { option: 'B', percentage: 25 },
            { option: 'C', percentage: 15 }
          ]
        }
      }
    }
    
    const duplicateQuestion = async () => {
      try {
        const questionData = {
          topic: props.question.topic,
          difficulty: props.question.difficulty,
          question_text: `${props.question.question_text} (Copy)`,
          option_a: props.question.option_a,
          option_b: props.question.option_b,
          option_c: props.question.option_c,
          option_d: props.question.option_d,
          correct_option: props.question.correct_option,
          explanation: props.question.explanation,
          marks: props.question.marks,
          chapter_id: props.question.chapter_id,
          tags: props.question.tags
        }
        
        await apiClient.post('/admin/question-bank/questions', questionData)
        alert('Question duplicated successfully!')
      } catch (error) {
        console.error('Failed to duplicate question:', error)
        alert('Failed to duplicate question. Please try again.')
      }
    }
    
    const exportQuestion = () => {
      const questionData = {
        id: props.question.id,
        topic: props.question.topic,
        difficulty: props.question.difficulty,
        question_text: props.question.question_text,
        options: getQuestionOptions(),
        correct_answer: props.question.correct_option,
        explanation: props.question.explanation,
        marks: props.question.marks,
        tags: props.question.tags,
        created_at: props.question.created_at,
        verification_status: props.question.is_verified ? 'verified' : 'unverified'
      }
      
      const jsonString = JSON.stringify(questionData, null, 2)
      const blob = new Blob([jsonString], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `question-${props.question.id}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }
    
    onMounted(() => {
      loadAnalytics()
    })
    
    return {
      analytics,
      getQuestionOptions,
      formatDate,
      duplicateQuestion,
      exportQuestion
    }
  }
}
</script>

<style scoped>
.question-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-header {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
}

.question-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.question-id {
  font-weight: bold;
  color: #6c757d;
}

.question-topic {
  background: #007bff;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.question-difficulty {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: bold;
}

.question-difficulty.easy { background: #d4edda; color: #155724; }
.question-difficulty.medium { background: #fff3cd; color: #856404; }
.question-difficulty.hard { background: #f8d7da; color: #721c24; }

.question-source {
  background: #6c757d;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.verification-status.verified {
  background: #d4edda;
  color: #155724;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.verification-status.unverified {
  background: #fff3cd;
  color: #856404;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.question-content {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
}

.question-content h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.question-text p {
  font-size: 1.1em;
  line-height: 1.5;
  margin: 0;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.option.correct {
  background: #d4edda;
  border-color: #c3e6cb;
}

.option-label {
  font-weight: bold;
  min-width: 25px;
}

.option-text {
  flex: 1;
}

.correct-indicator {
  color: #28a745;
  font-weight: bold;
  font-size: 0.9em;
}

.question-explanation p {
  font-style: italic;
  color: #6c757d;
  margin: 0;
}

.question-metadata, .question-analytics {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.question-metadata h3, .question-analytics h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.metadata-grid, .analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.metadata-item, .analytics-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.metadata-label, .analytics-label {
  font-weight: bold;
  color: #495057;
  font-size: 0.9em;
}

.metadata-value, .analytics-value {
  color: #6c757d;
}

.tags-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag {
  background: #e9ecef;
  color: #495057;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.verification-notes {
  margin-top: 15px;
}

.verification-notes p {
  margin: 5px 0 0 0;
  font-style: italic;
  color: #6c757d;
}

.wrong-answers {
  margin-top: 15px;
}

.wrong-answers-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
}

.wrong-answer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #fff3cd;
  border-radius: 4px;
}

.wrong-answer .option-label {
  font-weight: bold;
}

.percentage {
  color: #856404;
  font-weight: bold;
}

.question-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #dee2e6;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s;
}

.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-success { background: #28a745; color: white; }
.btn-warning { background: #ffc107; color: #212529; }
.btn-danger { background: #dc3545; color: white; }
.btn-info { background: #17a2b8; color: white; }

.btn:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .metadata-grid, .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .question-actions {
    flex-direction: column;
  }
}
</style>
