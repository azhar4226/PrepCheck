import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Import global styles
import '@/assets/styles/global.css'

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

// Register service worker to block tracking requests
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('🔧 Service worker registered successfully:', registration.scope);
            })
            .catch((error) => {
                console.log('❌ Service worker registration failed:', error);
            });
    });
}

app.use(router)
app.mount('#app')
