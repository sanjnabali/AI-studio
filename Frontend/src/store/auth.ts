// src/store/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '../api/client'

interface User {
  id: string
  name: string
  email: string
  avatar?: string
  createdAt?: string
}

interface LoginCredentials {
  email: string
  password: string
}

interface RegisterCredentials extends LoginCredentials {
  name: string
  confirmPassword: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userName = computed(() => user.value?.name || '')
  const userEmail = computed(() => user.value?.email || '')

  // Actions
  async function login(credentials: LoginCredentials): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.login(credentials)

      user.value = response.user
      token.value = response.access_token

      // Store in localStorage for persistence
      localStorage.setItem('auth_token', response.access_token)
      localStorage.setItem('user_data', JSON.stringify(response.user))

      // Store refresh token if provided
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token)
      }

      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function register(credentials: RegisterCredentials): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      // Validate passwords match
      if (credentials.password !== credentials.confirmPassword) {
        throw new Error('Passwords do not match')
      }

      // Validate password strength
      if (credentials.password.length < 6) {
        throw new Error('Password must be at least 6 characters long')
      }

      const response = await apiClient.register(credentials)
      
      user.value = response.user
      token.value = response.access_token
      
      // Store refresh token if provided
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token)
      }

      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Registration failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function logout(): Promise<void> {
    isLoading.value = true
    
    try {
      await apiClient.logout()
    } catch (err) {
      console.warn('Logout error:', err)
    } finally {
      // Clear state regardless of API call success
      user.value = null
      token.value = null
      error.value = null
      localStorage.removeItem('refresh_token')
      isLoading.value = false
    }
  }

  async function refreshToken(): Promise<boolean> {
    try {
      const response = await apiClient.refreshToken()
      user.value = response.user
      token.value = response.access_token
      
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token)
      }
      
      return true
    } catch (err) {
      console.error('Token refresh failed:', err)
      await logout()
      return false
    }
  }

  function initializeAuth(): void {
    // Try to restore auth state from localStorage
    const storedToken = localStorage.getItem('auth_token')
    const storedUser = localStorage.getItem('user_data')

    if (storedToken && storedUser) {
      try {
        token.value = storedToken
        user.value = JSON.parse(storedUser)
      } catch (err) {
        console.warn('Failed to restore auth state:', err)
        clearAuthState()
      }
    }

    // Listen for auth expiration events
    window.addEventListener('auth-expired', () => {
      logout()
    })
  }

  function clearAuthState(): void {
    user.value = null
    token.value = null
    error.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    localStorage.removeItem('refresh_token')
  }

  function clearError(): void {
    error.value = null
  }

  // Update user profile
  async function updateProfile(updates: Partial<User>): Promise<boolean> {
    if (!user.value) return false

    isLoading.value = true
    error.value = null

    try {
      // This would call a backend endpoint to update user profile
      // For now, we'll just update the local state
      user.value = { ...user.value, ...updates }
      localStorage.setItem('user_data', JSON.stringify(user.value))
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Profile update failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // Password change
  async function changePassword(currentPassword: string, newPassword: string): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      // This would call a backend endpoint to change password
      // For now, we'll simulate the API call
      if (newPassword.length < 6) {
        throw new Error('New password must be at least 6 characters long')
      }

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Password change failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    user,
    token,
    isLoading,
    error,
    
    // Computed
    isAuthenticated,
    userName,
    userEmail,
    
    // Actions
    login,
    register,
    logout,
    refreshToken,
    initializeAuth,
    clearAuthState,
    clearError,
    updateProfile,
    changePassword
  }
})