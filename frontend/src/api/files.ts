import apiClient from './client'

export interface PresignedUpload {
  uploadUrl: string
  fileKey: string
  expiresIn: number
}

export const filesApi = {
  async getPresignedUploadUrl(filename: string, fileType: string) {
    const { data } = await apiClient.post<PresignedUpload>('/files/upload/presigned/', {
      filename,
      fileType
    })
    return data
  },

  async uploadToS3(uploadUrl: string, file: File) {
    await fetch(uploadUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type
      }
    })
  },

  async getDownloadUrl(fileId: number) {
    const { data } = await apiClient.get<{ downloadUrl: string }>(`/files/download/${fileId}/`)
    return data
  }
}
