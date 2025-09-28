<!-- Frontend/src/components/chat/EnhancedChatWindow.vue -->
<template>
  <div class="flex flex-col h-full bg-white dark:bg-gray-900">
    <!-- Chat Header -->
    <div class="flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
          <ChatBubbleLeftRightIcon class="w-4 h-4 text-white" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ session?.name || 'New Chat' }}
          </h3>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            {{ messageCount }} messages • {{ formatDate(session?.updated_at) }}
          </p>
        </div>
      </div>

      <div class="flex items-center space-x-2">
        <!-- RAG Toggle -->
        <button
          @click="ragEnabled = !ragEnabled"
          :class="[
            'px-3 py-1.5 text-xs font-medium rounded-full border transition-all',
            ragEnabled 
              ? 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900 dark:text-green-100 dark:border-green-700'
              : 'bg-gray-100 text-gray-600 border-gray-300 dark:bg-gray-700 dark:text-gray-400 dark:border-gray-600'
          ]"
          title="Toggle RAG (Retrieval Augmented Generation)"
        >
          <DocumentMagnifyingGlassIcon class="w-3 h-3 inline mr-1" />
          RAG {{ ragEnabled ? 'ON' : 'OFF' }}
        </button>

        <!-- Model Info -->
        <div class="px-3 py-1.5 text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 rounded-full">
          {{ currentModel }}
        </div>

        <!-- More Actions -->
        <DropdownMenu>
          <template #trigger>
            <button class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
              <EllipsisVerticalIcon class="w-5 h-5" />
            </button>
          </template>
          <template #content>
            <button @click="exportChat" class="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700">
              Export Chat
            </button>
            <button @click="clearChat" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 dark:hover:bg-gray-700">
              Clear Chat
            </button>
          </template>
        </DropdownMenu>
      </div>
    </div>

    <!-- Messages Area -->
    <div 
      ref="messagesContainer"
      class="flex-1 overflow-y-auto px-6 py-4 space-y-6"
      @scroll="handleScroll"
    >
      <!-- Welcome Message -->
      <div v-if="messages.length === 0" class="flex items-center justify-center h-full">
        <div class="text-center max-w-md">
          <div class="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <SparklesIcon class="w-8 h-8 text-white" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Welcome to AI Studio
          </h3>
          <p class="text-gray-600 dark:text-gray-400 mb-4">
            Start a conversation, upload files, or use voice input to interact with your AI assistant.
          </p>
          <div class="flex flex-wrap gap-2 justify-center">
            <button 
              v-for="suggestion in quickSuggestions"
              :key="suggestion"
              @click="sendQuickMessage(suggestion)"
              class="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div
        v-for="(message, index) in messages"
        :key="message.id || index"
        :class="[
          'flex',
          message.role === 'user' ? 'justify-end' : 'justify-start'
        ]"
      >
        <div
          :class="[
            'max-w-3xl rounded-2xl px-6 py-4 shadow-sm',
            message.role === 'user'
              ? 'bg-blue-600 text-white ml-12'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white mr-12'
          ]"
        >
          <!-- Message Header -->
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center space-x-2">
              <div class="w-6 h-6 rounded-full bg-white bg-opacity-20 flex items-center justify-center">
                <component 
                  :is="message.role === 'user' ? UserIcon : CpuChipIcon" 
                  class="w-3 h-3"
                />
              </div>
              <span class="text-xs font-medium opacity-75">
                {{ message.role === 'user' ? 'You' : 'AI Assistant' }}
              </span>
            </div>
            <span class="text-xs opacity-50">
              {{ formatTime(message.timestamp) }}
            </span>
          </div>

          <!-- Message Content -->
          <MessageContent 
            :message="message"
            :is-user="message.role === 'user'"
            @copy="copyMessage"
            @regenerate="regenerateMessage"
          />

          <!-- Message Metadata (for assistant messages) -->
          <div 
            v-if="message.role === 'assistant' && message.metadata"
            class="mt-3 pt-3 border-t border-white border-opacity-20"
          >
            <div class="flex items-center justify-between text-xs opacity-75">
              <div class="flex items-center space-x-4">
                <span>{{ message.metadata.processing_time?.toFixed(2) }}s</span>
                <span>{{ message.metadata.token_count }} tokens</span>
                <span v-if="message.metadata.model_used">{{ message.metadata.model_used }}</span>
              </div>
              
              <!-- Sources (for RAG responses) -->
              <button
                v-if="message.metadata.sources && message.metadata.sources.length > 0"
                @click="showSources(message.metadata.sources)"
                class="flex items-center space-x-1 hover:underline"
              >
                <DocumentIcon class="w-3 h-3" />
                <span>{{ message.metadata.sources.length }} sources</span>
              </button>
            </div>
          </div>

          <!-- Message Actions -->
          <div 
            v-if="message.role === 'assistant'"
            class="flex items-center justify-end space-x-2 mt-3 pt-2 border-t border-white border-opacity-20"
          >
            <button
              @click="copyMessage(message.content)"
              class="p-1.5 rounded hover:bg-white hover:bg-opacity-20 transition-colors"
              title="Copy message"
            >
              <ClipboardIcon class="w-4 h-4" />
            </button>
            
            <button
              @click="speakMessage(message.content)"
              class="p-1.5 rounded hover:bg-white hover:bg-opacity-20 transition-colors"
              title="Read aloud"
            >
              <SpeakerWaveIcon class="w-4 h-4" />
            </button>
            
            <button
              @click="regenerateMessage(message)"
              class="p-1.5 rounded hover:bg-white hover:bg-opacity-20 transition-colors"
              title="Regenerate response"
            >
              <ArrowPathIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="isTyping" class="flex justify-start">
        <div class="bg-gray-100 dark:bg-gray-800 rounded-2xl px-6 py-4 mr-12">
          <div class="flex items-center space-x-2">
            <div class="w-6 h-6 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
              <CpuChipIcon class="w-3 h-3 text-white" />
            </div>
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-6">
      <!-- File Attachments Preview -->
      <div v-if="attachments.length > 0" class="mb-4">
        <div class="flex flex-wrap gap-2">
          <div
            v-for="(attachment, index) in attachments"
            :key="index"
            class="flex items-center space-x-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg"
          >
            <component :is="getFileIcon(attachment.type)" class="w-4 h-4 text-gray-500" />
            <span class="text-sm text-gray-700 dark:text-gray-300">{{ attachment.name }}</span>
            <button
              @click="removeAttachment(index)"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
            >
              <XMarkIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Input Controls -->
      <div class="flex items-end space-x-4">
        <!-- File Upload -->
        <div class="flex space-x-1">
          <label class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer transition-colors">
            <input
              type="file"
              multiple
              @change="handleFileUpload"
              accept="image/*,audio/*,.pdf,.docx,.txt,.py,.js,.ts,.java,.cpp,.c,.go,.rs,.php,.rb"
              class="hidden"
            />
            <PaperClipIcon class="w-5 h-5" />
          </label>

          <button
            @click="showImageGenerator = !showImageGenerator"
            class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Generate image"
          >
            <PhotoIcon class="w-5 h-5" />
          </button>

          <button
            @click="showCodeGenerator = !showCodeGenerator"
            class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Generate code"
          >
            <CodeBracketIcon class="w-5 h-5" />
          </button>
        </div>

        <!-- Voice Input -->
        <VoiceRecorder
          @start="handleVoiceStart"
          @stop="handleVoiceStop"
          @transcript="handleVoiceInput"
          :is-recording="isRecording"
        />

        <!-- Text Input -->
        <div class="flex-1 relative">
          <textarea
            ref="textInput"
            v-model="inputMessage"
            @keydown="handleKeyDown"
            @input="handleInput"
            placeholder="Type your message... (Shift+Enter for new line)"
            :disabled="isLoading || isTyping"
            class="w-full px-4 py-3 pr-12 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all"
            :class="{ 'cursor-not-allowed opacity-50': isLoading || isTyping }"
            rows="1"
            style="min-height: 48px; max-height: 120px;"
          ></textarea>

          <!-- Character count -->
          <div
            v-if="inputMessage.length > 500"
            class="absolute bottom-2 right-12 text-xs text-gray-400"
          >
            {{ inputMessage.length }}/2000
          </div>
        </div>

        <!-- Send Button -->
        <button
          @click="sendMessage"
          :disabled="!canSend || isLoading || isTyping"
          :class="[
            'px-4 py-3 rounded-xl font-medium transition-all',
            canSend && !isLoading && !isTyping
              ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg'
              : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
          ]"
        >
          <PaperAirplaneIcon v-if="!isLoading" class="w-5 h-5" />
          <div v-else class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        </button>
      </div>

      <!-- Quick Actions -->
      <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div class="flex items-center space-x-2">
          <button
            v-for="action in quickActions"
            :key="action.name"
            @click="executeQuickAction(action)"
            class="px-3 py-1.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            {{ action.name }}
          </button>
        </div>

        <div class="flex items-center space-x-3 text-xs text-gray-500 dark:text-gray-400">
          <div class="flex items-center space-x-1">
            <div :class="['w-2 h-2 rounded-full', connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500']"></div>
            <span>{{ connectionStatus }}</span>
          </div>
          <span>{{ messageCount }} / ∞ messages</span>
        </div>
      </div>

      <!-- Expandable Panels -->
      <ImageGeneratorPanel
        v-if="showImageGenerator"
        @close="showImageGenerator = false"
        @generate="handleImageGeneration"
      />

      <CodeGeneratorPanel
        v-if="showCodeGenerator"
        @close="showCodeGenerator = false"
        @generate="handleCodeGeneration"
      />
    </div>

    <!-- Modals -->
    <SourcesModal
      v-if="showSourcesModal"
      :sources="selectedSources"
      @close="showSourcesModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useTextToSpeech } from '@/composables/useTextToSpeech'
import { useClipboard } from '@/composables/useClipboard'
import { useAutoResize } from '@/composables/useAutoResize'
import { useChatStore } from '@/store/chat'
import { useSettingsStore } from '@/store/settings'
import { useNotificationStore } from '@/store/notification'
import { apiClient } from '@/api/client'

// Icons
import {
  ChatBubbleLeftRightIcon,
  UserIcon,
  CpuChipIcon,
  SparklesIcon,
  DocumentMagnifyingGlassIcon,
  EllipsisVerticalIcon,
  ClipboardIcon,
  SpeakerWaveIcon,
  ArrowPathIcon,
  PaperClipIcon,
  PhotoIcon,
  CodeBracketIcon,
  PaperAirplaneIcon,
  XMarkIcon,
  DocumentIcon,
  MicrophoneIcon
} from '@heroicons/vue/24/outline'

// Components
import MessageContent from './MessageContent.vue'
import VoiceRecorder from './VoiceRecorder.vue'
import DropdownMenu from './DropdownMenu.vue'
import ImageGeneratorPanel from './ImageGeneratorPanel.vue'
import CodeGeneratorPanel from './CodeGeneratorPanel.vue'
import SourcesModal from './SourcesModal.vue'

// Props
interface Props {
  session?: any
}

const props = withDefaults(defineProps<Props>(), {
  session: null
})

// Emits
const emit = defineEmits<{
  message: [content: string, options?: any]
  'voice-input': [transcript: string]
  'file-upload': [files: FileList]
}>()

// Stores
const chatStore = useChatStore()
const settingsStore = useSettingsStore()
const notificationStore = useNotificationStore()

// Composables
const { speak, isSupported: ttsSupported } = useTextToSpeech()
const { copy } = useClipboard()

// Refs
const messagesContainer = ref<HTMLElement>()
const textInput = ref<HTMLTextAreaElement>()

// State
const inputMessage = ref('')
const attachments = ref<File[]>([])
const isRecording = ref(false)
const isLoading = ref(false)
const isTyping = ref(false)
const ragEnabled = ref(false)
const showImageGenerator = ref(false)
const showCodeGenerator = ref(false)
const showSourcesModal = ref(false)
const selectedSources = ref<any[]>([])
const connectionStatus = ref<'connected' | 'connecting' | 'disconnected'>('connected')

// Computed
const messages = computed(() => chatStore.messages)
const messageCount = computed(() => messages.value.length)
const currentModel = computed(() => settingsStore.modelSettings.model_name)
const canSend = computed(() => {
  return (inputMessage.value.trim().length > 0 || attachments.value.length > 0) &&
         inputMessage.value.length <= 2000
})

const quickSuggestions = [
  "Explain this concept",
  "Write code for",
  "Summarize document",
  "Generate image"
]

const quickActions = [
  { name: "Summarize", action: "summarize" },
  { name: "Translate", action: "translate" },
  { name: "Code Review", action: "review" },
  { name: "Explain", action: "explain" }
]

// Lifecycle
onMounted(() => {
  scrollToBottom()
  textInput.value?.focus()
  
  // Auto-resize textarea
  useAutoResize(textInput)
})

// Watch for new messages
watch(() => messages.value.length, () => {
  nextTick(() => scrollToBottom())
})

watch(() => chatStore.isTyping, (typing) => {
  isTyping.value = typing
  if (typing) {
    nextTick(() => scrollToBottom())
  }
})

// Methods
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const handleScroll = () => {
  // Implement pagination or scroll-based features
  const container = messagesContainer.value
  if (!container) return
  
  if (container.scrollTop === 0) {
    // Load more messages if needed
    loadMoreMessages()
  }
}

const loadMoreMessages = async () => {
  // Implement message pagination
}

// Input Handling
const handleInput = () => {
  // Auto-resize textarea
  if (textInput.value) {
    textInput.value.style.height = 'auto'
    textInput.value.style.height = `${Math.min(textInput.value.scrollHeight, 120)}px`
  }
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const sendMessage = async () => {
  if (!canSend.value) return

  const message = inputMessage.value.trim()
  const files = [...attachments.value]

  // Clear input immediately for better UX
  inputMessage.value = ''
  attachments.value = []
  
  // Reset textarea height
  if (textInput.value) {
    textInput.value.style.height = '48px'
  }

  try {
    isLoading.value = true

    // Handle file attachments
    if (files.length > 0) {
      await handleAttachedFiles(files)
    }

    // Send message with options
    const options = {
      use_rag: ragEnabled.value,
      temperature: settingsStore.modelSettings.temperature,
      max_tokens: settingsStore.modelSettings.max_tokens
    }

    emit('message', message, options)

  } catch (error) {
    console.error('Failed to send message:', error)
    notificationStore.error('Failed to send message')
  } finally {
    isLoading.value = false
  }
}

const sendQuickMessage = (suggestion: string) => {
  inputMessage.value = suggestion
  nextTick(() => textInput.value?.focus())
}

// File Handling
const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files || files.length === 0) return

  for (const file of Array.from(files)) {
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      notificationStore.error(`File "${file.name}" is too large (max 10MB)`)
      continue
    }
    
    attachments.value.push(file)
  }

  // Reset input
  target.value = ''
}

const handleAttachedFiles = async (files: File[]) => {
  for (const file of files) {
    try {
      if (file.type.startsWith('image/')) {
        await handleImageFile(file)
      } else if (file.type.startsWith('audio/')) {
        await handleAudioFile(file)
      } else {
        await handleDocumentFile(file)
      }
    } catch (error) {
      console.error(`Failed to process file ${file.name}:`, error)
      notificationStore.error(`Failed to process file "${file.name}"`)
    }
  }
}

const handleImageFile = async (file: File) => {
  // Convert file to base64 string for API
  const reader = new FileReader()
  reader.onload = async () => {
    const imageData = reader.result as string
    const response = await apiClient.analyzeImage(imageData)
    notificationStore.success(`Image "${file.name}" analyzed successfully`)
  }
  reader.readAsDataURL(file)
}

const handleAudioFile = async (file: File) => {
  const response = await apiClient.speechToText(file)
  inputMessage.value += response.text
}

const handleDocumentFile = async (file: File) => {
  const response = await apiClient.uploadDocument(file)
  ragEnabled.value = true
  notificationStore.success(`Document "${file.name}" uploaded and indexed for RAG`)
}

const removeAttachment = (index: number) => {
  attachments.value.splice(index, 1)
}

const getFileIcon = (type: string) => {
  if (type.startsWith('image/')) return PhotoIcon
  if (type.startsWith('audio/')) return MicrophoneIcon
  if (type.includes('pdf')) return DocumentIcon
  return DocumentIcon
}

// Voice Handling
const handleVoiceStart = () => {
  isRecording.value = true
}

const handleVoiceStop = () => {
  isRecording.value = false
}

const handleVoiceInput = (transcript: string) => {
  inputMessage.value += transcript
  emit('voice-input', transcript)
}

// Message Actions
const copyMessage = async (content: string) => {
  try {
    await copy(content)
    notificationStore.success('Message copied to clipboard')
  } catch (error) {
    notificationStore.error('Failed to copy message')
  }
}

const speakMessage = async (content: string) => {
  if (!ttsSupported) {
    notificationStore.error('Text-to-speech not supported in this browser')
    return
  }

  try {
    await speak(content)
  } catch (error) {
    notificationStore.error('Failed to speak message')
  }
}

const regenerateMessage = async (message: any) => {
  try {
    // Find the user message that triggered this response
    const messageIndex = messages.value.findIndex(m => m.id === message.id)
    if (messageIndex > 0) {
      const userMessage = messages.value[messageIndex - 1]
      if (userMessage.role === 'user') {
        // Remove the assistant message and regenerate
        chatStore.messages.splice(messageIndex, 1)
        emit('message', userMessage.content)
      }
    }
  } catch (error) {
    notificationStore.error('Failed to regenerate message')
  }
}

const showSources = (sources: any[]) => {
  selectedSources.value = sources
  showSourcesModal.value = true
}

// Quick Actions
const executeQuickAction = async (action: any) => {
  let prompt = ''
  
  switch (action.action) {
    case 'summarize':
      prompt = 'Please provide a concise summary of our conversation.'
      break
    case 'translate':
      prompt = 'Please translate the last message to Spanish.'
      break
    case 'review':
      prompt = 'Please review any code in our conversation and provide feedback.'
      break
    case 'explain':
      prompt = 'Please explain the last concept discussed in simple terms.'
      break
  }
  
  if (prompt) {
    inputMessage.value = prompt
    await sendMessage()
  }
}

// Generation Handlers
const handleImageGeneration = async (prompt: string, options: any) => {
  try {
    isLoading.value = true
    const response = await apiClient.generateImage(prompt, options)
    
    // Add image to chat
    chatStore.messages.push({
      role: 'assistant',
      content: `Generated image: "${prompt}"`,
      message_type: 'image',
      timestamp: new Date().toISOString(),
      metadata: {
        image_data: response.image_data,
        prompt,
        ...options
      }
    })
    
    notificationStore.success('Image generated successfully')
  } catch (error) {
    notificationStore.error('Failed to generate image')
  } finally {
    isLoading.value = false
    showImageGenerator.value = false
  }
}

const handleCodeGeneration = async (prompt: string, language: string, options: any) => {
  try {
    isLoading.value = true
    const fullPrompt = `Generate ${language} code for: ${prompt}`
    
    const generationOptions = {
      ...options,
      generate_code: true,
      language
    }
    
    emit('message', fullPrompt, generationOptions)
  } catch (error) {
    notificationStore.error('Failed to generate code')
  } finally {
    isLoading.value = false
    showCodeGenerator.value = false
  }
}

// Chat Management
const exportChat = () => {
  const chatData = {
    session: props.session,
    messages: messages.value,
    exportDate: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `chat-${props.session?.name || 'session'}-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  notificationStore.success('Chat exported successfully')
}

const clearChat = () => {
  if (confirm('Are you sure you want to clear this chat? This action cannot be undone.')) {
    chatStore.clearMessages()
    notificationStore.success('Chat cleared successfully')
  }
}

// Utility Functions
const formatDate = (dateString: string | undefined) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const formatTime = (timestamp: string | undefined) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
/* Custom scrollbar for messages container */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgb(156 163 175 / 0.5);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgb(156 163 175 / 0.8);
}

/* Smooth scrolling */
.overflow-y-auto {
  scroll-behavior: smooth;
}

/* Message animations */
.message-enter-active {
  transition: all 0.3s ease-out;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

/* Typing indicator animation */
@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  } 40% {
    transform: scale(1);
  }
}

.animate-bounce {
  animation: bounce 1.4s infinite ease-in-out both;
}

/* Input focus styles */
textarea:focus {
  box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1);
}

/* File attachment styles */
.attachment-preview {
  transition: all 0.2s ease;
}

.attachment-preview:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

/* Responsive design */
@media (max-width: 768px) {
  .max-w-3xl {
    max-width: none;
  }
  
  .ml-12, .mr-12 {
    margin-left: 1rem;
    margin-right: 1rem;
  }
}
</style>