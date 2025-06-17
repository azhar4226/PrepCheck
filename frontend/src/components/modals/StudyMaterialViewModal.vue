<template>
  <div class="modal fade" id="studyMaterialViewModal" tabindex="-1" ref="viewModal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-eye me-2"></i>View Study Material
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        
        <div class="modal-body" v-if="material">
          <!-- Material Info -->
          <div class="row mb-4">
            <div class="col-md-8">
              <h4 class="mb-2">{{ material.title }}</h4>
              <p class="text-muted mb-3">{{ material.description }}</p>
            </div>
            <div class="col-md-4 text-end">
              <span 
                class="badge fs-6 mb-2"
                :class="{
                  'bg-info': material.material_type === 'text',
                  'bg-success': material.material_type === 'document',
                  'bg-warning': material.material_type === 'video',
                  'bg-danger': material.material_type === 'audio',
                  'bg-primary': material.material_type === 'link'
                }"
              >
                <i :class="getTypeIcon(material.material_type)" class="me-1"></i>
                {{ material.material_type.charAt(0).toUpperCase() + material.material_type.slice(1) }}
              </span>
              <div class="small text-muted">
                <div><strong>Subject:</strong> {{ material.subject?.name || 'N/A' }}</div>
                <div><strong>Chapter:</strong> {{ material.chapter?.name || 'N/A' }}</div>
                <div><strong>Status:</strong> 
                  <span :class="material.is_active ? 'text-success' : 'text-danger'">
                    {{ material.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
                <div><strong>Created:</strong> {{ formatDate(material.created_at) }}</div>
              </div>
            </div>
          </div>

          <!-- Material Content -->
          <div class="material-content">
            <!-- Text Content -->
            <div v-if="material.material_type === 'text'" class="card">
              <div class="card-header">
                <h6 class="mb-0"><i class="bi bi-file-text me-2"></i>Text Content</h6>
              </div>
              <div class="card-body">
                <div class="text-content" v-html="formatTextContent(material.content)"></div>
              </div>
            </div>

            <!-- Document/File -->
            <div v-else-if="['document', 'video', 'audio'].includes(material.material_type)" class="card">
              <div class="card-header">
                <h6 class="mb-0">
                  <i :class="getTypeIcon(material.material_type)" class="me-2"></i>
                  File Information
                </h6>
              </div>
              <div class="card-body">
                <div v-if="material.file_path" class="d-flex align-items-center justify-content-between">
                  <div>
                    <div class="fw-bold">{{ getFileName(material.file_path) }}</div>
                    <small class="text-muted">File path: {{ material.file_path }}</small>
                  </div>
                  <div>
                    <button 
                      class="btn btn-outline-primary btn-sm me-2"
                      @click="downloadFile"
                      :disabled="downloading"
                    >
                      <i class="bi bi-download me-1"></i>
                      {{ downloading ? 'Downloading...' : 'Download' }}
                    </button>
                    <button 
                      v-if="material.material_type === 'document'"
                      class="btn btn-outline-secondary btn-sm"
                      @click="previewFile"
                    >
                      <i class="bi bi-eye me-1"></i>Preview
                    </button>
                  </div>
                </div>
                <div v-else class="text-muted">
                  <i class="bi bi-exclamation-triangle me-1"></i>
                  No file associated with this material
                </div>
              </div>
            </div>

            <!-- Link Content -->
            <div v-else-if="material.material_type === 'link'" class="card">
              <div class="card-header">
                <h6 class="mb-0"><i class="bi bi-link-45deg me-2"></i>External Link</h6>
              </div>
              <div class="card-body">
                <div v-if="material.content" class="d-flex align-items-center justify-content-between">
                  <div>
                    <div class="fw-bold">{{ material.content }}</div>
                    <small class="text-muted">External resource link</small>
                  </div>
                  <div>
                    <a 
                      :href="material.content" 
                      target="_blank" 
                      class="btn btn-outline-primary btn-sm"
                      rel="noopener noreferrer"
                    >
                      <i class="bi bi-box-arrow-up-right me-1"></i>Open Link
                    </a>
                  </div>
                </div>
                <div v-else class="text-muted">
                  <i class="bi bi-exclamation-triangle me-1"></i>
                  No link provided
                </div>
              </div>
            </div>
          </div>

          <!-- Additional Notes -->
          <div v-if="material.additional_notes" class="card mt-3">
            <div class="card-header">
              <h6 class="mb-0"><i class="bi bi-sticky me-2"></i>Additional Notes</h6>
            </div>
            <div class="card-body">
              <div v-html="formatTextContent(material.additional_notes)"></div>
            </div>
          </div>

          <!-- File Preview Modal (for documents) -->
          <div v-if="showPreview" class="mt-3">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0"><i class="bi bi-file-earmark me-2"></i>File Preview</h6>
                <button class="btn btn-sm btn-outline-secondary" @click="closePreview">
                  <i class="bi bi-x"></i>
                </button>
              </div>
              <div class="card-body">
                <iframe 
                  v-if="previewUrl"
                  :src="previewUrl" 
                  class="w-100"
                  style="height: 500px; border: none;"
                ></iframe>
                <div v-else class="text-center text-muted py-5">
                  <i class="bi bi-file-earmark-x fs-1"></i>
                  <div>Unable to preview this file type</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            Close
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="editMaterial"
          >
            <i class="bi bi-pencil me-1"></i>Edit Material
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap'

export default {
  name: 'StudyMaterialViewModal',
  props: {
    material: {
      type: Object,
      default: null
    }
  },
  emits: ['edit-material'],
  data() {
    return {
      modal: null,
      downloading: false,
      showPreview: false,
      previewUrl: null
    }
  },
  mounted() {
    this.modal = new Modal(this.$refs.viewModal)
  },
  methods: {
    show() {
      if (this.modal) {
        this.modal.show()
      }
    },
    hide() {
      if (this.modal) {
        this.modal.hide()
      }
    },
    getTypeIcon(type) {
      const iconMap = {
        text: 'bi-file-text',
        document: 'bi-file-earmark-pdf',
        video: 'bi-play-circle',
        audio: 'bi-volume-up',
        link: 'bi-link-45deg'
      }
      return iconMap[type] || 'bi-file'
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    formatTextContent(content) {
      if (!content) return ''
      // Simple formatting - convert line breaks to <br> and preserve formatting
      return content.replace(/\n/g, '<br>')
    },
    getFileName(filePath) {
      if (!filePath) return 'Unknown file'
      return filePath.split('/').pop() || filePath
    },
    async downloadFile() {
      if (!this.material?.file_path) return
      
      this.downloading = true
      try {
        // Create a download link
        const link = document.createElement('a')
        link.href = `/api/admin/study-materials/${this.material.id}/download`
        link.download = this.getFileName(this.material.file_path)
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        console.error('Download failed:', error)
        alert('Failed to download file. Please try again.')
      } finally {
        this.downloading = false
      }
    },
    previewFile() {
      if (!this.material?.file_path) return
      
      // Generate preview URL
      this.previewUrl = `/api/admin/study-materials/${this.material.id}/preview`
      this.showPreview = true
    },
    closePreview() {
      this.showPreview = false
      this.previewUrl = null
    },
    editMaterial() {
      this.$emit('edit-material', this.material)
      this.hide()
    }
  }
}
</script>

<style scoped>
.text-content {
  max-height: 400px;
  overflow-y: auto;
  line-height: 1.6;
  white-space: pre-wrap;
}

.material-content .card {
  border-left: 4px solid var(--bs-primary);
}

.material-content .card-header {
  background-color: var(--bs-light);
  border-bottom: 1px solid var(--bs-border-color);
}

.badge {
  font-size: 0.75rem;
}

@media (max-width: 768px) {
  .modal-dialog {
    margin: 1rem;
  }
  
  .text-content {
    max-height: 300px;
  }
}
</style>
