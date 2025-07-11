<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <!-- Header -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2 class="mb-1">⚖️ Chapter Weightage Management</h2>
            <p class="text-muted mb-0">Configure weightage distribution for mock test generation across chapters</p>
          </div>
          <div class="d-flex gap-2">
            <button 
              class="btn btn-outline-primary"
              @click="refreshData"
            >
              <i class="bi bi-arrow-clockwise me-1"></i>
              Refresh
            </button>
          </div>
        </div>

        <!-- Subject Selection -->
        <div class="card shadow-sm mb-4">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label">Select Subject</label>
                <select 
                  v-model="selectedSubject" 
                  class="form-select" 
                  @change="loadChapters"
                  :disabled="loading"
                >
                  <option value="">{{ loading ? 'Loading subjects...' : 'Choose a subject' }}</option>
                  <option 
                    v-for="subject in subjects" 
                    :key="subject.id" 
                    :value="subject.id"
                  >
                    {{ subject.name }}
                  </option>
                </select>
                <div v-if="subjects.length === 0 && !loading" class="text-danger small mt-1">
                  No subjects available. Please add subjects first.
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Chapter Weightages -->
        <div v-if="selectedSubject" class="card shadow-sm">
          <div class="card-header bg-light">
            <h5 class="card-title mb-0">Chapter Weightages</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="chapters.length === 0" class="text-center py-4">
              <p class="text-muted mb-0">No chapters found for this subject</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th style="width: 50%">Chapter Name</th>
                    <th style="width: 50%">Weightage (%)</th>
                    <!-- <th style="width: 30%">Questions per Test</th> -->
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="chapter in chapters" :key="chapter.id">
                    <td>{{ chapter.name }}</td>
                    <td>
                      <div class="d-flex align-items-center gap-2">
                        <input 
                          type="number" 
                          class="form-control form-control-sm"
                          v-model.number="chapter.weightage"
                          min="0"
                          max="100"
                          @change="validateWeightages"
                        >
                        <span class="text-muted">%</span>
                      </div>
                    </td>
                    <!-- <td>
                      <input 
                        type="number" 
                        class="form-control form-control-sm"
                        v-model.number="chapter.questions_per_test"
                        min="0"
                        max="50"
                      >
                    </td> -->
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td><strong>Total</strong></td>
                    <td>
                      <strong :class="{ 'text-danger': totalWeightage !== 100 }">
                        {{ totalWeightage }}%
                      </strong>
                    </td>
                    <!-- <td>
                      <strong>{{ totalQuestions }} questions</strong>
                    </td> -->
                  </tr>
                </tfoot>
              </table>
            </div>

            <!-- Save Button -->
            <div class="mt-4 d-flex justify-content-end">
              <button 
                class="btn btn-primary" 
                @click="saveWeightages"
                :disabled="loading || totalWeightage !== 100"
              >
                <i class="bi bi-save me-1"></i>
                Save Changes
              </button>
            </div>
          </div>
        </div>

        <!-- No Subject Selected Message -->
        <div v-else class="card shadow-sm">
          <div class="card-body text-center py-5">
            <i class="bi bi-arrow-up-circle display-4 text-muted"></i>
            <p class="text-muted mt-3">Please select a subject to manage chapter weightages</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useNotifications } from '@/composables/useNotifications'
import ugcNetService from '@/services/ugcNetService'
import adminService from '@/services/adminService'

export default {
  name: 'UGCNetManagement',
  setup() {
    const { success: showSuccess, error: showError } = useNotifications()

    // State
    const loading = ref(false)
    const subjects = ref([])
    const chapters = ref([])
    const selectedSubject = ref('')

    // Computed
    const totalWeightage = computed(() => {
      return chapters.value.reduce((sum, chapter) => sum + (chapter.weightage || 0), 0)
    })

    const totalQuestions = computed(() => {
      return chapters.value.reduce((sum, chapter) => sum + (chapter.questions_per_test || 0), 0)
    })

    // Methods
    const loadSubjects = async () => {
      try {
        loading.value = true
        const response = await ugcNetService.getSubjects()
        console.log('Subjects API response:', response)
        
        if (response.success && Array.isArray(response.data)) {
          subjects.value = response.data
        } else if (response.success && Array.isArray(response.data.subjects)) {
          subjects.value = response.data.subjects
        } else {
          console.error('Unexpected subjects response format:', response)
          showError('Failed to load subjects data')
          subjects.value = []
        }
      } catch (err) {
        console.error('Failed to load subjects:', err)
        showError('Failed to load subjects')
        subjects.value = []
      } finally {
        loading.value = false
      }
    }

    const loadChapters = async () => {
      if (!selectedSubject.value) {
        chapters.value = []
        return
      }

      loading.value = true
      try {
        const response = await adminService.getChapters(selectedSubject.value)
        chapters.value = (response || []).map(chapter => ({
          ...chapter,
          weightage: chapter.weightage ?? 0,
          estimated_questions: chapter.estimated_questions ?? 0,
          chapter_order: chapter.chapter_order ?? 0
        }))
      } catch (err) {
        console.error('Failed to load chapters:', err)
        showError('Failed to load chapters')
        chapters.value = []
      } finally {
        loading.value = false
      }
    }

    const validateWeightages = () => {
      // Ensure weightages are between 0 and 100
      chapters.value = chapters.value.map(chapter => ({
        ...chapter,
        weightage: Math.min(100, Math.max(0, chapter.weightage || 0))
      }))
    }

    const saveWeightages = async () => {
      if (totalWeightage.value !== 100) {
        showError('Total weightage must equal 100%')
        return
      }

      loading.value = true
      try {
        await adminService.updateSubjectChapterWeightages(selectedSubject.value, {
          chapters: chapters.value.map(chapter => ({
            id: chapter.id,
            weightage: chapter.weightage,
            questions_per_test: chapter.questions_per_test
          }))
        })
        showSuccess('Chapter weightages updated successfully')
      } catch (err) {
        console.error('Failed to save weightages:', err)
        showError('Failed to update chapter weightages')
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      if (selectedSubject.value) {
        loadChapters()
      }
    }

    // Lifecycle
    onMounted(() => {
      loadSubjects()
    })

    return {
      loading,
      subjects,
      chapters,
      selectedSubject,
      totalWeightage,
      totalQuestions,
      loadChapters,
      validateWeightages,
      saveWeightages,
      refreshData
    }
  }
}
</script>

<style scoped>
.table > :not(caption) > * > * {
  padding: 0.75rem;
}

.form-control-sm {
  width: 80px;
}
</style>
