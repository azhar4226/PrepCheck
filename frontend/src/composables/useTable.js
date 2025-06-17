// Composable for table functionality (pagination, sorting, filtering)
import { ref, computed } from 'vue'

export function useTable(data, options = {}) {
  const currentPage = ref(1)
  const itemsPerPage = ref(options.itemsPerPage || 10)
  const sortBy = ref(options.defaultSort || '')
  const sortDirection = ref('asc')
  const searchQuery = ref('')
  const filters = ref(options.defaultFilters || {})
  
  const filteredData = computed(() => {
    // Handle both reactive refs and regular arrays/values
    const dataArray = data.value ? data.value : data
    if (!dataArray || !Array.isArray(dataArray)) {
      return []
    }
    
    let filtered = dataArray
    
    // Apply search
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(item => 
        Object.values(item).some(value => 
          String(value).toLowerCase().includes(query)
        )
      )
    }
    
    // Apply filters
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value && value !== '') {
        filtered = filtered.filter(item => item[key] === value)
      }
    })
    
    // Apply sorting
    if (sortBy.value) {
      filtered = [...filtered].sort((a, b) => {
        const aVal = a[sortBy.value]
        const bVal = b[sortBy.value]
        const modifier = sortDirection.value === 'desc' ? -1 : 1
        
        if (aVal < bVal) return -1 * modifier
        if (aVal > bVal) return 1 * modifier
        return 0
      })
    }
    
    return filtered
  })
  
  const totalPages = computed(() => {
    if (!filteredData.value || !Array.isArray(filteredData.value)) {
      return 1
    }
    return Math.ceil(filteredData.value.length / itemsPerPage.value)
  })
  
  const paginatedData = computed(() => {
    if (!filteredData.value || !Array.isArray(filteredData.value)) {
      return []
    }
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    const result = filteredData.value.slice(start, end)
    return result
  })
  
  const changePage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }
  
  const sort = (column) => {
    if (sortBy.value === column) {
      sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortBy.value = column
      sortDirection.value = 'asc'
    }
    currentPage.value = 1
  }
  
  const resetFilters = () => {
    filters.value = options.defaultFilters || {}
    searchQuery.value = ''
    currentPage.value = 1
  }
  
  return {
    // State
    currentPage,
    itemsPerPage,
    sortBy,
    sortDirection,
    searchQuery,
    filters,
    
    // Computed
    filteredData,
    paginatedData,
    totalPages,
    
    // Methods
    changePage,
    sort,
    resetFilters
  }
}
