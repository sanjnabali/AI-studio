<template>
  <div class="h-screen overflow-hidden bg-[#0b0f14] text-gray-200">
    <header class="h-14 border-b border-gray-800/60 flex items-center justify-between px-4">
      <div class="flex items-center gap-3">
        <button class="p-2 rounded-md hover:bg-white/5" @click="collapsed=!collapsed">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
        </button>
        <div class="text-white font-semibold">AI Studio</div>
      </div>
      <div class="flex items-center gap-2">
        <button @click="createNewChat" class="px-3 py-1.5 bg-[#4285F4] text-white rounded-lg hover:brightness-110">
          <PlusIcon class="w-4 h-4 inline mr-1"/> New Chat
        </button>
        <UserMenu />
      </div>
    </header>

    <div class="h-[calc(100vh-56px)] grid" :class="collapsed ? 'grid-cols-[64px_1fr_320px]' : 'grid-cols-[256px_1fr_320px]'">
      <!-- Left nav -->
      <SidebarNav :collapsed="collapsed" active="chat" @toggle="collapsed=!collapsed" @navigate="onNavigate" />

      <!-- Center workspace -->
      <main class="h-full overflow-hidden flex flex-col">
        <div class="p-4 border-b border-gray-800/60">
          <ModelGallery @select="onSelectModel" />
        </div>
        <div class="flex-1 min-h-0">
          <EnhancedChatWindow
            :session="chatStore.currentSession"
            @message="handleChatMessage"
            @voice-input="handleVoiceInput"
            @file-upload="handleFileUpload"
          />
        </div>
      </main>

      <!-- Right settings -->
      <RightSettings v-model:temperature="temperature" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/store/chat'
import { useAuthStore } from '@/store/auth'
import { useSettingsStore } from '@/store/settings'
import { useNotificationStore } from '@/store/notification'
import { apiClient } from '@/api/client'
import EnhancedChatWindow from '@/components/chat/EnhancedChatWindow.vue'
import UserMenu from '@/components/UserMenu.vue'
import SidebarNav from '@/components/layout/SidebarNav.vue'
import RightSettings from '@/components/layout/RightSettings.vue'
import ModelGallery from '@/components/ModelGallery.vue'
import { PlusIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const chatStore = useChatStore()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const notificationStore = useNotificationStore()

const collapsed = ref(false)
const currentSessionId = computed(() => chatStore.currentSessionId)
const selectedModel = ref('chat')
const temperature = ref(1.0)

onMounted(async () => {
  try {
    await chatStore.loadSessions()
    if (!chatStore.currentSession && chatStore.sessions[0]) {
      await chatStore.selectSession(chatStore.sessions[0].id)
    }
  } catch (e) {
    console.error(e)
  }
})

const createNewChat = async () => {
  try {
    const session = await chatStore.createSession('New Chat')
    await chatStore.selectSession(session.id)
  } catch (e) {
    notificationStore.error('Failed to create chat')
  }
}

const onNavigate = (key: string) => {
  const map: Record<string,string> = {
    home: '/',
    chat: '/playground',
    build: '/code-canvas',
    docs: '/rag',
    sessions: '/sessions',
    security: '/security',
    config: '/model-config',
    settings: '/settings'
  }
  router.push(map[key] || '/playground')
}

const onSelectModel = (m: any) => {
  if (m.key.includes('gemini')) selectedModel.value = 'chat'
}

const handleChatMessage = async (message: string) => {
  await chatStore.sendMessage(message, chatStore.currentSessionId, {
    ...settingsStore.modelSettings,
    model_type: selectedModel.value,
    temperature: Number(temperature.value)
  })
}

const handleVoiceInput = async (audio: Blob) => {
  try {
    const transcript = await apiClient.speechToText(audio)
    await handleChatMessage(transcript.text)
  } catch (e) {
    notificationStore.error('Voice input failed')
  }
}

const handleFileUpload = async (_files: FileList) => {
  // Hook for future multimodal features
}
</script>

<style scoped>
</style>
