<!-- Frontend/src/App.vue -->
<template>
  <div id="app" :data-theme="settingsStore.theme" class="min-h-screen">
    <!-- Loading screen -->
    <div v-if="isLoading" class="loading-screen">
      <div class="flex flex-col items-center justify-center min-h-screen">
        <div class="loading loading-spinner loading-lg text-primary"></div>
        <p class="mt-4 text-lg">Loading AI Studio...</p>
      </div>
    </div>

    <!-- Main app -->
    <div v-else class="app-container">
      <!-- Navigation bar -->
      <Navbar v-if="authStore.isAuthenticated" />
      
      <!-- Main content -->
      <main class="main-content">
        <RouterView />
      </main>

      <!-- Toast notifications -->
      <div class="toast toast-end z-50">
        <div v-for="notification in notifications" :key="notification.id" 
             :class="['alert', `alert-${notification.type}`]">
          <span>{{ notification.message }}</span>
          <button @click="removeNotification(notification.id)" class="btn btn-ghost btn-xs">
            ×
          </button>
        </div>
      </div>

      <!-- Error boundary -->
      <div v-if="hasError" class="error-boundary">
        <div class="alert alert-error">
          <svg class="stroke-current shrink-0 w-6 h-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="font-bold">Application Error</h3>
            <div class="text-xs">{{ errorMessage }}</div>
          </div>
          <button @click="resetError" class="btn btn-sm">Reload</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onErrorCaptured } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useAuthStore } from './store/auth'
import { useSettingsStore } from './store/settings'
import Navbar from './components/Navbar.vue'

const router = useRouter()

interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  timeout?: number
}

const authStore = useAuthStore()
const settingsStore = useSettingsStore()

const isLoading = ref(true)
const hasError = ref(false)
const errorMessage = ref('')
const notifications = ref<Notification[]>([])

onMounted(async () => {
  try {
    // Wait for router to be ready
    await router.isReady()
    console.log('✅ App: Router is ready')

    // Initialize auth
    await authStore.initializeAuth()
    console.log('✅ App: Auth initialized')

    // Check API health
    const healthResponse = await fetch('/api/health')
    if (!healthResponse.ok) {
      throw new Error(`API health check failed: ${healthResponse.status}`)
    }
    console.log('✅ App: API health check passed')

    // Load user settings if authenticated
    if (authStore.isAuthenticated) {
      settingsStore.loadSettings()
      console.log('✅ App: Settings loaded')
    }

    // If not authenticated, ensure we're on auth page
    if (!authStore.isAuthenticated && router.currentRoute.value.path !== '/auth') {
      console.log('🔀 App: Not authenticated, navigating to /auth')
      await router.replace('/auth')
    }
    
  } catch (error: any) {
    console.error('App initialization error:', error)
    if (error.response?.status === 401 || !authStore.isAuthenticated) {
      // Unauthorized - ensure auth page
      authStore.logout()
      if (router.currentRoute.value.path !== '/auth') {
        await router.replace('/auth')
      }
    } else {
      showNotification('error', 'Failed to initialize application')
      hasError.value = true
      errorMessage.value = error.message || 'Initialization failed'
    }
  } finally {
    isLoading.value = false
  }
})

onErrorCaptured((error: Error) => {
  console.error('Vue error captured:', error)
  hasError.value = true
  errorMessage.value = error.message
  return false
})

const showNotification = (type: Notification['type'], message: string, timeout = 5000) => {
  const notification: Notification = {
    id: Math.random().toString(36).substr(2, 9),
    type,
    message,
    timeout
  }
  
  notifications.value.push(notification)
  
  if (timeout > 0) {
    setTimeout(() => {
      removeNotification(notification.id)
    }, timeout)
  }
}

const removeNotification = (id: string) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

const resetError = () => {
  hasError.value = false
  errorMessage.value = ''
  window.location.reload()
}

// Global error handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  showNotification('error', 'An unexpected error occurred')
})

// Export for global use
window.showNotification = showNotification
</script>

<style>
/* Global styles */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  overflow: hidden;
}

.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--fallback-b1, oklch(var(--b1)/var(--tw-bg-opacity)));
  z-index: 9999;
}

.error-boundary {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 9999;
  max-width: 90vw;
}

/* Dark mode styles */
[data-theme="dark"] {
  --tw-bg-opacity: 1;
  background-color: rgb(30 41 59 / var(--tw-bg-opacity));
  color: rgb(248 250 252);
}

/* Custom scrollbars */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgb(156 163 175);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgb(107 114 128);
}

/* Code highlighting */
.hljs {
  background: #1e293b !important;
  border-radius: 8px;
}

/* Animation utilities */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(100%);
}
</style>