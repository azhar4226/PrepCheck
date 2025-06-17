<template>
  <BaseModal
    :show="show"
    @hide="$emit('hide')"
    title="Attempt Details"
    size="lg"
  >
    <div v-if="attempt">
      <div class="row">
        <div class="col-md-6">
          <h6>Quiz Information</h6>
          <p><strong>Quiz:</strong> {{ attempt.quiz_title }}</p>
          <p><strong>User:</strong> {{ attempt.user_name }}</p>
          <p><strong>Started:</strong> {{ formatDate(attempt.created_at) }}</p>
          <p><strong>Completed:</strong> {{ formatDate(attempt.completed_at) }}</p>
        </div>
        <div class="col-md-6">
          <h6>Results</h6>
          <p><strong>Score:</strong> {{ attempt.score }}%</p>
          <p><strong>Questions:</strong> {{ attempt.total_questions }}</p>
          <p><strong>Correct:</strong> {{ attempt.correct_answers }}</p>
          <p><strong>Time Taken:</strong> {{ formatTime(attempt.time_taken) }}</p>
        </div>
      </div>

      <div class="mt-4" v-if="attempt.answers">
        <h6>Answer Details</h6>
        <div class="table-responsive">
          <table class="table table-sm">
            <thead>
              <tr>
                <th>Question</th>
                <th>User Answer</th>
                <th>Correct Answer</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(answer, index) in attempt.answers" :key="index">
                <td>{{ answer.question_text || `Question ${index + 1}` }}</td>
                <td>{{ answer.user_answer }}</td>
                <td>{{ answer.correct_answer }}</td>
                <td>
                  <span :class="answer.is_correct ? 'text-success' : 'text-danger'">
                    {{ answer.is_correct ? 'Correct' : 'Incorrect' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <template #footer>
      <button type="button" class="btn btn-secondary" @click="$emit('hide')">
        Close
      </button>
    </template>
  </BaseModal>
</template>

<script>
import BaseModal from '@/components/ui/BaseModal.vue'
import { formatDate, formatTime } from '@/services/utils'

export default {
  name: 'AttemptDetailsModal',
  components: {
    BaseModal
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    attempt: {
      type: Object,
      default: null
    }
  },
  emits: ['hide'],
  methods: {
    formatDate,
    formatTime
  }
}
</script>
