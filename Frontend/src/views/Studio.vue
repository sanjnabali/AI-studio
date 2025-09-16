<!-- src/views/Studio.vue - Enhanced with Authentication and Backend Integration -->
<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Sidebar -->
    <div class="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <SparklesIcon class="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 class="text-lg font-semibold text-gray-900 dark:text-white">AI Studio</h1>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ authStore.userName }}</p>
            </div>
          </div>
          
          <!-- User Menu -->
          <div class="relative">
            <button
              @click="showUserMenu = !showUserMenu"
              class="flex items-center space-x-2 p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <div class="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <span class="text-xs font-medium text-white">{{ userInitials }}</span>
              </div>
            </button>
            
            <!-- User Dropdown -->
            <div
              v-if="showUserMenu"
              class="absolute right-0 top-full mt-2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50"
            >
              <div class="p-3 border-b border-gray-200 dark:border-gray-700">
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ authStore.userName }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ authStore.userEmail }}</p>
              </div>
              <div class="py-1">
                <button
                  @click="showSettings = true; showUserMenu = false"
                  class="w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <CogIcon class="w-4 h-4 inline mr-2" />
                  Settings
                </button>
                <button
                  @click="handleLogout"
                  class="w-full text-left px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <ArrowRightOnRectangleIcon class="w-4 h-4 inline mr-2" />
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <button
          @click="createNewChat"
          class="w-full flex items-center justify-center space-x-2 p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          <PlusIcon class="w-5 h-5" />
          <span>New Chat</span>
        </button>
      </div>

      <!-- System Status -->
      <div class="p-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-medium text-gray-600 dark:text-gray-400">System Status</span>
          <button
            @click="refreshSystemStatus"
            class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded"
          >
            <ArrowPathIcon class="w-3 h-3" :class="{ 'animate-spin': isRefreshing }" />
          </button>
        </div>
        <div class="space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-500 dark:text-gray-400">AI Models</span>
            <div class="flex items-center space-x-1">
              <div class="w-2 h-2 rounded-full" :class="systemStatusColor"></div>
              <span class="text-xs text-gray-600 dark:text-gray-300">{{ systemStatusText }}</span>
            </div>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-500 dark:text-gray-400">Code Execution</span>
            <div class="flex items-center space-x-1">
              <div class="w-2 h-2 bg-green-500 rounded-full"></div>
              <span class="text-xs text-gray-600 dark:text-gray-300">Ready</span>
            </div>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-500 dark:text-gray-400">Voice Processing</span>
            <div class="flex items-center space-x-1">
              <div class="w-2 h-2 bg-green-500 rounded-full"></div>
              <span class="text-xs text-gray-600 dark:text-gray-300">Ready</span>
            </div>
          </div>
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
                  <div class="w-2 h-2 rounded-full" :class="systemStatusColor"></div>
                  <span>{{ systemStatusText }}</span>
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
              <option value="gemini-pro">Gemini Pro</option>
              <option value="gemini-pro-vision">Gemini Pro Vision</option>
              <option value="claude-3">Claude 3</option>
              <option value="gpt-4">GPT-4</option>
            </select>

            <!-- Feature Toggles -->
            <div class="flex items-center space-x-1 border-l border-gray-200 dark:border-gray-700 pl-2">
              <button
                @click="showCanvas = !showCanvas"
                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                :class="{ 'bg-blue-100 dark:bg-blue-900/20 text-blue-600': showCanvas }"
                title="Toggle Code Canvas"
              >
                <CodeBracketIcon class="w-5 h-5" />
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
                      <span v-if="message.metadata?.model">{{ message.metadata.model }}</span>
                      <span v-if="message.metadata?.latency">{{ Math.round(message.metadata.latency) }}ms</span>
                      <span v-if="message.metadata?.sources?.length" class="text-green-600">
                        {{ message.metadata.sources.length }} sources
                      </span>
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
            <div v-if="chatStore.loading" class="flex justify-start">
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

            <!-- Error Display -->
            <div v-if="chatStore.error" class="flex justify-center">
              <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 max-w-md">
                <div class="flex items-center">
                  <ExclamationTriangleIcon class="h-5 w-5 text-red-400 mr-2" />
                  <div>
                    <div class="text-sm font-medium text-red-800 dark:text-red-200">
                      Message failed
                    </div>
                    <div class="text-sm text-red-600 dark:text-red-300 mt-1">
                      {{ chatStore.error }}
                    </div>
                  </div>
                </div>
                <button
                  @click="chatStore.clearError()"
                  class="mt-2 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
                >
                  Dismiss
                </button>
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
              <VoiceRecorder
                @recording-complete="handleVoiceInput"
                @recording-start="() => {}"
                @recording-stop="() => {}"
              />

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
                  :disabled="chatStore.loading"
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
                <option value="academic">Academic</option>
                <option value="business">Business</option>
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
            <div class="p-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h3 class="font-medium text-gray-900 dark:text-white">Code Canvas</h3>
              <select
                v-model="canvasLanguage"
                class="text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-2 py-1"
              >
                <option v-for="lang in chatStore.supportedLanguages" :key="lang" :value="lang">
                  {{ lang.charAt(0).toUpperCase() + lang.slice(1) }}
                </option>
              </select>
            </div>
            <div class="flex-1 relative">
              <textarea
                v-model="canvasCode"
                class="w-full h-full font-mono text-sm bg-gray-900 text-green-400 border-none outline-none resize-none p-4"
                placeholder="// Your code here..."
              ></textarea>
            </div>
            <div class="p-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
              <button
                @click="runCode"
                :disabled="codeExecuting"
                class="w-full px-3 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white rounded-lg text-sm flex items-center justify-center"
              >
                <span v-if="codeExecuting" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
                {{ codeExecuting ? 'Running...' : 'Run Code' }}
              </button>
              
              <!-- Code Output -->
              <div v-if="codeOutput" class="mt-3 p-3 bg-gray-100 dark:bg-gray-700 rounded text-sm font-mono max-h-40 overflow-y-auto">
                <div v-if="codeOutput.success" class="text-green-700 dark:text-green-300">
                  <div class="font-semibold mb-1">Output:</div>
                  <pre class="whitespace-pre-wrap">{{ codeOutput.output }}</pre>
                  <div class="text-xs mt-2 opacity-70">
                    Executed in {{ codeOutput.executionTime }}ms
                  </div>
                </div>
                <div v-else class="text-red-700 dark:text-red-300">
                  <div class="font-semibold mb-1">Error:</div>
                  <pre class="whitespace-pre-wrap">{{ codeOutput.error }}</pre>
                </div>
              </div>
            </div>
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

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { useChatStore } from '../store/chat'
import VoiceRecorder from '../composables/VoiceRecorder.vue'
import {
  PlusIcon, PencilIcon, TrashIcon, SparklesIcon, CogIcon, ChevronRightIcon,
  CodeBracketIcon, PaperClipIcon, PaperAirplaneIcon, XMarkIcon, ArrowPathIcon,
  ClipboardIcon, DocumentIcon, DocumentMagnifyingGlassIcon, ExclamationTriangleIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

// Reactive state
const messages = computed(() => chatStore.activeChatMessages)
const inputMessage = ref('')
const inputRows = ref(1)
const showSettings = ref(false)
const showCanvas = ref(false)
const showUserMenu = ref(false)
const ragEnabled = ref(false)
const canvasCode = ref('')
const canvasLanguage = ref('python')
const uploadedFiles = ref<File[]>([])
const codeExecuting = ref(false)
const codeOutput = ref<any>(null)
const isRefreshing = ref(false)

// Settings
const selectedDomain = ref('general')
const currentModel = ref('gemini-pro')

// UI elements
const messageInput = ref<HTMLTextAreaElement | null>(null)
const messagesContainer = ref<HTMLElement | null>(null)
const scrollAnchor = ref<HTMLElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

// Features
const features = ref([
  { name: 'Code', description: 'Generate and debug code', icon: CodeBracketIcon },
  { name: 'Chat', description: 'Natural conversation', icon: SparklesIcon },
  { name: 'Documents', description: 'Analyze documents', icon: DocumentIcon }
])

// Computed
const canSend = computed(() => inputMessage.value.trim().length > 0 && !chatStore.loading)
const userInitials = computed(() => {
  const name = authStore.userName
  return name.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'
})

const systemStatusColor = computed(() => {
  if (!chatStore.systemHealth) return 'bg-gray-500'
  return chatStore.isSystemReady ? 'bg-green-500' : 'bg-red-500'
})

const systemStatusText = computed(() => {
  if (!chatStore.systemHealth) return 'Unknown'
  return chatStore.isSystemReady ? 'Ready' : 'Loading'
})

// Watchers
watch(() => messages.value, () => {
  scrollToBottom()
}, { deep: true })

watch(() => chatStore.loading, (loading) => {
  if (!loading) {
    nextTick(() => scrollToBottom())
  }
})

// Lifecycle
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/auth')
    return
  }
  
  await chatStore.initialize()
  
  if (messageInput.value) {
    messageInput.value.focus()
  }
})

onUnmounted(() => {
  // Clean up any timers or listeners
})

// Methods
async function handleLogout() {
  showUserMenu.value = false
  await authStore.logout()
  router.push('/auth')
}

async function refreshSystemStatus() {
  isRefreshing.value = true
  await chatStore.checkSystemHealth()
  await chatStore.getModelStatus()
  setTimeout(() => {
    isRefreshing.value = false
  }, 1000)
}

function createNewChat() {
  chatStore.createChat()
  inputMessage.value = ''
  showUserMenu.value = false
  nextTick(() => {
    messageInput.value?.focus()
  })
}

function selectChat(chatId: string) {
  chatStore.selectChat(chatId)
  inputMessage.value = ''
  nextTick(() => {
    messageInput.value?.focus()
  })
}

function editChatTitle(chat: any) {
  const newTitle = prompt('Edit Chat Title', chat.title)
  if (newTitle !== null && newTitle.trim() !== '') {
    chatStore.updateChatTitle(chat.id, newTitle.trim())
  }
}

function deleteChat(chatId: string) {
  if (confirm('Are you sure you want to delete this chat?')) {
    chatStore.deleteChat(chatId)
  }
}

function selectFeature(feature: any) {
  if (feature.name === 'Code') {
    createNewChat()
    inputMessage.value = 'Generate a code snippet for...'
  } else if (feature.name === 'Documents') {
    triggerFileUpload()
  } else {
    createNewChat()
  }
  nextTick(() => {
    messageInput.value?.focus()
  })
}

function formatDate(date: Date) {
  return new Date(date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

function formatTime(date: Date) {
  return new Date(date).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}

function autoResize() {
  nextTick(() => {
    if (messageInput.value) {
      messageInput.value.style.height = 'auto'
      messageInput.value.style.height = `${messageInput.value.scrollHeight}px`
      inputRows.value = Math.min(Math.ceil(messageInput.value.scrollHeight / 24), 6)
    }
  })
}

function handleInputKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    if (canSend.value) {
      sendMessage()
    }
  }
}

async function sendMessage() {
  if (!canSend.value) return

  const content = inputMessage.value.trim()
  inputMessage.value = ''
  inputRows.value = 1

  await chatStore.sendMessage(content, {
    domain: selectedDomain.value,
    useRAG: ragEnabled.value,
    temperature: 0.7,
    maxTokens: 1024
  });



  // Clear uploaded files after sending
  uploadedFiles.value = []
}

function scrollToBottom() {
  nextTick(() => {
    if (scrollAnchor.value) {
      scrollAnchor.value.scrollIntoView({ behavior: 'smooth' })
    }
  })
}

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    // Could show a toast notification here
  } catch (err) {
    console.error('Failed to copy text:', err)
  }
}

async function regenerateResponse(message: any) {
  // Find the user message before this assistant message
  const messageIndex = messages.value.findIndex(m => m.id === message.id)
  if (messageIndex > 0) {
    const userMessage = messages.value[messageIndex - 1]
    if (userMessage.role === 'user') {
      await chatStore.sendMessage(userMessage.content, {
        domain: selectedDomain.value,
        useRAG: ragEnabled.value
      })
    }
  }
}

function toggleRAG() {
  ragEnabled.value = !ragEnabled.value
}

function triggerFileUpload() {
  fileInput.value?.click()
}

async function handleFileUpload(event: Event) {
  const files = Array.from((event.target as HTMLInputElement).files || [])
  if (files.length === 0) return

  const result = await chatStore.uploadDocuments(files)
  if (result.success) {
    uploadedFiles.value = [...uploadedFiles.value, ...files]
  }
}

function removeFile(fileName: string) {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.name !== fileName)
}

async function handleVoiceInput(audioBlob: Blob) {
  const audioFile = new File([audioBlob], 'voice_input.wav', { type: 'audio/wav' })
  const result = await chatStore.transcribeAudio(audioFile)
  
  if (result.success && result.transcription) {
    inputMessage.value = result.transcription
    autoResize()
    messageInput.value?.focus()
  }
}

async function runCode() {
  if (!canvasCode.value.trim()) return
  
  codeExecuting.value = true
  codeOutput.value = null
  
  const result = await chatStore.executeCode(canvasCode.value, canvasLanguage.value)
  codeOutput.value = result
  codeExecuting.value = false
}
</script>