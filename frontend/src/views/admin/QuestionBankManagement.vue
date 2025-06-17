<template>
  <div class="question-bank-management">
    <div class="page-header">
      <h1>🏦 Question Bank Management</h1>
      <p>Manage AI-generated and manually created questions for reuse across quizzes</p>
    </div>

    <!-- Statistics Dashboard -->
    <div class="stats-section">
      <h2>📊 Question Bank Statistics</h2>
      <div class="stats-grid" v-if="stats">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_questions }}</div>
          <div class="stat-label">Total Questions</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.verified_questions }}</div>
          <div class="stat-label">Verified Questions</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.verification_rate }}%</div>
          <div class="stat-label">Verification Rate</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.unverified_questions }}</div>
          <div class="stat-label">Unverified Questions</div>
        </div>
      </div>
      
      <div class="difficulty-breakdown" v-if="stats && stats.difficulty_breakdown.length > 0">
        <h3>Questions by Difficulty</h3>
        <div class="difficulty-stats">
          <div v-for="diff in stats.difficulty_breakdown" :key="diff.difficulty" class="difficulty-stat">
            <span class="difficulty-label">{{ diff.difficulty }}</span>
            <span class="difficulty-count">{{ diff.count }}</span>
          </div>
        </div>
      </div>

      <div class="topic-breakdown" v-if="stats && stats.top_topics.length > 0">
        <h3>Top Topics</h3>
        <div class="topic-stats">
          <div v-for="topic in stats.top_topics" :key="topic.topic" class="topic-stat">
            <span class="topic-label">{{ topic.topic }}</span>
            <span class="topic-count">{{ topic.count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="search-section">
      <h2>🔍 Search & Filter Questions</h2>
      <div class="search-controls">
        <div class="search-row">
          <FormField
            v-model="searchFilters.topic"
            label="Topic"
            placeholder="Search by topic..."
            @input="debounceSearch"
          />
          
          <FormField
            v-model="searchFilters.difficulty"
            label="Difficulty"
            type="select"
            :options="difficultyOptions"
            @change="searchQuestions"
          />
          
          <FormField
            v-model="searchFilters.verificationStatus"
            label="Verification Status"
            type="select"
            :options="verificationOptions"
            @change="searchQuestions"
          />
          
          <FormField
            v-model="searchFilters.source"
            label="Source"
            type="select"
            :options="sourceOptions"
            @change="searchQuestions"
          />
        </div>
        
        <div class="search-row">
          <FormField
            v-model="searchFilters.tags"
            label="Tags"
            placeholder="Enter tags separated by commas..."
            @input="debounceSearch"
          />
          
          <FormField
            v-model="searchFilters.limit"
            label="Results per page"
            type="number"
            min="10"
            max="100"
            @change="searchQuestions"
          />
          
          <button @click="clearFilters" class="btn btn-secondary">
            Clear Filters
          </button>
          
          <button @click="exportQuestions" class="btn btn-primary">
            📤 Export Questions
          </button>
        </div>
      </div>
    </div>

    <!-- Question Bank Actions -->
    <div class="actions-section">
      <div class="action-buttons">
        <button @click="showCreateModal = true" class="btn btn-primary">
          ➕ Add Question Manually
        </button>
        <button @click="showImportModal = true" class="btn btn-secondary">
          📥 Import Questions
        </button>
        <button @click="showAnalyticsModal = true" class="btn btn-info">
          📈 Advanced Analytics
        </button>
        <button @click="bulkVerifyQuestions" class="btn btn-success" :disabled="selectedQuestions.length === 0">
          ✅ Bulk Verify ({{ selectedQuestions.length }})
        </button>
        <button @click="bulkDeleteQuestions" class="btn btn-danger" :disabled="selectedQuestions.length === 0">
          🗑️ Bulk Delete ({{ selectedQuestions.length }})
        </button>
      </div>
    </div>

    <!-- Questions List -->
    <div class="questions-section">
      <div class="section-header">
        <h2>📝 Questions ({{ totalQuestions }} total)</h2>
        <div class="list-controls">
          <label class="select-all">
            <input 
              type="checkbox" 
              :checked="allQuestionsSelected"
              @change="toggleSelectAll"
            />
            Select All
          </label>
        </div>
      </div>

      <div v-if="loading" class="loading">Loading questions...</div>
      
      <div v-else-if="questions.length === 0" class="no-questions">
        <p>No questions found. Try adjusting your search criteria.</p>
      </div>
      
      <div v-else class="questions-list">
        <div 
          v-for="question in questions" 
          :key="question.id" 
          class="question-item"
          :class="{ 'selected': selectedQuestions.includes(question.id) }"
        >
          <div class="question-header">
            <label class="question-select">
              <input 
                type="checkbox" 
                :value="question.id"
                v-model="selectedQuestions"
              />
            </label>
            
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
            
            <div class="question-actions">
              <button @click="viewQuestion(question)" class="btn btn-sm btn-info">
                👁️ View
              </button>
              <button @click="editQuestion(question)" class="btn btn-sm btn-warning">
                ✏️ Edit
              </button>
              <button 
                v-if="!question.is_verified"
                @click="verifyQuestion(question)" 
                class="btn btn-sm btn-success"
              >
                ✅ Verify
              </button>
              <button @click="deleteQuestion(question)" class="btn btn-sm btn-danger">
                🗑️ Delete
              </button>
            </div>
          </div>
          
          <div class="question-content">
            <div class="question-text">
              {{ question.question_text }}
            </div>
            
            <div class="question-options">
              <div class="option" v-for="(option, key) in getQuestionOptions(question)" :key="key">
                <span class="option-label" :class="{ 'correct': key === question.correct_option }">
                  {{ key }})
                </span>
                <span class="option-text">{{ option }}</span>
              </div>
            </div>
            
            <div class="question-details">
              <div class="detail-row">
                <span><strong>Usage Count:</strong> {{ question.usage_count }}</span>
                <span><strong>Created:</strong> {{ formatDate(question.created_at) }}</span>
                <span v-if="question.last_used"><strong>Last Used:</strong> {{ formatDate(question.last_used) }}</span>
                <span v-if="question.verification_confidence">
                  <strong>Confidence:</strong> {{ (question.verification_confidence * 100).toFixed(1) }}%
                </span>
              </div>
              
              <div v-if="question.tags && question.tags.length > 0" class="tags">
                <span class="tag" v-for="tag in question.tags" :key="tag">{{ tag }}</span>
              </div>
              
              <div v-if="question.verification_notes" class="verification-notes">
                <strong>Verification Notes:</strong> {{ question.verification_notes }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalQuestions > searchFilters.limit" class="pagination">
        <button 
          @click="previousPage" 
          :disabled="currentPage === 1"
          class="btn btn-secondary"
        >
          ← Previous
        </button>
        
        <span class="page-info">
          Page {{ currentPage }} of {{ totalPages }} 
          ({{ questions.length }} of {{ totalQuestions }} questions)
        </span>
        
        <button 
          @click="nextPage" 
          :disabled="currentPage === totalPages"
          class="btn btn-secondary"
        >
          Next →
        </button>
      </div>
    </div>

    <!-- Modals -->
    <QuestionBankModal
      v-if="showCreateModal"
      :question="null"
      @close="showCreateModal = false"
      @save="handleQuestionSaved"
    />
    
    <QuestionBankModal
      v-if="showEditModal"
      :question="selectedQuestion"
      @close="showEditModal = false"
      @save="handleQuestionSaved"
    />
    
    <QuestionBankViewModal
      v-if="showViewModal"
      :question="selectedQuestion"
      @close="showViewModal = false"
      @edit="editQuestion"
      @verify="verifyQuestion"
      @delete="deleteQuestion"
    />
    
    <QuestionBankImportModal
      v-if="showImportModal"
      @close="showImportModal = false"
      @imported="handleQuestionsImported"
    />
    
    <QuestionBankAnalyticsModal
      v-if="showAnalyticsModal"
      @close="showAnalyticsModal = false"
    />
    
    <QuestionBankVerifyModal
      v-if="showVerifyModal"
      :question="selectedQuestion"
      @close="showVerifyModal = false"
      @verified="handleQuestionVerified"
    />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import adminService from '@/services/adminService'
import aiService from '@/services/aiService'
import apiClient from '@/services/apiClient'
import FormField from '@/components/ui/FormField.vue'
import QuestionBankModal from '@/components/modals/QuestionBankModal.vue'
import QuestionBankViewModal from '@/components/modals/QuestionBankViewModal.vue'
import QuestionBankImportModal from '@/components/modals/QuestionBankImportModal.vue'
import QuestionBankAnalyticsModal from '@/components/modals/QuestionBankAnalyticsModal.vue'
import QuestionBankVerifyModal from '@/components/modals/QuestionBankVerifyModal.vue'

export default {
  name: 'QuestionBankManagement',
  components: {
    FormField,
    QuestionBankModal,
    QuestionBankViewModal,
    QuestionBankImportModal,
    QuestionBankAnalyticsModal,
    QuestionBankVerifyModal
  },
  setup() {
    const stats = ref(null)
    const questions = ref([])
    const selectedQuestions = ref([])
    const selectedQuestion = ref(null)
    const loading = ref(false)
    const totalQuestions = ref(0)
    const currentPage = ref(1)
    
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showViewModal = ref(false)
    const showImportModal = ref(false)
    const showAnalyticsModal = ref(false)
    const showVerifyModal = ref(false)
    
    const searchFilters = reactive({
      topic: '',
      difficulty: '',
      verificationStatus: '',
      source: '',
      tags: '',
      limit: 20,
      offset: 0
    })
    
    const difficultyOptions = [
      { value: '', label: 'All Difficulties' },
      { value: 'easy', label: 'Easy' },
      { value: 'medium', label: 'Medium' },
      { value: 'hard', label: 'Hard' }
    ]
    
    const verificationOptions = [
      { value: '', label: 'All Questions' },
      { value: 'verified', label: 'Verified Only' },
      { value: 'unverified', label: 'Unverified Only' }
    ]
    
    const sourceOptions = [
      { value: '', label: 'All Sources' },
      { value: 'ai_generated', label: 'AI Generated' },
      { value: 'manual', label: 'Manual' },
      { value: 'imported', label: 'Imported' }
    ]
    
    const totalPages = computed(() => 
      Math.ceil(totalQuestions.value / searchFilters.limit)
    )
    
    const allQuestionsSelected = computed(() => 
      questions.value.length > 0 && selectedQuestions.value.length === questions.value.length
    )
    
    let searchTimeout = null
    
    const debounceSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(searchQuestions, 500)
    }
    
    const loadStats = async () => {
      try {
        const response = await apiClient.get('/admin/question-bank/stats')
        stats.value = response.data
      } catch (error) {
        console.error('Failed to load question bank stats:', error)
      }
    }
    
    const searchQuestions = async () => {
      loading.value = true
      try {
        const params = new URLSearchParams()
        
        if (searchFilters.topic) params.append('topic', searchFilters.topic)
        if (searchFilters.difficulty) params.append('difficulty', searchFilters.difficulty)
        if (searchFilters.verificationStatus === 'verified') params.append('verified_only', 'true')
        if (searchFilters.verificationStatus === 'unverified') params.append('verified_only', 'false')
        if (searchFilters.source) params.append('source', searchFilters.source)
        if (searchFilters.tags) {
          const tags = searchFilters.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
          tags.forEach(tag => params.append('tags', tag))
        }
        params.append('limit', searchFilters.limit)
        params.append('offset', searchFilters.offset)
        
        const response = await apiClient.get(`/admin/question-bank/search?${params}`)
        questions.value = response.data.questions
        totalQuestions.value = response.data.count
        selectedQuestions.value = []
      } catch (error) {
        console.error('Failed to search questions:', error)
        questions.value = []
      } finally {
        loading.value = false
      }
    }
    
    const clearFilters = () => {
      Object.assign(searchFilters, {
        topic: '',
        difficulty: '',
        verificationStatus: '',
        source: '',
        tags: '',
        limit: 20,
        offset: 0
      })
      currentPage.value = 1
      searchQuestions()
    }
    
    const toggleSelectAll = () => {
      if (allQuestionsSelected.value) {
        selectedQuestions.value = []
      } else {
        selectedQuestions.value = questions.value.map(q => q.id)
      }
    }
    
    const viewQuestion = (question) => {
      selectedQuestion.value = question
      showViewModal.value = true
    }
    
    const editQuestion = (question) => {
      selectedQuestion.value = question
      showEditModal.value = true
    }
    
    const verifyQuestion = (question) => {
      selectedQuestion.value = question
      showVerifyModal.value = true
    }
    
    const deleteQuestion = async (question) => {
      if (!confirm(`Are you sure you want to delete this question about "${question.topic}"?`)) {
        return
      }
      
      try {
        await apiClient.delete(`/admin/question-bank/questions/${question.id}`)
        await searchQuestions()
        await loadStats()
      } catch (error) {
        console.error('Failed to delete question:', error)
        alert('Failed to delete question. Please try again.')
      }
    }
    
    const bulkVerifyQuestions = async () => {
      if (!confirm(`Are you sure you want to verify ${selectedQuestions.value.length} questions?`)) {
        return
      }
      
      try {
        for (const questionId of selectedQuestions.value) {
          await apiClient.post(`/admin/question-bank/questions/${questionId}/verify`, {
            verification_method: 'manual',
            confidence: 1.0,
            notes: 'Bulk verification by admin'
          })
        }
        
        selectedQuestions.value = []
        await searchQuestions()
        await loadStats()
      } catch (error) {
        console.error('Failed to bulk verify questions:', error)
        alert('Failed to verify some questions. Please try again.')
      }
    }
    
    const bulkDeleteQuestions = async () => {
      if (!confirm(`Are you sure you want to delete ${selectedQuestions.value.length} questions? This action cannot be undone.`)) {
        return
      }
      
      try {
        for (const questionId of selectedQuestions.value) {
          await apiClient.delete(`/admin/question-bank/questions/${questionId}`)
        }
        
        selectedQuestions.value = []
        await searchQuestions()
        await loadStats()
      } catch (error) {
        console.error('Failed to bulk delete questions:', error)
        alert('Failed to delete some questions. Please try again.')
      }
    }
    
    const exportQuestions = async () => {
      try {
        // Create export with current filters
        const params = new URLSearchParams()
        if (searchFilters.topic) params.append('topic', searchFilters.topic)
        if (searchFilters.difficulty) params.append('difficulty', searchFilters.difficulty)
        if (searchFilters.verificationStatus === 'verified') params.append('verified_only', 'true')
        if (searchFilters.verificationStatus === 'unverified') params.append('verified_only', 'false')
        if (searchFilters.source) params.append('source', searchFilters.source)
        params.append('limit', 1000) // Export up to 1000 questions
        
        const response = await apiClient.get(`/admin/question-bank/search?${params}`)
        const exportData = response.data.questions
        
        // Convert to CSV
        const csvContent = convertToCSV(exportData)
        
        // Download file
        const blob = new Blob([csvContent], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `question-bank-export-${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('Failed to export questions:', error)
        alert('Failed to export questions. Please try again.')
      }
    }
    
    const convertToCSV = (questions) => {
      const headers = [
        'ID', 'Question Text', 'Option A', 'Option B', 'Option C', 'Option D',
        'Correct Option', 'Explanation', 'Topic', 'Difficulty', 'Source',
        'Is Verified', 'Usage Count', 'Tags', 'Created At'
      ]
      
      const rows = questions.map(q => [
        q.id,
        `"${q.question_text.replace(/"/g, '""')}"`,
        `"${q.option_a.replace(/"/g, '""')}"`,
        `"${q.option_b.replace(/"/g, '""')}"`,
        `"${q.option_c.replace(/"/g, '""')}"`,
        `"${q.option_d.replace(/"/g, '""')}"`,
        q.correct_option,
        `"${(q.explanation || '').replace(/"/g, '""')}"`,
        q.topic,
        q.difficulty,
        q.source,
        q.is_verified,
        q.usage_count,
        `"${(q.tags || []).join(', ')}"`,
        q.created_at
      ])
      
      return [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    }
    
    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        searchFilters.offset = (currentPage.value - 1) * searchFilters.limit
        searchQuestions()
      }
    }
    
    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
        searchFilters.offset = (currentPage.value - 1) * searchFilters.limit
        searchQuestions()
      }
    }
    
    const handleQuestionSaved = () => {
      searchQuestions()
      loadStats()
    }
    
    const handleQuestionsImported = () => {
      searchQuestions()
      loadStats()
    }
    
    const handleQuestionVerified = () => {
      searchQuestions()
      loadStats()
    }
    
    const getQuestionOptions = (question) => {
      return {
        A: question.option_a,
        B: question.option_b,
        C: question.option_c,
        D: question.option_d
      }
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    onMounted(() => {
      loadStats()
      searchQuestions()
    })
    
    return {
      stats,
      questions,
      selectedQuestions,
      selectedQuestion,
      loading,
      totalQuestions,
      currentPage,
      totalPages,
      allQuestionsSelected,
      searchFilters,
      difficultyOptions,
      verificationOptions,
      sourceOptions,
      showCreateModal,
      showEditModal,
      showViewModal,
      showImportModal,
      showAnalyticsModal,
      showVerifyModal,
      debounceSearch,
      searchQuestions,
      clearFilters,
      toggleSelectAll,
      viewQuestion,
      editQuestion,
      verifyQuestion,
      deleteQuestion,
      bulkVerifyQuestions,
      bulkDeleteQuestions,
      exportQuestions,
      previousPage,
      nextPage,
      handleQuestionSaved,
      handleQuestionsImported,
      handleQuestionVerified,
      getQuestionOptions,
      formatDate
    }
  }
}
</script>

<style scoped>
.question-bank-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.stats-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 2em;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 5px;
}

.stat-label {
  color: #6c757d;
  font-size: 0.9em;
}

.difficulty-breakdown, .topic-breakdown {
  margin-top: 20px;
}

.difficulty-stats, .topic-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.difficulty-stat, .topic-stat {
  background: #e9ecef;
  padding: 8px 12px;
  border-radius: 20px;
  display: flex;
  gap: 8px;
}

.difficulty-count, .topic-count {
  background: #007bff;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.8em;
}

.search-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.search-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.actions-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.questions-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.question-item {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 15px;
  transition: all 0.2s ease;
}

.question-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.question-item.selected {
  border-color: #007bff;
  background-color: #f8f9ff;
}

.question-header {
  background: #f8f9fa;
  padding: 15px;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  gap: 15px;
}

.question-meta {
  flex: 1;
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

.question-actions {
  display: flex;
  gap: 5px;
}

.question-content {
  padding: 15px;
}

.question-text {
  font-size: 1.1em;
  font-weight: 500;
  margin-bottom: 15px;
  line-height: 1.5;
}

.question-options {
  margin-bottom: 15px;
}

.option {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.option-label {
  font-weight: bold;
  min-width: 25px;
}

.option-label.correct {
  color: #28a745;
}

.option-text {
  flex: 1;
}

.question-details {
  border-top: 1px solid #dee2e6;
  padding-top: 15px;
}

.detail-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 10px;
  font-size: 0.9em;
  color: #6c757d;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 10px;
}

.tag {
  background: #e9ecef;
  color: #495057;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.verification-notes {
  font-size: 0.9em;
  color: #495057;
  font-style: italic;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #dee2e6;
}

.page-info {
  color: #6c757d;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.no-questions {
  text-align: center;
  padding: 40px;
  color: #6c757d;
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
  padding: 4px 8px;
  font-size: 0.8em;
}

.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-success { background: #28a745; color: white; }
.btn-warning { background: #ffc107; color: #212529; }
.btn-danger { background: #dc3545; color: white; }
.btn-info { background: #17a2b8; color: white; }

.btn:hover:not(:disabled) {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
