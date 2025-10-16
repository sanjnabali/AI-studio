<template>
  <div class="h-screen bg-[#0D1117] text-[#E6EDF3] grid" :class="collapsed ? 'grid-rows-[56px_1fr]' : 'grid-rows-[56px_1fr]'">
    <header class="h-14 border-b border-[#30363D] flex items-center justify-between px-4">
      <div class="text-[#00AEEF] font-semibold">Code Canvas</div>
      <UserMenu />
    </header>

    <div class="grid" :class="collapsed ? 'grid-cols-[64px_1fr]' : 'grid-cols-[256px_1fr]'">
      <SidebarNav :collapsed="collapsed" active="build" @toggle="collapsed=!collapsed" @navigate="onNavigate" />
      <main class="min-h-0 overflow-hidden p-4">
        <Suspense>
          <template #default>
            <CodeCanvas @execute="execute" />
          </template>
          <template #fallback>
            <div class="h-96 rounded-xl border border-[#30363D] bg-[#161B22] animate-pulse" />
          </template>
        </Suspense>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { defineAsyncComponent } from 'vue'
import SidebarNav from '@/components/layout/SidebarNav.vue'
import UserMenu from '@/components/UserMenu.vue'
const CodeCanvas = defineAsyncComponent(() => import('@/components/CodeCanvas.vue'))
import { apiClient } from '@/api/client'

const collapsed = ref(false)
const router = useRouter()

const onNavigate = (key: string) => {
  const map: Record<string,string> = { chat: '/playground', build: '/code-canvas', docs: '/rag', settings: '/settings' }
  router.push(map[key] || '/')
}

const execute = async (code: string, language: string) => apiClient.executeCode(code, language)
</script>

<style scoped></style>
