<!-- src/components/auth/ForgotPasswordForm.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto h-12 w-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
          <KeyIcon class="h-8 w-8 text-white" />
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          Reset your password
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          Or
          <button
            @click="$emit('switch-mode', 'login')"
            class="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400"
          >
            return to sign in
          </button>
        </p>
      </div>

      <div v-if="!emailSent">
        <form class="mt-8 space-y-6" @submit.prevent="handleForgotPassword">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Email address
            </label>
            <input
              id="email"
              v-model="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Enter your email address"
              :disabled="isLoading"
            />
            <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
              We'll send you a link to reset your password.
            </p>
          </div>

          <!-- Error Display -->
          <div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
            <div class="flex">
              <ExclamationTriangleIcon class="h-5 w-5 text-red-400 mr-2" />
              <div class="text-sm text-red-800 dark:text-red-200">
                {{ error }}
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              :disabled="!canSubmit"
              class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
                <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              </span>
              {{ isLoading ? 'Sending...' : 'Send reset link' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Success State -->
      <div v-else class="text-center">
        <div class="mx-auto h-16 w-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mb-4">
          <CheckCircleIcon class="h-8 w-8 text-green-600 dark:text-green-400" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
          Check your email
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
          We've sent a password reset link to <strong>{{ email }}</strong>
        </p>
        <div class="space-y-3">
          <button
            @click="resendEmail"
            :disabled="isLoading || resendCooldown > 0"
            class="w-full inline-flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="resendCooldown > 0">
              Resend in {{ resendCooldown }}s
            </span>
            <span v-else>
              Didn't receive the email? Resend
            </span>
          </button>
          <button
            @click="$emit('switch-mode', 'login')"
            class="w-full inline-flex justify-center py-2 px-4 border border-transparent text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300"
          >
            Back to sign in
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  KeyIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

interface Emits {
  (e: 'switch-mode', mode: 'register' | 'login' | 'forgot'): void
}

const emit = defineEmits<Emits>()

const email = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)
const emailSent = ref(false)
const resendCooldown = ref(0)

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const canSubmit = computed(() => {
  return email.value.trim() && emailRegex.test(email.value) && !isLoading.value
})

async function handleForgotPassword() {
  if (!canSubmit.value) return

  isLoading.value = true
  error.value = null

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // For demo purposes, always succeed
    emailSent.value = true
    startResendCooldown()
  } catch (err) {
    error.value = 'Failed to send reset email. Please try again.'
  } finally {
    isLoading.value = false
  }
}

async function resendEmail() {
  if (resendCooldown.value > 0) return

  isLoading.value = true
  error.value = null

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    startResendCooldown()
  } catch (err) {
    error.value = 'Failed to resend email. Please try again.'
  } finally {
    isLoading.value = false
  }
}

function startResendCooldown() {
  resendCooldown.value = 30
  const interval = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) {
      clearInterval(interval)
    }
  }, 1000)
}
</script>