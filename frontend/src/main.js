import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Configure axios defaults
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
axios.defaults.headers.common['Content-Type'] = 'application/json'

// Add token to requests if available
const token = localStorage.getItem('prepcheck_token')
if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// Axios response interceptor for token refresh/logout
axios.interceptors.response.use(
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

const app = createApp(App)

// Make axios available globally
app.config.globalProperties.$http = axios

app.use(router)
app.mount('#app')
