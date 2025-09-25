// Frontend/src/store/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient, type User, type AuthResponse, type LoginRequest, type RegisterRequest } from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const userLoaded = ref(false)
  const isAuthenticated = computed(() => !!user.value && !!token.value)
  const loading = ref(false)
  const isInitialized = ref(false)
  const error = ref<string | null>(null)

  // Computed properties for easier access
  const userName = computed(() => user.value?.username || '')
  const userEmail = computed(() => user.value?.email || '')

  async function login(credentials: LoginRequest): Promise<void> {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.login(credentials)
      user.value = response.user
      token.value = response.access_token
      userLoaded.value = true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(userData: RegisterRequest): Promise<void> {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.register(userData)
      user.value = response.user
      token.value = response.access_token
      userLoaded.value = true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      await apiClient.logout()
    } finally {
      user.value = null
      token.value = null
      userLoaded.value = false
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  async function getCurrentUser(): Promise<void> {
    if (!token.value) return

    try {
      user.value = await apiClient.getCurrentUser()
      userLoaded.value = true
    } catch (err) {
      console.error('Failed to get current user:', err)
      user.value = null
      token.value = null
      userLoaded.value = false
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  async function updateModelPreferences(preferences: any): Promise<void> {
    try {
      await apiClient.updateModelPreferences(preferences)
      if (user.value) {
        user.value.model_preferences = preferences
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update preferences'
      throw err
    }
  }

  async function updateProfile(profileData: { name: string; email: string }): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.updateProfile(profileData)
      user.value = response.user
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update profile'
      return false
    } finally {
      loading.value = false
    }
  }

  async function changePassword(currentPassword: string, newPassword: string): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await apiClient.changePassword({ currentPassword, newPassword })
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to change password'
      return false
    } finally {
      loading.value = false
    }
  }

  async function initializeAuth(): Promise<void> {
    isInitialized.value = true
    const storedToken = localStorage.getItem('access_token')
    if (storedToken) {
      token.value = storedToken
      if (!userLoaded.value) {
        await fetchUser()
      }
    }
  }

  async function fetchUser(): Promise<void> {
    if (userLoaded.value) return
    try {
      const userData = await apiClient.getCurrentUser()
      user.value = userData
      userLoaded.value = true
    } catch (err) {
      console.error('Failed to fetch user:', err)
      token.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      userLoaded.value = false
    }
  }



  function clearError(): void {
    error.value = null
  }

  return {
    user,
    token,
    userLoaded,
    isAuthenticated,
    loading,
    isInitialized,
    error,
    userName,
    userEmail,
    login,
    register,
    logout,
    getCurrentUser,
    updateModelPreferences,
    updateProfile,
    changePassword,
    initializeAuth,
    fetchUser,
    clearError
  }
})
