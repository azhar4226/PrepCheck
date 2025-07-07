<template>
  <div class="data-table">
    <!-- Filters Section -->
    <div v-if="showFilters" class="card shadow-sm mb-4">
      <div class="card-body">
        <slot name="filters">
          <div class="row g-3">
            <div v-for="filter in filters" :key="filter.key" class="col-md-3">
              <label class="form-label">{{ filter.label }}</label>
              <select 
                v-if="filter.type === 'select'"
                v-model="filterValues[filter.key]" 
                class="form-select"
                @change="onFilterChange"
              >
                <option value="">{{ filter.placeholder || `All ${filter.label}` }}</option>
                <option 
                  v-for="option in filter.options" 
                  :key="option.value" 
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
              <input 
                v-else
                v-model="filterValues[filter.key]"
                :type="filter.type || 'text'" 
                class="form-control" 
                :placeholder="filter.placeholder"
                @input="onFilterChange"
              >
            </div>
          </div>
        </slot>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">{{ loadingMessage }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle me-2"></i>
      {{ error }}
    </div>

    <!-- Data Table -->
    <div v-else class="card shadow-sm">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead class="table-dark">
              <tr>
                <th 
                  v-for="column in columns" 
                  :key="column.key"
                  :class="{ 'sortable': column.sortable }"
                  @click="column.sortable && toggleSort(column.key)"
                >
                  {{ column.label }}
                  <i 
                    v-if="column.sortable" 
                    class="bi ms-1"
                    :class="getSortIcon(column.key)"
                  ></i>
                </th>
                <th v-if="showActions" width="150">Actions</th>
              </tr>
            </thead>
            <tbody>
              <!-- Debug info -->
              <!-- DEBUG: Data length: {{ data?.length || 0 }}, Paginated length: {{ paginatedData?.length || 0 }} -->
              <tr v-if="paginatedData.length === 0">
                <td :colspan="columns.length + (showActions ? 1 : 0)" class="text-center text-muted py-4">
                  <slot name="empty">
                    <i class="bi bi-inbox fs-1 mb-2 opacity-50"></i>
                    <p class="mb-0">{{ emptyMessage }}</p>
                    <!-- Debug: Raw data: {{ JSON.stringify(data) }} -->
                  </slot>
                </td>
              </tr>
              <tr v-else v-for="(item, index) in paginatedData" :key="item?.id || `item-${index}`">
                <td v-for="column in columns" :key="column.key">
                  <slot :name="`cell-${column.key}`" :item="item" :value="getNestedValue(item, column.key)">
                    {{ formatValue(getNestedValue(item, column.key), column) }}
                  </slot>
                </td>
                <td v-if="showActions">
                  <slot name="actions" :item="item" :index="index">
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="$emit('edit', item)">
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button class="btn btn-outline-danger" @click="$emit('delete', item)">
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                  </slot>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="showPagination && totalPages > 1" class="d-flex justify-content-between align-items-center mt-3">
          <div class="text-muted">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredData.length }} entries
          </div>
          <nav>
            <ul class="pagination pagination-sm mb-0">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link" @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">
                  Previous
                </button>
              </li>
              <li 
                v-for="page in visiblePages" 
                :key="page" 
                class="page-item" 
                :class="{ active: page === currentPage }"
              >
                <button class="page-link" @click="goToPage(page)">{{ page }}</button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link" @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">
                  Next
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, toRef } from 'vue'
import { useTable } from '@/composables/useTable.js'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  columns: {
    type: Array,
    required: true
  },
  filters: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  loadingMessage: {
    type: String,
    default: 'Loading data...'
  },
  emptyMessage: {
    type: String,
    default: 'No data available'
  },
  showFilters: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  pageSize: {
    type: Number,
    default: 10
  },
  enableFrontendFiltering: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['edit', 'delete', 'filter-change'])

const filterValues = ref({})

// Initialize filter values
onMounted(() => {
  props.filters.forEach(filter => {
    filterValues.value[filter.key] = ''
  })
})

// Make data reactive
const reactiveData = toRef(props, 'data')

const {
  currentPage,
  sortBy,
  sortDesc,
  paginatedData,
  filteredData,
  totalPages,
  startIndex,
  endIndex,
  visiblePages,
  goToPage,
  toggleSort
} = useTable(reactiveData, {
  pageSize: props.pageSize,
  filters: filterValues,
  enableFrontendFiltering: props.enableFrontendFiltering
})

const getSortIcon = (key) => {
  if (sortBy.value !== key) return 'bi-arrow-down-up'
  return sortDesc.value ? 'bi-arrow-down' : 'bi-arrow-up'
}

const getNestedValue = (obj, path) => {
  if (!obj || !path) return ''
  return path.split('.').reduce((o, p) => (o && o[p] !== undefined) ? o[p] : '', obj)
}

const formatValue = (value, column) => {
  if (column.formatter && typeof column.formatter === 'function') {
    return column.formatter(value)
  }
  return value
}

const onFilterChange = () => {
  emit('filter-change', filterValues.value)
}
</script>

<style scoped>
.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.table th {
  vertical-align: middle;
}

.btn-group-sm > .btn {
  padding: 0.25rem 0.5rem;
}
</style>
