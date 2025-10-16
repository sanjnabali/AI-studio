<!-- src/components/auth/LoginForm.vue - Enhanced with Debug Logging -->
<template>
  <div class="min-h-screen bg-white flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo and Header -->
      <div class="text-center">
        <div class="mx-auto h-16 w-16 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 rounded-2xl flex items-center justify-center shadow-lg">
          <SparklesIcon class="h-8 w-8 text-white" />
        </div>
        <h1 class="mt-6 text-3xl font-bold text-gray-900 tracking-tight">
          Welcome back
        </h1>
        <p class="mt-2 text-sm text-gray-600">
          Sign in to your AI Studio account
        </p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="space-y-5">
          <!-- Email Field -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <div class="relative">
              <input
                id="email"
                v-model="form.email"
                name="email"
                type="email"
                autocomplete="email"
                required
                class="block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 hover:border-gray-400"
                placeholder="Enter your email"
                :disabled="authStore.loading"
              />
            </div>
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="form.password"
                name="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                required
                class="block w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 hover:border-gray-400"
                placeholder="Enter your password"
                :disabled="authStore.loading"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
              >
                <EyeIcon
                  v-if="!showPassword"
                  class="h-5 w-5"
                />
                <EyeSlashIcon
                  v-else
                  class="h-5 w-5"
                />
              </button>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="form.rememberMe"
              name="remember-me"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="remember-me" class="ml-2 block text-sm text-gray-700">
              Remember me
            </label>
          </div>

          <div class="text-sm">
            <button
              type="button"
              @click="$emit('switch-mode', 'forgot')"
              class="font-medium text-blue-600 hover:text-blue-500"
            >
              Forgot your password?
            </button>
          </div>
        </div>



        <!-- Error Display -->
        <div v-if="authStore.error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
          <div class="flex">
            <ExclamationTriangleIcon class="h-5 w-5 text-red-400 mr-2" />
            <div class="text-sm text-red-800 dark:text-red-200">
              {{ authStore.error }}
            </div>
          </div>
        </div>

        <!-- Success Display -->
        <div v-if="loginSuccess" class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
          <div class="flex">
            <CheckCircleIcon class="h-5 w-5 text-green-400 mr-2" />
            <div class="text-sm text-green-800 dark:text-green-200">
              Login successful! Redirecting to AI Studio...
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="!canSubmit"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="authStore.loading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            </span>
            {{ authStore.loading ? 'Signing in...' : 'Sign in' }}
          </button>
        </div>



        <!-- Social Login Options -->
        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300 dark:border-gray-600" />
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-gray-50 dark:bg-gray-900 text-gray-500">Or continue with</span>
            </div>
          </div>

          <div class="mt-6 grid grid-cols-2 gap-3">
            <button
              type="button"
              class="w-full inline-flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <svg class="h-4 w-4 mr-2" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Google
            </button>

            <button
              type="button"
              class="w-full inline-flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <svg class="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.174-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.739.099.120.112.225.085.347-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.750-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24.009 12.017 24.009c6.624 0 11.99-5.367 11.99-11.988C24.007 5.367 18.641.001 12.017.001z"/>
              </svg>
              GitHub
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import {
  SparklesIcon,
  EyeIcon,
  EyeSlashIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

interface Emits {
  (e: 'switch-mode', mode: 'register' | 'login' | 'forgot'): void
  (e: 'login-success'): void
}

const emit = defineEmits<Emits>()
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = ref({
  email: '',
  password: '',
  rememberMe: false
})

const showPassword = ref(false)
const loginSuccess = ref(false)
const isDev = computed(() => import.meta.env.DEV)

const canSubmit = computed(() => {
  return form.value.email.trim() &&
         form.value.password.trim() &&
         !authStore.loading
})

const localStorageToken = computed(() => !!localStorage.getItem('auth_token'))
const localStorageUser = computed(() => !!localStorage.getItem('user_data'))

async function handleLogin() {
  if (!canSubmit.value) return

  console.log('🔐 LOGIN: Starting login process...')
  console.log('🔐 LOGIN: Form data:', {
    email: form.value.email,
    hasPassword: !!form.value.password,
    rememberMe: form.value.rememberMe
  })

  authStore.clearError()
  loginSuccess.value = false

  try {
    console.log('🔐 LOGIN: Calling auth store login...')
    await authStore.login({
      email: form.value.email.trim(),
      password: form.value.password
    })

    console.log('🔐 LOGIN: Post-login auth state:', {
      isAuthenticated: authStore.isAuthenticated,
      hasUser: !!authStore.user,
      hasToken: !!authStore.token,
      userName: authStore.userName,
      localStorage: {
        token: !!localStorage.getItem('auth_token'),
        user: !!localStorage.getItem('user_data')
      }
    })

    // Check if login was successful by verifying authentication state
    if (authStore.isAuthenticated && authStore.user) {
      console.log('✅ LOGIN: Login successful, showing success message...')
      loginSuccess.value = true

      // Wait a bit for UI feedback
      await new Promise(resolve => setTimeout(resolve, 500))

      console.log('🔐 LOGIN: Emitting login-success event...')
      emit('login-success')

      // Fallback navigation after a longer delay
      setTimeout(async () => {
        console.log('🔐 LOGIN: Fallback navigation triggered...')
        if (authStore.isAuthenticated && route.path === '/auth') {
          console.log('🔐 LOGIN: Still on auth page, forcing navigation...')
          await forceNavigation()
        }
      }, 2000)

    } else {
      console.error('❌ LOGIN: Login failed - not authenticated after login attempt')
      loginSuccess.value = false
    }
  } catch (error) {
    console.error('💥 LOGIN: Login error:', error)
    loginSuccess.value = false
  }
}

async function forceNavigation() {
  console.log('🚨 FORCE NAV: Attempting force navigation...')
  
  const redirectPath = (route.query.redirect as string) || '/'
  console.log('🚨 FORCE NAV: Target path:', redirectPath)
  
  try {
    console.log('🚨 FORCE NAV: Trying router.push...')
    await router.push(redirectPath)
    console.log('✅ FORCE NAV: router.push successful')
  } catch (error) {
    console.error('❌ FORCE NAV: router.push failed:', error)
    
    try {
      console.log('🚨 FORCE NAV: Trying router.replace...')
      await router.replace(redirectPath)
      console.log('✅ FORCE NAV: router.replace successful')
    } catch (replaceError) {
      console.error('❌ FORCE NAV: router.replace failed:', replaceError)
      
      console.log('🚨 FORCE NAV: Using window.location.href...')
      window.location.href = redirectPath
    }
  }
}

function clearAllStorage() {
  console.log('🧹 DEBUG: Clearing all storage...')
  localStorage.clear()
  sessionStorage.clear()
  authStore.clearError()
  location.reload()
}

function logDebugInfo() {
  console.log('🐛 DEBUG INFO:', {
    route: {
      path: route.path,
      name: route.name,
      query: route.query,
      params: route.params
    },
    auth: {
      isAuthenticated: authStore.isAuthenticated,
      isLoading: authStore.loading,
      isInitialized: authStore.isInitialized,
      hasUser: !!authStore.user,
      hasToken: !!authStore.token,
      userName: authStore.userName,
      error: authStore.error
    },
    localStorage: {
      authToken: localStorage.getItem('auth_token'),
      userData: localStorage.getItem('user_data'),
      refreshToken: localStorage.getItem('refresh_token')
    },
    form: form.value,
    loginSuccess: loginSuccess.value
  })
}

onMounted(() => {
  console.log('🔐 LOGIN FORM: Mounted')
  logDebugInfo()
})
</script>