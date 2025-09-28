<template>
  <div class="relative">
    <!-- User Avatar/Button -->
    <button
      @click="isOpen = !isOpen"
      class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
    >
      <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
        <UserIcon class="w-5 h-5 text-white" />
      </div>
      <span class="text-sm font-medium text-gray-700 dark:text-gray-300 hidden sm:inline">
        {{ authStore.userName || 'User' }}
      </span>
      <ChevronDownIcon class="w-4 h-4 text-gray-400" :class="{ 'rotate-180': isOpen }" />
    </button>

    <!-- Dropdown Menu -->
    <div
      v-if="isOpen"
      class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-50 border border-gray-200 dark:border-gray-700"
      @click.outside="isOpen = false"
    >
      <div class="px-4 py-2 border-b border-gray-100 dark:border-gray-700">
        <p class="text-sm text-gray-900 dark:text-white">{{ authStore.userName || 'User' }}</p>
        <p class="text-xs text-gray-500 dark:text-gray-400">{{ authStore.user?.email || 'user@example.com' }}</p>
      </div>
      
      <a
        href="#"
        @click.prevent="showProfile = true"
        class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        Profile
      </a>
      
      <a
        href="#"
        @click.prevent="showSettings = true"
        class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        Settings
      </a>
      
      <a
        href="#"
        @click.prevent="handleLogout"
        class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        Sign out
      </a>
    </div>

    <!-- Profile Modal -->
    <ProfileModal
      v-if="showProfile"
      @close="showProfile = false"
    />

    <!-- Settings Modal -->
    <SettingsModal
      v-if="showSettings"
      @close="showSettings = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/store/auth'
import { UserIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'
import ProfileModal from './modals/ProfileModal.vue'
import SettingsModal from './modals/SettingsModal.vue'

const authStore = useAuthStore()

const isOpen = ref(false)
const showProfile = ref(false)
const showSettings = ref(false)

const handleLogout = async () => {
  try {
    await authStore.logout()
    // Emit event or navigate to login
    window.location.href = '/auth'
  } catch (error) {
    console.error('Logout failed:', error)
  }
  isOpen.value = false
}
</script>

<style scoped>
/* Click outside directive styles */
[click-outside] {
  position: relative;
}
</style>
