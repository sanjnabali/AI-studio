<!-- src/views/auth.vue - Simplified with Direct Navigation -->
<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="container mx-auto">
      <component
        :is="currentComponent"
        @switch-mode="switchMode"
        @login-success="handleAuthSuccess"
        @register-success="handleAuthSuccess"
      />
    </div>

    <!-- Debug Panel (Development Only) -->
    <div v-if="isDev" class="fixed bottom-4 left-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-lg max-w-sm">
      <div class="text-xs font-semibold mb-2 text-gray-800 dark:text-gray-200">Auth Debug</div>
      <div class="space-y-1 text-xs text-gray-600 dark:text-gray-400">
        <div>Route: {{ $route.path }}</div>
        <div>Auth: {{ authStore.isAuthenticated ? '✅' : '❌' }}</div>
        <div>User: {{ authStore.user?.username || 'None' }}</div>
        <div>Token: {{ authStore.token ? '✅' : '❌' }}</div>
        <div>Loading: {{ authStore.loading ? '⏳' : '✅' }}</div>
        <div>Initialized: {{ authStore.isInitialized ? '✅' : '❌' }}</div>
      </div>
      <div class="mt-2 space-y-1">
        <button
          @click="testNavigation"
          class="w-full px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Test Navigation
        </button>
        <button
          @click="forceReload"
          class="w-full px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600"
        >
          Force Reload
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

// Import auth components
import LoginForm from '../components/auth/Loginform.vue'
import RegisterForm from '../components/auth/registerform.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// State
const currentMode = ref<'login' | 'register' | 'forgot'>('login')
const isDev = computed(() => import.meta.env.DEV)

// Component mapping
const components = {
  login: LoginForm,
  register: RegisterForm,
  forgot: LoginForm // Replace with ForgotPasswordForm when created
}

// Computed
const currentComponent = computed(() => components[currentMode.value])

// Watch for auth state changes and immediately redirect
watch(
  () => authStore.isAuthenticated,
  async (isAuthenticated) => {
    console.log('🔄 AUTH VIEW: Auth state changed:', { isAuthenticated, path: route.path })
    
    if (isAuthenticated && route.path === '/auth') {
      console.log('✅ AUTH VIEW: User authenticated, starting immediate navigation...')
      await performNavigation()
    }
  }
)

// Methods
function switchMode(mode: any) {
  console.log('🔄 AUTH VIEW: Switching auth mode to:', mode)
  currentMode.value = mode
  authStore.clearError()
}

async function handleAuthSuccess() {
  console.log('✅ AUTH VIEW: Auth success handler called')

  // Immediate navigation attempt
  await performNavigation()

  // Additional fallback after a short delay
  setTimeout(async () => {
    console.log('🔄 AUTH VIEW: Fallback navigation check...')
    if (authStore.isAuthenticated && route.path === '/auth') {
      console.log('🔄 AUTH VIEW: Still on auth page, forcing navigation...')
      await performNavigation()
    }
  }, 500)

  // Final fallback with window.location
  setTimeout(() => {
    if (authStore.isAuthenticated && route.path === '/auth') {
      console.log('🚨 AUTH VIEW: Emergency navigation with window.location...')
      window.location.href = '/'
    }
  }, 2000)
}

async function performNavigation() {
  const redirectPath = (route.query.redirect as string) || '/'
  console.log('🚀 AUTH VIEW: Performing navigation to:', redirectPath)
  
  // Method 1: Try router.replace (preferred)
  try {
    console.log('🚀 AUTH VIEW: Trying router.replace...')
    await router.replace(redirectPath)
    console.log('✅ AUTH VIEW: router.replace successful')
    return
  } catch (error) {
    console.error('❌ AUTH VIEW: router.replace failed:', error)
  }
  
  // Method 2: Try router.push
  try {
    console.log('🚀 AUTH VIEW: Trying router.push...')
    await router.push(redirectPath)
    console.log('✅ AUTH VIEW: router.push successful')
    return
  } catch (error) {
    console.error('❌ AUTH VIEW: router.push failed:', error)
  }
  
  // Method 3: Force navigation with window.location
  console.log('🚀 AUTH VIEW: Force navigation with window.location...')
  window.location.href = redirectPath
}

async function testNavigation() {
  console.log('🧪 TEST: Testing navigation...')
  if (authStore.isAuthenticated) {
    await performNavigation()
  } else {
    console.log('🧪 TEST: Not authenticated, cannot navigate')
  }
}

function forceReload() {
  console.log('🔄 RELOAD: Force reloading page...')
  window.location.reload()
}

// Lifecycle
onMounted(async () => {
  console.log('🔐 AUTH VIEW: Mounted')
  
  // Initialize auth if not already done
  if (!authStore.isInitialized) {
    console.log('⏳ AUTH VIEW: Initializing auth...')
    await authStore.initializeAuth()
  }
  
  // Immediate redirect if already authenticated
  if (authStore.isAuthenticated) {
    console.log('✅ AUTH VIEW: Already authenticated, redirecting immediately...')
    await performNavigation()
  }
  
  authStore.clearError()
})
</script>