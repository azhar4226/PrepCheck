<template>
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-eye me-2"></i>
            Question Details
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div v-if="question">
            <!-- Question Info -->
            <div class="card mb-3">
              <div class="card-header">
                <h6 class="mb-0">Question Information</h6>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6">
                    <strong>Quiz:</strong> {{ question.quiz_title }}<br>
                    <strong>Subject:</strong> {{ question.subject_name }}<br>
                    <strong>Chapter:</strong> {{ question.chapter_name }}<br>
                    <strong>Type:</strong> 
                    <span class="badge bg-info">{{ formatQuestionType(question.question_type) }}</span><br>
                  </div>
                  <div class="col-md-6">
                    <strong>Difficulty:</strong> 
                    <span class="badge" :class="getDifficultyClass(question.difficulty)">
                      {{ question.difficulty || 'Medium' }}
                    </span><br>
                    <strong>Points:</strong> {{ question.points || 1 }}<br>
                    <strong>Created:</strong> {{ formatDate(question.created_at) }}<br>
                    <strong>Updated:</strong> {{ formatDate(question.updated_at) }}<br>
                  </div>
                </div>
              </div>
            </div>

            <!-- Question Content -->
            <div class="card mb-3">
              <div class="card-header">
                <h6 class="mb-0">Question</h6>
              </div>
              <div class="card-body">
                <p class="mb-0">{{ question.question_text }}</p>
              </div>
            </div>

            <!-- Options -->
            <div class="card mb-3">
              <div class="card-header">
                <h6 class="mb-0">Answer Options</h6>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6 mb-2">
                    <div class="option-item" :class="{ 'correct-answer': question.correct_option === 'A' }">
                      <strong>A:</strong> {{ question.option_a }}
                      <i v-if="question.correct_option === 'A'" class="bi bi-check-circle-fill text-success ms-2"></i>
                    </div>
                  </div>
                  <div class="col-md-6 mb-2">
                    <div class="option-item" :class="{ 'correct-answer': question.correct_option === 'B' }">
                      <strong>B:</strong> {{ question.option_b }}
                      <i v-if="question.correct_option === 'B'" class="bi bi-check-circle-fill text-success ms-2"></i>
                    </div>
                  </div>
                  <div v-if="question.option_c" class="col-md-6 mb-2">
                    <div class="option-item" :class="{ 'correct-answer': question.correct_option === 'C' }">
                      <strong>C:</strong> {{ question.option_c }}
                      <i v-if="question.correct_option === 'C'" class="bi bi-check-circle-fill text-success ms-2"></i>
                    </div>
                  </div>
                  <div v-if="question.option_d" class="col-md-6 mb-2">
                    <div class="option-item" :class="{ 'correct-answer': question.correct_option === 'D' }">
                      <strong>D:</strong> {{ question.option_d }}
                      <i v-if="question.correct_option === 'D'" class="bi bi-check-circle-fill text-success ms-2"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Explanation -->
            <div v-if="question.explanation" class="card mb-3">
              <div class="card-header">
                <h6 class="mb-0">Explanation</h6>
              </div>
              <div class="card-body">
                <p class="mb-0">{{ question.explanation }}</p>
              </div>
            </div>

            <!-- AI Verification Status -->
            <div v-if="question.is_ai_generated" class="card mb-3">
              <div class="card-header">
                <h6 class="mb-0">AI Verification Status</h6>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6">
                    <strong>AI Generated:</strong> 
                    <span class="badge bg-info">Yes</span><br>
                    <strong>Verified:</strong> 
                    <span class="badge" :class="question.is_verified ? 'bg-success' : 'bg-warning'">
                      {{ question.is_verified ? 'Verified' : 'Pending' }}
                    </span><br>
                  </div>
                  <div class="col-md-6">
                    <div v-if="question.verification_confidence">
                      <strong>Confidence:</strong> 
                      <span class="badge" :class="getConfidenceClass(question.verification_confidence)">
                        {{ Math.round(question.verification_confidence * 100) }}%
                      </span><br>
                    </div>
                    <div v-if="question.verified_at">
                      <strong>Verified At:</strong> {{ formatDate(question.verified_at) }}<br>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Statistics -->
            <div class="card">
              <div class="card-header">
                <h6 class="mb-0">Usage Statistics</h6>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-4 text-center">
                    <div class="stat-item">
                      <h4 class="text-primary">{{ question.times_used || 0 }}</h4>
                      <small class="text-muted">Times Used</small>
                    </div>
                  </div>
                  <div class="col-md-4 text-center">
                    <div class="stat-item">
                      <h4 class="text-success">{{ question.correct_rate || 0 }}%</h4>
                      <small class="text-muted">Correct Rate</small>
                    </div>
                  </div>
                  <div class="col-md-4 text-center">
                    <div class="stat-item">
                      <h4 class="text-info">{{ question.difficulty_rating || 'N/A' }}</h4>
                      <small class="text-muted">Avg. Difficulty</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">
            Close
          </button>
          <button type="button" class="btn btn-primary" @click="$emit('edit', question)">
            <i class="bi bi-pencil me-1"></i>
            Edit Question
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuestionViewModal',
  props: {
    question: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'edit'],
  setup() {
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatQuestionType = (type) => {
      switch (type) {
        case 'multiple_choice':
          return 'Multiple Choice'
        case 'true_false':
          return 'True/False'
        default:
          return 'Multiple Choice'
      }
    }

    const getDifficultyClass = (difficulty) => {
      switch (difficulty?.toLowerCase()) {
        case 'easy':
          return 'bg-success'
        case 'medium':
          return 'bg-warning'
        case 'hard':
          return 'bg-danger'
        default:
          return 'bg-secondary'
      }
    }

    const getConfidenceClass = (confidence) => {
      if (confidence >= 0.8) return 'bg-success'
      if (confidence >= 0.6) return 'bg-warning'
      return 'bg-danger'
    }

    return {
      formatDate,
      formatQuestionType,
      getDifficultyClass,
      getConfidenceClass
    }
  }
}
</script>

<style scoped>
.modal {
  z-index: 1050;
}

.option-item {
  padding: 0.5rem;
  border: 1px solid #e9ecef;
  border-radius: 0.375rem;
  background-color: #f8f9fa;
}

.option-item.correct-answer {
  background-color: #d1ecf1;
  border-color: #b6d7ff;
}

.card {
  border: 1px solid #e9ecef;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.stat-item {
  padding: 0.5rem;
}

.stat-item h4 {
  margin-bottom: 0.25rem;
}

.badge {
  font-size: 0.75em;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  opacity: 0.5;
}

.btn-close:hover {
  opacity: 0.75;
}
</style>
