// Unified API service that aggregates all domain-specific services
// This maintains backward compatibility while providing a cleaner structure

import authService from './authService'
import userService from './userService'
import adminService from './adminService'
import analyticsService from './analyticsService'
import aiService from './aiService'
import notificationsService from './notificationsService'
import studyMaterialsService from './studyMaterialsService'
import ugcNetService from './ugcNetService'
import apiClient from './apiClient'

class ApiService {
  constructor() {
    // Expose domain services
    this.auth = {
      ...authService,
      getProfile: () => userService.getProfile()  // Add getProfile to auth service
    }
    this.user = userService
    this.admin = adminService
    this.analytics = analyticsService
    this.ai = aiService
    this.notifications = notificationsService
    this.studyMaterials = studyMaterialsService
    this.ugcNet = ugcNetService
    
    // Expose raw client for direct access
    this.client = apiClient
  }
}

export default new ApiService()
