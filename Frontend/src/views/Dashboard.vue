<template>
  <div class="h-screen bg-[#0D1117] text-[#E6EDF3] grid" :class="collapsed ? 'grid-rows-[56px_1fr]' : 'grid-rows-[56px_1fr]'">
    <!-- Top Nav -->
    <header class="h-14 border-b border-[#30363D] flex items-center justify-between px-4">
      <div class="flex items-center gap-4">
        <div class="text-[#00AEEF] font-semibold">AI Studio</div>
        <nav class="hidden lg:flex items-center gap-4 text-sm text-gray-300">
          <RouterLink to="/" class="hover:text-white">Dashboard</RouterLink>
          <RouterLink to="/playground" class="hover:text-white">Workspace</RouterLink>
          <RouterLink to="/model-config" class="hover:text-white">Model Hub</RouterLink>
          <RouterLink to="/rag" class="hover:text-white">Documents</RouterLink>
          <RouterLink to="/settings" class="hover:text-white">Settings</RouterLink>
        </nav>
      </div>
      <div class="flex items-center gap-2">
        <button class="px-3 py-1.5 bg-[#00AEEF] text-white rounded-lg hover:brightness-110" @click="goPlayground">Start Chat</button>
        <UserMenu />
      </div>
    </header>

    <!-- Content -->
    <div class="grid" :class="collapsed ? 'grid-cols-[64px_1fr]' : 'grid-cols-[256px_1fr]'">
      <SidebarNav :collapsed="collapsed" active="home" @toggle="collapsed=!collapsed" @navigate="onNavigate" />
      <main class="min-h-0 overflow-auto p-4 space-y-4">
        <!-- Overview Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
            <div class="text-sm text-gray-400">Active Models</div>
            <div class="mt-2 text-2xl font-semibold">3</div>
          </div>
          <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
            <div class="text-sm text-gray-400">Recent Sessions</div>
            <div class="mt-2 text-2xl font-semibold">12</div>
          </div>
          <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
            <div class="text-sm text-gray-400">System Health</div>
            <div class="mt-2 text-2xl font-semibold text-[#00C853]">OK</div>
          </div>
          <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
            <div class="text-sm text-gray-400">Storage Usage</div>
            <div class="mt-2 text-2xl font-semibold">42%</div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
          <div class="text-sm font-semibold mb-3">Quick Actions</div>
          <div class="flex flex-wrap gap-2">
            <button class="px-3 py-2 bg-[#00AEEF] rounded-lg" @click="goPlayground">Start Chat</button>
            <RouterLink to="/rag" class="px-3 py-2 bg-white/10 rounded-lg">Upload Document</RouterLink>
            <RouterLink to="/code-canvas" class="px-3 py-2 bg-white/10 rounded-lg">Run Code</RouterLink>
            <RouterLink to="/model-config" class="px-3 py-2 bg-white/10 rounded-lg">Open Config</RouterLink>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink, RouterView } from 'vue-router'
import SidebarNav from '@/components/layout/SidebarNav.vue'
import UserMenu from '@/components/UserMenu.vue'

const collapsed = ref(false)
const router = useRouter()

const onNavigate = (key: string) => {
  const map: Record<string,string> = {
    chat: '/playground',
    build: '/code-canvas',
    dashboard: '/',
    docs: '/rag',
    settings: '/settings'
  }
  router.push(map[key] || '/')
}

const goPlayground = () => router.push('/playground')
</script>

<style scoped></style>
