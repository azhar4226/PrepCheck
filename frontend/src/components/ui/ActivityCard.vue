<template>
  <div class="activity-card">
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">
          <i v-if="icon" :class="[icon, 'me-2']"></i>
          {{ title }}
        </h5>
        <div v-if="$slots.actions" class="card-actions">
          <slot name="actions"></slot>
        </div>
      </div>
      <div class="card-body">
        <!-- Empty State -->
        <div v-if="items.length === 0" class="text-center text-muted py-3">
          <slot name="empty">
            <i :class="[emptyIcon, 'fs-1 mb-3 opacity-50']"></i>
            <p>{{ emptyMessage }}</p>
            <slot name="empty-action"></slot>
          </slot>
        </div>

        <!-- Activity List -->
        <div v-else>
          <div class="list-group list-group-flush">
            <div 
              v-for="(item, index) in items" 
              :key="item.id || index" 
              class="list-group-item"
              :class="{ 'list-group-item-action': item.clickable }"
              @click="item.clickable && handleItemClick(item)"
            >
              <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                  <slot name="item" :item="item" :index="index">
                    <h6 class="mb-1">{{ item.title }}</h6>
                    <p class="mb-1 text-muted">{{ item.subtitle }}</p>
                    <small class="text-muted">{{ formatTimestamp(item.timestamp) }}</small>
                  </slot>
                </div>
                <div class="item-badge">
                  <slot name="badge" :item="item">
                    <span 
                      v-if="item.badge" 
                      class="badge" 
                      :class="getBadgeClass(item)"
                    >
                      {{ item.badge }}
                    </span>
                  </slot>
                </div>
              </div>
            </div>
          </div>

          <!-- Show More Button -->
          <div v-if="showMore && items.length >= limit" class="text-center mt-3">
            <button class="btn btn-outline-primary btn-sm" @click="$emit('show-more')">
              <i class="bi bi-chevron-down me-1"></i>
              Show More
            </button>
          </div>
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
  icon: {
    type: String,
    default: 'bi bi-list'
  },
  items: {
    type: Array,
    default: () => []
  },
  emptyMessage: {
    type: String,
    default: 'No items available'
  },
  emptyIcon: {
    type: String,
    default: 'bi bi-inbox'
  },
  showMore: {
    type: Boolean,
    default: false
  },
  limit: {
    type: Number,
    default: 5
  },
  dateFormat: {
    type: String,
    default: 'relative' // 'relative', 'absolute', or 'custom'
  }
})

const emit = defineEmits(['item-click', 'show-more'])

const handleItemClick = (item) => {
  emit('item-click', item)
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (props.dateFormat === 'relative') {
    if (diffMinutes < 1) return 'Just now'
    if (diffMinutes < 60) return `${diffMinutes}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  } else {
    return date.toLocaleString()
  }
}

const getBadgeClass = (item) => {
  if (item.badgeClass) return item.badgeClass
  
  // Auto-determine badge class based on content
  const badge = item.badge?.toString().toLowerCase()
  if (!badge) return 'bg-secondary'
  
  if (badge.includes('success') || badge.includes('completed') || badge.includes('passed')) return 'bg-success'
  if (badge.includes('warning') || badge.includes('pending')) return 'bg-warning'
  if (badge.includes('danger') || badge.includes('failed') || badge.includes('error')) return 'bg-danger'
  if (badge.includes('info') || badge.includes('started')) return 'bg-info'
  
  // Score-based badges
  const score = parseInt(badge)
  if (!isNaN(score)) {
    if (score >= 80) return 'bg-success'
    if (score >= 60) return 'bg-warning'
    if (score < 60) return 'bg-danger'
  }
  
  return 'bg-secondary'
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: between;
  align-items: center;
}

.card-actions {
  margin-left: auto;
}

.list-group-item-action {
  cursor: pointer;
}

.list-group-item-action:hover {
  background-color: var(--color-gray-50);
}

.item-badge {
  flex-shrink: 0;
  margin-left: var(--spacing-2);
}
</style>
