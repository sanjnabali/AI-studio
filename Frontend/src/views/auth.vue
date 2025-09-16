<!-- src/views/Auth.vue -->
<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Background Pattern -->
    <div class="absolute inset-0 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 opacity-50"></div>
    <div class="absolute inset-0 bg-grid-pattern opacity-5"></div>
    
    <!-- Content -->
    <div class="relative">
      <Transition
        name="slide"
        mode="out-in"
        appear
      >
        <LoginForm
          v-if="currentMode === 'login'"
          @switch-mode="currentMode = $event"
          @login-success="handleAuthSuccess"
        />
        <RegisterForm
          v-else-if="currentMode === 'register'"
          @switch-mode="currentMode = $event"
          @register-success="handleAuthSuccess"
        />
        <ForgotPasswordForm
          v-else
          @switch-mode="currentMode = $event"
        />
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import LoginForm from '../components/auth/Loginform.vue'
import RegisterForm from '../components/auth/registerform.vue'
import ForgotPasswordForm from '../components/auth/ForgotpasswordForm.vue'

const router = useRouter()
const authStore = useAuthStore()

const currentMode = ref<'login' | 'register' | 'forgot'>('login')

function handleAuthSuccess() {
  // Redirect to main app
  router.push('/')
}

onMounted(() => {
  // If already authenticated, redirect to main app
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>

<style scoped>
.bg-grid-pattern {
  background-image: 
    linear-gradient(rgba(0, 0, 0, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease-in-out;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>