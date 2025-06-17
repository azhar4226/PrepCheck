<template>
  <div class="page-header" :class="{ 'has-actions': $slots.actions }">
    <div class="container-fluid">
      <div class="row">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 class="h2 text-primary">
                <i v-if="icon" :class="icon" class="me-2"></i>
                {{ title }}
              </h1>
              <p v-if="subtitle" class="text-muted mb-0">{{ subtitle }}</p>
            </div>
            <div v-if="$slots.actions" class="d-flex gap-2">
              <slot name="actions"></slot>
            </div>
          </div>
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
    default: ''
  },
  icon: {
    type: String,
    default: ''
  }
})

defineSlots()
</script>

<style scoped>
.page-header {
  padding: var(--spacing-4) 0;
}

@media (max-width: 768px) {
  .page-header {
    padding: var(--spacing-3) 0;
  }
  
  .d-flex {
    flex-direction: column;
    gap: var(--spacing-3);
  }
  
  .d-flex .d-flex {
    flex-direction: row;
  }
}
</style>
