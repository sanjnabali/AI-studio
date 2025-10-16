<template>
  <div class="h-screen bg-[#0D1117] text-[#E6EDF3] grid" :class="collapsed ? 'grid-rows-[56px_1fr]' : 'grid-rows-[56px_1fr]'">
    <header class="h-14 border-b border-[#30363D] flex items-center justify-between px-4">
      <div class="flex items-center gap-3">
        <div class="text-[#00AEEF] font-semibold">AI Playground</div>
      </div>
      <div class="flex items-center gap-2">
        <UserMenu />
      </div>
    </header>

    <div class="grid" :class="collapsed ? 'grid-cols-[64px_1fr_320px]' : 'grid-cols-[256px_1fr_320px]'">
      <SidebarNav :collapsed="collapsed" active="chat" @toggle="collapsed=!collapsed" @navigate="onNavigate" />
      <main class="min-h-0 overflow-hidden flex flex-col">
        <Suspense>
          <template #default>
            <EnhancedChatWindow
              :session="chatStore.currentSession"
              @message="handleChatMessage"
              @voice-input="handleVoiceInput"
              @file-upload="handleFileUpload"
            />
          </template>
          <template #fallback>
            <div class="flex-1 p-4">
              <div class="h-full rounded-xl border border-[#30363D] bg-[#161B22] animate-pulse" />
            </div>
          </template>
        </Suspense>
      </main>
      <RightSettings v-model:temperature="temperature" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/store/chat'
import { useSettingsStore } from '@/store/settings'
import SidebarNav from '@/components/layout/SidebarNav.vue'
import RightSettings from '@/components/layout/RightSettings.vue'
import EnhancedChatWindow from '@/components/chat/EnhancedChatWindow.vue'
import UserMenu from '@/components/UserMenu.vue'
import { apiClient } from '@/api/client'

const router = useRouter()
const chatStore = useChatStore()
const settingsStore = useSettingsStore()

const collapsed = ref(false)
const temperature = ref(1.0)

onMounted(async () => {
  await chatStore.loadSessions()
  if (!chatStore.currentSession && chatStore.sessions[0]) {
    await chatStore.selectSession(chatStore.sessions[0].id)
  }
})

const handleChatMessage = async (message: string) => {
  await chatStore.sendMessage(message, chatStore.currentSessionId, {
    ...settingsStore.modelSettings,
    temperature: Number(temperature.value)
  })
}

const handleVoiceInput = async (audio: Blob) => {
  const transcript = await apiClient.speechToText(audio)
  await handleChatMessage(transcript.text)
}

const handleFileUpload = async (_files: FileList) => {}

const onNavigate = (key: string) => {
  const map: Record<string,string> = {
    chat: '/playground',
    build: '/code-canvas',
    docs: '/rag',
    settings: '/settings'
  }
  router.push(map[key] || '/')
}
</script>

<style scoped></style>
