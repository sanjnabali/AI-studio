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

function handleAuthSuccess() {
  const redirectPath = (route.query.redirect as string) || '/'
  router.push(redirectPath)
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