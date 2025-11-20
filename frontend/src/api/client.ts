/**
 * Axios client with JWT token management
 * 
 * Features:
 * - Automatic access token injection
 * - Token refresh on 401 errors
 * - HTTP-only cookie support for refresh tokens
 * - Request/response interceptors
 */
import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important: Send HTTP-only cookies
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: any) => void
  reject: (reason?: any) => void
}> = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })

  failedQueue = []
}

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get access token from window (set by auth store) or localStorage
    const accessToken = (window as any).__ACCESS_TOKEN__ || localStorage.getItem('access_token')
    
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If error is not 401 or already retried, reject
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    // If already refreshing, queue this request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return apiClient(originalRequest)
        })
        .catch((err) => Promise.reject(err))
    }

    originalRequest._retry = true
    isRefreshing = true

    try {
      // Get refresh token from localStorage (fallback for cookie issues)
      const refreshToken = localStorage.getItem('refresh_token')
      
      // Try to refresh token - send refresh token in body if available
      const response = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/auth/refresh/`,
        refreshToken ? { refresh: refreshToken } : {},
        { withCredentials: true }
      )

      const newAccessToken = response.data.access

      // Update global access token and localStorage
      localStorage.setItem('access_token', newAccessToken)
      ;(window as any).__ACCESS_TOKEN__ = newAccessToken

      // Notify queued requests
      processQueue(null, newAccessToken)

      // Retry original request
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
      return apiClient(originalRequest)
    } catch (refreshError) {
      // Refresh failed, clear auth state
      processQueue(refreshError, null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      ;(window as any).__ACCESS_TOKEN__ = null

      // Don't redirect here - let router guard handle it
      // Just reject the error
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

export default apiClient

