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

  // =============================================================================
  // BACKWARD COMPATIBILITY METHODS
  // =============================================================================
  // These methods maintain the existing API interface while delegating to the new services
  // Note: Most components have been migrated to use services directly
  
  // Legacy endpoints (for remaining unmigrated components)
  // Question Management endpoints
  async getQuestions(params = {}) {
    return await this.admin.getQuestions(params)
  }

  async getQuestionById(questionId) {
    return await this.admin.getQuestionById(questionId)
  }

  async updateQuestion(questionId, questionData) {
    return await this.admin.updateQuestion(questionId, questionData)
  }

  async deleteQuestion(questionId) {
    return await this.admin.deleteQuestion(questionId)
  }

  async bulkCreateQuestions(questionsData) {
    return await this.admin.bulkCreateQuestions(questionsData)
  }

  async deleteQuestions(questionIds) {
    return await this.admin.deleteQuestions(questionIds)
  }

  async exportQuestions(filters = {}) {
    return await this.admin.exportQuestions(filters)
  }

  async importQuestions(formData) {
    return await this.admin.importQuestions(formData)
  }

  // Study Materials Management
  async getStudyMaterials(filters = {}) {
    return await this.studyMaterials.getMaterials(filters)
  }

  async getStudyMaterial(materialId) {
    return await this.studyMaterials.getMaterial(materialId)
  }

  async createStudyMaterial(materialData) {
    return await this.studyMaterials.createMaterial(materialData)
  }

  async updateStudyMaterial(materialId, materialData) {
    return await this.studyMaterials.updateMaterial(materialId, materialData)
  }

  async deleteStudyMaterial(materialId) {
    return await this.studyMaterials.deleteMaterial(materialId)
  }

  async uploadStudyMaterialFile(materialId, formData) {
    return await this.studyMaterials.uploadFile(materialId, formData)
  }

  async uploadStudyMaterialFileStandalone(formData) {
    return await this.studyMaterials.uploadFileStandalone(formData)
  }

  async downloadStudyMaterialFile(materialId) {
    return await this.studyMaterials.downloadFile(materialId)
  }

  async previewStudyMaterialFile(materialId) {
    return await this.studyMaterials.previewFile(materialId)
  }

  // Generic HTTP methods for flexibility
  async get(url) {
    return await this.client.get(url)
  }

  async post(url, data) {
    return await this.client.post(url, data)
  }

  async put(url, data) {
    return await this.client.put(url, data)
  }

  async delete(url) {
    return await this.client.delete(url)
  }
}

export default new ApiService()
