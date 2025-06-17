import apiClient from './apiClient'

class StudyMaterialsService {
  async getMaterials(filters = {}) {
    const queryString = new URLSearchParams(filters).toString()
    return await apiClient.get(`/api/study-materials?${queryString}`)
  }

  async getMaterial(materialId) {
    return await apiClient.get(`/api/study-materials/${materialId}`)
  }

  async createMaterial(materialData) {
    return await apiClient.post('/api/study-materials', materialData)
  }

  async updateMaterial(materialId, materialData) {
    return await apiClient.put(`/api/study-materials/${materialId}`, materialData)
  }

  async deleteMaterial(materialId) {
    return await apiClient.delete(`/api/study-materials/${materialId}`)
  }

  async uploadFile(materialId, formData) {
    return await apiClient.post(`/api/study-materials/${materialId}/upload`, formData)
  }

  async uploadFileStandalone(formData) {
    return await apiClient.post('/api/study-materials/upload', formData)
  }

  async downloadFile(materialId) {
    return await apiClient.downloadFile(`/api/study-materials/${materialId}/download`)
  }

  async previewFile(materialId) {
    return await apiClient.downloadFile(`/api/study-materials/${materialId}/preview`)
  }
}

export default new StudyMaterialsService()
