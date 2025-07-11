import apiClient from './apiClient'

class AuthService {
  async login(credentials) {
    return await apiClient.post('/api/v1/auth/login', credentials)
  }

  async register(userData) {
    return await apiClient.post('/api/v1/auth/register', userData)
  }
}

export default new AuthService()
