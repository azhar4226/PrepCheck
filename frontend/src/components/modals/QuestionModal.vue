<template>
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-question-circle me-2"></i>
            {{ editingQuestion ? 'Edit Question' : 'Add New Question' }}
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Quiz Selection -->
            <div class="mb-3">
              <label class="form-label">Quiz *</label>
              <select v-model="form.quiz_id" class="form-select" required>
                <option value="">Select Quiz</option>
                <option v-for="quiz in quizzes" :key="quiz.id" :value="quiz.id">
                  {{ quiz.title }}
                </option>
              </select>
            </div>

            <!-- Question Text -->
            <div class="mb-3">
              <label class="form-label">Question Text *</label>
              <textarea 
                v-model="form.question_text" 
                class="form-control" 
                rows="3"
                placeholder="Enter the question..."
                required
              ></textarea>
            </div>

            <!-- Question Type -->
            <div class="mb-3">
              <label class="form-label">Question Type</label>
              <select v-model="form.question_type" class="form-select">
                <option value="multiple_choice">Multiple Choice</option>
                <option value="true_false">True/False</option>
              </select>
            </div>

            <!-- Options -->
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Option A *</label>
                <input 
                  v-model="form.option_a" 
                  type="text" 
                  class="form-control"
                  placeholder="First option"
                  required
                >
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Option B *</label>
                <input 
                  v-model="form.option_b" 
                  type="text" 
                  class="form-control"
                  placeholder="Second option"
                  required
                >
              </div>
            </div>

            <div v-if="form.question_type === 'multiple_choice'" class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Option C</label>
                <input 
                  v-model="form.option_c" 
                  type="text" 
                  class="form-control"
                  placeholder="Third option"
                >
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Option D</label>
                <input 
                  v-model="form.option_d" 
                  type="text" 
                  class="form-control"
                  placeholder="Fourth option"
                >
              </div>
            </div>

            <!-- Correct Answer -->
            <div class="mb-3">
              <label class="form-label">Correct Answer *</label>
              <select v-model="form.correct_option" class="form-select" required>
                <option value="">Select correct answer</option>
                <option value="A">A - {{ form.option_a || 'Option A' }}</option>
                <option value="B">B - {{ form.option_b || 'Option B' }}</option>
                <option v-if="form.question_type === 'multiple_choice'" value="C">C - {{ form.option_c || 'Option C' }}</option>
                <option v-if="form.question_type === 'multiple_choice'" value="D">D - {{ form.option_d || 'Option D' }}</option>
              </select>
            </div>

            <!-- Explanation -->
            <div class="mb-3">
              <label class="form-label">Explanation</label>
              <textarea 
                v-model="form.explanation" 
                class="form-control" 
                rows="2"
                placeholder="Explain why this answer is correct..."
              ></textarea>
            </div>

            <!-- Difficulty -->
            <div class="mb-3">
              <label class="form-label">Difficulty</label>
              <select v-model="form.difficulty" class="form-select">
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>

            <!-- Points -->
            <div class="mb-3">
              <label class="form-label">Points</label>
              <input 
                v-model.number="form.points" 
                type="number" 
                class="form-control"
                min="1"
                max="10"
                placeholder="1"
              >
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">
            Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="handleSubmit"
            :disabled="saving"
          >
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            {{ editingQuestion ? 'Update Question' : 'Create Question' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'

export default {
  name: 'QuestionModal',
  props: {
    question: {
      type: Object,
      default: null
    },
    quizzes: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'save'],
  setup(props, { emit }) {
    const { api } = useAuth()
    const saving = ref(false)
    
    const form = ref({
      quiz_id: '',
      question_text: '',
      question_type: 'multiple_choice',
      option_a: '',
      option_b: '',
      option_c: '',
      option_d: '',
      correct_option: '',
      explanation: '',
      difficulty: 'medium',
      points: 1
    })

    const editingQuestion = ref(false)

    const resetForm = () => {
      form.value = {
        quiz_id: '',
        question_text: '',
        question_type: 'multiple_choice',
        option_a: '',
        option_b: '',
        option_c: '',
        option_d: '',
        correct_option: '',
        explanation: '',
        difficulty: 'medium',
        points: 1
      }
    }

    const loadQuestion = (question) => {
      if (question) {
        editingQuestion.value = true
        form.value = {
          quiz_id: question.quiz_id,
          question_text: question.question_text,
          question_type: question.question_type || 'multiple_choice',
          option_a: question.option_a,
          option_b: question.option_b,
          option_c: question.option_c,
          option_d: question.option_d,
          correct_option: question.correct_option,
          explanation: question.explanation || '',
          difficulty: question.difficulty || 'medium',
          points: question.points || 1
        }
      } else {
        editingQuestion.value = false
        resetForm()
      }
    }

    const handleSubmit = async () => {
      try {
        saving.value = true
        
        if (editingQuestion.value) {
          await api.updateQuestion(props.question.id, form.value)
        } else {
          await api.createQuestion(form.value)
        }
        
        emit('save')
      } catch (error) {
        console.error('Error saving question:', error)
        alert('Failed to save question: ' + (error.response?.data?.error || error.message))
      } finally {
        saving.value = false
      }
    }

    // Watch for changes in props.question
    watch(() => props.question, loadQuestion, { immediate: true })

    // Watch question type changes
    watch(() => form.value.question_type, (newType) => {
      if (newType === 'true_false') {
        form.value.option_a = 'True'
        form.value.option_b = 'False'
        form.value.option_c = ''
        form.value.option_d = ''
        if (!['A', 'B'].includes(form.value.correct_option)) {
          form.value.correct_option = ''
        }
      } else if (newType === 'multiple_choice' && form.value.option_a === 'True') {
        // Reset options if switching from true/false
        form.value.option_a = ''
        form.value.option_b = ''
        form.value.option_c = ''
        form.value.option_d = ''
        form.value.correct_option = ''
      }
    })

    onMounted(() => {
      loadQuestion(props.question)
    })

    return {
      form,
      saving,
      editingQuestion,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.modal {
  z-index: 1050;
}

.form-label {
  font-weight: 600;
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
