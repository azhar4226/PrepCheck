// Base Modal Component
<template>
  <div class="modal fade show d-block" :style="modalStyle" @click.self="handleBackdropClick">
    <div class="modal-dialog" :class="modalSize">
      <div class="modal-content">
        <!-- Header -->
        <div class="modal-header" v-if="showHeader">
          <h5 class="modal-title">
            <i v-if="icon" :class="icon" class="me-2"></i>
            {{ title }}
          </h5>
          <button 
            v-if="showCloseButton" 
            type="button" 
            class="btn-close" 
            @click="$emit('close')"
          ></button>
        </div>
        
        <!-- Body -->
        <div class="modal-body">
          <slot></slot>
        </div>
        
        <!-- Footer -->
        <div class="modal-footer" v-if="showFooter">
          <slot name="footer">
            <button type="button" class="btn btn-secondary" @click="$emit('close')">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="$emit('confirm')"
              :disabled="confirmDisabled"
            >
              {{ confirmText }}
            </button>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: String,
  icon: String,
  size: {
    type: String,
    default: 'lg',
    validator: (value) => ['sm', 'lg', 'xl'].includes(value)
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  showCloseButton: {
    type: Boolean,
    default: true
  },
  backdropDismiss: {
    type: Boolean,
    default: true
  },
  confirmText: {
    type: String,
    default: 'Save'
  },
  confirmDisabled: {
    type: Boolean,
    default: false
  },
  zIndex: {
    type: Number,
    default: 1050
  }
})

const emit = defineEmits(['close', 'confirm'])

const modalStyle = computed(() => ({
  backgroundColor: 'rgba(0,0,0,0.5)',
  zIndex: props.zIndex
}))

const modalSize = computed(() => {
  const sizeMap = {
    sm: 'modal-sm',
    lg: 'modal-lg',
    xl: 'modal-xl'
  }
  return sizeMap[props.size] || 'modal-lg'
})

const handleBackdropClick = () => {
  if (props.backdropDismiss) {
    emit('close')
  }
}
</script>

<style scoped>
.modal {
  display: block !important;
}
</style>
