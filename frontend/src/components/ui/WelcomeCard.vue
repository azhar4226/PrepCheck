<template>
  <div class="welcome-section">
    <div class="card">
      <div class="card-body">
        <h4 class="card-title">
          <i v-if="icon" :class="[icon, iconClass, 'me-2']"></i>
          {{ title }}
        </h4>
        <p class="card-text text-muted">
          {{ subtitle }}
        </p>
        <div v-if="$slots.default" class="mt-3">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: ''
  },
  iconClass: {
    type: String,
    default: 'text-primary'
  }
})

defineSlots()
</script>

<style scoped>
.welcome-section {
  margin-bottom: 1rem;
  border-radius: 0.5rem;
  background-color: var(--bg-color);

}
</style>
