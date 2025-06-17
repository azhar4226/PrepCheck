<template>
  <BaseModal
    :show="true"
    :title="isEdit ? 'Edit Question' : 'Create New Question'"
    size="large"
    @close="$emit('close')"
  >
    <form @submit.prevent="saveQuestion" class="question-form">
      <div class="form-row">
        <FormField
          v-model="form.topic"
          label="Topic *"
          placeholder="e.g., Python Programming, Data Structures..."
          :error="errors.topic"
          required
        />
        
        <FormField
          v-model="form.difficulty"
          label="Difficulty *"
          type="select"
          :options="difficultyOptions"
          :error="errors.difficulty"
          required
        />
      </div>

      <FormField
        v-model="form.question_text"
        label="Question Text *"
        type="textarea"
        placeholder="Enter the question text..."
        :error="errors.question_text"
        required
        rows="3"
      />

      <div class="options-section">
        <h3>Answer Options</h3>
        
        <FormField
          v-model="form.option_a"
          label="Option A *"
          placeholder="Enter option A..."
          :error="errors.option_a"
          required
        />
        
        <FormField
          v-model="form.option_b"
          label="Option B *"
          placeholder="Enter option B..."
          :error="errors.option_b"
          required
        />
        
        <FormField
          v-model="form.option_c"
          label="Option C *"
          placeholder="Enter option C..."
          :error="errors.option_c"
          required
        />
        
        <FormField
          v-model="form.option_d"
          label="Option D *"
          placeholder="Enter option D..."
          :error="errors.option_d"
          required
        />
        
        <FormField
          v-model="form.correct_option"
          label="Correct Answer *"
          type="select"
          :options="answerOptions"
          :error="errors.correct_option"
          required
        />
      </div>

      <FormField
        v-model="form.explanation"
        label="Explanation"
        type="textarea"
        placeholder="Provide an explanation for the correct answer..."
        rows="3"
      />

      <div class="form-row">
        <FormField
          v-model="form.marks"
          label="Marks"
          type="number"
          min="1"
          max="10"
        />
        
        <FormField
          v-model="form.chapter_id"
          label="Chapter"
          type="select"
          :options="chapterOptions"
          placeholder="Select a chapter (optional)"
        />
      </div>

      <FormField
        v-model="tagsInput"
        label="Tags"
        placeholder="Enter tags separated by commas (e.g., basic, syntax, loops)"
        @input="updateTags"
      />

      <div v-if="form.tags && form.tags.length > 0" class="tags-preview">
        <span class="tag" v-for="tag in form.tags" :key="tag">
          {{ tag }}
          <button type="button" @click="removeTag(tag)" class="tag-remove">×</button>
        </span>
      </div>

      <div class="form-actions">
        <button type="button" @click="$emit('close')" class="btn btn-secondary">
          Cancel
        </button>
        <button type="submit" :disabled="saving" class="btn btn-primary">
          {{ saving ? 'Saving...' : (isEdit ? 'Update Question' : 'Create Question') }}
        </button>
      </div>
    </form>
  </BaseModal>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import FormField from '@/components/ui/FormField.vue'
import adminService from '@/services/adminService'
import apiClient from '@/services/apiClient'

export default {
  name: 'QuestionBankModal',
  components: {
    BaseModal,
    FormField
  },
  props: {
    question: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'save'],
  setup(props, { emit }) {
    const saving = ref(false)
    const chapters = ref([])
    const tagsInput = ref('')
    
    const form = reactive({
      topic: '',
      difficulty: 'medium',
      question_text: '',
      option_a: '',
      option_b: '',
      option_c: '',
      option_d: '',
      correct_option: 'A',
      explanation: '',
      marks: 1,
      chapter_id: null,
      tags: []
    })
    
    const errors = reactive({})
    
    const isEdit = computed(() => !!props.question)
    
    const difficultyOptions = [
      { value: 'easy', label: 'Easy' },
      { value: 'medium', label: 'Medium' },
      { value: 'hard', label: 'Hard' }
    ]
    
    const answerOptions = [
      { value: 'A', label: 'A' },
      { value: 'B', label: 'B' },
      { value: 'C', label: 'C' },
      { value: 'D', label: 'D' }
    ]
    
    const chapterOptions = computed(() => [
      { value: null, label: 'No Chapter' },
      ...chapters.value.map(chapter => ({
        value: chapter.id,
        label: chapter.title
      }))
    ])
    
    const loadChapters = async () => {
      try {
        const response = await adminService.getChapters()
        chapters.value = response.chapters || []
      } catch (error) {
        console.error('Failed to load chapters:', error)
        chapters.value = []
      }
    }
    
    const updateTags = () => {
      const tags = tagsInput.value
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)
      form.tags = [...new Set(tags)] // Remove duplicates
    }
    
    const removeTag = (tagToRemove) => {
      form.tags = form.tags.filter(tag => tag !== tagToRemove)
      tagsInput.value = form.tags.join(', ')
    }
    
    const validateForm = () => {
      const newErrors = {}
      
      if (!form.topic.trim()) {
        newErrors.topic = 'Topic is required'
      }
      
      if (!form.difficulty) {
        newErrors.difficulty = 'Difficulty is required'
      }
      
      if (!form.question_text.trim()) {
        newErrors.question_text = 'Question text is required'
      }
      
      if (!form.option_a.trim()) {
        newErrors.option_a = 'Option A is required'
      }
      
      if (!form.option_b.trim()) {
        newErrors.option_b = 'Option B is required'
      }
      
      if (!form.option_c.trim()) {
        newErrors.option_c = 'Option C is required'
      }
      
      if (!form.option_d.trim()) {
        newErrors.option_d = 'Option D is required'
      }
      
      if (!form.correct_option) {
        newErrors.correct_option = 'Correct answer is required'
      }
      
      // Check for duplicate options
      const options = [form.option_a, form.option_b, form.option_c, form.option_d]
        .map(opt => opt.trim().toLowerCase())
        .filter(opt => opt)
      
      const uniqueOptions = new Set(options)
      if (options.length !== uniqueOptions.size) {
        newErrors.option_a = 'Options must be unique'
      }
      
      Object.assign(errors, newErrors)
      return Object.keys(newErrors).length === 0
    }
    
    const saveQuestion = async () => {
      // Clear previous errors
      Object.keys(errors).forEach(key => delete errors[key])
      
      if (!validateForm()) {
        return
      }
      
      saving.value = true
      
      try {
        const questionData = {
          ...form,
          topic: form.topic.trim(),
          question_text: form.question_text.trim(),
          option_a: form.option_a.trim(),
          option_b: form.option_b.trim(),
          option_c: form.option_c.trim(),
          option_d: form.option_d.trim(),
          explanation: form.explanation.trim(),
          chapter_id: form.chapter_id || undefined
        }
        
        if (isEdit.value) {
          await apiClient.put(`/admin/question-bank/questions/${props.question.id}`, questionData)
        } else {
          await apiClient.post('/admin/question-bank/questions', questionData)
        }
        
        emit('save')
        emit('close')
      } catch (error) {
        console.error('Failed to save question:', error)
        
        if (error.response?.data?.error) {
          if (error.response.data.error.includes('already exists')) {
            errors.question_text = 'A question with this content already exists in the question bank'
          } else {
            errors.general = error.response.data.error
          }
        } else {
          errors.general = 'Failed to save question. Please try again.'
        }
      } finally {
        saving.value = false
      }
    }
    
    // Initialize form with question data if editing
    watch(() => props.question, (question) => {
      if (question) {
        Object.assign(form, {
          topic: question.topic || '',
          difficulty: question.difficulty || 'medium',
          question_text: question.question_text || '',
          option_a: question.option_a || '',
          option_b: question.option_b || '',
          option_c: question.option_c || '',
          option_d: question.option_d || '',
          correct_option: question.correct_option || 'A',
          explanation: question.explanation || '',
          marks: question.marks || 1,
          chapter_id: question.chapter_id || null,
          tags: question.tags || []
        })
        tagsInput.value = form.tags.join(', ')
      }
    }, { immediate: true })
    
    onMounted(() => {
      loadChapters()
    })
    
    return {
      saving,
      form,
      errors,
      tagsInput,
      isEdit,
      difficultyOptions,
      answerOptions,
      chapterOptions,
      updateTags,
      removeTag,
      saveQuestion
    }
  }
}
</script>

<style scoped>
.question-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.options-section h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 5px;
}

.tags-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.tag {
  background: #e9ecef;
  color: #495057;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  display: flex;
  align-items: center;
  gap: 5px;
}

.tag-remove {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  font-size: 1.2em;
  padding: 0;
  line-height: 1;
}

.tag-remove:hover {
  color: #dc3545;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #dee2e6;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn:hover:not(:disabled) {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
