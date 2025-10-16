<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-brand">
        <router-link to="/" class="navbar-logo">
          <div class="logo-icon">
            <svg class="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
          <span class="logo-text">AI Studio</span>
        </router-link>
      </div>

      <div class="navbar-menu">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="navbar-link"
          active-class="navbar-link--active"
        >
          {{ item.name }}
        </router-link>
      </div>

      <div class="navbar-actions">
        <button
          @click="toggleTheme"
          class="navbar-button"
          title="Toggle theme"
        >
          <SunIcon v-if="isDark" class="w-5 h-5" />
          <MoonIcon v-else class="w-5 h-5" />
        </button>

        <DropdownMenu>
          <template #trigger>
            <div class="user-menu-trigger">
              <div class="user-avatar">
                {{ userInitials }}
              </div>
              <ChevronDownIcon class="w-4 h-4" />
            </div>
          </template>

          <div class="dropdown-item" @click="logout">
            <ArrowRightOnRectangleIcon class="w-4 h-4" />
            Sign out
          </div>
        </DropdownMenu>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import {
  SunIcon,
  MoonIcon,
  ChevronDownIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/vue/24/outline'
import DropdownMenu from './DropdownMenu.vue'

const router = useRouter()
const authStore = useAuthStore()

const isDark = computed(() => false) // TODO: implement theme store

const userInitials = computed(() => {
  const name = authStore.userName || 'User'
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
})

const menuItems = [
  { name: 'Dashboard', path: '/' },
  { name: 'Projects', path: '/projects' },
  { name: 'Settings', path: '/settings' }
]

const toggleTheme = () => {
  // TODO: implement theme toggle
}

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0.75rem 0;
}


.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border: 1px solid #ffd6b5;
  border-radius: 0.75rem;
  background: rgba(255, 244, 232, 0.7);
  cursor: pointer;
  box-shadow: 0 2px 8px #ffd6b5;
  transition: all 0.2s;
}
.user-menu-trigger:hover {
  border-color: #ff6a1a;
}
.user-avatar {
  width: 2.25rem;
  height: 2.25rem;
  background: linear-gradient(135deg, #e0117a 0%, #ff6a1a 100%);
  color: #fff7ed;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
  box-shadow: 0 2px 8px #ffd6b5;
}
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #b34713;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: background 0.2s, color 0.2s;
}
.dropdown-item:hover {
  background: #ffe4d5;
  color: #ff6a1a;
}

.navbar-link {
  color: #6b7280;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0;
  transition: color 0.2s;
}

.navbar-link:hover {
  color: #374151;
}

.navbar-link--active {
  color: #3b82f6;
  border-bottom: 2px solid #3b82f6;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.navbar-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  color: #6b7280;
  transition: all 0.2s;
}

.navbar-button:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.user-menu-trigger:hover {
  border-color: #9ca3af;
}

.user-avatar {
  width: 2rem;
  height: 2rem;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #374151;
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: #f9fafb;
}
</style>
