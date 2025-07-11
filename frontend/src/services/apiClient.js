import axios from 'axios'

// const apiClient = axios.create({
//   baseURL: '/api', // or your API base URL
//   // ...other config
// });

class ApiClient {
  constructor() {
    // Use proxy through Vite server in development
    // This will route through the proxy setup in vite.config.js
    // In production, use relative path or the configured API URL
    this.baseURL = import.meta.env.VITE_API_URL || ''
    
    this.http = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30 second timeout
      withCredentials: false // Disable withCredentials for now
      // Don't set default Content-Type - let axios handle it based on data type
    })

    // Add token to requests
    this.http.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('prepcheck_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        
        // Set Content-Type for JSON requests only (not for FormData)
        if (config.data && !(config.data instanceof FormData)) {
          config.headers['Content-Type'] = 'application/json'
        }
        
        return config
      },
      (error) => Promise.reject(error)
    )

    // Handle responses
    this.http.interceptors.response.use(
      (response) => response,
      (error) => {
        // Enhanced error handling with CORS debugging info
        const errorInfo = {
          message: error.message,
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          url: error.config?.url,
          method: error.config?.method,
          // Add CORS debug info
          isCORS: error.message === 'Network Error' || 
                  error.code === 'ERR_NETWORK' ||
                  error.response?.status === 0,
          baseURL: this.baseURL
        };
        
        // Log error details
        console.error('🚨 API Error:', {
          message: errorInfo.message,
          status: errorInfo.status,
          data: errorInfo.data,
          url: errorInfo.url
        });
        
        // Log error but prevent LaunchDarkly errors from cluttering console
        if (!errorInfo.url?.includes('launchdarkly')) {
          console.error('🚨 API Client Error:', errorInfo);
          
          // Add additional debug info for CORS errors
          if (errorInfo.isCORS) {
            console.warn('🔍 Possible CORS issue detected. Check:');
            console.warn('- Backend CORS configuration (http://localhost:8000)');
            console.warn('- Vite proxy settings in vite.config.js');
            console.warn('- Browser console Network tab for preflight errors');
          }
        }
        
        if (error.response?.status === 401) {
          console.warn('🔐 Unauthorized - redirecting to login')
          localStorage.removeItem('prepcheck_token')
          localStorage.removeItem('prepcheck_user')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Generic HTTP methods for flexibility
  async get(url, config = {}) {
    const response = await this.http.get(url, config)
    return response.data
  }

  async post(url, data, config = {}) {
    const response = await this.http.post(url, data, config)
    return response.data
  }

  async put(url, data, config = {}) {
    const response = await this.http.put(url, data, config)
    return response.data
  }

  async delete(url, config = {}) {
    const response = await this.http.delete(url, config)
    return response.data
  }

  // For file downloads that need the full response
  async downloadFile(url, config = {}) {
    return await this.http.get(url, { ...config, responseType: 'blob' })
  }
}

export default new ApiClient()
