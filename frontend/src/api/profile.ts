/**
 * Profile API Client
 * 
 * Endpoints:
 * - GET /api/auth/profile/ - Get current user profile with completion
 * - PUT /api/auth/profile/ - Update profile (partial updates supported)
 */

import client from './client'
import type { User, ProfileCompletionResponse } from '@/types'

/**
 * Get current user profile with completion percentage
 */
export async function getProfile(): Promise<ProfileCompletionResponse> {
  const response = await client.get<ProfileCompletionResponse>('/auth/profile/')
  return response.data
}

/**
 * Update user profile
 * @param data - Partial profile data to update
 */
export async function updateProfile(data: Partial<User>): Promise<ProfileCompletionResponse> {
  const response = await client.put<ProfileCompletionResponse>('/auth/profile/', data)
  return response.data
}

export default {
  getProfile,
  updateProfile
}
