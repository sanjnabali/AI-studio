<template>
  <div class="h-screen bg-[#0D1117] text-[#E6EDF3] grid" :class="collapsed ? 'grid-rows-[56px_1fr]' : 'grid-rows-[56px_1fr]'">
    <header class="h-14 border-b border-[#30363D] flex items-center justify-between px-4">
      <div class="text-[#00AEEF] font-semibold">Sessions</div>
      <UserMenu />
    </header>

    <div class="grid" :class="collapsed ? 'grid-cols-[64px_1fr]' : 'grid-cols-[256px_1fr]'">
      <SidebarNav :collapsed="collapsed" active="sessions" @toggle="collapsed=!collapsed" @navigate="onNavigate" />
      <main class="min-h-0 overflow-auto p-4">
        <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
          <div class="flex items-center justify-between mb-2">
            <div class="text-sm font-semibold">Conversation History</div>
            <button class="px-3 py-1.5 bg-[#00AEEF] rounded-lg" @click="exportJSON">Export JSON</button>
          </div>
          <div v-if="sessions.length===0" class="text-sm text-gray-400">No sessions yet.</div>
          <div v-else class="divide-y divide-[#30363D]">
            <div v-for="s in sessions" :key="s.id" class="py-2 flex items-center justify-between">
              <div class="text-sm">{{ s.name }}</div>
              <div class="flex items-center gap-2">
                <button class="px-2 py-1 text-xs bg-white/10 rounded" @click="open(s.id)">Open</button>
                <button class="px-2 py-1 text-xs bg-red-500/20 text-red-300 rounded" @click="remove(s.id)">Delete</button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/store/chat'
import SidebarNav from '@/components/layout/SidebarNav.vue'
import UserMenu from '@/components/UserMenu.vue'

const collapsed = ref(false)
const router = useRouter()
const chat = useChatStore()

onMounted(() => chat.loadSessions())

const sessions = computed(() => chat.sessions)

const open = async (id: number) => { await chat.selectSession(id); router.push('/playground') }
const remove = async (id: number) => { await chat.deleteSession(id) }
const exportJSON = () => {
  const blob = new Blob([JSON.stringify(chat.sessions, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'ai-studio-sessions.json'
  a.click()
  URL.revokeObjectURL(url)
}

const onNavigate = (key: string) => {
  const map: Record<string,string> = { chat: '/playground', build: '/code-canvas', docs: '/rag', settings: '/settings' }
  router.push(map[key] || '/')
}
</script>

<style scoped></style>
