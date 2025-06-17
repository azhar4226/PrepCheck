<template>
  <div v-if="isVisible" class="loading-overlay" :style="{ zIndex }">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">{{ message }}</span>
    </div>
    <p v-if="showMessage" class="mt-2 text-muted">{{ message }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: 'Loading...'
  },
  showMessage: {
    type: Boolean,
    default: false
  },
  zIndex: {
    type: Number,
    default: 9999
  }
})
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>
