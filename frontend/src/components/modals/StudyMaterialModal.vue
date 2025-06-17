<template>
  <div 
    v-if="show" 
    class="modal d-block" 
    style="background-color: rgba(0,0,0,0.5)"
    @click.self="$emit('close')"
  >
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-book me-2"></i>
            {{ material ? 'Edit Study Material' : 'Create New Study Material' }}
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="row g-3">
              <!-- Title -->
              <div class="col-12">
                <label class="form-label">Title *</label>
                <input 
                  v-model="form.title" 
                  type="text" 
                  class="form-control" 
                  required
                  placeholder="Enter material title"
                >
              </div>
              
              <!-- Description -->
              <div class="col-12">
                <label class="form-label">Description</label>
                <textarea 
                  v-model="form.description" 
                  class="form-control" 
                  rows="3"
                  placeholder="Brief description of the material"
                ></textarea>
              </div>
              
              <!-- Material Type -->
              <div class="col-md-6">
                <label class="form-label">Material Type *</label>
                <select v-model="form.material_type" class="form-select" required @change="onTypeChange">
                  <option value="">Select type...</option>
                  <option value="text">Text Content</option>
                  <option value="document">Document File</option>
                  <option value="video">Video</option>
                  <option value="audio">Audio</option>
                  <option value="link">External Link</option>
                </select>
              </div>
              
              <!-- Subject -->
              <div class="col-md-6">
                <label class="form-label">Subject</label>
                <select v-model="form.subject_id" class="form-select" @change="onSubjectChange">
                  <option value="">Select subject...</option>
                  <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                    {{ subject.name }}
                  </option>
                </select>
              </div>
              
              <!-- Chapter -->
              <div class="col-md-6">
                <label class="form-label">Chapter</label>
                <select v-model="form.chapter_id" class="form-select" :disabled="!form.subject_id">
                  <option value="">{{ form.subject_id ? 'Select chapter...' : 'Select subject first' }}</option>
                  <option v-for="chapter in filteredChapters" :key="chapter.id" :value="chapter.id">
                    {{ chapter.name }}
                  </option>
                </select>
              </div>
              
              <!-- Status -->
              <div class="col-md-6">
                <label class="form-label">Status</label>
                <select v-model="form.is_active" class="form-select">
                  <option :value="true">Active</option>
                  <option :value="false">Inactive</option>
                </select>
              </div>
              
              <!-- Content based on type -->
              <div class="col-12" v-if="form.material_type">
                <!-- Text Content -->
                <div v-if="form.material_type === 'text'">
                  <label class="form-label">Content *</label>
                  <div class="mb-2">
                    <small class="text-muted">You can use markdown formatting</small>
                  </div>
                  <textarea 
                    v-model="form.content" 
                    class="form-control" 
                    rows="8"
                    placeholder="Enter your text content here..."
                    required
                  ></textarea>
                </div>
                
                <!-- Document Upload -->
                <div v-else-if="form.material_type === 'document'">
                  <label class="form-label">Document File</label>
                  <div 
                    class="upload-area border rounded p-4 text-center"
                    :class="{ 'border-primary': dragOver }"
                    @dragover.prevent="dragOver = true"
                    @dragleave="dragOver = false"
                    @drop.prevent="handleFileDrop"
                  >
                    <div v-if="!selectedFile && !form.file_path">
                      <i class="bi bi-cloud-upload display-4 text-muted"></i>
                      <p class="mt-2 mb-2">Drop file here or click to browse</p>
                      <input 
                        ref="fileInput"
                        type="file" 
                        class="d-none" 
                        accept=".pdf,.doc,.docx,.txt,.md,.html,.ppt,.pptx"
                        @change="handleFileSelect"
                      >
                      <button type="button" class="btn btn-outline-primary" @click="$refs.fileInput.click()">
                        Choose File
                      </button>
                      <small class="d-block mt-2 text-muted">
                        Supported: PDF, DOC, DOCX, TXT, MD, HTML, PPT, PPTX
                      </small>
                    </div>
                    
                    <div v-else-if="selectedFile">
                      <i class="bi bi-file-earmark-check display-4 text-success"></i>
                      <p class="mt-2 mb-2">{{ selectedFile.name }}</p>
                      <button type="button" class="btn btn-outline-danger btn-sm" @click="removeFile">
                        <i class="bi bi-trash me-1"></i>Remove
                      </button>
                    </div>
                    
                    <div v-else-if="form.file_path">
                      <i class="bi bi-file-earmark display-4 text-info"></i>
                      <p class="mt-2 mb-2">Current file: {{ getFileName(form.file_path) }}</p>
                      <button type="button" class="btn btn-outline-primary btn-sm" @click="$refs.fileInput.click()">
                        Replace File
                      </button>
                    </div>
                  </div>
                  
                  <!-- Upload Progress -->
                  <div v-if="uploading" class="mt-3">
                    <div class="progress">
                      <div class="progress-bar" :style="`width: ${uploadProgress}%`"></div>
                    </div>
                    <small class="text-muted">Uploading... {{ uploadProgress }}%</small>
                  </div>
                </div>
                
                <!-- Video/Audio URL -->
                <div v-else-if="form.material_type === 'video' || form.material_type === 'audio'">
                  <label class="form-label">{{ form.material_type === 'video' ? 'Video' : 'Audio' }} URL *</label>
                  <input 
                    v-model="form.url" 
                    type="url" 
                    class="form-control" 
                    required
                    :placeholder="`Enter ${form.material_type} URL (YouTube, Vimeo, etc.)`"
                  >
                  <small class="text-muted">
                    Supported: YouTube, Vimeo, direct media URLs
                  </small>
                </div>
                
                <!-- External Link -->
                <div v-else-if="form.material_type === 'link'">
                  <label class="form-label">External Link URL *</label>
                  <input 
                    v-model="form.url" 
                    type="url" 
                    class="form-control" 
                    required
                    placeholder="Enter external link URL"
                  >
                  <small class="text-muted">
                    Link to external resources, websites, or documents
                  </small>
                </div>
              </div>
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
            :disabled="!isFormValid || submitting"
          >
            <i v-if="submitting" class="bi bi-hourglass-split me-1"></i>
            <i v-else class="bi bi-check me-1"></i>
            {{ submitting ? 'Saving...' : (material ? 'Update' : 'Create') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'

const props = defineProps({
  show: Boolean,
  material: Object,
  subjects: Array,
  chapters: Array
})

const emit = defineEmits(['close', 'save'])

// Form state
const form = reactive({
  title: '',
  description: '',
  content: '',
  material_type: '',
  file_path: '',
  url: '',
  chapter_id: '',
  subject_id: '',
  is_active: true
})

// File upload state
const selectedFile = ref(null)
const dragOver = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const submitting = ref(false)

// Computed
const filteredChapters = computed(() => {
  if (!form.subject_id) return []
  return props.chapters.filter(chapter => chapter.subject_id == form.subject_id)
})

const isFormValid = computed(() => {
  if (!form.title || !form.material_type) return false
  
  switch (form.material_type) {
    case 'text':
      return !!form.content
    case 'document':
      return !!(selectedFile.value || form.file_path)
    case 'video':
    case 'audio':
    case 'link':
      return !!form.url
    default:
      return false
  }
})

// Watchers
watch(() => props.material, (newMaterial) => {
  if (newMaterial) {
    Object.assign(form, {
      title: newMaterial.title || '',
      description: newMaterial.description || '',
      content: newMaterial.content || '',
      material_type: newMaterial.material_type || '',
      file_path: newMaterial.file_path || '',
      url: newMaterial.url || '',
      chapter_id: newMaterial.chapter_id || '',
      subject_id: newMaterial.subject_id || '',
      is_active: newMaterial.is_active !== undefined ? newMaterial.is_active : true
    })
  } else {
    // Reset form for new material
    Object.assign(form, {
      title: '',
      description: '',
      content: '',
      material_type: '',
      file_path: '',
      url: '',
      chapter_id: '',
      subject_id: '',
      is_active: true
    })
  }
  selectedFile.value = null
}, { immediate: true })

// Methods
const onTypeChange = () => {
  // Reset type-specific fields when type changes
  form.content = ''
  form.file_path = ''
  form.url = ''
  selectedFile.value = null
}

const onSubjectChange = () => {
  form.chapter_id = ''
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const handleFileDrop = (event) => {
  dragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const removeFile = () => {
  selectedFile.value = null
  form.file_path = ''
}

const getFileName = (path) => {
  if (!path) return ''
  return path.split('/').pop()
}

const uploadFile = async () => {
  if (!selectedFile.value) return null
  
  try {
    uploading.value = true
    uploadProgress.value = 0
    
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    // Simulate upload progress
    const interval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)
    
    const response = await apiService.uploadStudyMaterialFileStandalone(formData)
    
    clearInterval(interval)
    uploadProgress.value = 100
    
    return response.file_path
    
  } catch (error) {
    uploadProgress.value = 0
    throw error
  } finally {
    uploading.value = false
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value || submitting.value) return
  
  try {
    submitting.value = true
    
    let filePath = form.file_path
    
    // Upload file if selected
    if (selectedFile.value) {
      filePath = await uploadFile()
    }
    
    const materialData = {
      ...form,
      file_path: filePath
    }
    
    if (props.material) {
      await apiService.updateStudyMaterial(props.material.id, materialData)
    } else {
      await apiService.createStudyMaterial(materialData)
    }
    
    emit('save')
    
  } catch (error) {
    console.error('Error saving material:', error)
    // Handle error (could emit an error event or show notification)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.upload-area {
  transition: border-color 0.3s ease;
  cursor: pointer;
}

.upload-area:hover {
  border-color: #0d6efd !important;
}

.upload-area.border-primary {
  border-color: #0d6efd !important;
  background-color: rgba(13, 110, 253, 0.1);
}

.modal {
  z-index: 1055;
}

.progress {
  height: 8px;
}

.form-control:focus,
.form-select:focus {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}
</style>
