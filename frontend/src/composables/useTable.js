// Composable for table functionality (pagination, sorting, filtering)
import { ref, computed } from 'vue'

export function useTable(data, options = {}) {
  const currentPage = ref(1)
  const pageSize = ref(options.pageSize || 10)
  const sortBy = ref(options.defaultSort || '')
  const sortDesc = ref(false)
  const searchQuery = ref('')
  const filters = ref(options.filters || {})
  
  const filteredData = computed(() => {
    // Handle both reactive refs and regular arrays/values
    const dataArray = data.value ? data.value : data
    console.log('useTable: Processing data:', dataArray, 'Type:', typeof dataArray, 'IsArray:', Array.isArray(dataArray))
    
    if (!dataArray || !Array.isArray(dataArray)) {
      console.log('useTable: Data is not an array, returning empty array')
      return []
    }
    
    let filtered = dataArray
    console.log('useTable: Starting with data length:', filtered.length)
    
    // Check if frontend filtering is disabled
    if (options.enableFrontendFiltering === false) {
      console.log('useTable: Frontend filtering disabled, returning all data')
      return filtered
    }
    
    // Skip frontend filtering if filters object is empty or only contains empty values
    // This prevents double-filtering when backend already handles filtering
    const hasActiveFilters = filters.value && Object.values(filters.value).some(value => value && value !== '')
    console.log('useTable: Has active frontend filters:', hasActiveFilters, 'Filters:', filters.value)
    
    if (!hasActiveFilters) {
      console.log('useTable: No frontend filters active, returning all data')
      return filtered
    }
    
    // Apply search
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(item => 
        Object.values(item).some(value => 
          String(value).toLowerCase().includes(query)
        )
      )
      console.log('useTable: After search filter:', filtered.length)
    }
    
    // Apply filters
    if (filters.value) {
      Object.entries(filters.value).forEach(([key, value]) => {
        if (value && value !== '') {
          filtered = filtered.filter(item => item[key] === value)
        }
      })
      console.log('useTable: After custom filters:', filtered.length)
    }
    
    // Apply sorting
    if (sortBy.value) {
      filtered = [...filtered].sort((a, b) => {
        const aVal = a[sortBy.value]
        const bVal = b[sortBy.value]
        const modifier = sortDesc.value ? -1 : 1
        
        if (aVal < bVal) return -1 * modifier
        if (aVal > bVal) return 1 * modifier
        return 0
      })
      console.log('useTable: After sorting:', filtered.length)
    }
    
    console.log('useTable: Final filtered data:', filtered.length)
    return filtered
  })
  
  const totalPages = computed(() => {
    if (!filteredData.value || !Array.isArray(filteredData.value)) {
      return 1
    }
    return Math.ceil(filteredData.value.length / pageSize.value)
  })
  
  const paginatedData = computed(() => {
    if (!filteredData.value || !Array.isArray(filteredData.value)) {
      console.log('useTable: No filtered data for pagination')
      return []
    }
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    const result = filteredData.value.slice(start, end)
    console.log('useTable: Paginated data:', result.length, 'items from', start, 'to', end)
    return result
  })
  
  const startIndex = computed(() => {
    return (currentPage.value - 1) * pageSize.value + 1
  })
  
  const endIndex = computed(() => {
    return Math.min(currentPage.value * pageSize.value, filteredData.value.length)
  })
  
  const visiblePages = computed(() => {
    const pages = []
    const total = totalPages.value
    const current = currentPage.value
    const delta = 2
    
    for (let i = Math.max(1, current - delta); i <= Math.min(total, current + delta); i++) {
      pages.push(i)
    }
    
    return pages
  })
  
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }
  
  const toggleSort = (column) => {
    if (sortBy.value === column) {
      sortDesc.value = !sortDesc.value
    } else {
      sortBy.value = column
      sortDesc.value = false
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
    pageSize,
    sortBy,
    sortDesc,
    searchQuery,
    filters,
    
    // Computed
    filteredData,
    paginatedData,
    totalPages,
    startIndex,
    endIndex,
    visiblePages,
    
    // Methods
    goToPage,
    toggleSort,
    resetFilters
  }
}
