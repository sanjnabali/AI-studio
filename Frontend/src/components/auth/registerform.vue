<!-- src/components/auth/RegisterForm.vue -->

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto h-12 w-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
          <SparklesIcon class="h-8 w-8 text-white" />
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          Create your account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          Or
          <button
            @click="$emit('switch-mode', 'login')"
            class="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400"
          >
            sign in to your existing account
          </button>
        </p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="space-y-4">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Full name
            </label>
            <input
              id="name"
              v-model="form.name"
              name="name"
              type="text"
              autocomplete="name"
              required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Enter your full name"
              :disabled="authStore.isLoading"
            />
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Email address
            </label>
            <input
              id="email"
              v-model="form.email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              :class="{
                'border-red-300 dark:border-red-600': emailError,
                'border-green-300 dark:border-green-600': isValidEmail && form.email.length > 0
              }"
              placeholder="Enter your email"
              :disabled="authStore.isLoading"
            />
            <p v-if="emailError" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ emailError }}
            </p>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Password
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="form.password"
                name="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                class="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                :class="{
                  'border-red-300 dark:border-red-600': passwordError,
                  'border-green-300 dark:border-green-600': isStrongPassword && form.password.length > 0
                }"
                placeholder="Create a password"
                :disabled="authStore.isLoading"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <EyeIcon
                  v-if="!showPassword"
                  class="h-4 w-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                />
                <EyeSlashIcon
                  v-else
                  class="h-4 w-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                />
              </button>
            </div>
            
            <!-- Password Strength Indicator -->
            <div v-if="form.password.length > 0" class="mt-2">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs text-gray-600 dark:text-gray-400">Password strength:</span>
                <span class="text-xs font-medium" :class="passwordStrengthColor">
                  {{ passwordStrengthText }}
                </span>
              </div>
              <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1">
                <div
                  class="h-1 rounded-full transition-all duration-300"
                  :class="passwordStrengthColor"
                  :style="{ width: `${passwordStrengthPercentage}%` }"
                ></div>
              </div>
              <div class="mt-1 space-y-1">
                <div class="flex items-center text-xs">
                  <CheckCircleIcon 
                    v-if="passwordChecks.length"
                    class="w-3 h-3 text-green-500 mr-1"
                  />
                  <XCircleIcon 
                    v-else
                    class="w-3 h-3 text-red-400 mr-1"
                  />
                  <span :class="passwordChecks.length ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                    At least 8 characters
                  </span>
                </div>
                <div class="flex items-center text-xs">
                  <CheckCircleIcon 
                    v-if="passwordChecks.uppercase"
                    class="w-3 h-3 text-green-500 mr-1"
                  />
                  <XCircleIcon 
                    v-else
                    class="w-3 h-3 text-red-400 mr-1"
                  />
                  <span :class="passwordChecks.uppercase ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                    One uppercase letter
                  </span>
                </div>
                <div class="flex items-center text-xs">
                  <CheckCircleIcon 
                    v-if="passwordChecks.number"
                    class="w-3 h-3 text-green-500 mr-1"
                  />
                  <XCircleIcon 
                    v-else
                    class="w-3 h-3 text-red-400 mr-1"
                  />
                  <span :class="passwordChecks.number ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                    One number
                  </span>
                </div>
              </div>
            </div>
            
            <p v-if="passwordError" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ passwordError }}
            </p>
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Confirm password
            </label>
            <div class="relative">
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                name="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                class="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                :class="{
                  'border-red-300 dark:border-red-600': confirmPasswordError,
                  'border-green-300 dark:border-green-600': passwordsMatch && form.confirmPassword.length > 0
                }"
                placeholder="Confirm your password"
                :disabled="authStore.isLoading"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <EyeIcon
                  v-if="!showConfirmPassword"
                  class="h-4 w-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                />
                <EyeSlashIcon
                  v-else
                  class="h-4 w-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                />
              </button>
            </div>
            <p v-if="confirmPasswordError" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ confirmPasswordError }}
            </p>
          </div>
        </div>

        <!-- Terms and Privacy -->
        <div class="flex items-start">
          <input
            id="terms"
            v-model="form.acceptTerms"
            name="terms"
            type="checkbox"
            required
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-0.5"
          />
          <label for="terms" class="ml-2 block text-sm text-gray-900 dark:text-gray-300">
            I agree to the
            <a href="#" class="text-blue-600 hover:text-blue-500 dark:text-blue-400">Terms of Service</a>
            and
            <a href="#" class="text-blue-600 hover:text-blue-500 dark:text-blue-400">Privacy Policy</a>
          </label>
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

        <div>
          <button
            type="submit"
            :disabled="!canSubmit"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="authStore.isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            </span>
            {{ authStore.isLoading ? 'Creating account...' : 'Create account' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '../../store/auth'
import {
  SparklesIcon,
  EyeIcon,
  EyeSlashIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'

interface Emits {
  (e: 'switch-mode', mode: 'register' | 'login' | 'forgot'): void
  (e: 'register-success'): void
}

const emit = defineEmits<Emits>()
const authStore = useAuthStore()

const form = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Email validation
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const isValidEmail = computed(() => emailRegex.test(form.value.email))
const emailError = computed(() => {
  if (!form.value.email) return null
  return isValidEmail.value ? null : 'Please enter a valid email address'
})

// Password validation
const passwordChecks = computed(() => ({
  length: form.value.password.length >= 8,
  uppercase: /[A-Z]/.test(form.value.password),
  lowercase: /[a-z]/.test(form.value.password),
  number: /\d/.test(form.value.password),
  special: /[!@#$%^&*(),.?":{}|<>]/.test(form.value.password)
}))

const passwordStrengthScore = computed(() => {
  const checks = passwordChecks.value
  let score = 0
  if (checks.length) score++
  if (checks.uppercase) score++
  if (checks.lowercase) score++
  if (checks.number) score++
  if (checks.special) score++
  return score
})

const passwordStrengthPercentage = computed(() => {
  return (passwordStrengthScore.value / 5) * 100
})

const passwordStrengthText = computed(() => {
  const score = passwordStrengthScore.value
  if (score < 2) return 'Weak'
  if (score < 4) return 'Fair'
  if (score < 5) return 'Good'
  return 'Strong'
})

const passwordStrengthColor = computed(() => {
  const score = passwordStrengthScore.value
  if (score < 2) return 'text-red-600 dark:text-red-400 bg-red-500'
  if (score < 4) return 'text-yellow-600 dark:text-yellow-400 bg-yellow-500'
  if (score < 5) return 'text-blue-600 dark:text-blue-400 bg-blue-500'
  return 'text-green-600 dark:text-green-400 bg-green-500'
})

const isStrongPassword = computed(() => passwordStrengthScore.value >= 3)

const passwordError = computed(() => {
  if (!form.value.password) return null
  if (form.value.password.length < 8) return 'Password must be at least 8 characters long'
  return null
})

// Confirm password validation
const passwordsMatch = computed(() => {
  return form.value.password === form.value.confirmPassword
})

const confirmPasswordError = computed(() => {
  if (!form.value.confirmPassword) return null
  return passwordsMatch.value ? null : 'Passwords do not match'
})

// Form validation
const canSubmit = computed(() => {
  return form.value.name.trim() &&
         isValidEmail.value &&
         isStrongPassword.value &&
         passwordsMatch.value &&
         form.value.acceptTerms &&
         !authStore.isLoading
})

async function handleRegister() {
  if (!canSubmit.value) return

  authStore.clearError()

  const success = await authStore.register({
    name: form.value.name.trim(),
    email: form.value.email.trim(),
    password: form.value.password,
    confirmPassword: form.value.confirmPassword
  })

  if (success) {
    emit('register-success')
  }
}
</script>