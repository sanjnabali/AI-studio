<!-- src/views/auth.vue - Fixed Authentication View -->
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

// Import auth components
import LoginForm from '../components/auth/Loginform.vue'
import RegisterForm from '../components/auth/registerform.vue'
import ForgotPasswordForm from '../components/auth/ForgotpasswordForm.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// State
const currentMode = ref<'login' | 'register' | 'forgot'>('login')

// Component mapping
const components = {
  login: LoginForm,
  register: RegisterForm,
  forgot: ForgotPasswordForm
}

// Computed
const currentComponent = computed(() => components[currentMode.value])

// Methods
function switchMode(mode: 'login' | 'register' | 'forgot') {
  currentMode.value = mode
  // Clear any existing errors when switching modes
  authStore.clearError()
}

async function handleAuthSuccess() {
  console.log('Auth success: navigating to studio page')
  console.log('Current auth state:', {
    isAuthenticated: authStore.isAuthenticated,
    user: authStore.user,
    token: !!authStore.token,
    localStorage: {
      token: !!localStorage.getItem('auth_token'),
      user: !!localStorage.getItem('user_data')
    }
  })

  // Wait for auth state to be fully updated
  await new Promise(resolve => setTimeout(resolve, 200))

  console.log('Auth state after delay:', {
    isAuthenticated: authStore.isAuthenticated,
    user: authStore.user,
    token: !!authStore.token
  })

  // Additional check to ensure auth state is set before navigation
  if (!authStore.isAuthenticated) {
    console.warn('Auth state not set yet, delaying navigation')
    await new Promise(resolve => setTimeout(resolve, 300))
  }

  // Emit event to notify login form to reset
  window.dispatchEvent(new CustomEvent('login-success'))

  // Force navigation with multiple fallbacks
  try {
    console.log('Attempting router.push...')
    await router.push('/')
    console.log('Router navigation successful')
  } catch (error) {
    console.error('Router navigation failed:', error)
    try {
      console.log('Attempting router.replace...')
      await router.replace('/')
      console.log('Router replace successful')
    } catch (replaceError) {
      console.error('Router replace failed:', replaceError)
      console.log('Using window.location.href as final fallback')
      window.location.href = '/'
    }
  }
}

// Lifecycle
onMounted(() => {
  // If user is already authenticated, redirect them
  if (authStore.isAuthenticated) {
    const redirectPath = (route.query.redirect as string) || '/'
    router.push(redirectPath)
  }
  
  // Clear any existing errors
  authStore.clearError()
})
</script>