import axios from 'axios'

class ApiClient {
  constructor() {
    // Use relative path in production (when served by nginx with proxy)
    // Use localhost:8000 in development
    this.baseURL = import.meta.env.VITE_API_URL || (
      import.meta.env.DEV ? 'http://localhost:8000' : ''
    )
    this.http = axios.create({
      baseURL: this.baseURL
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
        if (error.response?.status === 401) {
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
