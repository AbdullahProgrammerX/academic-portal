/**
 * Authentication API client
 * All endpoints under /api/auth/
 */
import apiClient from './client'
import type { User } from '@/types'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  password_confirm: string
  full_name: string
}

export interface AuthResponse {
  user: User
  tokens: {
    access: string
    refresh: string
  }
}

export interface TokenRefreshResponse {
  access: string
}

export const authAPI = {
  /**
   * Register new user
   * POST /api/auth/register/
   */
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register/', data)
    return response.data
  },

  /**
   * Login with email/password
   * POST /api/auth/login/
   * Sets HTTP-only refresh token cookie
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login/', credentials)
    return response.data
  },

  /**
   * Logout (blacklist refresh token)
   * POST /api/auth/logout/
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout/')
  },

  /**
   * Refresh access token using HTTP-only cookie
   * POST /api/auth/refresh/
   */
  async refresh(): Promise<TokenRefreshResponse> {
    const response = await apiClient.post<TokenRefreshResponse>('/auth/refresh/')
    return response.data
  },

  /**
   * Get current user profile
   * GET /api/auth/me/
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me/')
    return response.data
  },

  /**
   * Update current user profile
   * PUT /api/auth/me/
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>('/auth/me/', data)
    return response.data
  },

  /**
   * Change password
   * POST /api/auth/change-password/
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password_confirm: newPassword
    })
  },

  /**
   * Get ORCID authorization URL
   * GET /api/auth/orcid/authorize/
   */
  async getORCIDAuthURL(): Promise<{ authorization_url: string }> {
    const response = await apiClient.get<{ authorization_url: string }>('/auth/orcid/authorize/')
    return response.data
  },

  /**
   * ORCID OAuth callback
   * POST /api/auth/orcid/callback/
   */
  async orcidCallback(code: string, state?: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/orcid/callback/', {
      code,
      state
    })
    return response.data
  }
}

