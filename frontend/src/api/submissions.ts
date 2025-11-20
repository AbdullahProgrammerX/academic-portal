import apiClient from './client'
import type { Manuscript, PaginatedResponse, ApiResponse } from '@/types'

export interface Author {
  id?: string
  author?: string
  author_order: number
  author_name?: string
  author_email?: string
  external_author_name?: string
  external_author_email?: string
  affiliation?: string
  orcid?: string
  is_corresponding: boolean
  contribution_statement?: string
}

export interface Submission {
  id: string
  title: string
  abstract?: string
  manuscript_type: string
  subject_area?: string
  status: string
  submitting_author?: string
  submitting_author_name?: string
  authors?: Author[]
  submitted_at?: string
  created_at: string
  updated_at: string
}

export interface ExtractionResult {
  submission_id: string
  task_id?: string
  extracted?: {
    title?: string
    abstract?: string
    keywords?: string[]
    authors?: Array<{
      name: string
      email: string
      affiliation?: string
    }>
  }
  errors?: string[]
  warnings?: string[]
  success: boolean
  message?: string
}

export interface ExtractionStatus {
  state: 'PENDING' | 'SUCCESS' | 'FAILURE'
  result?: ExtractionResult
  error?: string
  message?: string
}

export const submissionsApi = {
  /**
   * Start new submission with DOCX file upload
   * Triggers async metadata extraction
   */
  async startSubmission(file: File, manuscriptType: string = 'RESEARCH_ARTICLE'): Promise<ExtractionResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('manuscript_type', manuscriptType)
    
    const { data } = await apiClient.post<ExtractionResult>('/submissions/start/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return data
  },

  /**
   * Check status of metadata extraction task
   */
  async checkExtractionStatus(taskId: string): Promise<ExtractionStatus> {
    const { data } = await apiClient.get<ExtractionStatus>(`/submissions/extraction-status/${taskId}/`)
    return data
  },

  /**
   * Poll extraction status until complete
   * Returns when extraction is done (success or failure)
   */
  async waitForExtraction(taskId: string, onProgress?: (status: ExtractionStatus) => void): Promise<ExtractionResult> {
    return new Promise((resolve, reject) => {
      const pollInterval = setInterval(async () => {
        try {
          const status = await this.checkExtractionStatus(taskId)
          
          if (onProgress) {
            onProgress(status)
          }
          
          if (status.state === 'SUCCESS') {
            clearInterval(pollInterval)
            resolve(status.result!)
          } else if (status.state === 'FAILURE') {
            clearInterval(pollInterval)
            reject(new Error(status.error || 'Extraction failed'))
          }
          // PENDING: continue polling
        } catch (error) {
          clearInterval(pollInterval)
          reject(error)
        }
      }, 2000) // Poll every 2 seconds
      
      // Timeout after 2 minutes
      setTimeout(() => {
        clearInterval(pollInterval)
        reject(new Error('Extraction timeout'))
      }, 120000)
    })
  },

  /**
   * Get list of submissions for current user
   */
  async getSubmissions(params?: { 
    status?: string
    manuscript_type?: string
    page?: number 
  }): Promise<PaginatedResponse<Submission>> {
    const { data } = await apiClient.get<PaginatedResponse<Submission>>('/submissions/', { params })
    return data
  },

  /**
   * Get single submission detail
   */
  async getSubmission(id: string): Promise<Submission> {
    const { data } = await apiClient.get<Submission>(`/submissions/${id}/`)
    return data
  },

  /**
   * Update submission (only DRAFT)
   */
  async updateSubmission(id: string, submissionData: Partial<Submission>): Promise<Submission> {
    const { data } = await apiClient.patch<Submission>(`/submissions/${id}/`, submissionData)
    return data
  },

  /**
   * Submit a DRAFT submission (change status to SUBMITTED)
   */
  async submitDraft(id: string): Promise<Submission> {
    const { data } = await apiClient.post<Submission>(`/submissions/${id}/submit/`)
    return data
  },

  /**
   * Delete submission (only DRAFT)
   */
  async deleteSubmission(id: string): Promise<void> {
    await apiClient.delete(`/submissions/${id}/`)
  },

  /**
   * Add author to submission
   */
  async addAuthor(submissionId: string, authorData: Partial<Author>): Promise<Author> {
    const { data } = await apiClient.post<Author>('/submissions/authorships/', {
      submission: submissionId,
      ...authorData
    })
    return data
  },

  /**
   * Update author
   */
  async updateAuthor(authorId: string, authorData: Partial<Author>): Promise<Author> {
    const { data } = await apiClient.patch<Author>(`/submissions/authorships/${authorId}/`, authorData)
    return data
  },

  /**
   * Remove author from submission
   */
  async removeAuthor(authorId: string): Promise<void> {
    await apiClient.delete(`/submissions/authorships/${authorId}/`)
  }
}

// Keep legacy API for backward compatibility
export { submissionsApi as default }
