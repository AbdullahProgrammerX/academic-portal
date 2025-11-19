import apiClient from './client'
import type { Manuscript, PaginatedResponse, ApiResponse } from '@/types'

export const submissionsApi = {
  async getSubmissions(params?: { status?: string; page?: number }) {
    const { data } = await apiClient.get<PaginatedResponse<Manuscript>>('/submissions/', { params })
    return data
  },

  async getSubmission(id: number) {
    const { data } = await apiClient.get<ApiResponse<Manuscript>>(`/submissions/${id}/`)
    return data
  },

  async createSubmission(manuscriptData: Partial<Manuscript>) {
    const { data } = await apiClient.post<ApiResponse<Manuscript>>('/submissions/create/', manuscriptData)
    return data
  },

  async updateSubmission(id: number, manuscriptData: Partial<Manuscript>) {
    const { data } = await apiClient.patch<ApiResponse<Manuscript>>(`/submissions/${id}/`, manuscriptData)
    return data
  },

  async deleteSubmission(id: number) {
    await apiClient.delete(`/submissions/${id}/`)
  }
}
