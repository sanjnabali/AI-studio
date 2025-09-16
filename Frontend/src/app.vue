<!-- src/app.vue - Fixed Main App Component -->
<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Global Loading Indicator -->
    <div
      v-if="authStore.isLoading && !authStore.isInitialized"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl">
        <div class="flex items-center space-x-3">
          <div class="w-6 h-6 border-3 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-gray-700 dark:text-gray-300">Initializing...</span>
        </div>
      </div>
    </div>

    <!-- Main App Content -->
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component || 'div'" />
      </transition>
    </router-view>

    <!-- Global Error Handler -->
    <div
      v-if="globalError"
      class="fixed bottom-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg max-w-sm z-40"
    >
      <div class="flex items-start">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Error</h3>
          <div class="mt-2 text-sm text-red-700">{{ globalError }}</div>
          <div class="mt-3">
            <button
              @click="clearError"
              class="text-sm bg-red-100 text-red-800 hover:bg-red-200 px-2 py-1 rounded"
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onErrorCaptured, ref, watch, nextTick } from 'vue'
import { useAuthStore } from './store/auth'
import { useRouter, useRoute } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const globalError = ref<string | null>(null)

onMounted(async () => {
  console.log('🚀 App mounted, initializing...')

  // Initialize authentication first
  await authStore.initializeAuth()

  console.log('✅ Auth initialized, current state:', {
    isAuthenticated: authStore.isAuthenticated,
    hasUser: !!authStore.user,
    hasToken: !!authStore.token,
    path: route.path
  })
})

// Auth navigation is handled by the auth.vue component and router guards

// Watch for initialization completion
watch(
  () => authStore.isInitialized,
  (isInitialized) => {
    if (isInitialized) {
      console.log('🎯 Auth initialization complete, handling navigation...')
      
      // Small delay to ensure router is ready
      setTimeout(() => {
        if (!authStore.isAuthenticated && route.path !== '/auth') {
          console.log('🔀 Redirecting unauthenticated user to auth')
          router.push('/auth')
        } else if (authStore.isAuthenticated && route.path === '/auth') {
          console.log('🔀 Redirecting authenticated user to studio')
          router.push('/')
        }
      }, 100)
    }
  }
)

// Global error handler
onErrorCaptured((error: Error) => {
  console.error('💥 Global error caught:', error)
  globalError.value = error.message || 'An unexpected error occurred'
  return false
})

function clearError() {
  globalError.value = null
}

// Listen for auth state changes from the store
watch(
  () => authStore.isAuthenticated,
  (newValue, oldValue) => {
    console.log('🔄 Auth store subscription triggered:', {
      isAuthenticated: newValue,
      wasAuthenticated: oldValue,
      path: route.path
    })
  },
  { immediate: false }
)
</script>

<style>
/* Global Styles */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
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

/* scrollbar.css */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-800;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-400 dark:bg-gray-600 rounded-full transition-colors duration-200;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-500 dark:bg-gray-500;
}

/* ==================== */
/* Firefox Support      */
/* ==================== */
* {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.400') theme('colors.gray.100');
}

html.dark * {
  scrollbar-color: theme('colors.gray.600') theme('colors.gray.800');
}

/* ==================== */
/* Dark mode support    */
/* ==================== */
@media (prefers-color-scheme: dark) {
  html {
    color-scheme: dark;
  }
}

/* Loading animations */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(-25%);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: none;
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}

.animate-bounce {
  animation: bounce 1s infinite;
}

/* Custom utility classes */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

.from-blue-500 {
  --tw-gradient-from: #3b82f6;
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(59, 130, 246, 0));
}

.to-purple-600 {
  --tw-gradient-to: #9333ea;
}

/* Responsive design helpers */
.container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
}

@media (min-width: 640px) {
  .container {
    max-width: 640px;
  }
}

@media (min-width: 768px) {
  .container {
    max-width: 768px;
  }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1024px;
  }
}

@media (min-width: 1280px) {
  .container {
    max-width: 1280px;
  }
}
</style>