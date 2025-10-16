<template>
  <div class="enhanced-chat-window flex-1 flex flex-col">
    <!-- Messages -->
    <div ref="scrollArea" class="flex-1 overflow-y-auto p-4 space-y-4 bg-transparent">
      <template v-if="chatMessages.length">
        <div v-for="(message, idx) in chatMessages" :key="idx" :class="message.role === 'user' ? 'text-right' : 'text-left'">
          <div :class="[
            'inline-block px-4 py-3 rounded-2xl max-w-[75%] shadow-sm',
            message.role === 'user'
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
          ]">
            <MessageContent :message="message" :isUser="message.role === 'user'" />
          </div>
        </div>
      </template>
      <div v-else class="h-full flex items-center justify-center text-sm text-gray-500 dark:text-gray-400">
        Type a message below to start chatting.
      </div>
    </div>

    <!-- Composer -->
    <div class="border-t border-gray-200 dark:border-gray-700 p-4 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-gray-900/60">
      <div class="flex items-end gap-2">
        <div class="flex-1 relative">
          <textarea
            v-model="draft"
            @keydown.enter.exact.prevent="send"
            @input="autoResize"
            ref="textareaRef"
            rows="1"
            placeholder="Ask anything..."
            class="w-full resize-none rounded-2xl bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 px-4 py-3 leading-6"
          />
          <div class="absolute left-2 bottom-2 flex gap-1">
            <input ref="fileInput" type="file" class="hidden" multiple @change="onFiles" />
            <button class="icon-btn" title="Attach files" @click.prevent="fileInput?.click()">
              <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M7 7v10a5 5 0 0 0 10 0V7a3 3 0 0 0-6 0v9a1 1 0 0 0 2 0V7h2v9a3 3 0 0 1-6 0V7a5 5 0 1 1 10 0v10a7 7 0 1 1-14 0V7z"/></svg>
            </button>
            <button class="icon-btn" title="Voice input" @click.prevent="emitVoice">
              <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V5a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3zm-1 1.93A7.001 7.001 0 0 1 5 9h2a5 5 0 1 0 10 0h2a7.001 7.001 0 0 1-6 6.93V19h3v2H8v-2h3v-3.07z"/></svg>
            </button>
          </div>
        </div>
        <button :disabled="!canSend" @click="send" class="send-btn" title="Send">
          <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useChatStore } from '@/store/chat'
import MessageContent from '@/components/MessageContent.vue'

interface Props { session: any }
const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'message', message: string, options?: any): void
  (e: 'voiceInput', audioBlob: Blob): void
  (e: 'fileUpload', files: FileList): void
}>()

const chatStore = useChatStore()
const draft = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const scrollArea = ref<HTMLDivElement | null>(null)

const chatMessages = computed(() => chatStore.messages)
const canSend = computed(() => draft.value.trim().length > 0 && !chatStore.loading)

const autoResize = () => {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}

const scrollToBottom = async () => {
  await nextTick()
  scrollArea.value?.scrollTo({ top: scrollArea.value.scrollHeight, behavior: 'smooth' })
}

const onFiles = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length) emit('fileUpload', target.files)
  target.value = ''
}

const send = async () => {
  if (!canSend.value) return
  const text = draft.value.trim()
  draft.value = ''
  autoResize()
  emit('message', text)
  await scrollToBottom()
}

const emitVoice = () => {
  try {
    const blob = new Blob([], { type: 'audio/wav' })
    emit('voiceInput', blob)
  } catch (e) {
    // Fallback to window.Blob for older TS template inference
    const blob = new (window as any).Blob([])
    emit('voiceInput', blob)
  }
}

onMounted(scrollToBottom)
</script>

<style scoped>
.icon-btn { @apply p-1.5 rounded-full text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors; }
.send-btn { @apply p-3 rounded-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white shadow-md transition-colors; }
</style>
