<!-- Frontend/src/components/chatbot_window.vue -->
<template>
  <div class="chat-window">
    <!-- Chat Header -->
    <div class="chat-header">
      <div class="session-info">
        <h3 v-if="chatStore.currentSession">
          {{ chatStore.currentSession.name }}
        </h3>
        <span v-else class="text-gray-500">No session selected</span>
      </div>
      <div class="chat-actions">
        <button 
          @click="toggleSettings"
          class="btn btn-ghost btn-sm"
          title="Settings"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
        <button 
          @click="clearChat"
          class="btn btn-ghost btn-sm"
          title="Clear Chat"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Messages Area -->
    <div class="messages-container" ref="messagesContainer">
      <div v-if="!chatStore.hasMessages" class="empty-state">
        <div class="text-center py-12">
          <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-500 mb-2">Start a conversation</h3>
          <p class="text-gray-400">Ask me anything or upload a document to analyze</p>
        </div>
      </div>

      <div v-for="message in chatStore.messages" :key="message.id || message.timestamp" class="message">
        <div :class="['message-bubble', message.role]">
          <div class="message-header">
            <span class="message-role">{{ message.role === 'user' ? 'You' : 'AI Assistant' }}</span>
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
          </div>
          
          <div class="message-content">
            <div v-if="message.message_type === 'code'" class="code-block">
              <pre><code>{{ message.content }}</code></pre>
            </div>
            <div v-else-if="message.message_type === 'image'" class="image-block">
              <img :src="message.content" alt="Generated image" class="max-w-full h-auto rounded" />
            </div>
            <div v-else class="text-content" v-html="formatMessage(message.content)"></div>
          </div>

          <div v-if="message.metadata && message.role === 'assistant'" class="message-metadata">
            <small class="text-gray-500">
              Model: {{ message.metadata.model_used }} | 
              Time: {{ message.metadata.processing_time?.toFixed(2) }}s |
              Tokens: {{ message.metadata.token_count }}
            </small>
            <div v-if="message.metadata.sources" class="sources mt-2">
              <details class="text-sm">
                <summary class="cursor-pointer text-blue-600">Sources ({{ message.metadata.sources.length }})</summary>
                <ul class="mt-2 space-y-1">
                  <li v-for="source in message.metadata.sources" :key="source.document" 
                      class="bg-gray-100 dark:bg-gray-800 p-2 rounded">
                    <strong>{{ source.document }}</strong>
                    <span class="text-gray-600"> ({{ (source.similarity * 100).toFixed(1) }}% match)</span>
                  </li>
                </ul>
              </details>
            </div>
          </div>
        </div>
      </div>

      <div v-if="chatStore.isTyping" class="typing-indicator">
        <div class="message-bubble assistant">
          <div class="typing-animation">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="chat-input">
      <div class="input-container">
        <div class="flex items-end space-x-2">
          <!-- File upload -->
          <label class="file-upload-btn">
            <input 
              type="file" 
              @change="handleFileUpload" 
              accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
              class="hidden"
            />
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
            </svg>
          </label>

          <!-- Voice input -->
          <VoiceRecorder @transcript="handleVoiceInput" />

          <!-- Text input -->
          <div class="flex-1">
            <textarea
              v-model="inputMessage"
              @keydown="handleKeyDown"
              placeholder="Type your message..."
              class="textarea textarea-bordered w-full resize-none"
              rows="1"
              :disabled="chatStore.loading || chatStore.isTyping"
            ></textarea>
          </div>

          <!-- Send button -->
          <button 
            @click="sendMessage"
            :disabled="!inputMessage.trim() || chatStore.loading || chatStore.isTyping"
            class="btn btn-primary"
          >
            <svg v-if="!chatStore.loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            <span v-else class="loading loading-spinner loading-sm"></span>
          </button>
        </div>

        <!-- Input options -->
        <div v-if="showInputOptions" class="input-options mt-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div class="grid grid-cols-2 gap-4">
            <label class="flex items-center">
              <input type="checkbox" v-model="useRAG" class="checkbox checkbox-sm" />
              <span class="ml-2 text-sm">Use uploaded documents</span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" v-model="generateCode" class="checkbox checkbox-sm" />
              <span class="ml-2 text-sm">Generate code</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettings" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">Chat Settings</h3>
        
        <ModelSelector 
          :model-config="settingsStore.modelSettings" 
          @update="handleSettingsUpdate" 
        />
        
        <div class="modal-action">
          <button @click="showSettings = false" class="btn">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from 'vue'
import { useChatStore } from '../store/chat'
import { useSettingsStore } from '../store/settings'
import VoiceRecorder from './VoiceRecorder.vue'
import ModelSelector from './ModelSelector.vue'
import { apiClient } from '../api/client'

const chatStore = useChatStore()
const settingsStore = useSettingsStore()

const inputMessage = ref('')
const showSettings = ref(false)
const showInputOptions = ref(false)
const useRAG = ref(false)
const generateCode = ref(false)
const messagesContainer = ref<HTMLElement>()

// Auto-scroll to bottom when new messages arrive
watch(() => chatStore.messages.length, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
})

onMounted(() => {
  chatStore.loadSessions()
})

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const message = inputMessage.value
  inputMessage.value = ''

  try {
    let sessionId = chatStore.currentSessionId

    // Create new session if none exists
    if (!sessionId) {
      const session = await chatStore.createSession()
      sessionId = session.id
    }

    const modelConfig = useRAG.value || generateCode.value 
      ? { ...settingsStore.modelSettings, use_rag: useRAG.value, generate_code: generateCode.value }
      : settingsStore.modelSettings

    if (useRAG.value) {
      // Use RAG query endpoint
      const response = await apiClient.queryDocuments(message, undefined, modelConfig)
      
      // Add user message
      chatStore.messages.push({
        role: 'user',
        content: message,
        message_type: 'text',
        timestamp: new Date().toISOString()
      })

      // Add assistant response with sources
      chatStore.messages.push({
        role: 'assistant',
        content: response.response,
        message_type: 'text',
        timestamp: new Date().toISOString(),
        metadata: {
          model_used: response.model_used,
          processing_time: response.processing_time,
          token_count: response.token_count,
          sources: response.sources
        }
      })
    } else {
      await chatStore.sendMessage(message, sessionId, modelConfig)
    }
  } catch (error) {
    console.error('Error sending message:', error)
  }
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    if (file.type.startsWith('image/')) {
      // Handle image upload for analysis
      const reader = new FileReader()
      reader.onload = async (e) => {
        const base64 = (e.target?.result as string)?.split(',')[1]
        if (base64) {
          const response = await apiClient.analyzeImage(base64, inputMessage.value || 'Describe this image')
          
          // Add messages to chat
          chatStore.messages.push({
            role: 'user',
            content: `[Image uploaded: ${file.name}]`,
            message_type: 'image',
            timestamp: new Date().toISOString()
          })

          chatStore.messages.push({
            role: 'assistant',
            content: response.analysis,
            message_type: 'text',
            timestamp: new Date().toISOString(),
            metadata: {
              confidence: response.confidence
            }
          })
        }
      }
      reader.readAsDataURL(file)
    } else {
      // Handle document upload for RAG
      const response = await apiClient.uploadDocument(file)
      
      // Add confirmation message
      chatStore.messages.push({
        role: 'assistant',
        content: `Document "${file.name}" uploaded successfully! It has been processed into ${response.chunks_processed} chunks and is ready for questions.`,
        message_type: 'text',
        timestamp: new Date().toISOString()
      })

      useRAG.value = true
    }
  } catch (error) {
    console.error('Error handling file upload:', error)
  }

  // Reset input
  target.value = ''
}

const handleVoiceInput = (transcript: string) => {
  inputMessage.value = transcript
}

const toggleSettings = () => {
  showSettings.value = !showSettings.value
}

const clearChat = () => {
  chatStore.clearMessages()
}

const handleSettingsUpdate = (newSettings: any) => {
  settingsStore.updateModelSettings(newSettings)
}

const formatTime = (timestamp: string | undefined): string => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatMessage = (content: string): string => {
  // Basic markdown-like formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="bg-gray-200 dark:bg-gray-700 px-1 rounded">$1</code>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
.chat-window {
  @apply flex flex-col h-full bg-white dark:bg-gray-900;
}

.chat-header {
  @apply flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700;
}

.messages-container {
  @apply flex-1 overflow-y-auto p-4 space-y-4;
  scroll-behavior: smooth;
}

.message-bubble {
  @apply max-w-3xl p-4 rounded-lg;
}

.message-bubble.user {
  @apply bg-blue-600 text-white ml-auto;
}

.message-bubble.assistant {
  @apply bg-gray-100 dark:bg-gray-800 mr-auto;
}

.message-header {
  @apply flex items-center justify-between mb-2 text-sm opacity-75;
}

.message-content {
  @apply break-words;
}

.code-block {
  @apply bg-gray-900 text-green-400 p-3 rounded overflow-x-auto;
}

.code-block pre {
  @apply text-sm font-mono;
}

.message-metadata {
  @apply mt-3 pt-2 border-t border-gray-200 dark:border-gray-600;
}

.chat-input {
  @apply p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800;
}

.file-upload-btn {
  @apply btn btn-ghost btn-sm cursor-pointer;
}

.typing-indicator {
  @apply flex justify-start;
}

.typing-animation {
  @apply flex space-x-1;
}

.typing-animation span {
  @apply w-2 h-2 bg-gray-400 rounded-full animate-bounce;
  animation-delay: calc(var(--i) * 0.1s);
}

.typing-animation span:nth-child(1) { --i: 0; }
.typing-animation span:nth-child(2) { --i: 1; }
.typing-animation span:nth-child(3) { --i: 2; }
</style>
