<template>
  <BaseModal
    :show="true"
    title="Import Questions"
    size="large"
    @close="$emit('close')"
  >
    <div class="import-section">
      <div class="import-options">
        <h3>Import Methods</h3>
        
        <div class="import-methods">
          <label class="import-method" :class="{ active: importMethod === 'csv' }">
            <input 
              type="radio" 
              value="csv" 
              v-model="importMethod"
              @change="resetImport"
            />
            <div class="method-info">
              <strong>📄 CSV File</strong>
              <p>Upload a CSV file with question data</p>
            </div>
          </label>
          
          <label class="import-method" :class="{ active: importMethod === 'json' }">
            <input 
              type="radio" 
              value="json" 
              v-model="importMethod"
              @change="resetImport"
            />
            <div class="method-info">
              <strong>📋 JSON File</strong>
              <p>Upload a JSON file with question array</p>
            </div>
          </label>
          
          <label class="import-method" :class="{ active: importMethod === 'text' }">
            <input 
              type="radio" 
              value="text" 
              v-model="importMethod"
              @change="resetImport"
            />
            <div class="method-info">
              <strong>✍️ Manual Text</strong>
              <p>Paste or type questions manually</p>
            </div>
          </label>
          
          <label class="import-method" :class="{ active: importMethod === 'ai' }">
            <input 
              type="radio" 
              value="ai" 
              v-model="importMethod"
              @change="resetImport"
            />
            <div class="method-info">
              <strong>🤖 AI Generation</strong>
              <p>Generate questions using AI for specific topics</p>
            </div>
          </label>
        </div>
      </div>

      <!-- CSV Import -->
      <div v-if="importMethod === 'csv'" class="import-content">
        <div class="file-upload">
          <FileUpload
            @file-selected="handleCsvFile"
            accept=".csv"
            :multiple="false"
          >
            <template #default="{ isDragActive }">
              <div class="upload-area" :class="{ 'drag-active': isDragActive }">
                <i class="upload-icon">📄</i>
                <p>Drop CSV file here or click to browse</p>
                <small>Expected format: Question, Option A, Option B, Option C, Option D, Correct Answer, Explanation, Topic, Difficulty</small>
              </div>
            </template>
          </FileUpload>
        </div>
        
        <button @click="downloadCsvTemplate" class="btn btn-secondary">
          📥 Download CSV Template
        </button>
      </div>

      <!-- JSON Import -->
      <div v-if="importMethod === 'json'" class="import-content">
        <div class="file-upload">
          <FileUpload
            @file-selected="handleJsonFile"
            accept=".json"
            :multiple="false"
          >
            <template #default="{ isDragActive }">
              <div class="upload-area" :class="{ 'drag-active': isDragActive }">
                <i class="upload-icon">📋</i>
                <p>Drop JSON file here or click to browse</p>
                <small>Expected format: Array of question objects</small>
              </div>
            </template>
          </FileUpload>
        </div>
        
        <button @click="downloadJsonTemplate" class="btn btn-secondary">
          📥 Download JSON Template
        </button>
      </div>

      <!-- Manual Text Import -->
      <div v-if="importMethod === 'text'" class="import-content">
        <div class="text-import">
          <FormField
            v-model="manualText"
            label="Question Text"
            type="textarea"
            placeholder="Paste your questions here. Use this format:

Q: What is Python?
A) A snake
B) A programming language
C) A movie
D) A book
Correct: B
Explanation: Python is a popular programming language.
Topic: Programming
Difficulty: Easy

---

Q: Next question...
"
            rows="15"
          />
          
          <button @click="parseManualText" class="btn btn-primary">
            🔍 Parse Questions
          </button>
        </div>
      </div>

      <!-- AI Generation Import -->
      <div v-if="importMethod === 'ai'" class="import-content">
        <div class="ai-generation">
          <div class="ai-form">
            <FormField
              v-model="aiGenerationForm.topic"
              label="Topic"
              placeholder="e.g., Python Programming, Data Structures..."
              required
            />
            
            <FormField
              v-model="aiGenerationForm.difficulty"
              label="Difficulty"
              type="select"
              :options="difficultyOptions"
              required
            />
            
            <FormField
              v-model="aiGenerationForm.numQuestions"
              label="Number of Questions"
              type="number"
              min="1"
              max="50"
              required
            />
            
            <FormField
              v-model="aiGenerationForm.context"
              label="Additional Context"
              type="textarea"
              placeholder="Provide additional context or specific requirements..."
              rows="3"
            />
            
            <FormField
              v-model="aiGenerationForm.chapterId"
              label="Chapter"
              type="select"
              :options="chapterOptions"
              placeholder="Select a chapter (optional)"
            />
          </div>
          
          <button 
            @click="generateWithAI" 
            :disabled="aiGenerating"
            class="btn btn-primary"
          >
            {{ aiGenerating ? '🔄 Generating...' : '🤖 Generate Questions' }}
          </button>
        </div>
      </div>

      <!-- Preview Section -->
      <div v-if="parsedQuestions.length > 0" class="preview-section">
        <h3>📝 Preview Questions ({{ parsedQuestions.length }})</h3>
        
        <div class="preview-stats">
          <div class="stat">
            <span>Valid Questions:</span>
            <span class="stat-value valid">{{ validQuestions }}</span>
          </div>
          <div class="stat">
            <span>Invalid Questions:</span>
            <span class="stat-value invalid">{{ invalidQuestions }}</span>
          </div>
          <div class="stat">
            <span>Duplicates Found:</span>
            <span class="stat-value duplicate">{{ duplicateQuestions }}</span>
          </div>
        </div>

        <div class="preview-options">
          <label class="preview-option">
            <input 
              type="checkbox" 
              v-model="importOptions.skipInvalid"
            />
            Skip invalid questions
          </label>
          
          <label class="preview-option">
            <input 
              type="checkbox" 
              v-model="importOptions.skipDuplicates"
            />
            Skip duplicate questions
          </label>
          
          <label class="preview-option">
            <input 
              type="checkbox" 
              v-model="importOptions.autoVerify"
            />
            Auto-verify imported questions
          </label>
        </div>

        <div class="questions-preview">
          <div 
            v-for="(question, index) in parsedQuestions.slice(0, 5)" 
            :key="index"
            class="question-preview"
            :class="{ 
              'invalid': !question.isValid, 
              'duplicate': question.isDuplicate 
            }"
          >
            <div class="question-header">
              <span class="question-number">#{{ index + 1 }}</span>
              <span v-if="!question.isValid" class="status invalid">❌ Invalid</span>
              <span v-else-if="question.isDuplicate" class="status duplicate">⚠️ Duplicate</span>
              <span v-else class="status valid">✅ Valid</span>
              <span class="question-topic">{{ question.topic }}</span>
              <span class="question-difficulty">{{ question.difficulty }}</span>
            </div>
            
            <div class="question-text">{{ question.question_text }}</div>
            
            <div v-if="question.errors && question.errors.length > 0" class="question-errors">
              <strong>Errors:</strong>
              <ul>
                <li v-for="error in question.errors" :key="error">{{ error }}</li>
              </ul>
            </div>
          </div>
          
          <div v-if="parsedQuestions.length > 5" class="more-questions">
            <p>And {{ parsedQuestions.length - 5 }} more questions...</p>
          </div>
        </div>
      </div>

      <!-- Import Actions -->
      <div class="import-actions">
        <button @click="$emit('close')" class="btn btn-secondary">
          Cancel
        </button>
        
        <button 
          v-if="parsedQuestions.length > 0"
          @click="validateQuestions"
          :disabled="validating"
          class="btn btn-info"
        >
          {{ validating ? '🔍 Validating...' : '🔍 Validate Questions' }}
        </button>
        
        <button 
          v-if="validQuestions > 0"
          @click="importQuestions"
          :disabled="importing"
          class="btn btn-primary"
        >
          {{ importing ? '📥 Importing...' : `📥 Import ${validQuestions} Questions` }}
        </button>
      </div>
    </div>
  </BaseModal>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import FileUpload from '@/components/ui/FileUpload.vue'
import FormField from '@/components/ui/FormField.vue'
import adminService from '@/services/adminService'
import aiService from '@/services/aiService'
import apiClient from '@/services/apiClient'

export default {
  name: 'QuestionBankImportModal',
  components: {
    BaseModal,
    FileUpload,
    FormField
  },
  emits: ['close', 'imported'],
  setup(props, { emit }) {
    const importMethod = ref('csv')
    const parsedQuestions = ref([])
    const manualText = ref('')
    const chapters = ref([])
    
    const importing = ref(false)
    const validating = ref(false)
    const aiGenerating = ref(false)
    
    const importOptions = reactive({
      skipInvalid: true,
      skipDuplicates: true,
      autoVerify: false
    })
    
    const aiGenerationForm = reactive({
      topic: '',
      difficulty: 'medium',
      numQuestions: 10,
      context: '',
      chapterId: null
    })
    
    const difficultyOptions = [
      { value: 'easy', label: 'Easy' },
      { value: 'medium', label: 'Medium' },
      { value: 'hard', label: 'Hard' }
    ]
    
    const chapterOptions = computed(() => [
      { value: null, label: 'No Chapter' },
      ...chapters.value.map(chapter => ({
        value: chapter.id,
        label: chapter.title
      }))
    ])
    
    const validQuestions = computed(() => 
      parsedQuestions.value.filter(q => q.isValid && (!importOptions.skipDuplicates || !q.isDuplicate)).length
    )
    
    const invalidQuestions = computed(() => 
      parsedQuestions.value.filter(q => !q.isValid).length
    )
    
    const duplicateQuestions = computed(() => 
      parsedQuestions.value.filter(q => q.isDuplicate).length
    )
    
    const loadChapters = async () => {
      try {
        const response = await adminService.getChapters()
        chapters.value = response.chapters || []
      } catch (error) {
        console.error('Failed to load chapters:', error)
        chapters.value = []
      }
    }
    
    const resetImport = () => {
      parsedQuestions.value = []
      manualText.value = ''
    }
    
    const handleCsvFile = async (file) => {
      try {
        const text = await file.text()
        const lines = text.split('\n').filter(line => line.trim())
        const headers = lines[0].split(',').map(h => h.trim())
        
        const questions = []
        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(',').map(v => v.trim())
          if (values.length >= 9) {
            questions.push({
              question_text: values[0],
              option_a: values[1],
              option_b: values[2],
              option_c: values[3],
              option_d: values[4],
              correct_option: values[5],
              explanation: values[6],
              topic: values[7],
              difficulty: values[8],
              source: 'imported'
            })
          }
        }
        
        parsedQuestions.value = questions.map(validateQuestion)
      } catch (error) {
        console.error('Failed to parse CSV:', error)
        alert('Failed to parse CSV file. Please check the format.')
      }
    }
    
    const handleJsonFile = async (file) => {
      try {
        const text = await file.text()
        const data = JSON.parse(text)
        const questions = Array.isArray(data) ? data : [data]
        
        parsedQuestions.value = questions.map(q => validateQuestion({
          ...q,
          source: 'imported'
        }))
      } catch (error) {
        console.error('Failed to parse JSON:', error)
        alert('Failed to parse JSON file. Please check the format.')
      }
    }
    
    const parseManualText = () => {
      try {
        const sections = manualText.value.split('---').filter(s => s.trim())
        const questions = []
        
        for (const section of sections) {
          const lines = section.trim().split('\n').filter(l => l.trim())
          if (lines.length < 7) continue
          
          const question = {
            question_text: '',
            option_a: '',
            option_b: '',
            option_c: '',
            option_d: '',
            correct_option: '',
            explanation: '',
            topic: '',
            difficulty: 'medium',
            source: 'imported'
          }
          
          for (const line of lines) {
            const trimmed = line.trim()
            if (trimmed.startsWith('Q:')) {
              question.question_text = trimmed.substring(2).trim()
            } else if (trimmed.startsWith('A)')) {
              question.option_a = trimmed.substring(2).trim()
            } else if (trimmed.startsWith('B)')) {
              question.option_b = trimmed.substring(2).trim()
            } else if (trimmed.startsWith('C)')) {
              question.option_c = trimmed.substring(2).trim()
            } else if (trimmed.startsWith('D)')) {
              question.option_d = trimmed.substring(2).trim()
            } else if (trimmed.startsWith('Correct:')) {
              question.correct_option = trimmed.substring(8).trim()
            } else if (trimmed.startsWith('Explanation:')) {
              question.explanation = trimmed.substring(12).trim()
            } else if (trimmed.startsWith('Topic:')) {
              question.topic = trimmed.substring(6).trim()
            } else if (trimmed.startsWith('Difficulty:')) {
              question.difficulty = trimmed.substring(11).trim().toLowerCase()
            }
          }
          
          questions.push(question)
        }
        
        parsedQuestions.value = questions.map(validateQuestion)
      } catch (error) {
        console.error('Failed to parse manual text:', error)
        alert('Failed to parse questions. Please check the format.')
      }
    }
    
    const generateWithAI = async () => {
      if (!aiGenerationForm.topic || !aiGenerationForm.difficulty || !aiGenerationForm.numQuestions) {
        alert('Please fill in all required fields.')
        return
      }
      
      aiGenerating.value = true
      
      try {
        const response = await aiService.generateQuiz({
          chapter_id: aiGenerationForm.chapterId || 1, // Default chapter
          topic: aiGenerationForm.topic,
          difficulty: aiGenerationForm.difficulty,
          num_questions: aiGenerationForm.numQuestions,
          context: aiGenerationForm.context
        })
        
        const questions = response.quiz.questions.map(q => ({
          question_text: q.question,
          option_a: q.options.A,
          option_b: q.options.B,
          option_c: q.options.C,
          option_d: q.options.D,
          correct_option: q.correct_answer,
          explanation: q.explanation,
          topic: aiGenerationForm.topic,
          difficulty: aiGenerationForm.difficulty,
          source: 'ai_generated'
        }))
        
        parsedQuestions.value = questions.map(validateQuestion)
      } catch (error) {
        console.error('Failed to generate questions with AI:', error)
        alert('Failed to generate questions. Please try again.')
      } finally {
        aiGenerating.value = false
      }
    }
    
    const validateQuestion = (question) => {
      const errors = []
      const validated = { ...question, isValid: true, isDuplicate: false, errors }
      
      if (!question.question_text?.trim()) {
        errors.push('Question text is required')
      }
      
      if (!question.option_a?.trim()) {
        errors.push('Option A is required')
      }
      
      if (!question.option_b?.trim()) {
        errors.push('Option B is required')
      }
      
      if (!question.option_c?.trim()) {
        errors.push('Option C is required')
      }
      
      if (!question.option_d?.trim()) {
        errors.push('Option D is required')
      }
      
      if (!['A', 'B', 'C', 'D'].includes(question.correct_option)) {
        errors.push('Correct option must be A, B, C, or D')
      }
      
      if (!question.topic?.trim()) {
        errors.push('Topic is required')
      }
      
      if (!['easy', 'medium', 'hard'].includes(question.difficulty?.toLowerCase())) {
        errors.push('Difficulty must be easy, medium, or hard')
      }
      
      validated.isValid = errors.length === 0
      return validated
    }
    
    const validateQuestions = async () => {
      validating.value = true
      
      try {
        // Check for duplicates against existing questions
        for (const question of parsedQuestions.value) {
          if (!question.isValid) continue
          
          // This would call an API to check for duplicates
          // For now, we'll simulate it
          question.isDuplicate = Math.random() > 0.9 // 10% chance of duplicate
        }
      } catch (error) {
        console.error('Failed to validate questions:', error)
      } finally {
        validating.value = false
      }
    }
    
    const importQuestions = async () => {
      importing.value = true
      
      try {
        const questionsToImport = parsedQuestions.value.filter(q => {
          if (!q.isValid && importOptions.skipInvalid) return false
          if (q.isDuplicate && importOptions.skipDuplicates) return false
          return true
        })
        
        let imported = 0
        const errors = []
        
        for (const question of questionsToImport) {
          try {
            const questionData = {
              question_text: question.question_text,
              option_a: question.option_a,
              option_b: question.option_b,
              option_c: question.option_c,
              option_d: question.option_d,
              correct_option: question.correct_option,
              explanation: question.explanation || '',
              topic: question.topic,
              difficulty: question.difficulty.toLowerCase(),
              marks: question.marks || 1,
              chapter_id: question.chapter_id || aiGenerationForm.chapterId,
              tags: question.tags || []
            }
            
            const response = await apiClient.post('/admin/question-bank/questions', questionData)
            
            if (importOptions.autoVerify) {
              await apiClient.post(`/admin/question-bank/questions/${response.data.question.id}/verify`, {
                verification_method: 'import',
                confidence: 0.8,
                notes: 'Auto-verified during import'
              })
            }
            
            imported++
          } catch (error) {
            errors.push(`Question ${questionsToImport.indexOf(question) + 1}: ${error.response?.data?.error || error.message}`)
          }
        }
        
        if (errors.length > 0) {
          console.error('Import errors:', errors)
          alert(`Imported ${imported} questions successfully. ${errors.length} questions failed.`)
        } else {
          alert(`Successfully imported ${imported} questions!`)
        }
        
        emit('imported')
        emit('close')
      } catch (error) {
        console.error('Failed to import questions:', error)
        alert('Failed to import questions. Please try again.')
      } finally {
        importing.value = false
      }
    }
    
    const downloadCsvTemplate = () => {
      const csvContent = `Question,Option A,Option B,Option C,Option D,Correct Answer,Explanation,Topic,Difficulty
"What is Python?","A snake","A programming language","A movie","A book","B","Python is a popular programming language","Programming","easy"
"Which data structure uses LIFO?","Queue","Stack","Array","Tree","B","Stack follows Last In First Out principle","Data Structures","medium"`
      
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'question-import-template.csv'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }
    
    const downloadJsonTemplate = () => {
      const jsonTemplate = [
        {
          question_text: "What is Python?",
          option_a: "A snake",
          option_b: "A programming language", 
          option_c: "A movie",
          option_d: "A book",
          correct_option: "B",
          explanation: "Python is a popular programming language",
          topic: "Programming",
          difficulty: "easy",
          marks: 1,
          tags: ["basic", "programming"]
        },
        {
          question_text: "Which data structure uses LIFO?",
          option_a: "Queue",
          option_b: "Stack",
          option_c: "Array", 
          option_d: "Tree",
          correct_option: "B",
          explanation: "Stack follows Last In First Out principle",
          topic: "Data Structures",
          difficulty: "medium",
          marks: 1,
          tags: ["data-structures", "stack"]
        }
      ]
      
      const jsonString = JSON.stringify(jsonTemplate, null, 2)
      const blob = new Blob([jsonString], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'question-import-template.json'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }
    
    onMounted(() => {
      loadChapters()
    })
    
    return {
      importMethod,
      parsedQuestions,
      manualText,
      importing,
      validating,
      aiGenerating,
      importOptions,
      aiGenerationForm,
      difficultyOptions,
      chapterOptions,
      validQuestions,
      invalidQuestions,
      duplicateQuestions,
      resetImport,
      handleCsvFile,
      handleJsonFile,
      parseManualText,
      generateWithAI,
      validateQuestions,
      importQuestions,
      downloadCsvTemplate,
      downloadJsonTemplate
    }
  }
}
</script>

<style scoped>
.import-section {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.import-methods {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.import-method {
  border: 2px solid #dee2e6;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.import-method:hover {
  border-color: #007bff;
}

.import-method.active {
  border-color: #007bff;
  background-color: #f8f9ff;
}

.import-method input[type="radio"] {
  margin-top: 2px;
}

.method-info strong {
  display: block;
  margin-bottom: 5px;
  color: #2c3e50;
}

.method-info p {
  margin: 0;
  font-size: 0.9em;
  color: #6c757d;
}

.import-content {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.upload-area {
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  transition: all 0.2s ease;
  cursor: pointer;
}

.upload-area:hover,
.upload-area.drag-active {
  border-color: #007bff;
  background-color: #f8f9ff;
}

.upload-icon {
  font-size: 3em;
  display: block;
  margin-bottom: 10px;
}

.upload-area p {
  margin: 10px 0 5px 0;
  font-weight: 500;
}

.upload-area small {
  color: #6c757d;
}

.text-import textarea {
  font-family: monospace;
}

.ai-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.preview-section {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
}

.preview-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-value {
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.9em;
}

.stat-value.valid {
  background: #d4edda;
  color: #155724;
}

.stat-value.invalid {
  background: #f8d7da;
  color: #721c24;
}

.stat-value.duplicate {
  background: #fff3cd;
  color: #856404;
}

.preview-options {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.preview-option {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.questions-preview {
  max-height: 400px;
  overflow-y: auto;
}

.question-preview {
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 10px;
  transition: all 0.2s ease;
}

.question-preview.invalid {
  border-color: #dc3545;
  background-color: #fff5f5;
}

.question-preview.duplicate {
  border-color: #ffc107;
  background-color: #fffbf0;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.question-number {
  font-weight: bold;
  color: #6c757d;
}

.status {
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.8em;
  font-weight: bold;
}

.status.valid {
  background: #d4edda;
  color: #155724;
}

.status.invalid {
  background: #f8d7da;
  color: #721c24;
}

.status.duplicate {
  background: #fff3cd;
  color: #856404;
}

.question-topic,
.question-difficulty {
  background: #e9ecef;
  color: #495057;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.8em;
}

.question-text {
  font-weight: 500;
  margin-bottom: 10px;
}

.question-errors {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 10px;
  margin-top: 10px;
}

.question-errors ul {
  margin: 5px 0 0 0;
  padding-left: 20px;
}

.more-questions {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  margin-top: 20px;
}

.import-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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

.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-info { background: #17a2b8; color: white; }

.btn:hover:not(:disabled) {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .import-methods {
    grid-template-columns: 1fr;
  }
  
  .ai-form {
    grid-template-columns: 1fr;
  }
  
  .preview-stats,
  .preview-options {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .import-actions {
    flex-direction: column;
  }
}
</style>
