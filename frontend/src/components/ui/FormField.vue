// Form Field Component
<template>
  <div class="form-field" :class="fieldClass">
    <label v-if="label" :for="fieldId" class="form-label">
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>
    
    <!-- Text Input -->
    <input 
      v-if="type === 'text' || type === 'email' || type === 'password' || type === 'number'"
      :id="fieldId"
      :type="type"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      class="form-control"
      :class="inputClass"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :min="min"
      :max="max"
      :step="step"
    >
    
    <!-- Textarea -->
    <textarea 
      v-else-if="type === 'textarea'"
      :id="fieldId"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      class="form-control"
      :class="inputClass"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :rows="rows"
    ></textarea>
    
    <!-- Select -->
    <select 
      v-else-if="type === 'select'"
      :id="fieldId"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="form-select"
      :class="inputClass"
      :required="required"
      :disabled="disabled"
    >
      <option v-if="placeholder" value="">{{ placeholder }}</option>
      <option 
        v-for="option in options" 
        :key="option.value" 
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
    
    <!-- Checkbox -->
    <div v-else-if="type === 'checkbox'" class="form-check">
      <input 
        :id="fieldId"
        type="checkbox"
        :checked="modelValue"
        @change="$emit('update:modelValue', $event.target.checked)"
        class="form-check-input"
        :class="inputClass"
        :required="required"
        :disabled="disabled"
      >
      <label v-if="checkboxLabel" :for="fieldId" class="form-check-label">
        {{ checkboxLabel }}
      </label>
    </div>
    
    <!-- Radio Group -->
    <div v-else-if="type === 'radio'" class="radio-group">
      <div 
        v-for="option in options" 
        :key="option.value" 
        class="form-check"
        :class="{ 'form-check-inline': inline }"
      >
        <input 
          :id="`${fieldId}_${option.value}`"
          type="radio"
          :name="fieldId"
          :value="option.value"
          :checked="modelValue === option.value"
          @change="$emit('update:modelValue', option.value)"
          class="form-check-input"
          :required="required"
          :disabled="disabled"
        >
        <label :for="`${fieldId}_${option.value}`" class="form-check-label">
          {{ option.label }}
        </label>
      </div>
    </div>
    
    <!-- Date Input -->
    <input 
      v-else-if="type === 'date'"
      :id="fieldId"
      type="date"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      class="form-control"
      :class="inputClass"
      :required="required"
      :disabled="disabled"
      :min="min"
      :max="max"
    >
    
    <!-- Help Text -->
    <small v-if="helpText" class="form-text text-muted">
      {{ helpText }}
    </small>
    
    <!-- Error Message -->
    <div v-if="error" class="invalid-feedback d-block">
      <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
    </div>
    
    <!-- Success Message -->
    <div v-if="success" class="valid-feedback d-block">
      <i class="bi bi-check-circle me-1"></i>{{ success }}
    </div>
  </div>
</template>

<script setup>
import { computed, useId } from 'vue'

const props = defineProps({
  modelValue: [String, Number, Boolean, Array],
  type: {
    type: String,
    default: 'text',
    validator: (value) => [
      'text', 'email', 'password', 'number', 'textarea', 'select', 
      'checkbox', 'radio', 'date', 'file'
    ].includes(value)
  },
  label: String,
  placeholder: String,
  helpText: String,
  error: String,
  success: String,
  required: Boolean,
  disabled: Boolean,
  readonly: Boolean,
  
  // Input specific props
  min: [String, Number],
  max: [String, Number],
  step: [String, Number],
  rows: {
    type: Number,
    default: 3
  },
  
  // Select/Radio specific props
  options: {
    type: Array,
    default: () => []
  },
  
  // Checkbox specific props
  checkboxLabel: String,
  
  // Radio specific props
  inline: Boolean,
  
  // CSS Classes
  fieldClass: String,
  inputClass: String,
  
  // ID override
  id: String
})

const emit = defineEmits(['update:modelValue'])

// Generate unique ID if not provided
const generatedId = useId()
const fieldId = computed(() => props.id || generatedId)

// Computed input classes
const computedInputClass = computed(() => {
  const classes = [props.inputClass]
  
  if (props.error) {
    classes.push('is-invalid')
  } else if (props.success) {
    classes.push('is-valid')
  }
  
  return classes.filter(Boolean).join(' ')
})
</script>

<style scoped>
.form-field {
  margin-bottom: 1rem;
}

.radio-group .form-check:not(.form-check-inline) {
  margin-bottom: 0.5rem;
}

.radio-group .form-check:last-child {
  margin-bottom: 0;
}

.form-check-inline {
  margin-right: 1rem;
}

/* Focus styles */
.form-control:focus,
.form-select:focus {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

/* Invalid state */
.form-control.is-invalid,
.form-select.is-invalid {
  border-color: #dc3545;
}

.form-control.is-invalid:focus,
.form-select.is-invalid:focus {
  border-color: #dc3545;
  box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
}

/* Valid state */
.form-control.is-valid,
.form-select.is-valid {
  border-color: #198754;
}

.form-control.is-valid:focus,
.form-select.is-valid:focus {
  border-color: #198754;
  box-shadow: 0 0 0 0.2rem rgba(25, 135, 84, 0.25);
}
</style>
