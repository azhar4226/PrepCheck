<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <div class="modal-icon" :class="iconClass">
          <i :class="icon"></i>
        </div>
        <h4 class="modal-title">{{ title }}</h4>
        <button class="modal-close" @click="closeModal" aria-label="Close">
          <i class="bi bi-x"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <p class="modal-message">{{ message }}</p>
        <div v-if="details" class="modal-details">
          <i class="bi bi-info-circle me-2"></i>{{ details }}
        </div>
      </div>
      
      <div class="modal-footer">
        <button 
          v-if="type === 'confirm'"
          class="btn btn-outline-secondary"
          @click="handleCancel"
        >
          <i class="bi bi-x-circle me-1"></i>{{ cancelText }}
        </button>
        <button 
          class="btn"
          :class="buttonClass"
          @click="handleConfirm"
        >
          <i :class="buttonIcon" class="me-1"></i>{{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'NotificationModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'success', // success, error, warning, info, confirm
      validator: value => ['success', 'error', 'warning', 'info', 'confirm'].includes(value)
    },
    title: {
      type: String,
      default: ''
    },
    message: {
      type: String,
      required: true
    },
    details: {
      type: String,
      default: ''
    },
    confirmText: {
      type: String,
      default: 'OK'
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },
    autoClose: {
      type: Number,
      default: 0 // 0 means no auto close
    }
  },
  emits: ['close', 'confirm', 'cancel'],
  setup(props, { emit }) {
    const autoCloseTimer = ref(null)

    const icon = computed(() => {
      switch (props.type) {
        case 'success':
          return 'bi bi-check-circle-fill'
        case 'error':
          return 'bi bi-x-circle-fill'
        case 'warning':
          return 'bi bi-exclamation-triangle-fill'
        case 'info':
          return 'bi bi-info-circle-fill'
        case 'confirm':
          return 'bi bi-question-circle-fill'
        default:
          return 'bi bi-info-circle-fill'
      }
    })

    const iconClass = computed(() => {
      switch (props.type) {
        case 'success':
          return 'icon-success'
        case 'error':
          return 'icon-error'
        case 'warning':
          return 'icon-warning'
        case 'info':
          return 'icon-info'
        case 'confirm':
          return 'icon-confirm'
        default:
          return 'icon-info'
      }
    })

    const buttonClass = computed(() => {
      switch (props.type) {
        case 'success':
          return 'btn-success'
        case 'error':
          return 'btn-danger'
        case 'warning':
          return 'btn-warning'
        case 'info':
          return 'btn-primary'
        case 'confirm':
          return 'btn-primary'
        default:
          return 'btn-primary'
      }
    })

    const buttonIcon = computed(() => {
      switch (props.type) {
        case 'success':
          return 'bi bi-check-circle'
        case 'error':
          return 'bi bi-exclamation-circle'
        case 'warning':
          return 'bi bi-exclamation-triangle'
        case 'info':
          return 'bi bi-info-circle'
        case 'confirm':
          return 'bi bi-check'
        default:
          return 'bi bi-check'
      }
    })

    const closeModal = () => {
      if (autoCloseTimer.value) {
        clearTimeout(autoCloseTimer.value)
        autoCloseTimer.value = null
      }
      emit('close')
    }

    const handleOverlayClick = () => {
      if (props.type !== 'confirm') {
        closeModal()
      }
    }

    const handleConfirm = () => {
      emit('confirm')
      closeModal()
    }

    const handleCancel = () => {
      emit('cancel')
      closeModal()
    }

    // Auto close functionality
    watch(() => props.show, (newValue) => {
      if (newValue && props.autoClose > 0 && props.type !== 'confirm') {
        autoCloseTimer.value = setTimeout(() => {
          closeModal()
        }, props.autoClose)
      }
    })

    // Handle escape key
    const handleKeydown = (event) => {
      if (event.key === 'Escape' && props.show) {
        if (props.type === 'confirm') {
          handleCancel()
        } else {
          closeModal()
        }
      }
    }

    // Add/remove event listeners
    watch(() => props.show, (newValue) => {
      if (newValue) {
        document.addEventListener('keydown', handleKeydown)
        document.body.style.overflow = 'hidden'
      } else {
        document.removeEventListener('keydown', handleKeydown)
        document.body.style.overflow = ''
      }
    })

    return {
      icon,
      iconClass,
      buttonClass,
      buttonIcon,
      closeModal,
      handleOverlayClick,
      handleConfirm,
      handleCancel
    }
  }
}
</script>

<style scoped>
/* Use Bootstrap's consistent styling approach */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(var(--bs-dark-rgb, 33, 37, 41), 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1055; /* Bootstrap modal z-index + 5 */
  animation: fadeIn 0.15s ease-out;
  backdrop-filter: blur(2px);
}

.modal-container {
  background: var(--bs-body-bg, #ffffff);
  border: 1px solid var(--bs-border-color, #dee2e6);
  border-radius: var(--bs-border-radius-lg, 0.5rem);
  box-shadow: 0 0.5rem 1rem rgba(var(--bs-dark-rgb, 0, 0, 0), 0.15);
  max-width: 32rem;
  width: 90%;
  max-height: 90vh;
  overflow: hidden;
  animation: slideIn 0.15s ease-out;
  color: var(--bs-body-color, #212529);
}

.modal-header {
  display: flex;
  align-items: center;
  padding: 1.25rem 1.5rem 1rem;
  border-bottom: 1px solid var(--bs-border-color, #dee2e6);
  background: linear-gradient(135deg, var(--bs-light, #f8f9fa) 0%, var(--bs-body-bg, #ffffff) 100%);
}

.modal-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  font-size: 1.25rem;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.modal-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.1) 100%);
  border-radius: 50%;
}

.icon-success {
  background: linear-gradient(135deg, var(--bs-success, #198754) 0%, #20c997 100%);
  color: white;
  box-shadow: 0 0.25rem 0.5rem rgba(var(--bs-success-rgb, 25, 135, 84), 0.3);
}

.icon-error {
  background: linear-gradient(135deg, var(--bs-danger, #dc3545) 0%, #e74c3c 100%);
  color: white;
  box-shadow: 0 0.25rem 0.5rem rgba(var(--bs-danger-rgb, 220, 53, 69), 0.3);
}

.icon-warning {
  background: linear-gradient(135deg, var(--bs-warning, #ffc107) 0%, #f39c12 100%);
  color: white;
  box-shadow: 0 0.25rem 0.5rem rgba(var(--bs-warning-rgb, 255, 193, 7), 0.3);
}

.icon-info {
  background: linear-gradient(135deg, var(--bs-info, #0dcaf0) 0%, #17a2b8 100%);
  color: white;
  box-shadow: 0 0.25rem 0.5rem rgba(var(--bs-info-rgb, 13, 202, 240), 0.3);
}

.icon-confirm {
  background: linear-gradient(135deg, var(--bs-primary, #0d6efd) 0%, #6f42c1 100%);
  color: white;
  box-shadow: 0 0.25rem 0.5rem rgba(var(--bs-primary-rgb, 13, 110, 253), 0.3);
}

.modal-title {
  flex: 1;
  margin: 0;
  font-size: 1.375rem;
  font-weight: 600;
  color: var(--bs-heading-color, var(--bs-body-color, #212529));
  line-height: 1.3;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--bs-secondary, #6c757d);
  cursor: pointer;
  padding: 0.375rem;
  border-radius: var(--bs-border-radius, 0.375rem);
  transition: all 0.15s ease-in-out;
  flex-shrink: 0;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: var(--bs-danger, #dc3545);
  background: var(--bs-danger-bg-subtle, #f8d7da);
  transform: scale(1.1);
}

.modal-body {
  padding: 1.5rem;
  background: var(--bs-body-bg, #ffffff);
}

.modal-message {
  margin: 0;
  font-size: 1.1rem;
  line-height: 1.6;
  color: var(--bs-body-color, #212529);
  font-weight: 400;
}

.modal-details {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--bs-light, #f8f9fa);
  border: 1px solid var(--bs-border-color, #dee2e6);
  border-radius: var(--bs-border-radius, 0.375rem);
  font-size: 0.9rem;
  color: var(--bs-secondary, #6c757d);
  border-left: 0.25rem solid var(--bs-primary, #0d6efd);
  display: flex;
  align-items: flex-start;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem 1.25rem;
  border-top: 1px solid var(--bs-border-color, #dee2e6);
  background: linear-gradient(135deg, var(--bs-body-bg, #ffffff) 0%, var(--bs-light, #f8f9fa) 100%);
}

/* Enhanced Bootstrap button styling */
.btn {
  display: inline-block;
  padding: 0.5rem 1.25rem;
  margin-bottom: 0;
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.5;
  text-align: center;
  text-decoration: none;
  vertical-align: middle;
  cursor: pointer;
  border: 1px solid transparent;
  border-radius: var(--bs-border-radius, 0.375rem);
  transition: all 0.15s ease-in-out;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn:hover::before {
  left: 100%;
}

.btn-primary {
  color: #fff;
  background: linear-gradient(135deg, var(--bs-primary, #0d6efd) 0%, #0b5ed7 100%);
  border-color: var(--bs-primary, #0d6efd);
  box-shadow: 0 0.125rem 0.25rem rgba(var(--bs-primary-rgb, 13, 110, 253), 0.3);
}

.btn-primary:hover {
  color: #fff;
  background: linear-gradient(135deg, #0b5ed7 0%, #0a58ca 100%);
  border-color: #0a58ca;
  transform: translateY(-1px);
  box-shadow: 0 0.25rem 0.5rem rgba(var(--bs-primary-rgb, 13, 110, 253), 0.4);
}

.btn-success {
  color: #fff;
  background: linear-gradient(135deg, var(--bs-success, #198754) 0%, #20c997 100%);
  border-color: var(--bs-success, #198754);
  box-shadow: 0 0.125rem 0.25rem rgba(var(--bs-success-rgb, 25, 135, 84), 0.3);
}

.btn-success:hover {
  color: #fff;
  background: linear-gradient(135deg, #157347 0%, #1aa179 100%);
  border-color: #146c43;
  transform: translateY(-1px);
  box-shadow: 0 0.25rem 0.5rem rgba(var(--bs-success-rgb, 25, 135, 84), 0.4);
}

.btn-danger {
  color: #fff;
  background: linear-gradient(135deg, var(--bs-danger, #dc3545) 0%, #e74c3c 100%);
  border-color: var(--bs-danger, #dc3545);
  box-shadow: 0 0.125rem 0.25rem rgba(var(--bs-danger-rgb, 220, 53, 69), 0.3);
}

.btn-danger:hover {
  color: #fff;
  background: linear-gradient(135deg, #bb2d3b 0%, #c0392b 100%);
  border-color: #b02a37;
  transform: translateY(-1px);
  box-shadow: 0 0.25rem 0.5rem rgba(var(--bs-danger-rgb, 220, 53, 69), 0.4);
}

.btn-warning {
  color: #000;
  background: linear-gradient(135deg, var(--bs-warning, #ffc107) 0%, #f39c12 100%);
  border-color: var(--bs-warning, #ffc107);
  box-shadow: 0 0.125rem 0.25rem rgba(var(--bs-warning-rgb, 255, 193, 7), 0.3);
}

.btn-warning:hover {
  color: #000;
  background: linear-gradient(135deg, #ffca2c 0%, #e67e22 100%);
  border-color: #ffc720;
  transform: translateY(-1px);
  box-shadow: 0 0.25rem 0.5rem rgba(var(--bs-warning-rgb, 255, 193, 7), 0.4);
}

.btn-outline-secondary {
  color: var(--bs-secondary, #6c757d);
  border-color: var(--bs-secondary, #6c757d);
  background-color: transparent;
}

.btn-outline-secondary:hover {
  color: #fff;
  background: linear-gradient(135deg, var(--bs-secondary, #6c757d) 0%, #5a6268 100%);
  border-color: var(--bs-secondary, #6c757d);
  transform: translateY(-1px);
  box-shadow: 0 0.25rem 0.5rem rgba(var(--bs-secondary-rgb, 108, 117, 125), 0.3);
}

.btn:focus {
  outline: 0;
  box-shadow: 0 0 0 0.25rem rgba(var(--bs-primary-rgb, 13, 110, 253), 0.25);
}

.btn:active {
  transform: translateY(0);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateY(-1rem) scale(0.95);
    opacity: 0;
  }
  to {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

/* Responsive design */
@media (max-width: 576px) {
  .modal-container {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1rem;
  }
  
  .modal-footer {
    flex-direction: column-reverse;
    gap: 0.5rem;
  }
  
  .modal-footer .btn {
    width: 100%;
  }
  
  .modal-icon {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1.1rem;
  }
  
  .modal-title {
    font-size: 1.25rem;
  }
}
</style>
