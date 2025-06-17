<template>
  <div class="stat-card" :class="[variant, { clickable: clickable }]" @click="handleClick">
    <div class="card-body">
      <div class="d-flex justify-content-between">
        <div>
          <h6 class="card-title">{{ title }}</h6>
          <h3 class="mb-0">{{ value }}</h3>
          <small v-if="subtitle" class="subtitle">{{ subtitle }}</small>
        </div>
        <div class="align-self-center">
          <i :class="icon" class="fs-1 opacity-75"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    required: true
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'info', 'danger'].includes(value)
  },
  clickable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.stat-card {
  color: white;
  border-radius: var(--border-radius-lg);
  transition: transform 0.2s ease-in-out;
}

.stat-card.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.success {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card.warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card.info {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card.danger {
  background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  transform: translateY(-2px);
}

.subtitle {
  opacity: 0.8;
}
</style>
