
// src/store/auth.ts - Fixed Version
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
  const isInitialized = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userName = computed(() => user.value?.name || '')
  const userEmail = computed(() => user.value?.email || '')

  // Actions
  async function login(credentials: LoginCredentials): Promise<boolean> {
    console.log('🔐 Starting login process...')
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.login(credentials)
      console.log('✅ Login API response received:', { 
        hasUser: !!response.user, 
        hasToken: !!response.access_token 
      })

      // Set token first
      token.value = response.access_token

      // Store token in localStorage
      localStorage.setItem('auth_token', response.access_token)

      // Set user if present
      if (response.user) {
        user.value = response.user
        localStorage.setItem('user_data', JSON.stringify(response.user))
      } else {
        // If user not present, fetch user info
        await fetchUser()
      }

      // Store refresh token if provided
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token)
      }

      console.log('✅ Auth state updated:', {
        isAuthenticated: isAuthenticated.value,
        userName: userName.value,
        hasToken: !!token.value,
        hasUser: !!user.value
      })

      return true
    } catch (err) {
      console.error('❌ Login failed:', err)
      error.value = err instanceof Error ? err.message : 'Login failed'
      
      // Clear any partial state
      user.value = null
      token.value = null
      clearLocalStorage()
      
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUser(): Promise<void> {
    try {
      const response = await apiClient.getCurrentUser()
      if (response && response.user) {
        user.value = response.user
        localStorage.setItem('user_data', JSON.stringify(response.user))
        console.log('✅ User info fetched and set')
      } else {
        console.warn('⚠️ User info fetch returned no user')
        user.value = null
        clearLocalStorage()
      }
    } catch (error) {
      console.error('❌ Failed to fetch user info:', error)
      user.value = null
      clearLocalStorage()
    }
  }

  async function register(credentials: RegisterCredentials): Promise<boolean> {
    console.log('🔐 Starting registration process...')
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
      console.log('✅ Registration API response received')
      
      // Set user and token immediately
      user.value = response.user
      token.value = response.access_token
      
      // Store in localStorage for persistence
      localStorage.setItem('auth_token', response.access_token)
      localStorage.setItem('user_data', JSON.stringify(response.user))
      
      // Store refresh token if provided
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token)
      }

      console.log('✅ Registration successful, auth state updated')
      return true
    } catch (err) {
      console.error('❌ Registration failed:', err)
      error.value = err instanceof Error ? err.message : 'Registration failed'
      
      // Clear any partial state
      user.value = null
      token.value = null
      clearLocalStorage()
      
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function logout(): Promise<void> {
    console.log('🔓 Starting logout process...')
    isLoading.value = true
    
    try {
      // Try to call logout API (don't fail if it doesn't work)
      await apiClient.logout().catch(err => {
        console.warn('⚠️ Logout API call failed (continuing anyway):', err)
      })
    } finally {
      // Clear state regardless of API call success
      console.log('🧹 Clearing auth state...')
      user.value = null
      token.value = null
      error.value = null
      clearLocalStorage()
      isLoading.value = false
      console.log('✅ Logout complete')
    }
  }

  async function refreshToken(): Promise<boolean> {
    console.log('🔄 Attempting token refresh...')
    try {
      const response = await apiClient.refreshToken()
      
      user.value = response.user
      token.value = response.access_token
      
      // Update localStorage
      localStorage.setItem('auth_token', response.access_token)
      localStorage.setItem('user_data', JSON.stringify(response.user))
      
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token)
      }
      
      console.log('✅ Token refresh successful')
      return true
    } catch (err) {
      console.error('❌ Token refresh failed:', err)
      await logout()
      return false
    }
  }

  async function initializeAuth(): Promise<void> {
    if (isInitialized.value) {
      console.log('🔐 Auth already initialized')
      return
    }

    console.log('🔐 Initializing auth state...')
    isLoading.value = true

    try {
      // Try to restore auth state from localStorage
      const storedToken = localStorage.getItem('auth_token')
      const storedUser = localStorage.getItem('user_data')

      console.log('📦 Checking localStorage:', {
        hasToken: !!storedToken,
        hasUser: !!storedUser
      })

      if (storedToken && storedUser) {
        try {
          const userData = JSON.parse(storedUser)
          
          // Validate the stored data
          if (userData && userData.id && userData.email) {
            token.value = storedToken
            user.value = userData
            
            console.log('✅ Auth state restored from localStorage:', {
              userName: userData.name,
              isAuthenticated: isAuthenticated.value
            })
          } else {
            console.warn('⚠️ Invalid user data in localStorage')
            clearLocalStorage()
          }
        } catch (parseError) {
          console.warn('⚠️ Failed to parse stored user data:', parseError)
          clearLocalStorage()
        }
      } else {
        console.log('📭 No stored auth data found')
      }

      // If we have a refresh token but no access token, try to refresh
      const refreshTokenValue = localStorage.getItem('refresh_token')
      if (refreshTokenValue && !token.value) {
        console.log('🔄 Found refresh token, attempting refresh...')
        await refreshToken()
      }

    } catch (err) {
      console.error('❌ Auth initialization error:', err)
      clearLocalStorage()
    } finally {
      isLoading.value = false
      isInitialized.value = true
      console.log('🔐 Auth initialization complete:', {
        isAuthenticated: isAuthenticated.value,
        hasUser: !!user.value,
        hasToken: !!token.value
      })
    }

    // Listen for auth expiration events
    if (!window.authEventListenerAdded) {
      window.addEventListener('auth-expired', () => {
        console.log('🚨 Auth expired event received')
        logout()
      })
      window.authEventListenerAdded = true
    }
  }

  function clearLocalStorage(): void {
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
      if (newPassword.length < 6) {
        throw new Error('New password must be at least 6 characters long')
      }

      // Simulate API call - replace with actual API call
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
    isInitialized,

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
    fetchUser,
    clearError,
    updateProfile,
    changePassword,
    clearLocalStorage
  }
})