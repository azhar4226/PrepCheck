<template>
  <form @submit.prevent="$emit('submit')">
    <div class="row">
      <div class="col-md-6">
        <FormField
          v-model="localForm.full_name"
          type="text"
          label="Full Name"
          :required="true"
          :error="errors.full_name"
          placeholder="Enter full name"
        />
      </div>
      <div class="col-md-6">
        <FormField
          v-model="localForm.email"
          type="email"
          label="Email Address"
          :required="true"
          :error="errors.email"
          placeholder="Enter email address"
        />
      </div>
    </div>

    <div class="row" v-if="!isEditing">
      <div class="col-md-12">
        <FormField
          v-model="localForm.password"
          type="password"
          label="Password"
          :required="!isEditing"
          :error="errors.password"
          placeholder="Enter password"
        />
      </div>
    </div>

    <div class="row">
      <div class="col-md-6">
        <FormField
          v-model="localForm.is_admin"
          type="checkbox"
          label="Administrator Role"
          checkbox-label="Grant administrator privileges"
          :error="errors.is_admin"
        />
      </div>
      <div class="col-md-6">
        <FormField
          v-model="localForm.is_active"
          type="checkbox"
          label="Account Status"
          checkbox-label="Account is active"
          :error="errors.is_active"
        />
      </div>
    </div>

    <div v-if="isEditing" class="alert alert-info">
      <i class="bi bi-info-circle me-2"></i>
      Leave password field empty to keep current password unchanged.
    </div>
  </form>
</template>

<script setup>
import { computed, watch } from 'vue'
import FormField from '@/components/ui/FormField.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  errors: {
    type: Object,
    default: () => ({})
  },
  isEditing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const localForm = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Watch for changes and emit updates
watch(localForm, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })
</script>

<style scoped>
.alert-info {
  font-size: 0.875rem;
}
</style>
