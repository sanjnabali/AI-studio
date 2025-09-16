<!-- src/App.vue - Updated -->
<template>
  <div id="app" class="h-screen bg-gray-50 dark:bg-gray-900" :class="{ 'dark': isDarkMode }">
    <!-- Global Loading Overlay -->
    <div v-if="isInitializing" class="fixed inset-0 bg-white dark:bg-gray-900 z-50 flex items-center justify-center">
      <div class="text-center">
        <div class="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-pulse">
          <SparklesIcon class="w-8 h-8 text-white" />
        </div>
        <div class="text-lg font-semibold text-gray-900 dark:text-white mb-2">AI Studio</div>
        <div class="flex items-center justify-center space-x-1">
          <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
          <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
          <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
        </div>
      </div>
    </div>

    <!-- Navigation Bar (only show for authenticated routes) -->
    <Navbar v-if="showNavbar" />
    
    <!-- Main Content -->
    <div class="flex-1" :class="{ 'pt-16': showNavbar }">
      <router-view />
    </div>

    <!-- Global Notifications -->
    <div v-if="notifications.length" class="fixed top-4 right-4 space-y-2 z-40">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="max-w-sm w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden"
      >
        <div class="p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <CheckCircleIcon v-if="notification.type === 'success'" class="h-6 w-6 text-green-400" />
              <ExclamationTriangleIcon v-else-if="notification.type === 'warning'" class="h-6 w-6 text-yellow-400" />
              <XCircleIcon v-else-if="notification.type === 'error'" class="h-6 w-6 text-red-400" />
              <InformationCircleIcon v-else class="h-6 w-6 text-blue-400" />
            </div>
            <div class="ml-3 w-0 flex-1 pt-0.5">
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                {{ notification.title }}
              </p>
              <p v-if="notification.message" class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {{ notification.message }}
              </p>
            </div>
            <div class="ml-4 flex-shrink-0 flex">
              <button
                @click="removeNotification(notification.id)"
                class="bg-white dark:bg-gray-800 rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <XMarkIcon class="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Offline Indicator -->
    <div v-if="!isOnline" class="fixed bottom-4 left-4 bg-yellow-100 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-700 rounded-lg p-3 shadow-lg">
      <div class="flex items-center">
        <ExclamationTriangleIcon class="h-5 w-5 text-yellow-600 dark:text-yellow-400 mr-2" />
        <span class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
          You're offline. Some features may not work.
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './store/auth'
import { useChatStore } from './store/chat'
import Navbar from './composables/Navbar.vue'
import {
  SparklesIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  timeout?: number
}

const route = useRoute()
const authStore = useAuthStore()
const chatStore = useChatStore()

const isInitializing = ref(true)
const isDarkMode = ref(false)
const isOnline = ref(navigator.onLine)
const notifications = ref<Notification[]>([])

const showNavbar = computed(() => {
  return authStore.isAuthenticated && route.name !== 'auth'
})

// Dark mode management
watch(isDarkMode, (newValue) => {
  if (newValue) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
})

// Online/offline status
function updateOnlineStatus() {
  isOnline.value = navigator.onLine
  
  if (navigator.onLine) {
    addNotification({
      type: 'success',
      title: 'Connection restored',
      message: 'You\'re back online',
      timeout: 3000
    })
  } else {
    addNotification({
      type: 'warning',
      title: 'Connection lost',
      message: 'You\'re currently offline'
    })
  }
}

// Notification management
function addNotification(notification: Omit<Notification, 'id'>) {
  const id = Date.now().toString() + Math.random().toString(36).slice(2, 11)
  const newNotification: Notification = {
    id,
    ...notification
  }
  
  notifications.value.push(newNotification)
  
  // Auto-remove after timeout
  if (notification.timeout !== undefined) {
    setTimeout(() => {
      removeNotification(id)
    }, notification.timeout)
  } else {
    // Default timeout for success messages
    if (notification.type === 'success') {
      setTimeout(() => {
        removeNotification(id)
      }, 5000)
    }
  }
}

function removeNotification(id: string) {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

// Global notification system
window.addEventListener('app-notification', (event: Event) => {
  const customEvent = event as CustomEvent
  addNotification(customEvent.detail)
})

// Helper function to show notifications from anywhere
window.showNotification = addNotification

onMounted(async () => {
  // Initialize dark mode from localStorage
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDarkMode.value = true
  }

  // Initialize auth
  authStore.initializeAuth()
  
  // Add online/offline listeners
  window.addEventListener('online', updateOnlineStatus)
  window.addEventListener('offline', updateOnlineStatus)
  
  // Global error handling
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason)
    addNotification({
      type: 'error',
      title: 'Something went wrong',
      message: 'An unexpected error occurred'
    })
  })

  // Listen for auth state changes
  watch(() => authStore.isAuthenticated, (isAuth) => {
    if (isAuth) {
      addNotification({
        type: 'success',
        title: 'Welcome back!',
        message: `Signed in as ${authStore.userName}`,
        timeout: 3000
      })
    }
  })

  // Listen for chat errors
  watch(() => chatStore.error, (error) => {
    if (error) {
      addNotification({
        type: 'error',
        title: 'Chat Error',
        message: error
      })
    }
  })

  // Simulate initialization delay
  setTimeout(() => {
    isInitializing.value = false
  }, 1000)
})

// Expose global functions
declare global {
  interface Window {
    showNotification: (notification: Omit<Notification, 'id'>) => void
  }
}
</script>

<style lang="postcss">
/* Global styles */
#app {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-800;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gray-500;
}

/* Custom animations */
@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.slide-in {
  animation: slideIn 0.3s ease-out;
}

/* Loading animations */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse-slow {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Focus styles for accessibility */
.focus-visible {
  @apply outline-none ring-2 ring-blue-500 ring-offset-2;
}

/* Print styles */
@media print {
  .no-print {
    display: none !important;
  }
}
</style>
