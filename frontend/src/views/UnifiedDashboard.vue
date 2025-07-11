<template>
  <!-- <div style="color:red">DEBUG: [Dashboard.vue](http://_vscodecontentref_/2) loaded</div> -->
  <div class="container-fluid">
    <div class="unified-dashboard">
        
      <!-- Tab Navigation -->
      <div class="dashboard-tabs mb-0">
        <ul class="nav nav-tabs" role="tablist">
          <li class="nav-item" role="presentation">
            <button 
              class="nav-link" 
              :class="{ active: activeTab === 'overview' }"
              @click="setActiveTab('overview')"
              type="button"
            >
              <i class="bi bi-house me-1"></i>Overview
            </button>
          </li>
          
          <!-- User-specific tabs -->
          <template v-if="!user?.is_admin">
            <li class="nav-item" role="presentation">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'analytics' }"
                @click="setActiveTab('analytics')"
                type="button"
              >
                <i class="bi bi-bar-chart me-1"></i>My Analytics
              </button>
            </li>
          </template>

          <!-- Admin-specific tabs -->
          <template v-if="user?.is_admin">
            <li class="nav-item" role="presentation">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'analytics' }"
                @click="setActiveTab('analytics')"
                type="button"
              >
                <i class="bi bi-bar-chart me-1"></i>System Analytics
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'subjects' }"
                @click="setActiveTab('subjects')"
                type="button"
              >
                <i class="bi bi-collection me-1"></i>Subjects
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'mock_tests' }"
                @click="setActiveTab('mock_tests')"
                type="button"
              >
                <i class="bi bi-clipboard-check me-1"></i>Mock Tests
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'users' }"
                @click="setActiveTab('users')"
                type="button"
              >
                <i class="bi bi-people me-1"></i>Users
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'questions' }"
                @click="setActiveTab('questions')"
                type="button"
              >
                <i class="bi bi-patch-question me-1"></i>Questions
              </button>
            </li>
          </template>
        </ul>
      </div>

      <!-- Dynamic Content Area -->
      <div class="dashboard-content">
        <!-- Add top margin to ensure content is visible below fixed header -->
        <div class="tab-content mt-2">
          <!-- Overview Tab - Only one tab should have 'active' class -->
          <div v-if="activeTab === 'overview'" class="tab-pane fade show active">
            <div class="tab-content-wrapper">
              <UserOverview v-if="!user?.is_admin" />
              <AdminOverview v-else />
            </div>
          </div>

          <!-- Analytics Tab -->
          <div v-else-if="activeTab === 'analytics'" class="tab-pane fade show active">
            <div class="tab-content-wrapper">
              <UserAnalytics v-if="!user?.is_admin" />
              <AdminAnalytics v-else />
            </div>
          </div>

          <!-- Admin-only tabs -->
          <template v-if="user?.is_admin">
            <div v-if="activeTab === 'subjects'" class="tab-pane fade show active">
              <div class="tab-content-wrapper">
                <SubjectManagement />
              </div>
            </div>

            <div v-else-if="activeTab === 'mock_tests'" class="tab-pane fade show active">
              <div class="tab-content-wrapper">
                <UGCNetManagement />
              </div>
            </div>

            <div v-else-if="activeTab === 'users'" class="tab-pane fade show active">
              <div class="tab-content-wrapper">
                <UserManagement />
              </div>
            </div>

            <div v-else-if="activeTab === 'questions'" class="tab-pane fade show active">
              <div class="tab-content-wrapper">
                <QuestionManagement />
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Loading Overlay -->
      <div v-if="loading" class="loading-overlay">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useRouter, useRoute } from 'vue-router'

// 📚 PDF EXPORT DEPENDENCIES
// Run these commands to install PDF generation libraries:
// npm install jspdf jspdf-autotable
// 
// Alternative libraries you can use:
// - html2pdf.js (for HTML to PDF conversion)
// - puppeteer (for server-side PDF generation)
// - react-pdf (if using React components in Vue)

// Import component variations
import PageHeader from '@/components/ui/PageHeader.vue'
import UserOverview from '@/components/dashboard/UserOverview.vue'
import AdminOverview from '@/components/dashboard/AdminOverview.vue'
import UserAnalytics from '@/components/features/UserAnalytics.vue'

// Import real admin components from views/admin
import AdminAnalytics from '@/views/admin/Analytics.vue'
import SubjectManagement from '@/views/admin/SubjectManagement.vue'
import UGCNetManagement from '@/views/admin/UGCNetManagement.vue'
import UserManagement from '@/views/admin/UserManagement.vue'
import QuestionManagement from '@/views/admin/QuestionManagement.vue'

export default {
  name: 'UnifiedDashboard',
  components: {
    PageHeader,
    UserOverview,
    AdminOverview,
    UserAnalytics,
    AdminAnalytics,
    SubjectManagement,
    UGCNetManagement,
    UserManagement,
    QuestionManagement
  },
  setup() {
    const { user, api } = useAuth()  // ✅ Now we have access to API methods
    const router = useRouter()
    const route = useRoute()
    
    const activeTab = ref('overview')
    const loading = ref(false)

    // Set initial tab based on user role
    const initializeTab = () => {
      // Check if there's a tab specified in query params
      const queryTab = route.query.tab
      if (queryTab) {
        activeTab.value = queryTab
        return
      }

      // Default to overview for new users
      activeTab.value = 'overview'
    }

    // Tab handling methods
    const setActiveTab = (tab) => {
      activeTab.value = tab
      // Update URL based on whether it's admin or user dashboard
      if (user.value?.is_admin) {
        router.push({
          path: '/admin/dashboard',
          query: { tab }
        }).catch(() => {})  // Ignore redundant navigation errors
      } else {
        router.push({
          path: '/dashboard',
          query: { tab }
        }).catch(() => {})  // Ignore redundant navigation errors
      }
    }

    // Watch for route changes
    watch(() => route.query.tab, (newTab) => {
      if (newTab && activeTab.value !== newTab) {
        activeTab.value = newTab
      }
    }, { immediate: true })

    // Initialize based on route
    onMounted(() => {
      console.log('UnifiedDashboard mounted, initializing tab')
      console.log('Current user:', user)
      // Set initial tab from route or default
      activeTab.value = route.query.tab || 'overview'
    })

    // Refresh data for current tab
    const refreshData = () => {
      loading.value = true
      
      // Emit refresh event that child components can listen to
      setTimeout(() => {
        loading.value = false
        // You can implement specific refresh logic here
        console.log('Dashboard data refreshed')
      }, 1000)
    }

    // Start new UGC NET mock test for users
    const startNewMockTest = () => {
      router.push('/ugc-net')
    }

    // Navigate to AI Question Generator
    const navigateToAIQuestions = () => {
      router.push('/admin/ai-questions')
    }

    // Export data functionality - PDF FORMAT
    const exportData = async () => {
      try {
        loading.value = true
        console.log('Starting admin data export as PDF...')
        
        // 📚 STEP 1: Call Backend API for PDF Export
        // Request PDF format specifically
        const response = await api.post('/api/admin/export', {
          format: 'pdf',  // 🔄 Changed from 'csv' to 'pdf'
          include: ['users', 'tests', 'attempts', 'subjects'],
          options: {
            title: 'PrepCheck Admin Data Export',
            orientation: 'landscape',  // Better for tables
            pageSize: 'A4'
          }
        }, {
          // 📚 Important: Tell axios this is a binary response
          responseType: 'blob'  // This handles PDF binary data correctly
        })
        
        // 📚 STEP 2: Handle PDF Response
        let downloadData, mimeType, fileExtension
        
        if (response.data instanceof Blob) {
          // Backend returned PDF directly
          downloadData = response.data
          mimeType = 'application/pdf'
          fileExtension = 'pdf'
        } else {
          // Backend returned JSON data - we generate PDF on frontend
          downloadData = await generatePDFFromData(response.data)
          mimeType = 'application/pdf'
          fileExtension = 'pdf'
        }
        
        // 📚 STEP 3: Create PDF Blob
        const blob = new Blob([downloadData], { type: mimeType })
        
        // 📚 STEP 4: Generate Download Link
        const downloadUrl = window.URL.createObjectURL(blob)
        
        // 📚 STEP 5: Create Download Link with PDF-specific naming
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = `prepcheck-admin-report-${getCurrentDateString()}.${fileExtension}`
        
        // 📚 STEP 6: Trigger Download
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        // 📚 STEP 7: Cleanup
        window.URL.revokeObjectURL(downloadUrl)
        
        console.log('PDF export completed successfully')
        showSuccessMessage('Admin report exported as PDF successfully!')
        
      } catch (error) {
        console.error('PDF Export error:', error)
        
        // 📚 PDF-Specific Error Handling
        if (error.response?.status === 403) {
          showErrorMessage('You do not have permission to export admin data')
        } else if (error.response?.status === 500) {
          showErrorMessage('Server error during PDF generation. Please try again later.')
        } else if (error.message?.includes('PDF generation failed')) {
          showErrorMessage('PDF generation failed. The data might be too large.')
        } else if (error.code === 'NETWORK_ERROR') {
          showErrorMessage('Network error. Check your connection.')
        } else {
          showErrorMessage('PDF export failed. Please try again.')
        }
      } finally {
        loading.value = false
      }
    }

    // 📚 HELPER FUNCTIONS for PDF Export Functionality
    
    // Generate PDF from JSON data using jsPDF (frontend approach)
    const generatePDFFromData = async (jsonData) => {
      // 📚 NOTE: This requires jsPDF library
      // Install with: npm install jspdf jspdf-autotable
      
      try {
        // Dynamic import to avoid loading jsPDF unless needed
        const { jsPDF } = await import('jspdf')
        await import('jspdf-autotable')  // For table generation
        
        // 📚 Create new PDF document
        const doc = new jsPDF({
          orientation: 'landscape',  // Better for data tables
          unit: 'mm',
          format: 'a4'
        })
        
        // 📚 Add header
        doc.setFontSize(20)
        doc.text('PrepCheck Admin Data Export', 20, 20)
        
        doc.setFontSize(12)
        doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 20, 30)
        doc.text(`Total Records: ${jsonData.length}`, 20, 40)
        
        // 📚 Add data table
        if (jsonData && jsonData.length > 0) {
          const headers = Object.keys(jsonData[0])
          const rows = jsonData.map(row => headers.map(header => row[header] || ''))
          
          doc.autoTable({
            head: [headers],
            body: rows,
            startY: 50,
            styles: {
              fontSize: 8,
              cellPadding: 2
            },
            headStyles: {
              fillColor: [41, 128, 185],  // Blue header
              textColor: 255
            },
            alternateRowStyles: {
              fillColor: [245, 245, 245]  // Light gray alternating rows
            }
          })
        } else {
          doc.text('No data available for export', 20, 60)
        }
        
        // 📚 Return PDF as blob
        return doc.output('blob')
        
      } catch (error) {
        console.error('Frontend PDF generation error:', error)
        
        // 📚 Fallback: Create simple text PDF
        return createFallbackPDF(jsonData)
      }
    }
    
    // Fallback PDF generation without external libraries
    const createFallbackPDF = (jsonData) => {
      // 📚 Simple PDF generation using basic PDF structure
      const pdfContent = `%PDF-1.4
        1 0 obj
        << /Type /Catalog /Pages 2 0 R >>
        endobj
        2 0 obj
        << /Type /Pages /Kids [3 0 R] /Count 1 >>
        endobj
        3 0 obj
        << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>
        endobj
        4 0 obj
        << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
        endobj
        5 0 obj
        << /Length ${estimateContentLength(jsonData)} >>
        stream
        BT
        /F1 12 Tf
        50 750 Td
        (PrepCheck Admin Data Export) Tj
        0 -20 Td
        (Generated: ${new Date().toLocaleDateString()}) Tj
        0 -20 Td
        (Records: ${jsonData?.length || 0}) Tj
        0 -40 Td
        (Please contact support for detailed export) Tj
        ET
        endstream
        endobj
        xref
        0 6
        0000000000 65535 f 
        0000000009 00000 n 
        0000000058 00000 n 
        0000000115 00000 n 
        0000000245 00000 n 
        0000000323 00000 n 
        trailer
        << /Size 6 /Root 1 0 R >>
        startxref
        ${400 + estimateContentLength(jsonData)}
        %%EOF`
      
      return new Blob([pdfContent], { type: 'application/pdf' })
    }
    
    // Estimate content length for PDF structure
    const estimateContentLength = (data) => {
      return 200 + (data?.length || 0) * 10
    }
    
    // Remove old CSV conversion function and replace with PDF utilities
    // Convert JSON data to CSV format (keeping as backup)
    const convertToCSV = (jsonData) => {
      if (!jsonData || !Array.isArray(jsonData) || jsonData.length === 0) {
        return 'No data available'
      }
      
      // Get headers from first object
      const headers = Object.keys(jsonData[0])
      const csvHeaders = headers.join(',')
      
      // Convert each row to CSV
      const csvRows = jsonData.map(row => {
        return headers.map(header => {
          const value = row[header]
          // Handle commas and quotes in data
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`
          }
          return value || ''
        }).join(',')
      })
      
      return [csvHeaders, ...csvRows].join('\n')
    }
    
    // Get current date as string for filename
    const getCurrentDateString = () => {
      const now = new Date()
      return now.toISOString().split('T')[0] // Returns YYYY-MM-DD
    }
    
    // Show success message (you can replace with your toast/notification system)
    const showSuccessMessage = (message) => {
      // For now, just console log. You can integrate with your notification system
      console.log('✅ Success:', message)
      // Example: toast.success(message)
    }
    
    // Show error message (you can replace with your toast/notification system)
    const showErrorMessage = (message) => {
      // For now, just console log. You can integrate with your notification system
      console.error('❌ Error:', message)
      // Example: toast.error(message)
    }

    // Watch for user changes (role switching)
    watch(user, (newUser, oldUser) => {
      if (newUser?.is_admin !== oldUser?.is_admin) {
        // Reset to overview when role changes
        setActiveTab('overview')
      }
    }, { deep: true })

    onMounted(() => {
      console.log('UnifiedDashboard mounted, initializing tab')
      console.log('Current user:', user)
      // Set active tab based on initial route query or default to 'overview'
      activeTab.value = route.query.tab || 'overview'
    })

    return {
      user,
      activeTab,
      loading,
      setActiveTab,
      refreshData,
      startNewMockTest,
      navigateToAIQuestions,
      exportData,
      // Helper functions (optional to expose)
      showSuccessMessage,
      showErrorMessage
    }
  }
}
</script>

<style scoped>
.unified-dashboard {
  /* padding: 1rem 1rem; */
  max-width: 1500px;
  margin: 0 auto;
}

.dashboard-header {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 1rem;
}

.nav-tabs {
  border-bottom: 2px solid #dee2e6;
}

.nav-tabs .nav-link {
  border: none;
  border-bottom: 3px solid transparent;
  background: none;
  color: #6c757d;
  font-weight: 500;
  padding: 0.75rem 1.5rem;
  margin-right: 0.5rem;
  transition: all 0.3s ease;
}

.nav-tabs .nav-link:hover {
  border-color: transparent;
  color: #0d6efd;
  background-color: rgba(13, 110, 253, 0.1);
}

.nav-tabs .nav-link.active {
  color: #0d6efd;
  border-bottom-color: #0d6efd;
  background-color: rgba(13, 110, 253, 0.1);
}

.dashboard-content {
  position: relative;
  min-height: 500px;
}

.tab-pane {
  animation: fadeIn 0.3s ease-in-out;
}

.tab-content-wrapper {
  padding: 0.5rem 0;
}

/* Override admin component styles for tab embedding */
.tab-content-wrapper .subject-management,
.tab-content-wrapper .test-management,
.tab-content-wrapper .user-management,
.tab-content-wrapper .question-management,
.tab-content-wrapper .analytics-dashboard {
  padding: 0;
  margin: 0;
}

.tab-content-wrapper h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  z-index: 10;
}

/* Responsive design */
@media (max-width: 768px) {
  .unified-dashboard {
    padding: 1rem 0.5rem;
  }
  
  .dashboard-header {
    padding: 1rem;
  }
  
  .nav-tabs .nav-link {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
  
  .d-flex.gap-2 {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .d-flex.gap-2 .btn {
    width: 100%;
  }
}
</style>
