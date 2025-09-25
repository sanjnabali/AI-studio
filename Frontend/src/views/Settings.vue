<!-- src/views/Settings.vue -->
<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <Navbar />
    
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Manage your account and application preferences
        </p>
      </div>

      <div class="space-y-6">
        <!-- Profile Settings -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Profile Information</h3>
            
            <form @submit.prevent="updateProfile" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Full Name
                </label>
                <input
                  v-model="profileForm.name"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email
                </label>
                <input
                  v-model="profileForm.email"
                  type="email"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              
              <button
                type="submit"
                :disabled="authStore.loading"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
              >
                {{ authStore.loading ? 'Updating...' : 'Update Profile' }}
              </button>
            </form>
          </div>
        </div>

        <!-- Password Change -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Change Password</h3>
            
            <form @submit.prevent="changePassword" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Current Password
                </label>
                <input
                  v-model="passwordForm.current"
                  type="password"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  New Password
                </label>
                <input
                  v-model="passwordForm.new"
                  type="password"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Confirm New Password
                </label>
                <input
                  v-model="passwordForm.confirm"
                  type="password"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              
              <button
                type="submit"
                :disabled="authStore.loading || !canChangePassword"
                class="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
              >
                {{ authStore.loading ? 'Changing...' : 'Change Password' }}
              </button>
            </form>
          </div>
        </div>

        <!-- Application Settings -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Application Settings</h3>
            
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Dark Mode
                  </label>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    Use dark theme for the interface
                  </p>
                </div>
                <button
                  @click="toggleDarkMode"
                  class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  :class="isDarkMode ? 'bg-blue-600' : 'bg-gray-200'"
                >
                  <span
                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                    :class="isDarkMode ? 'translate-x-5' : 'translate-x-0'"
                  ></span>
                </button>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Voice Input
                  </label>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    Enable voice input for messages
                  </p>
                </div>
                <button
                  @click="settings.voiceEnabled = !settings.voiceEnabled"
                  class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  :class="settings.voiceEnabled ? 'bg-blue-600' : 'bg-gray-200'"
                >
                  <span
                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                    :class="settings.voiceEnabled ? 'translate-x-5' : 'translate-x-0'"
                  ></span>
                </button>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Code Execution
                  </label>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    Enable code execution features
                  </p>
                </div>
                <button
                  @click="settings.codeExecutionEnabled = !settings.codeExecutionEnabled"
                  class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  :class="settings.codeExecutionEnabled ? 'bg-blue-600' : 'bg-gray-200'"
                >
                  <span
                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                    :class="settings.codeExecutionEnabled ? 'translate-x-5' : 'translate-x-0'"
                  ></span>
                </button>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Default AI Model
                </label>
                <select
                  v-model="settings.defaultModel"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="gemini-pro">Gemini Pro</option>
                  <option value="gemini-pro-vision">Gemini Pro Vision</option>
                  <option value="claude-3">Claude 3</option>
                  <option value="gpt-4">GPT-4</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Response Temperature
                </label>
                <input
                  v-model.number="settings.temperature"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  class="w-full"
                />
                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>Focused (0.0)</span>
                  <span>{{ settings.temperature }}</span>
                  <span>Creative (1.0)</span>
                </div>
              </div>
            </div>
            
            <button
              @click="saveSettings"
              class="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Save Settings
            </button>
          </div>
        </div>

        <!-- Data Management -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Data Management</h3>
            
            <div class="space-y-4">
              <div class="flex items-center justify-between p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <div>
                  <p class="text-sm font-medium text-yellow-800 dark:text-yellow-200">Export Chat History</p>
                  <p class="text-xs text-yellow-600 dark:text-yellow-300">Download all your conversations</p>
                </div>
                <button
                  @click="exportData"
                  class="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded"
                >
                  Export
                </button>
              </div>
              
              <div class="flex items-center justify-between p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <div>
                  <p class="text-sm font-medium text-red-800 dark:text-red-200">Clear All Data</p>
                  <p class="text-xs text-red-600 dark:text-red-300">Permanently delete all conversations</p>
                </div>
                <button
                  @click="clearAllData"
                  class="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded"
                >
                  Clear All
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Account Actions -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Account Actions</h3>
            
            <div class="space-y-3">
              <button
                @click="handleLogout"
                class="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors text-left"
              >
                Sign Out
              </button>
              
              <button
                @click="deleteAccount"
                class="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors text-left"
              >
                Delete Account
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Success/Error Messages -->
      <div
        v-if="message"
        class="fixed bottom-4 right-4 bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg max-w-sm"
      >
        <div class="flex items-center">
          <svg class="h-5 w-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          <span class="text-sm text-green-700">{{ message }}</span>
        </div>
      </div>

      <div
        v-if="authStore.error"
        class="fixed bottom-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg max-w-sm"
      >
        <div class="flex items-start">
          <svg class="h-5 w-5 text-red-400 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
          </svg>
          <div>
            <p class="text-sm text-red-700">{{ authStore.error }}</p>
            <button
              @click="authStore.clearError()"
              class="mt-1 text-xs text-red-600 hover:text-red-800"
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { useChatStore } from '../store/chat'
import Navbar from '../components/Navbar.vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

// Reactive state
const message = ref<string | null>(null)
const isDarkMode = ref(false)

const profileForm = ref({
  name: '',
  email: ''
})

const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

const settings = ref({
  voiceEnabled: true,
  codeExecutionEnabled: true,
  defaultModel: 'gemini-pro',
  temperature: 0.7
})

// Computed
const canChangePassword = computed(() => {
  return passwordForm.value.current && 
         passwordForm.value.new && 
         passwordForm.value.confirm &&
         passwordForm.value.new === passwordForm.value.confirm &&
         passwordForm.value.new.length >= 6
})

// Methods
async function updateProfile() {
  const success = await authStore.updateProfile({
    name: profileForm.value.name,
    email: profileForm.value.email
  })
  
  if (success) {
    showMessage('Profile updated successfully')
  }
}

async function changePassword() {
  if (!canChangePassword.value) return
  
  const success = await authStore.changePassword(
    passwordForm.value.current,
    passwordForm.value.new
  )
  
  if (success) {
    showMessage('Password changed successfully')
    passwordForm.value = { current: '', new: '', confirm: '' }
  }
}

function toggleDarkMode() {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
  localStorage.setItem('darkMode', isDarkMode.value.toString())
}

function saveSettings() {
  localStorage.setItem('appSettings', JSON.stringify(settings.value))
  showMessage('Settings saved successfully')
}

function exportData() {
  const data = {
    chats: chatStore.chats,
    settings: settings.value,
    exportDate: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ai-studio-export-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  showMessage('Data exported successfully')
}

function clearAllData() {
  if (confirm('Are you sure? This will permanently delete all your conversations and cannot be undone.')) {
    chatStore.clearChats()
    localStorage.removeItem('ai_studio_chats')
    showMessage('All data cleared successfully')
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push('/auth')
}

function deleteAccount() {
  if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
    if (confirm('This will permanently delete all your data. Are you absolutely sure?')) {
      // TODO: Implement account deletion
      alert('Account deletion would be implemented here')
    }
  }
}

function showMessage(msg: string) {
  message.value = msg
  setTimeout(() => {
    message.value = null
  }, 3000)
}

// Lifecycle
onMounted(() => {
  // Load user data
  profileForm.value.name = authStore.userName
  profileForm.value.email = authStore.userEmail
  
  // Load dark mode preference
  const darkMode = localStorage.getItem('darkMode')
  if (darkMode === 'true') {
    isDarkMode.value = true
    document.documentElement.classList.add('dark')
  }
  
  // Load app settings
  const savedSettings = localStorage.getItem('appSettings')
  if (savedSettings) {
    settings.value = { ...settings.value, ...JSON.parse(savedSettings) }
  }
})
</script>