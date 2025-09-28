<!-- Frontend/src/App.vue - Enhanced with proper theming and multimodal support -->
<template>
  <div id="app" :class="[themeClass, 'min-h-screen transition-all duration-300']">
    <!-- Loading screen -->
    <div v-if="isLoading" class="loading-screen">
      <div class="flex flex-col items-center justify-center min-h-screen">
        <div class="relative">
          <div class="w-16 h-16 border-4 border-blue-200 dark:border-blue-800 rounded-full animate-spin">
            <div class="absolute top-0 left-0 w-4 h-4 bg-blue-600 rounded-full"></div>
          </div>
        </div>
        <h2 class="mt-6 text-xl font-semibold text-gray-900 dark:text-white">AI Studio</h2>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Initializing multimodal AI workspace...</p>
      </div>
    </div>

    <!-- Main app -->
    <div v-else class="app-container">
      <!-- Navigation bar -->
      <Navbar v-if="authStore.isAuthenticated" />
      
      <!-- Main content -->
      <main class="main-content">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>

      <!-- Global notifications -->
      <NotificationContainer />

      <!-- Error boundary -->
      <div v-if="hasError" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
          <div class="flex items-center mb-4">
            <div class="w-10 h-10 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center mr-3">
              <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Application Error</h3>
          </div>
          <p class="text-gray-600 dark:text-gray-300 mb-4">{{ errorMessage }}</p>
          <div class="flex space-x-3">
            <button 
              @click="resetError" 
              class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Reload App
            </button>
            <button 
              @click="reportError" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Report Issue
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onErrorCaptured, watch } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useAuthStore } from './store/auth'
import { useSettingsStore } from './store/settings'
import { useNotificationStore } from './store/notification'
import Navbar from './components/Navbar.vue'
import NotificationContainer from './components/NotificationContainer.vue'

const router = useRouter()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const notificationStore = useNotificationStore()

const isLoading = ref(true)
const hasError = ref(false)
const errorMessage = ref('')

// Theme management
const themeClass = computed(() => {
  return settingsStore.isDarkMode ? 'dark' : 'light'
})

// Watch for theme changes and apply to DOM
watch(
  () => settingsStore.theme,
  (newTheme) => {
    document.documentElement.classList.remove('light', 'dark')
    document.documentElement.classList.add(newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
  },
  { immediate: true }
)

onMounted(async () => {
  try {
    console.log('🚀 AI Studio: Initializing application...')

    // Wait for router to be ready
    await router.isReady()
    console.log('✅ Router initialized')

    // Initialize auth system
    await authStore.initializeAuth()
    console.log('✅ Authentication system initialized')

    // Initialize settings and apply theme
    settingsStore.loadSettings()
    console.log('✅ Settings loaded')

    // Check API health
    try {
      const healthResponse = await fetch('/api/health')
      if (!healthResponse.ok) {
        throw new Error(`API health check failed: ${healthResponse.status}`)
      }
      console.log('✅ Backend API is healthy')
    } catch (apiError) {
      console.warn('⚠️ Backend API health check failed:', apiError)
      notificationStore.add({
        type: 'warning',
        message: 'Backend API is not responding. Some features may be limited.',
        duration: 5000
      })
    }

    // Load user-specific data if authenticated
    if (authStore.isAuthenticated) {
      await loadUserData()
    }

    console.log('✅ AI Studio initialization complete')
    
  } catch (error: any) {
    console.error('❌ Application initialization error:', error)
    handleInitializationError(error)
  } finally {
    isLoading.value = false
  }
})

const loadUserData = async () => {
  try {
    // Load user preferences and settings
    await settingsStore.loadUserPreferences()
    console.log('✅ User preferences loaded')
  } catch (error) {
    console.warn('⚠️ Failed to load user preferences:', error)
  }
}

const handleInitializationError = (error: any) => {
  if (error.response?.status === 401 || !authStore.isAuthenticated) {
    // Authentication error - redirect to auth
    authStore.logout()
    router.replace('/auth').catch(console.error)
  } else {
    // Other initialization errors
    hasError.value = true
    errorMessage.value = error.message || 'Failed to initialize AI Studio'
    notificationStore.add({
      type: 'error',
      message: 'Failed to initialize application',
      duration: 0 // Persistent until dismissed
    })
  }
}

onErrorCaptured((error: Error, instance, info) => {
  console.error('🚨 Vue error captured:', error, info)
  hasError.value = true
  errorMessage.value = `Component error: ${error.message}`
  
  // Report to error tracking service
  reportErrorToService(error, info)
  
  return false
})

const resetError = () => {
  hasError.value = false
  errorMessage.value = ''
  window.location.reload()
}

const reportError = () => {
  // Implement error reporting
  const errorReport = {
    message: errorMessage.value,
    timestamp: new Date().toISOString(),
    url: window.location.href,
    userAgent: navigator.userAgent
  }
  
  console.log('📊 Error report:', errorReport)
  notificationStore.add({
    type: 'info',
    message: 'Error report generated. Check console for details.',
    duration: 3000
  })
}

const reportErrorToService = (error: Error, info?: string) => {
  // In a real application, send to error tracking service
  if (import.meta.env.PROD) {
    // Example: Sentry, LogRocket, etc.
    console.log('📊 Would report to error service:', { error, info })
  }
}

// Global error handler for unhandled promises
window.addEventListener('unhandledrejection', (event) => {
  console.error('🚨 Unhandled promise rejection:', event.reason)
  notificationStore.add({
    type: 'error',
    message: 'An unexpected error occurred. Please refresh the page.',
    duration: 5000
  })
})

// Global performance monitoring
if (import.meta.env.PROD) {
  // Monitor performance
  window.addEventListener('load', () => {
    if (performance.mark) {
      performance.mark('app-loaded')
    }
  })
}
</script>

<style scoped>
/* App container */
.app-container {
  @apply flex flex-col min-h-screen;
}

.main-content {
  @apply flex-1 overflow-hidden;
}

/* Loading screen */
.loading-screen {
  @apply fixed inset-0 bg-white dark:bg-gray-900 z-50 flex items-center justify-center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.loading-screen.dark {
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
}

/* Page transitions */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Theme transitions */
.app-container {
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Scrollbar styling */
:deep(::-webkit-scrollbar) {
  @apply w-2 h-2;
}

:deep(::-webkit-scrollbar-track) {
  @apply bg-gray-100 dark:bg-gray-800;
}

:deep(::-webkit-scrollbar-thumb) {
  @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  @apply bg-gray-400 dark:bg-gray-500;
}

/* Focus styles for accessibility */
:deep(*:focus-visible) {
  @apply outline-2 outline-blue-500 outline-offset-2;
}
</style>