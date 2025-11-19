/**
 * Authentication store using Pinia.
 * 
 * Manages:
 * - User authentication state
 * - JWT tokens (access token in memory, refresh token in HTTP-only cookie)
 * - User profile data
 * - Auto token refresh
 */
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { authAPI, type LoginCredentials, type RegisterData } from '@/api/auth'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Sync access token to global window object for axios interceptor
  watch(accessToken, (newToken) => {
    if (newToken) {
      ;(window as any).__ACCESS_TOKEN__ = newToken
    } else {
      ;(window as any).__ACCESS_TOKEN__ = null
    }
  }, { immediate: true })

  // Computed
  const isAuthenticated = computed(() => !!user.value && !!accessToken.value)
  const isEmailVerified = computed(() => user.value?.email_verified ?? false)
  const isORCIDVerified = computed(() => user.value?.orcid_verified ?? false)
  const hasVerifiedIdentity = computed(() => isEmailVerified.value || isORCIDVerified.value)
  const canSubmitManuscript = computed(() => hasVerifiedIdentity.value && user.value?.is_active)

  // Actions
  async function register(data: RegisterData) {
    loading.value = true
    error.value = null

    try {
      const response = await authAPI.register(data)
      user.value = response.user
      accessToken.value = response.tokens.access
      return response
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function login(credentials: LoginCredentials) {
    loading.value = true
    error.value = null

    try {
      const response = await authAPI.login(credentials)
      user.value = response.user
      accessToken.value = response.tokens.access
      return response
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    error.value = null

    try {
      await authAPI.logout()
    } catch (err: any) {
      console.error('Logout error:', err)
    } finally {
      user.value = null
      accessToken.value = null
      loading.value = false
    }
  }

  async function refreshToken() {
    try {
      const response = await authAPI.refresh()
      accessToken.value = response.access
      return response
    } catch (err) {
      // Refresh failed, logout user
      user.value = null
      accessToken.value = null
      throw err
    }
  }

  async function fetchCurrentUser() {
    loading.value = true
    error.value = null

    try {
      const userData = await authAPI.getCurrentUser()
      user.value = userData
      return userData
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to fetch user'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(data: Partial<User>) {
    loading.value = true
    error.value = null

    try {
      const userData = await authAPI.updateProfile(data)
      user.value = userData
      return userData
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to update profile'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function changePassword(oldPassword: string, newPassword: string) {
    loading.value = true
    error.value = null

    try {
      await authAPI.changePassword(oldPassword, newPassword)
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to change password'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loginWithORCID(code: string, state?: string) {
    loading.value = true
    error.value = null

    try {
      const response = await authAPI.orcidCallback(code, state)
      user.value = response.user
      accessToken.value = response.tokens.access
      return response
    } catch (err: any) {
      error.value = err.response?.data?.error || 'ORCID login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  // Initialize: try to fetch current user if we have a stored token
  async function initialize() {
    try {
      await fetchCurrentUser()
    } catch (err) {
      // No valid session, user needs to login
      user.value = null
      accessToken.value = null
    }
  }

  return {
    // State
    user,
    accessToken,
    loading,
    error,
    
    // Computed
    isAuthenticated,
    isEmailVerified,
    isORCIDVerified,
    hasVerifiedIdentity,
    canSubmitManuscript,
    
    // Actions
    register,
    login,
    logout,
    refreshToken,
    fetchCurrentUser,
    updateProfile,
    changePassword,
    loginWithORCID,
    clearError,
    initialize
  }
})


