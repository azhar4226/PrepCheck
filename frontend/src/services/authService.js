import apiClient from './apiClient'

class AuthService {
  async login(credentials) {
    return await apiClient.post('/api/auth/login', credentials)
  }

  async register(userData) {
    return await apiClient.post('/api/auth/register', userData)
  }
}

export default new AuthService()
