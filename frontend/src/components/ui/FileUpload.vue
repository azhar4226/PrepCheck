// File Upload Component
<template>
  <div class="file-upload-area">
    <!-- Upload Zone -->
    <div 
      class="upload-zone border rounded p-4 text-center"
      :class="{ 
        'border-primary': dragOver, 
        'border-success': selectedFile,
        'border-danger': error 
      }"
      @dragover.prevent="dragOver = true"
      @dragleave="dragOver = false"
      @drop.prevent="handleFileDrop"
      @click="triggerFileInput"
    >
      <input 
        ref="fileInput"
        type="file" 
        class="d-none" 
        :accept="accept"
        :multiple="multiple"
        @change="handleFileSelect"
      >
      
      <!-- No file selected -->
      <div v-if="!selectedFile && !currentFile">
        <i class="bi bi-cloud-upload display-4 text-muted"></i>
        <p class="mt-2 mb-2">{{ placeholder }}</p>
        <button type="button" class="btn btn-outline-primary">
          {{ buttonText }}
        </button>
        <small v-if="acceptDescription" class="d-block mt-2 text-muted">
          {{ acceptDescription }}
        </small>
      </div>
      
      <!-- File selected -->
      <div v-else-if="selectedFile">
        <i class="bi bi-file-earmark-check display-4 text-success"></i>
        <p class="mt-2 mb-2">{{ selectedFile.name }}</p>
        <div class="mt-2">
          <small class="text-muted me-3">{{ formatFileSize(selectedFile.size) }}</small>
          <button type="button" class="btn btn-outline-danger btn-sm" @click.stop="removeFile">
            <i class="bi bi-trash me-1"></i>Remove
          </button>
        </div>
      </div>
      
      <!-- Current file (editing mode) -->
      <div v-else-if="currentFile">
        <i class="bi bi-file-earmark display-4 text-info"></i>
        <p class="mt-2 mb-2">Current: {{ getFileName(currentFile) }}</p>
        <button type="button" class="btn btn-outline-primary btn-sm">
          Replace File
        </button>
      </div>
    </div>
    
    <!-- Upload Progress -->
    <div v-if="uploading" class="mt-3">
      <div class="progress">
        <div 
          class="progress-bar" 
          :style="`width: ${uploadProgress}%`"
          :class="{ 'bg-success': uploadProgress === 100 }"
        ></div>
      </div>
      <small class="text-muted">
        {{ uploadProgress < 100 ? `Uploading... ${uploadProgress}%` : 'Upload complete!' }}
      </small>
    </div>
    
    <!-- Error Message -->
    <div v-if="error" class="mt-2 text-danger">
      <small><i class="bi bi-exclamation-triangle me-1"></i>{{ error }}</small>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  accept: {
    type: String,
    default: '*/*'
  },
  multiple: {
    type: Boolean,
    default: false
  },
  maxSize: {
    type: Number,
    default: 10 * 1024 * 1024 // 10MB
  },
  placeholder: {
    type: String,
    default: 'Drop files here or click to browse'
  },
  buttonText: {
    type: String,
    default: 'Choose File'
  },
  acceptDescription: String,
  currentFile: String,
  autoUpload: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['file-selected', 'file-removed', 'upload-progress', 'upload-complete', 'error'])

// State
const fileInput = ref(null)
const selectedFile = ref(null)
const dragOver = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const error = ref('')

// Methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const files = event.target.files
  if (files && files.length > 0) {
    selectFile(files[0])
  }
}

const handleFileDrop = (event) => {
  dragOver.value = false
  const files = event.dataTransfer.files
  if (files && files.length > 0) {
    selectFile(files[0])
  }
}

const selectFile = (file) => {
  error.value = ''
  
  // Validate file size
  if (file.size > props.maxSize) {
    error.value = `File size exceeds ${formatFileSize(props.maxSize)} limit`
    return
  }
  
  // Validate file type if accept is specified
  if (props.accept !== '*/*') {
    const acceptedTypes = props.accept.split(',').map(type => type.trim())
    const fileType = file.type
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
    
    const isValidType = acceptedTypes.some(type => {
      if (type.startsWith('.')) {
        return type === fileExtension
      }
      return fileType.startsWith(type.replace('*', ''))
    })
    
    if (!isValidType) {
      error.value = 'File type not supported'
      return
    }
  }
  
  selectedFile.value = file
  emit('file-selected', file)
  
  if (props.autoUpload) {
    uploadFile()
  }
}

const removeFile = () => {
  selectedFile.value = null
  uploadProgress.value = 0
  uploading.value = false
  error.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('file-removed')
}

const uploadFile = async () => {
  if (!selectedFile.value) return
  
  uploading.value = true
  uploadProgress.value = 0
  
  // Simulate upload progress
  const interval = setInterval(() => {
    if (uploadProgress.value < 90) {
      uploadProgress.value += 10
      emit('upload-progress', uploadProgress.value)
    }
  }, 200)
  
  try {
    // This would be replaced with actual upload logic
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    clearInterval(interval)
    uploadProgress.value = 100
    emit('upload-progress', 100)
    emit('upload-complete', selectedFile.value)
    
  } catch (err) {
    clearInterval(interval)
    error.value = 'Upload failed. Please try again.'
    emit('error', err)
  } finally {
    uploading.value = false
  }
}

// Utility functions
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileName = (filePath) => {
  if (!filePath) return 'Unknown file'
  return filePath.split('/').pop() || filePath
}

// Expose methods for parent component
defineExpose({
  uploadFile,
  removeFile,
  triggerFileInput
})
</script>

<style scoped>
.upload-zone {
  transition: all 0.3s ease;
  cursor: pointer;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.upload-zone:hover {
  border-color: #0d6efd !important;
}

.upload-zone.border-primary {
  background-color: rgba(13, 110, 253, 0.1);
}

.upload-zone.border-success {
  background-color: rgba(25, 135, 84, 0.1);
}

.upload-zone.border-danger {
  background-color: rgba(220, 53, 69, 0.1);
}

.progress {
  height: 8px;
}
</style>
