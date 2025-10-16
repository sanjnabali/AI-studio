<template>
  <div class="h-screen bg-[#0D1117] text-[#E6EDF3] grid" :class="collapsed ? 'grid-rows-[56px_1fr]' : 'grid-rows-[56px_1fr]'">
    <header class="h-14 border-b border-[#30363D] flex items-center justify-between px-4">
      <div class="text-[#00AEEF] font-semibold">Security Center</div>
      <UserMenu />
    </header>

    <div class="grid" :class="collapsed ? 'grid-cols-[64px_1fr]' : 'grid-cols-[256px_1fr]'">
      <SidebarNav :collapsed="collapsed" active="security" @toggle="collapsed=!collapsed" @navigate="onNavigate" />
      <main class="min-h-0 overflow-auto p-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
          <div class="text-sm font-semibold mb-3">API Key</div>
          <div class="flex items-center gap-2">
            <input v-model="apiKey" class="flex-1 bg-[#0D1117] border border-[#30363D] rounded-lg p-2 text-sm" readonly />
            <button class="px-3 py-2 bg-[#00AEEF] rounded-lg" @click="regenerate">Regenerate</button>
          </div>
        </div>
        <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
          <div class="text-sm font-semibold mb-3">Password</div>
          <div class="space-y-2">
            <input v-model="currentPassword" type="password" class="w-full bg-[#0D1117] border border-[#30363D] rounded-lg p-2 text-sm" placeholder="Current password" />
            <input v-model="newPassword" type="password" class="w-full bg-[#0D1117] border border-[#30363D] rounded-lg p-2 text-sm" placeholder="New password" />
            <button class="px-3 py-2 bg-white/10 rounded-lg" @click="changePassword">Change Password</button>
          </div>
          <p class="text-xs text-gray-500 mt-2">Password change is not implemented on the backend; this is a stub action.</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import SidebarNav from '@/components/layout/SidebarNav.vue'
import UserMenu from '@/components/UserMenu.vue'
import { apiClient } from '@/api/client'

const collapsed = ref(false)
const router = useRouter()

const apiKey = ref('')
const currentPassword = ref('')
const newPassword = ref('')

const regenerate = async () => {
  try {
    const res = await fetch('/api/auth/regenerate-api-key', { method: 'POST' })
    const data = await res.json()
    apiKey.value = data.api_key || ''
  } catch {}
}

const changePassword = async () => {
  try { await apiClient.changePassword({ currentPassword: currentPassword.value, newPassword: newPassword.value }) } catch {}
}

const onNavigate = (key: string) => {
  const map: Record<string,string> = { chat: '/playground', build: '/code-canvas', docs: '/rag', settings: '/settings' }
  router.push(map[key] || '/')
}
</script>

<style scoped></style>
