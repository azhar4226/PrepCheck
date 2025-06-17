<template>
  <BaseModal
    :show="show"
    @hide="$emit('hide')"
    title="Verify Question Bank"
    size="lg"
  >
    <div v-if="questionBank">
      <div class="alert alert-info">
        <i class="bi bi-info-circle me-2"></i>
        Review and verify the questions in this question bank.
      </div>

      <div class="mb-3">
        <h6>Question Bank Details</h6>
        <p><strong>Title:</strong> {{ questionBank.title }}</p>
        <p><strong>Subject:</strong> {{ questionBank.subject_name }}</p>
        <p><strong>Total Questions:</strong> {{ questionBank.question_count }}</p>
        <p><strong>Status:</strong> 
          <span :class="getStatusClass(questionBank.verification_status)">
            {{ questionBank.verification_status }}
          </span>
        </p>
      </div>

      <div class="mb-3">
        <label class="form-label">Verification Status</label>
        <select v-model="verificationData.status" class="form-select">
          <option value="pending">Pending</option>
          <option value="verified">Verified</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label">Verification Notes</label>
        <textarea 
          v-model="verificationData.notes" 
          class="form-control" 
          rows="4"
          placeholder="Add verification notes..."
        ></textarea>
      </div>

      <div class="mb-3">
        <label class="form-label">Quality Score (1-10)</label>
        <input 
          v-model.number="verificationData.quality_score" 
          type="number" 
          class="form-control" 
          min="1" 
          max="10"
        >
      </div>
    </div>
    
    <template #footer>
      <button type="button" class="btn btn-secondary" @click="$emit('hide')">
        Cancel
      </button>
      <button 
        type="button" 
        class="btn btn-primary" 
        @click="handleVerify"
        :disabled="loading"
      >
        <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
        Update Verification
      </button>
    </template>
  </BaseModal>
</template>

<script>
import { ref, reactive, watch } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'

export default {
  name: 'QuestionBankVerifyModal',
  components: {
    BaseModal
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    questionBank: {
      type: Object,
      default: null
    }
  },
  emits: ['hide', 'verify'],
  setup(props, { emit }) {
    const loading = ref(false)
    const verificationData = reactive({
      status: 'pending',
      notes: '',
      quality_score: 5
    })

    watch(() => props.questionBank, (newVal) => {
      if (newVal) {
        verificationData.status = newVal.verification_status || 'pending'
        verificationData.notes = newVal.verification_notes || ''
        verificationData.quality_score = newVal.quality_score || 5
      }
    })

    const getStatusClass = (status) => {
      switch (status) {
        case 'verified': return 'badge bg-success'
        case 'rejected': return 'badge bg-danger'
        default: return 'badge bg-warning'
      }
    }

    const handleVerify = async () => {
      loading.value = true
      try {
        emit('verify', {
          questionBankId: props.questionBank.id,
          verificationData: { ...verificationData }
        })
      } finally {
        loading.value = false
      }
    }

    return {
      loading,
      verificationData,
      getStatusClass,
      handleVerify
    }
  }
}
</script>
