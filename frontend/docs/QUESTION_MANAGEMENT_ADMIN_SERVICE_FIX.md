# Question Management AdminService Fix

## Problem
Multiple errors were occurring in the admin dashboard:

1. **QuestionManagement.vue Error**: `adminService is not defined` when calling `loadQuizzes()` and `loadSubjects()`
2. **useDashboard.js Error**: `Cannot read properties of undefined (reading 'total_users')`
3. **Analytics.vue Error**: Canvas ref not found when creating charts
4. **Backend Error**: `type object 'QuizAttempt' has no attribute 'created_at'`

## Root Causes

### 1. QuestionManagement.vue Issue
- The `loadQuizzes` and `loadSubjects` functions were defined in the setup function but not included in the return statement
- This meant they were not accessible in the component scope when called from `onMounted`

### 2. useDashboard.js Issue
- The `adminStats.value` could be undefined when the computed property tried to access `total_users`
- API failures would leave the stats in an undefined state

### 3. Analytics.vue Issue
- Chart creation was happening before DOM was ready
- Missing timing control for canvas element availability

### 4. Backend QuizAttempt Model Issue
- The analytics code in `admin_controller.py` was trying to access `QuizAttempt.created_at`
- But the QuizAttempt model uses `started_at` instead of `created_at`

## Solutions Applied

### 1. Fixed QuestionManagement.vue Return Statement
```javascript
// Added missing functions to return statement
return {
  // State
  loading,
  error,
  questions,
  quizzes,
  subjects,
  currentPage,
  totalPages,
  filters,
  
  // Modals
  showCreateModal,
  showEditModal,
  showViewModal,
  editingQuestion,
  viewingQuestion,
  
  // Methods
  loadQuestions,
  loadQuizzes,        // ← Added
  loadSubjects,       // ← Added
  filterBySubject,
  debounceSearch,
  viewQuestion,
  editQuestion,
  duplicateQuestion,
  confirmDelete,
  deleteQuestion,
  handleQuestionSave,
  closeModal,
  changePage,
  truncateText
}
```

### 2. Enhanced useDashboard.js Error Handling
```javascript
// Added safer computed property with fallback values
const dashboardStats = computed(() => {
  if (!user.value) return []
  
  if (user.value.is_admin) {
    const stats = adminStats.value || {}
    // Ensure stats has the expected properties with fallback values
    const safeStats = {
      total_users: stats.total_users || 0,
      total_quizzes: stats.total_quizzes || 0,
      total_attempts: stats.total_attempts || 0,
      total_subjects: stats.total_subjects || 0
    }
    
    return [
      {
        key: 'users',
        title: 'Total Users',
        value: safeStats.total_users,
        icon: 'bi bi-people',
        variant: 'primary',
        clickable: true
      },
      // ... rest of stats
    ]
  }
})

// Enhanced loadAdminDashboard with initial fallback data
const loadAdminDashboard = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // Initialize with fallback data first
    adminStats.value = {
      total_users: 0,
      total_quizzes: 0,
      total_attempts: 0,
      total_subjects: 0
    }
    adminRecentActivity.value = []
    
    const [statsRes, activityRes] = await Promise.all([
      adminService.getDashboardStats(),
      adminService.getRecentActivity()
    ])
    
    // Update with actual data if API calls succeed
    if (statsRes && statsRes.data) {
      adminStats.value = {
        total_users: statsRes.data.total_users || 0,
        total_quizzes: statsRes.data.total_quizzes || 0,
        total_attempts: statsRes.data.total_attempts || 0,
        total_subjects: statsRes.data.total_subjects || 0
      }
    }
    
    if (activityRes && activityRes.data) {
      adminRecentActivity.value = activityRes.data || []
    }
    
  } catch (err) {
    console.error('Error loading admin dashboard:', err)
    error.value = 'Failed to load admin dashboard data'
    // Fallback data is already set above
  } finally {
    loading.value = false
  }
}
```

### 3. Fixed Analytics.vue Chart Timing
```javascript
const createDailyChart = (dailyTrendsData = []) => {
  try {
    console.log('Creating daily chart with data:', dailyTrendsData)
    
    // Wait for next tick to ensure DOM is ready
    nextTick(() => {
      if (!dailyChart.value) {
        console.error('Canvas ref not found')
        return
      }
      
      // Destroy existing chart
      if (dailyChartInstance.value) {
        dailyChartInstance.value.destroy()
      }
    
      // ... chart creation logic inside nextTick callback
    })
  } catch (error) {
    console.error('Chart creation error:', error)
  }
}
```

### 4. Fixed Backend QuizAttempt Field Reference
```python
# Fixed line 147 in admin_controller.py - changed created_at to started_at
try:
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users_30_days = db.session.query(User).join(QuizAttempt).filter(
        QuizAttempt.started_at >= thirty_days_ago,  # ← Fixed: was created_at
        User.is_admin == False
    ).distinct().count()
    
    if total_users > 0:
        retention_rate = round((active_users_30_days / total_users) * 100, 1)
except Exception as e:
    print(f"Error calculating retention rate: {e}")
```

## Files Modified
- `/frontend/src/views/admin/QuestionManagement.vue`
- `/frontend/src/composables/useDashboard.js`
- `/frontend/src/views/admin/Analytics.vue`
- `/backend/app/controllers/admin_controller.py`

## Testing Required
1. Navigate to admin question management page
2. Verify quizzes and subjects load in dropdown filters
3. Check admin dashboard loads without console errors
4. Verify analytics charts render properly
5. Test API failure scenarios show graceful fallbacks
6. Check backend logs show no more "created_at" errors

## Expected Results
- No more "adminService is not defined" errors
- No more "Cannot read properties of undefined" errors
- Admin dashboard displays with default values even if API fails
- Charts render properly with timing control and retry mechanism
- Question management filters populate correctly
- Backend analytics calculation works without QuizAttempt attribute errors

Date: December 17, 2024
