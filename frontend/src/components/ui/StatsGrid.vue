<template>
  <div class="stats-grid">
    <div class="row">
      <div 
        v-for="(stat, index) in stats" 
        :key="stat.key || index"
        class="col-md-3 mb-3"
      >
        <StatCard
          :title="stat.title"
          :value="stat.value"
          :subtitle="stat.subtitle"
          :icon="stat.icon"
          :variant="stat.variant || 'primary'"
          :clickable="stat.clickable || false"
          @click="handleStatClick(stat)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import StatCard from '@/components/ui/StatCard.vue'

defineProps({
  stats: {
    type: Array,
    required: true,
    validator: (stats) => {
      return stats.every(stat => 
        stat.title && 
        (stat.value !== undefined) && 
        stat.icon
      )
    }
  }
})

const emit = defineEmits(['stat-click'])

const handleStatClick = (stat) => {
  if (stat.clickable) {
    emit('stat-click', stat)
  }
}
</script>

<style scoped>
.stats-grid {
  margin-bottom: var(--spacing-4);
}
</style>
