<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Sidebar -->
    <div class="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-xl font-semibold text-gray-900 dark:text-white">AI Studio</h1>
          <button
            @click="createNewChat"
            class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="New Chat"
          >
            <PlusIcon class="w-5 h-5" />
          </button>
        </div>
        
        <!-- Quick Actions -->
        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="action in quickActions"
            :key="action.id"
            @click="selectQuickAction(action)"
            class="flex flex-col items-center p-2 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-center transition-colors"
            :class="{ 'bg-blue-100 dark:bg-blue-900/20 text-blue-600': selectedAction === action.id }"
          >
            <component :is="action.icon" class="w-4 h-4 mb-1" />
            {{ action.name }}
          </button>
        </div>
      </div>

      <!-- Chat List -->
      <div class="flex-1 overflow-y-auto p-4">
        <div class="space-y-2">
          <div
            v-for="chat in chatStore.chats"
            :key="chat.id"
            class="group relative"
          >
            <div
              @click="selectChat(chat.id)"
              class="p-3 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              :class="{
                'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500': chatStore.activeChat?.id === chat.id
              }"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-gray-900 dark:text-white text-sm truncate">
                    {{ chat.title }}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center space-x-2">
                    <span>{{ formatDate(chat.updated) }}</span>
                    <span>•</span>
                    <span>{{ chat.messages.length }} msgs</span>
                  </div>
                </div>
                
                <!-- Chat Actions -->
                <div class="opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-1">
                  <button
                    @click.stop="editChatTitle(chat)"
                    class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded"
                  >
                    <PencilIcon class="w-3 h-3" />
                  </button>
                  <button
                    @click.stop="deleteChat(chat.id)"
                    class="p-1 text-gray-400 hover:text-red-600 rounded"
                  >
                    <TrashIcon class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-if="!chatStore.chats.length" class="text-center py-8">
            <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-3">
              <SparklesIcon class="w-6 h-6 text-white" />
            </div>
            <p class="text-sm text-gray-500 dark:text-gray-400">No conversations yet</p>
            <button
              @click="createNewChat"
              class="mt-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800"
            >
              Start your first chat
            </button>
          </div>
        </div>
      </div>

      <!-- Settings Panel Toggle -->
      <div class="p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="showSettings = !showSettings"
          class="w-full p-2 text-left text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg flex items-center justify-between transition-colors"
        >
          <div class="flex items-center space-x-2">
            <CogIcon class="w-4 h-4" />
            <span>Settings</span>
          </div>
          <ChevronRightIcon 
            class="w-4 h-4 transition-transform"
            :class="{ 'rotate-90': showSettings }"
          />
        </button>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col">
      <!-- Chat Header -->
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <SparklesIcon class="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 class="font-semibold text-gray-900 dark:text-white">
                {{ chatStore.activeChat?.title || 'New Chat' }}
              </h2>
              <p class="text-sm text-gray-500 dark:text-gray-400 flex items-center space-x-2">
                <span>{{ currentModel }}</span>
                <span>•</span>
                <span class="flex items-center space-x-1">
                  <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Connected</span>
                </span>
              </p>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <!-- Model Selector -->
            <select
              v-model="currentModel"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="Phi-2">Phi-2 (General)</option>
              <option value="Phi-2-Code">Phi-2 (Code)</option>
              <option value="T5-Small">T5 (Summarization)</option>
            </select>

            <!-- Feature Toggles -->
            <div class="flex items-center space-x-1 border-l border-gray-200 dark:border-gray-700 pl-2">
              <button
                @click="showCanvas = !showCanvas"
                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                :class="{ 'bg-blue-100 dark:bg-blue-900/20 text-blue-600': showCanvas }"
              >
                <CodeBracketIcon class="w-5 h-5" />
              </button>

              <button
                @click="toggleVoice"
                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                :class="{ 'bg-red-100 dark:bg-red-900/20 text-red-600': isRecording }"
              >
                <MicrophoneIcon class="w-5 h-5" />
              </button>

              <button
                @click="toggleRAG"
                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                :class="{ 'bg-green-100 dark:bg-green-900/20 text-green-600': ragEnabled }"
                title="Toggle RAG"
              >
                <DocumentMagnifyingGlassIcon class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="flex-1 flex">
        <!-- Messages Area -->
        <div class="flex-1 flex flex-col">
          <!-- Messages -->
          <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth">
            <!-- Welcome Message -->
            <div v-if="!messages.length" class="text-center py-12">
              <div class="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <SparklesIcon class="w-8 h-8 text-white" />
              </div>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Welcome to AI Studio
              </h3>
              <p class="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
                Your multimodal AI workspace for coding, analysis, creative writing, and more.
              </p>
              
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
                <div
                  v-for="feature in features"
                  :key="feature.name"
                  class="p-4 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer"
                  @click="selectFeature(feature)"
                >
                  <component :is="feature.icon" class="w-8 h-8 text-blue-500 mx-auto mb-2" />
                  <div class="text-sm font-medium text-gray-900 dark:text-white">{{ feature.name }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ feature.description }}</div>
                </div>
              </div>
            </div>

            <!-- Chat Messages -->
            <div
              v-for="message in messages"
              :key="message.id"
              class="flex"
              :class="{
                'justify-end': message.role === 'user',
                'justify-start': message.role === 'assistant'
              }"
            >
              <div
                class="max-w-4xl group relative"
                :class="{
                  'ml-12': message.role === 'user',
                  'mr-12': message.role === 'assistant'
                }"
              >
                <div
                  class="px-4 py-3 rounded-2xl shadow-sm"
                  :class="{
                    'bg-blue-500 text-white': message.role === 'user',
                    'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700': message.role === 'assistant'
                  }"
                >
                  <div class="whitespace-pre-wrap">{{ message.content }}</div>
                  <div class="flex items-center justify-between mt-2 text-xs opacity-70">
                    <span>{{ formatTime(message.timestamp) }}</span>
                    <div class="flex items-center space-x-2">
                      <span v-if="message.model">{{ message.model }}</span>
                      <span v-if="message.latency">{{ message.latency.toFixed(0) }}ms</span>
                    </div>
                  </div>
                </div>

                <div 
                  v-if="message.role === 'assistant'"
                  class="absolute -bottom-2 left-4 opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-1"
                >
                  <button
                    @click="copyToClipboard(message.content)"
                    class="p-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full shadow-sm hover:shadow-md transition-shadow"
                  >
                    <ClipboardIcon class="w-3 h-3 text-gray-600 dark:text-gray-400" />
                  </button>
                  <button
                    @click="regenerateResponse(message)"
                    class="p-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full shadow-sm hover:shadow-md transition-shadow"
                  >
                    <ArrowPathIcon class="w-3 h-3 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Typing Indicator -->
            <div v-if="isLoading" class="flex justify-start">
              <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3 shadow-sm">
                <div class="flex items-center space-x-2">
                  <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  </div>
                  <span class="text-sm text-gray-500 dark:text-gray-400">AI is thinking...</span>
                </div>
              </div>
            </div>

            <!-- Auto-scroll anchor -->
            <div ref="scrollAnchor" class="h-1"></div>
          </div>

          <!-- Input Area -->
          <div class="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
            <div class="flex items-end space-x-3">
              <!-- File Upload -->
              <button
                @click="triggerFileUpload"
                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Upload Files"
              >
                <PaperClipIcon class="w-5 h-5" />
              </button>

              <!-- Voice Input -->
              <button
                @click="toggleVoiceInput"
                :disabled="isRecording"
                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                :class="{ 'bg-red-100 text-red-600': isRecording }"
                title="Voice Input"
              >
                <MicrophoneIcon class="w-5 h-5" />
              </button>

              <!-- Message Input -->
              <div class="flex-1 relative">
                <textarea
                  ref="messageInput"
                  v-model="inputMessage"
                  @keydown="handleInputKeydown"
                  @input="autoResize"
                  placeholder="Message AI Studio..."
                  class="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-xl bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  :rows="inputRows"
                  :disabled="isLoading"
                ></textarea>
                
                <!-- Send Button -->
                <button
                  @click="sendMessage"
                  :disabled="!canSend"
                  class="absolute right-2 bottom-2 p-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                  title="Send Message"
                >
                  <PaperAirplaneIcon class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Domain Selector -->
            <div class="mt-3 flex items-center space-x-2">
              <span class="text-sm text-gray-500 dark:text-gray-400">Domain:</span>
              <select
                v-model="selectedDomain"
                class="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="general">General</option>
                <option value="code">Code</option>
                <option value="creative">Creative</option>
                <option value="analysis">Analysis</option>
                <option value="summarizer">Summarizer</option>
              </select>

              <div v-if="ragEnabled" class="flex items-center space-x-2 ml-4">
                <span class="text-sm text-green-600 dark:text-green-400">RAG Enabled</span>
                <div class="w-2 h-2 bg-green-500 rounded-full"></div>
              </div>
            </div>

            <!-- Upload Status -->
            <div v-if="uploadedFiles.length" class="mt-3 flex flex-wrap gap-2">
              <div
                v-for="file in uploadedFiles"
                :key="file.name"
                class="flex items-center space-x-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg px-3 py-1"
              >
                <DocumentIcon class="w-4 h-4 text-blue-500" />
                <span class="text-sm text-blue-700 dark:text-blue-300">{{ file.name }}</span>
                <button
                  @click="removeFile(file.name)"
                  class="text-blue-400 hover:text-red-500 transition-colors"
                >
                  <XMarkIcon class="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Code Canvas Panel -->
        <div
          v-if="showCanvas"
          class="w-96 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
        >
          <div class="h-full flex flex-col">
            <div class="p-3 border-b border-gray-200 dark:border-gray-700">
              <h3 class="font-medium text-gray-900 dark:text-white">Code Canvas</h3>
            </div>
            <div class="flex-1 p-4">
              <textarea
                v-model="canvasCode"
                class="w-full h-full font-mono text-sm bg-gray-900 text-green-400 border-none outline-none resize-none p-4 rounded"
                placeholder="// Your code here..."
              ></textarea>
            </div>
            <div class="p-3 border-t border-gray-200 dark:border-gray-700">
              <button
                @click="runCode"
                class="w-full px-3 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm"
              >
                Run Code
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Panel -->
    <div
      v-if="showSettings"
      class="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700"
    >
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h3 class="font-semibold text-gray-900 dark:text-white">Settings</h3>
        <button
          @click="showSettings = false"
          class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded"
        >
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
      
      <div class="p-4 space-y-6">
        <!-- Temperature -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Temperature</label>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ temperature }}</span>
          </div>
          <input
            v-model.number="temperature"
            type="range"
            min="0"
            max="1"
            step="0.1"
            class="w-full"
          />
        </div>

        <!-- Max Tokens -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Max Tokens</label>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ maxTokens }}</span>
          </div>
          <input
            v-model.number="maxTokens"
            type="range"
            min="50"
            max="500"
            step="50"
            class="w-full"
          />
        </div>

        <!-- System Status -->
        <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
          <h4 class="font-medium text-gray-700 dark:text-gray-300 mb-3">System Status</h4>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Models Loaded</span>
              <div class="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">RAG Engine</span>
              <div class="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Voice Processing</span>
              <div class="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
          </div>
        </div>

        <!-- Data Management -->
        <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
          <h4 class="font-medium text-gray-700 dark:text-gray-300 mb-3">Data Management</h4>
          <div class="space-y-2">
            <button
              @click="exportChats"
              class="w-full px-3 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
            >
              Export Chats
            </button>
            <button
              @click="clearAllChats"
              class="w-full px-3 py-2 text-sm bg-red-500 hover:bg-red-600 text-white rounded-lg"
            >
              Clear All Chats
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Hidden File Input -->
    <input
      ref="fileInput"
      type="file"
      multiple
      accept=".txt,.pdf,.docx,.md,.json"
      class="hidden"
      @change="handleFileUpload"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import {
  PlusIcon, PencilIcon, TrashIcon, SparklesIcon, CogIcon, ChevronRightIcon,
  CodeBracketIcon, MicrophoneIcon, PaperClipIcon, PaperAirplaneIcon,
  XMarkIcon, ArrowPathIcon, ClipboardIcon, DocumentIcon,
  DocumentMagnifyingGlassIcon
} from '@heroicons/vue/24/outline'

// Constants
const API_BASE = 'http://localhost:8000'
const STORAGE_KEY = 'ai-studio-chats'
const SETTINGS_KEY = 'ai-studio-settings'

// Reactive state
const chatStore = ref({
  chats: [],
  activeChat: null
})

const messages = ref([])
const inputMessage = ref('')
const inputRows = ref(1)
const isLoading = ref(false)
const isRecording = ref(false)
const showSettings = ref(false)
const showCanvas = ref(false)
const ragEnabled = ref(false)
const canvasCode = ref('')
const uploadedFiles = ref([])

// Settings
const temperature = ref(0.7)
const maxTokens = ref(200)
const selectedDomain = ref('general')
const currentModel = ref('Phi-2')
const selectedAction = ref(null)

// UI elements
const messageInput = ref(null)
const messagesContainer = ref(null)
const scrollAnchor = ref(null)
const fileInput = ref(null)

// Quick actions
const quickActions = ref([
  { id: 'code', name: 'Code', icon: CodeBracketIcon },
  { id: 'voice', name: 'Voice', icon: MicrophoneIcon },
  { id: 'file', name: 'File', icon: PaperClipIcon }
])

// Features
const features = ref([
  { name: 'Code', description: 'Generate and debug code', icon: CodeBracketIcon },
  { name: 'Chat', description: 'Natural conversation', icon: SparklesIcon },
  { name: 'Voice', description: 'Speech-to-text', icon: MicrophoneIcon },
  { name: 'Documents', description: 'Analyze documents', icon: DocumentIcon }
])

// Computed
const canSend = computed(() => inputMessage.value.trim().length > 0 && !isLoading.value)

// Watchers
watch(() => chatStore.value, (newStore) => {
  saveToStorage()
}, { deep: true })

watch(() => messages.value, () => {
  scrollToBottom()
}, { deep: true })

watch(() => isLoading.value, (loading) => {
  if (!loading) {
    nextTick(() => scrollToBottom())
  }
})

// Storage functions
const saveToStorage = () => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      chats: chatStore.value.chats,
      activeChat: chatStore.value.activeChat
    }))
    
    localStorage.setItem(SETTINGS_KEY, JSON.stringify({
      temperature: temperature.value,
      maxTokens: maxTokens.value,
      selectedDomain: selectedDomain.value,
      currentModel: currentModel.value,
      ragEnabled: ragEnabled.value
    }))
  } catch (error) {
    console.warn('Failed to save to localStorage:', error)
  }
}

const loadFromStorage = () => {
  try {
    const chatData = localStorage.getItem(STORAGE_KEY)
    if (chatData) {
      const parsed = JSON.parse(chatData)
      chatStore.value.chats = parsed.chats || []
      
      // Restore active chat and messages
      if (parsed.activeChat && chatStore.value.chats.length > 0) {
        const activeChat = chatStore.value.chats.find(c => c.id === parsed.activeChat.id)
        if (activeChat) {
          chatStore.value.activeChat = activeChat
          messages.value = activeChat.messages || []
        } else {
          chatStore.value.activeChat = chatStore.value.chats[0]
          messages.value = chatStore.value.chats[0].messages || []
        }
      }
    }
    
    const settingsData = localStorage.getItem(SETTINGS_KEY)
    if (settingsData) {
      const settings = JSON.parse(settingsData)
      temperature.value = settings.temperature || 0.7
      maxTokens.value = settings.maxTokens || 200
      selectedDomain.value = settings.selectedDomain || 'general'
      currentModel.value = settings.currentModel || 'Phi-2'
      ragEnabled.value = settings.ragEnabled || false
    }
  } catch (error) {
    console.warn('Failed to load from localStorage:', error)
  }
}

// Chat methods
const createNewChat = () => {
  const chat = {
    id: Date.now().toString(),
    title: `Chat ${chatStore.value.chats.length + 1}`,
    messages: [],
    created: new Date().toISOString(),
    updated: new Date().toISOString()
  }
  chatStore.value.chats.unshift(chat)
  chatStore.value.activeChat = chat
  messages.value = []
  inputMessage.value = ''
  selectedAction.value = null

  saveToStorage()
  nextTick(() => {
    messageInput.value.focus()
  })
}
const selectChat = (chatId) => {
  const chat = chatStore.value.chats.find(c => c.id === chatId)
  if (chat) {
    chatStore.value.activeChat = chat
    messages.value = chat.messages || []
    inputMessage.value = ''
    selectedAction.value = null

    saveToStorage()
    nextTick(() => {
      messageInput.value.focus()
    })
  }
}
const editChatTitle = (chat) => {
  const newTitle = prompt('Edit Chat Title', chat.title)
  if (newTitle !== null && newTitle.trim() !== '') {
    chat.title = newTitle.trim()
    chat.updated = new Date().toISOString()
    saveToStorage()
  }
}
const deleteChat = (chatId) => {
  if (confirm('Are you sure you want to delete this chat?')) {
    chatStore.value.chats = chatStore.value.chats.filter(c => c.id !== chatId)
    if (chatStore.value.activeChat?.id === chatId) {
      if (chatStore.value.chats.length > 0) {
        chatStore.value.activeChat = chatStore.value.chats[0]
        messages.value = chatStore.value.activeChat.messages || []
      } else {
        chatStore.value.activeChat = null
        messages.value = []
      }
    }
    saveToStorage()
  }
}
const clearAllChats = () => {
  if (confirm('Are you sure you want to clear all chats? This action cannot be undone.')) {
    chatStore.value.chats = []
    chatStore.value.activeChat = null
    messages.value = []
    saveToStorage()
  }
}
const exportChats = () => {
  const dataStr = JSON.stringify(chatStore.value.chats, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'ai-studio-chats.json'
  a.click()
  URL.revokeObjectURL(url)
}


const selectQuickAction = (action) => {
  selectedAction.value = action.id
  if (action.id === 'code') {
    createNewChat()
    inputMessage.value = 'Generate a code snippet for...'
  } else if (action.id === 'voice') {
    toggleVoice()
  } else if (action.id === 'file') {
    triggerFileUpload()
  }
  nextTick(() => {
    messageInput.value.focus()
  })
}
const selectFeature = (feature) => {
  if (feature.name === 'Code') {
    createNewChat()
    inputMessage.value = 'Generate a code snippet for...'
  } else if (feature.name === 'Voice') {
    toggleVoice()
  } else if (feature.name === 'Documents') {
    triggerFileUpload()
  } else {
    createNewChat()
  }
  nextTick(() => {
    messageInput.value.focus()
  })
}
const formatDate = (isoString) => {
  const date = new Date(isoString)
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}
const formatTime = (isoString) => {
  const date = new Date(isoString)
  return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}
const autoResize = () => {
  nextTick(() => {
    const el = messageInput.value
    el.style.height = 'auto'
    el.style.height = `${el.scrollHeight}px`
    inputRows.value = Math.min(Math.ceil(el.scrollHeight / 24), 6) // Assuming line-height ~24px
  })
}
const handleInputKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    if (canSend.value) {
      sendMessage()
    }
  }
}
const sendMessage = async () => {
  if (!canSend.value) return

  const userMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date().toISOString(),
    model: currentModel.value
  }

  messages.value.push(userMessage)
  if (chatStore.value.activeChat) {
    chatStore.value.activeChat.messages.push(userMessage)
    chatStore.value.activeChat.updated = new Date().toISOString()
  }

  inputMessage.value = ''
  inputRows.value = 1
  isLoading.value = true

  try {
    const startTime = performance.now()
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMessage.content,
        model: currentModel.value,
        temperature: temperature.value,
        max_tokens: maxTokens.value,
        domain: selectedDomain.value,
        rag: ragEnabled.value,
        files: uploadedFiles.value.map(f => f.name)
      })
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }

    const data = await response.json()
    const latency = performance.now() - startTime

    const assistantMessage = {
      id: Date.now().toString() + '-resp',
      role: 'assistant',
      content: data.reply,
      timestamp: new Date().toISOString(),
      model: currentModel.value,
      latency
    }

    messages.value.push(assistantMessage)
    if (chatStore.value.activeChat) {
      chatStore.value.activeChat.messages.push(assistantMessage)
      chatStore.value.activeChat.updated = new Date().toISOString()
    }

    // Clear uploaded files after sending
    uploadedFiles.value = []
  } catch (error) {
    console.error('Error sending message:', error)
    alert('Failed to get response from AI. Please try again.')
  } finally {
    isLoading.value = false
    saveToStorage()
  }
}
const scrollToBottom = () => {
  nextTick(() => {
    if (scrollAnchor.value) {
      scrollAnchor.value.scrollIntoView({ behavior: 'smooth' })
    }
  })
}

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    alert('Message copied to clipboard')
  }).catch(err => {
    console.error('Failed to copy text: ', err)
  })
}

</script>