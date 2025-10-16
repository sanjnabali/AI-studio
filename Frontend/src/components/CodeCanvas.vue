<template>
  <div class="flex flex-col h-full bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 min-h-screen">
    <!-- Toolbar -->
    <div class="flex items-center justify-between px-6 py-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-orange-200/50 dark:border-gray-700/50 shadow-sm">
      <div class="flex items-center space-x-4">
        <!-- Project Info -->
        <div class="flex items-center space-x-3 group">
          <div class="w-10 h-10 bg-gradient-to-r from-green-500 via-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 hover:scale-105">
            <CodeBracketIcon class="w-5 h-5 text-white" />
          </div>
          <div class="flex-1">
            <input
              v-model="projectName"
              @blur="saveProject"
              class="text-xl font-bold bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-orange-400 rounded-lg px-3 py-2 text-gray-900 dark:text-white transition-all duration-200 hover:bg-white/10"
              placeholder="Project Name"
            />
            <div class="flex items-center space-x-4 mt-1">
              <p class="text-sm text-gray-600 dark:text-gray-300 font-medium">
                {{ formatFileSize(codeContent.length) }}
              </p>
              <span class="text-gray-400">•</span>
              <p class="text-sm text-gray-600 dark:text-gray-300 font-medium">
                {{ getLineCount() }} lines
              </p>
              <div class="flex items-center space-x-1">
                <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span class="text-xs text-green-600 dark:text-green-400 font-medium">Active</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Language Selector -->
        <select
          v-model="selectedLanguage"
          @change="onLanguageChange"
          class="px-3 py-1.5 text-sm bg-[#fff7ed] dark:bg-[#292524] border border-[#ffd6b5] dark:border-[#44403c] rounded-lg focus:ring-2 focus:ring-[#ff6a1a] text-[#b34713] dark:text-[#ffd6b5]"
        >
          <option v-for="lang in availableLanguages" :key="lang" :value="lang">
            {{ lang.charAt(0).toUpperCase() + lang.slice(1) }}
          </option>
        </select>
      </div>

      <div class="flex items-center space-x-2">
        <!-- AI Assistant Toggle -->
        <button
          @click="showAIAssistant = !showAIAssistant"
          :class="[
            'px-3 py-1.5 text-xs font-medium rounded-lg border transition-all',
            showAIAssistant
              ? 'bg-purple-100 text-purple-800 border-purple-300 dark:bg-purple-900 dark:text-purple-100 dark:border-purple-700'
              : 'bg-gray-100 text-gray-600 border-gray-300 dark:bg-gray-700 dark:text-gray-400 dark:border-gray-600'
          ]"
        >
          <SparklesIcon class="w-3 h-3 inline mr-1" />
          AI Assistant
        </button>

        <!-- Version Control -->
        <button
          @click="showVersionHistory = true"
          class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          title="Version History"
        >
          <ClockIcon class="w-5 h-5" />
        </button>

        <!-- Share/Export -->
          <DropdownMenu>
            <button 
              slot="trigger"
              class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <ShareIcon class="w-5 h-5" />
            </button>
            <div slot="content">
              <button @click="exportCode" class="w-full text-left px-4 py-2 text-sm hover:bg-[#ffe4d5] dark:hover:bg-[#292524]">
                Export Code
              </button>
              <button @click="shareProject" class="w-full text-left px-4 py-2 text-sm hover:bg-[#ffe4d5] dark:hover:bg-[#292524]">
                Share Project
              </button>
              <button @click="generateAPI" class="w-full text-left px-4 py-2 text-sm hover:bg-[#ffe4d5] dark:hover:bg-[#292524]">
                Generate API
              </button>
            </div>
        </DropdownMenu>        <!-- Run/Execute -->
        <button
          @click="executeCode"
          :disabled="isExecuting || !codeContent.trim()"
          :class="[
            'px-4 py-2 rounded-lg font-medium transition-all flex items-center space-x-2',
            canExecute && !isExecuting
              ? 'bg-green-600 hover:bg-green-700 text-white shadow-md hover:shadow-lg'
              : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
          ]"
        >
          <PlayIcon v-if="!isExecuting" class="w-4 h-4" />
          <div v-else class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          <span>{{ isExecuting ? 'Running...' : 'Run' }}</span>
        </button>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Code Editor -->
      <div class="flex-1 flex flex-col">
        <!-- Editor Tabs -->
        <div class="flex items-center px-6 py-2 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div class="flex space-x-1">
            <div
              v-for="(file, index) in openFiles"
              :key="file.name" 
              :class="{
                'flex items-center space-x-2 px-3 py-1.5 rounded-lg text-sm cursor-pointer transition-all relative': true,
                'bg-orange-50 text-orange-800 shadow-sm': activeFileIndex === index,
                'text-gray-600 hover:text-gray-900 hover:bg-orange-50/50': activeFileIndex !== index,
                'unsaved': !file.saved
              }"
              @click="activeFileIndex = index"
            >
              <component :is="getLanguageIcon(file.language)" class="w-4 h-4" />
              <span>{{ file.name }}</span>
              <button
                v-if="openFiles.length > 1"
                @click.stop="closeFile(index)"
                class="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
              >
                <XMarkIcon class="w-3 h-3" />
              </button>
            </div>
          </div>

          <button
            @click="addNewFile"
            class="ml-2 p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <PlusIcon class="w-4 h-4" />
          </button>
        </div>

        <!-- Code Editor Container -->
        <div class="flex-1 relative">
          <div
            ref="editorContainer"
            class="absolute inset-0 font-mono text-sm"
          ></div>

          <!-- Line Numbers (if Monaco is not available) -->
          <div
            v-if="!isMonacoLoaded"
            class="flex h-full"
          >
            <div class="w-12 bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 py-4">
              <div
                v-for="(line, index) in codeLines"
                :key="index"
                class="h-6 text-xs text-gray-500 text-right pr-2 leading-6"
              >
                {{ index + 1 }}
              </div>
            </div>
            
            <textarea
              v-model="codeContent"
              @input="onCodeChange"
              @keydown="handleEditorKeydown"
              class="flex-1 p-4 bg-[#fff7ed] dark:bg-[#292524] border-none resize-none focus:outline-none font-mono text-sm text-[#b34713] dark:text-[#ffd6b5]"
              placeholder="Start coding here..."
              spellcheck="false"
              :style="{ tabSize: 2 }"
            ></textarea>
          </div>

          <!-- AI Code Suggestions Overlay -->
          <div
            v-if="aiSuggestion && showAISuggestion"
            class="absolute top-4 right-4 max-w-md bg-[#fff7ed] dark:bg-[#292524] border border-[#ffd6b5] dark:border-[#44403c] rounded-xl shadow-lg p-4 z-10"
          >
            <div class="flex items-start justify-between mb-2">
              <div class="flex items-center space-x-2">
                <SparklesIcon class="w-4 h-4 text-purple-500" />
                <span class="text-sm font-medium text-gray-900 dark:text-white">AI Suggestion</span>
              </div>
              <button
                @click="showAISuggestion = false"
                class="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon class="w-4 h-4" />
              </button>
            </div>
            
            <p class="text-sm text-gray-600 dark:text-gray-300 mb-3">{{ aiSuggestion.description }}</p>
            
            <div class="flex space-x-2">
              <button
                @click="applyAISuggestion"
                class="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-xs rounded-lg transition-colors"
              >
                Apply
              </button>
              <button
                @click="showAISuggestion = false"
                class="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>

        <!-- Output/Console Area -->
        <div
          v-if="showOutput"
          class="h-64 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 flex flex-col"
        >
          <div class="flex items-center justify-between px-4 py-2 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center space-x-4">
              <h3 class="text-sm font-medium text-gray-900 dark:text-white">Output</h3>
              <div class="flex space-x-2">
                <button
                  @click="activeOutputTab = 'console'"
                  :class="[
                    'px-2 py-1 text-xs rounded',
                    activeOutputTab === 'console'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  ]"
                >
                  Console
                </button>
                <button
                  @click="activeOutputTab = 'errors'"
                  :class="[
                    'px-2 py-1 text-xs rounded',
                    activeOutputTab === 'errors'
                      ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  ]"
                >
                  Errors
                  <span v-if="executionErrors.length > 0" class="ml-1 px-1.5 py-0.5 bg-red-500 text-white text-xs rounded-full">
                    {{ executionErrors.length }}
                  </span>
                </button>
                <button
                  @click="activeOutputTab = 'tests'"
                  :class="[
                    'px-2 py-1 text-xs rounded',
                    activeOutputTab === 'tests'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  ]"
                >
                  Tests
                </button>
              </div>
            </div>

            <div class="flex items-center space-x-2">
              <button
                @click="clearOutput"
                class="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded"
                title="Clear output"
              >
                <TrashIcon class="w-4 h-4" />
              </button>
              <button
                @click="showOutput = false"
                class="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded"
                title="Hide output"
              >
                <ChevronDownIcon class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div class="flex-1 overflow-y-auto p-4">
            <!-- Console Output -->
            <div v-if="activeOutputTab === 'console'" class="space-y-2">
              <div
                v-for="(output, index) in executionOutput"
                :key="index"
                class="font-mono text-sm"
                :class="output.type === 'error' ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-gray-100'"
              >
                <span class="text-gray-500 text-xs mr-2">{{ formatTime(output.timestamp) }}</span>
                <span>{{ output.content }}</span>
              </div>
              
              <div v-if="executionOutput.length === 0" class="text-gray-500 dark:text-gray-400 text-sm italic">
                No output yet. Run your code to see results.
              </div>
            </div>

            <!-- Errors -->
            <div v-else-if="activeOutputTab === 'errors'" class="space-y-3">
              <div
                v-for="(error, index) in executionErrors"
                :key="index"
                class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <h4 class="text-sm font-medium text-red-800 dark:text-red-200">{{ error.type }}</h4>
                    <p class="mt-1 text-sm text-red-700 dark:text-red-300">{{ error.message }}</p>
                    <p v-if="error.line" class="mt-1 text-xs text-red-600 dark:text-red-400">
                      Line {{ error.line }}{{ error.column ? `, Column ${error.column}` : '' }}
                    </p>
                  </div>
                  <button
                    @click="goToError(error)"
                    class="ml-2 px-2 py-1 bg-red-100 dark:bg-red-800 text-red-700 dark:text-red-200 text-xs rounded hover:bg-red-200 dark:hover:bg-red-700 transition-colors"
                  >
                    Go to line
                  </button>
                </div>
              </div>

              <div v-if="executionErrors.length === 0" class="text-gray-500 dark:text-gray-400 text-sm italic">
                No errors. Great job! 🎉
              </div>
            </div>

            <!-- Tests -->
            <div v-else-if="activeOutputTab === 'tests'" class="space-y-2">
              <div
                v-for="(test, index) in testResults"
                :key="index"
                class="flex items-center justify-between p-2 rounded-lg"
                :class="test.passed ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'"
              >
                <div class="flex items-center space-x-2">
                  <CheckCircleIcon v-if="test.passed" class="w-4 h-4 text-green-600" />
                  <XCircleIcon v-else class="w-4 h-4 text-red-600" />
                  <span class="text-sm font-medium">{{ test.name }}</span>
                </div>
                <span class="text-xs text-gray-500">{{ test.duration }}ms</span>
              </div>

              <div v-if="testResults.length === 0" class="text-gray-500 dark:text-gray-400 text-sm italic">
                No tests found. Add test functions to see results.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Assistant Panel -->
      <div
        v-if="showAIAssistant"
        class="w-80 bg-[#fff7ed] dark:bg-[#292524] border-l border-[#ffd6b5] dark:border-[#44403c] flex flex-col shadow-xl"
      >
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">AI Assistant</h3>
            <button
              @click="showAIAssistant = false"
              class="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
        

          <!-- AI Actions -->
          <div class="grid grid-cols-2 gap-2">
            <button
              @click="requestCodeReview"
              class="p-2 text-sm bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors"
            >
              <EyeIcon class="w-4 h-4 mx-auto mb-1" />
              Review Code
            </button>
            <button
              @click="requestOptimization"
              class="p-2 text-sm bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
            >
              <BoltIcon class="w-4 h-4 mx-auto mb-1" />
              Optimize
            </button>
            <button
              @click="generateDocumentation"
              class="p-2 text-sm bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-lg hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors"
            >
              <DocumentTextIcon class="w-4 h-4 mx-auto mb-1" />
              Document
            </button>
            <button
              @click="generateTests"
              class="p-2 text-sm bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 rounded-lg hover:bg-yellow-200 dark:hover:bg-yellow-900/50 transition-colors"
            >
              <BeakerIcon class="w-4 h-4 mx-auto mb-1" />
              Add Tests
            </button>
          </div>
        </div>

        <!-- AI Chat -->
        <div class="flex-1 flex flex-col">
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
            <div
              v-for="(message, index) in aiMessages"
              :key="index"
              :class="[
                'p-3 rounded-lg max-w-full',
                message.role === 'user'
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-900 dark:text-blue-100 ml-4'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white mr-4'
              ]"
            >
              <div class="flex items-start space-x-2">
                <component
                  :is="message.role === 'user' ? UserIcon : CpuChipIcon"
                  class="w-4 h-4 mt-0.5 flex-shrink-0"
                />
                <div class="flex-1 text-sm">
                  <div v-if="message.type === 'code'" class="font-mono bg-gray-800 text-green-400 p-2 rounded text-xs mb-2">
                    {{ message.content }}
                  </div>
                  <div v-else>{{ message.content }}</div>
                </div>
              </div>
            </div>

            <div v-if="aiTyping" class="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
              <CpuChipIcon class="w-4 h-4" />
              <div class="flex space-x-1">
                <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
            </div>
          </div>

          <!-- AI Input -->
          <div class="p-4 border-t border-gray-200 dark:border-gray-700">
            <div class="flex space-x-2">
          <input
            v-model="aiInput"
            @keydown.enter="sendAIMessage"
            placeholder="Ask about your code..."
            class="flex-1 px-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white"
          />
              <button
                @click="sendAIMessage"
                :disabled="!aiInput.trim() || aiTyping"
                class="px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white rounded-lg transition-colors"
              >
                <PaperAirplaneIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <VersionHistoryModal
      v-if="showVersionHistory"
      :versions="codeVersions"
      @close="showVersionHistory = false"
      @restore="restoreVersion"
    />

    <NewFileModal
      v-if="showNewFileModal"
      @close="showNewFileModal = false"
      @create="createNewFile"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useSettingsStore } from '@/store/settings'
import { useNotificationStore } from '@/store/notification'
import { apiClient, type CodeExecutionResult } from '@/api/client'

// Icons
import {
  CodeBracketIcon,
  PlayIcon,
  SparklesIcon,
  ShareIcon,
  ClockIcon,
  PlusIcon,
  XMarkIcon,
  TrashIcon,
  ChevronDownIcon,
  CheckCircleIcon,
  XCircleIcon,
  EyeIcon,
  BoltIcon,
  DocumentTextIcon,
  BeakerIcon,
  UserIcon,
  CpuChipIcon,
  PaperAirplaneIcon
} from '@heroicons/vue/24/outline'

// Components
import DropdownMenu from './DropdownMenu.vue'
import VersionHistoryModal from './VersionHistoryModal.vue'
import NewFileModal from './NewFileModal.vue'

// Props
interface Props {
  project?: any
}

const props = withDefaults(defineProps<Props>(), {
  project: null
})

// Emits
const emit = defineEmits<{
  execute: [code: string, language: string]
  save: [project: any]
}>()

// Stores
const settingsStore = useSettingsStore()
const notificationStore = useNotificationStore()

// Refs
const editorContainer = ref<HTMLElement>()
const autoSaveInterval = ref<ReturnType<typeof setInterval> | null>(null)

// State
const projectName = ref('Untitled Project')
const selectedLanguage = ref('python')
const codeContent = ref('')
const openFiles = ref([
  { name: 'main.py', content: '', language: 'python', saved: true }
])
const activeFileIndex = ref(0)
const isMonacoLoaded = ref(false)
const monacoEditor = ref<any>(null)

// AI Assistant
const showAIAssistant = ref(false)
const aiMessages = ref<any[]>([
  {
    role: 'assistant',
    content: 'Hello! I\'m here to help you with your code. You can ask me to review, optimize, document, or generate tests for your code.',
    type: 'text'
  }
])
const aiInput = ref('')
const aiTyping = ref(false)
const aiSuggestion = ref<any>(null)
const showAISuggestion = ref(false)

// Execution
const isExecuting = ref(false)
const showOutput = ref(false)
const activeOutputTab = ref<'console' | 'errors' | 'tests'>('console')
const executionOutput = ref<any[]>([])
const executionErrors = ref<any[]>([])
const testResults = ref<any[]>([])

// Version Control
const showVersionHistory = ref(false)
const codeVersions = ref<any[]>([])

// File Management
const showNewFileModal = ref(false)

// Computed
const availableLanguages = computed(() => settingsStore.availableCodeLanguages)
const canExecute = computed(() => 
  codeContent.value.trim().length > 0 && ['python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'go', 'rust'].includes(selectedLanguage.value)
)
const codeLines = computed(() => codeContent.value.split('\n'))
const activeFile = computed(() => openFiles.value[activeFileIndex.value])

// Lifecycle
// Cleanup function
onUnmounted(() => {
  if (autoSaveInterval.value) {
    clearInterval(autoSaveInterval.value)
  }
  if (monacoEditor.value) {
    monacoEditor.value.dispose()
  }
})

onMounted(async () => {
  if (props.project) {
    loadProject(props.project)
  }
  
  await initializeEditor()
  loadAutoSave()

  // Auto-save every 30 seconds
  autoSaveInterval.value = setInterval(autoSave, 30000)
})

// Watch for active file changes
watch(activeFileIndex, (newIndex) => {
  if (openFiles.value[newIndex]) {
    const file = openFiles.value[newIndex]
    codeContent.value = file.content
    selectedLanguage.value = file.language
    
    if (monacoEditor.value) {
      monacoEditor.value.setValue(file.content)
      monacoEditor.value.getModel()?.setLanguage(file.language)
    }
  }
})

// Watch for code content changes
watch(codeContent, (newContent) => {
  if (activeFile.value) {
    activeFile.value.content = newContent
    activeFile.value.saved = false
  }
  
  // Trigger AI suggestions for certain patterns
  if (settingsStore.experimentSettings.enable_beta_features) {
    checkForAISuggestions(newContent)
  }
})

// Methods
const initializeEditor = async () => {
  try {
    // Try to load Monaco Editor
    const monaco = await import('monaco-editor')
    
    if (editorContainer.value) {
      monacoEditor.value = monaco.editor.create(editorContainer.value, {
        value: codeContent.value,
        language: selectedLanguage.value,
        theme: settingsStore.isDarkMode ? 'vs-dark' : 'vs',
        fontSize: settingsStore.codeSettings.font_size,
        wordWrap: settingsStore.codeSettings.word_wrap ? 'on' : 'off',
        lineNumbers: settingsStore.codeSettings.show_line_numbers ? 'on' : 'off',
        automaticLayout: true,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        renderWhitespace: 'selection',
        tabSize: 2,
        insertSpaces: true
      })
      
      // Listen for content changes
      monacoEditor.value.onDidChangeModelContent(() => {
        codeContent.value = monacoEditor.value.getValue()
      })
      
      // Listen for cursor position changes
      monacoEditor.value.onDidChangeCursorPosition((e: any) => {
        // Could be used for context-aware AI suggestions
      })
      
      isMonacoLoaded.value = true
      console.log('✅ Monaco Editor loaded successfully')
    }
  } catch (error) {
    console.warn('Monaco Editor not available, using fallback textarea:', error)
    isMonacoLoaded.value = false
  }
}

const loadProject = (project: any) => {
  projectName.value = project.name || 'Untitled Project'
  
  if (project.files && project.files.length > 0) {
    openFiles.value = project.files
  } else {
    // Single file project
    openFiles.value = [{
      name: project.filename || 'main.py',
      content: project.content || '',
      language: project.language || 'python',
      saved: true
    }]
  }
  
  activeFileIndex.value = 0
  codeContent.value = openFiles.value[0].content
  selectedLanguage.value = openFiles.value[0].language
}

const saveProject = () => {
  const project = {
    name: projectName.value,
    files: openFiles.value,
    language: selectedLanguage.value,
    lastModified: new Date().toISOString()
  }
  
  emit('save', project)
  
  // Mark all files as saved
  openFiles.value.forEach(file => {
    file.saved = true
  })
  
  // Save version
  saveVersion()
  
  notificationStore.success('Project saved successfully')
}

const autoSave = () => {
  if (settingsStore.codeSettings.auto_save && activeFile.value && !activeFile.value.saved) {
    saveProject()
  }
}

const loadAutoSave = () => {
  const autoSaved = localStorage.getItem(`code-canvas-autosave-${projectName.value}`)
  if (autoSaved) {
    try {
      const data = JSON.parse(autoSaved)
      if (data.timestamp > Date.now() - 24 * 60 * 60 * 1000) { // Within 24 hours
        openFiles.value = data.files
        codeContent.value = data.files[0]?.content || ''
        notificationStore.info('Auto-saved content restored')
      }
    } catch (error) {
      console.error('Failed to load auto-save:', error)
    }
  }
}

const saveVersion = () => {
  const version = {
    id: Date.now().toString(),
    timestamp: new Date().toISOString(),
    files: JSON.parse(JSON.stringify(openFiles.value)),
    message: `Auto-save: ${new Date().toLocaleString()}`
  }
  
  codeVersions.value.unshift(version)
  
  // Keep only last 20 versions
  if (codeVersions.value.length > 20) {
    codeVersions.value = codeVersions.value.slice(0, 20)
  }
}

// File Management
const addNewFile = () => {
  showNewFileModal.value = true
}

const createNewFile = (filename: string, language: string) => {
  const newFile = {
    name: filename,
    content: '',
    language,
    saved: false
  }
  
  openFiles.value.push(newFile)
  activeFileIndex.value = openFiles.value.length - 1
  showNewFileModal.value = false
}

const closeFile = (index: number) => {
  if (openFiles.value.length === 1) {
    notificationStore.warning('Cannot close the last file')
    return
  }
  
  const file = openFiles.value[index]
  if (!file.saved) {
    if (!confirm(`File "${file.name}" has unsaved changes. Close anyway?`)) {
      return
    }
  }
  
  openFiles.value.splice(index, 1)
  
  if (activeFileIndex.value >= openFiles.value.length) {
    activeFileIndex.value = openFiles.value.length - 1
  } else if (activeFileIndex.value > index) {
    activeFileIndex.value--
  }
}

// Code Execution
const executeCode = async (): Promise<void> => {
  if (!canExecute.value || isExecuting.value) return

  isExecuting.value = true
  showOutput.value = true
  activeOutputTab.value = 'console'

  // Clear previous results
  executionOutput.value = []
  executionErrors.value = []
  testResults.value = []

  try {
    const result: CodeExecutionResult = await apiClient.executeCode(codeContent.value, selectedLanguage.value)

    if (result.status === 'success') {
      executionOutput.value.push({
        type: 'success',
        content: result.output || 'Code executed successfully',
        timestamp: new Date()
      })

      // Note: The API doesn't return tests in the execution result
      // Tests would need to be handled separately if implemented
    } else {
      executionErrors.value.push({
        type: 'Runtime Error',
        message: result.error || 'Unknown error occurred',
        line: null,
        column: null
      })

      executionOutput.value.push({
        type: 'error',
        content: result.error || 'Code execution failed',
        timestamp: new Date()
      })
    }
  } catch (error: any) {
    executionErrors.value.push({
      type: 'Execution Error',
      message: error.message || 'Failed to execute code',
      line: null,
      column: null
    })

    executionOutput.value.push({
      type: 'error',
      content: `Execution failed: ${error.message}`,
      timestamp: new Date()
    })
  } finally {
    isExecuting.value = false
  }
}

// AI Assistant Functions
const requestCodeReview = async () => {
  aiTyping.value = true
  
  try {
    const response = await apiClient.requestCodeReview(codeContent.value, selectedLanguage.value)
    
    aiMessages.value.push({
      role: 'assistant',
      content: response.review,
      type: 'text'
    })
    
    if (response.suggestions) {
      aiSuggestion.value = response.suggestions[0]
      showAISuggestion.value = true
    }
  } catch (error) {
    aiMessages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error while reviewing your code. Please try again.',
      type: 'text'
    })
  } finally {
    aiTyping.value = false
  }
}

const requestOptimization = async () => {
  aiTyping.value = true
  
  try {
    const response = await apiClient.optimizeCode(codeContent.value, selectedLanguage.value)
    
    aiMessages.value.push({
      role: 'assistant',
      content: 'Here\'s an optimized version of your code:',
      type: 'text'
    })
    
    aiMessages.value.push({
      role: 'assistant',
      content: response.optimized_code,
      type: 'code'
    })
    
    aiMessages.value.push({
      role: 'assistant',
      content: response.explanation,
      type: 'text'
    })
  } catch (error) {
    aiMessages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error while optimizing your code. Please try again.',
      type: 'text'
    })
  } finally {
    aiTyping.value = false
  }
}

const generateDocumentation = async () => {
  aiTyping.value = true
  
  try {
    const response = await apiClient.generateDocumentation(codeContent.value, selectedLanguage.value)
    
    aiMessages.value.push({
      role: 'assistant',
      content: 'Here\'s the generated documentation for your code:',
      type: 'text'
    })
    
    aiMessages.value.push({
      role: 'assistant',
      content: response.documentation,
      type: 'code'
    })
  } catch (error) {
    aiMessages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error while generating documentation. Please try again.',
      type: 'text'
    })
  } finally {
    aiTyping.value = false
  }
}

const generateTests = async () => {
  aiTyping.value = true
  
  try {
    const response = await apiClient.generateTests(codeContent.value, selectedLanguage.value)
    
    aiMessages.value.push({
      role: 'assistant',
      content: 'Here are some test cases for your code:',
      type: 'text'
    })
    
    aiMessages.value.push({
      role: 'assistant',
      content: response.test_code,
      type: 'code'
    })
  } catch (error) {
    aiMessages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error while generating tests. Please try again.',
      type: 'text'
    })
  } finally {
    aiTyping.value = false
  }
}

const sendAIMessage = async () => {
  if (!aiInput.value.trim() || aiTyping.value) return
  
  const userMessage = aiInput.value.trim()
  aiInput.value = ''
  
  aiMessages.value.push({
    role: 'user',
    content: userMessage,
    type: 'text'
  })
  
  aiTyping.value = true
  
  try {
    const response = await apiClient.chatWithAI(userMessage, {
      code: codeContent.value,
      language: selectedLanguage.value,
      context: 'code_assistant'
    })
    
    aiMessages.value.push({
      role: 'assistant',
      content: response.message,
      type: 'text'
    })
  } catch (error) {
    aiMessages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again.',
      type: 'text'
    })
  } finally {
    aiTyping.value = false
  }
}

const checkForAISuggestions = (code: string) => {
  // Simple pattern matching for AI suggestions
  const patterns = [
    { pattern: /for.*in.*range\(\d+\)/, suggestion: 'Consider using list comprehension for better performance' },
    { pattern: /if.*==.*True/, suggestion: 'You can simplify this condition' },
    { pattern: /try:.*except:/, suggestion: 'Consider specifying the exception type' }
  ]
  
  for (const { pattern, suggestion } of patterns) {
    if (pattern.test(code)) {
      aiSuggestion.value = {
        description: suggestion,
        code: code
      }
      showAISuggestion.value = true
      break
    }
  }
}

const applyAISuggestion = () => {
  if (aiSuggestion.value && aiSuggestion.value.improved_code) {
    codeContent.value = aiSuggestion.value.improved_code
    
    if (monacoEditor.value) {
      monacoEditor.value.setValue(codeContent.value)
    }
  }
  
  showAISuggestion.value = false
  aiSuggestion.value = null
}

// Utility Functions
const onLanguageChange = () => {
  if (activeFile.value) {
    activeFile.value.language = selectedLanguage.value
  }
  
  if (monacoEditor.value) {
    monacoEditor.value.getModel()?.setLanguage(selectedLanguage.value)
  }
}

const onCodeChange = () => {
  if (activeFile.value) {
    activeFile.value.content = codeContent.value
    activeFile.value.saved = false
  }
}

const handleEditorKeydown = (event: KeyboardEvent) => {
  // Handle tab indentation
  if (event.key === 'Tab') {
    event.preventDefault()
    const textarea = event.target as HTMLTextAreaElement
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    
    const spaces = '  ' // 2 spaces
    textarea.value = textarea.value.substring(0, start) + spaces + textarea.value.substring(end)
    textarea.selectionStart = textarea.selectionEnd = start + spaces.length
    
    codeContent.value = textarea.value
  }
  
  // Save on Ctrl/Cmd + S
  if ((event.ctrlKey || event.metaKey) && event.key === 's') {
    event.preventDefault()
    saveProject()
  }
}

const getLineCount = () => {
  return codeContent.value.split('\n').length
}

const formatFileSize = (length: number) => {
  if (length < 1024) return `${length} B`
  if (length < 1024 * 1024) return `${(length / 1024).toFixed(1)} KB`
  return `${(length / (1024 * 1024)).toFixed(1)} MB`
}

const formatTime = (timestamp: Date) => {
  return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getLanguageIcon = (language: string) => {
  // Return appropriate icon component for language
  return CodeBracketIcon // Fallback
}

const goToError = (error: any) => {
  if (error.line && monacoEditor.value) {
    monacoEditor.value.revealLineInCenter(error.line)
    monacoEditor.value.setPosition({ lineNumber: error.line, column: error.column || 1 })
    monacoEditor.value.focus()
  }
}

const clearOutput = () => {
  executionOutput.value = []
  executionErrors.value = []
  testResults.value = []
}

const exportCode = () => {
  const fileContent = activeFile.value ? activeFile.value.content : codeContent.value
  const fileName = activeFile.value ? activeFile.value.name : `code.${selectedLanguage.value}`
  
  const blob = new Blob([fileContent], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = fileName
  a.click()
  URL.revokeObjectURL(url)
}

const shareProject = () => {
  // Implement project sharing
  notificationStore.info('Project sharing feature coming soon!')
}

const generateAPI = () => {
  // Implement API generation
  notificationStore.info('API generation feature coming soon!')
}

const restoreVersion = (version: any) => {
  openFiles.value = JSON.parse(JSON.stringify(version.files))
  activeFileIndex.value = 0
  codeContent.value = openFiles.value[0].content
  selectedLanguage.value = openFiles.value[0].language
  
  if (monacoEditor.value) {
    monacoEditor.value.setValue(codeContent.value)
  }
  
  showVersionHistory.value = false
  notificationStore.success('Version restored successfully')
}
</script>

<style scoped>
/* Monaco Editor container */
.monaco-editor-container {
  width: 100%;
  height: 100%;
}

/* Custom scrollbar for output area */
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

/* File tab styles */
.file-tab {
  position: relative;
}

.file-tab.unsaved::after {
  content: '•';
  position: absolute;
  top: 50%;
  right: 4px;
  transform: translateY(-50%);
  color: #ef4444;
  font-weight: bold;
}

/* Code syntax highlighting fallback */
.code-fallback {
  font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Monaco, Inconsolata, 'Roboto Mono', monospace;
  line-height: 1.5;
  tab-size: 2;
}

/* AI suggestion animation */
.ai-suggestion-enter-active,
.ai-suggestion-leave-active {
  transition: all 0.3s ease;
}

.ai-suggestion-enter-from,
.ai-suggestion-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* Responsive design */
@media (max-width: 1024px) {
  .w-80 {
    width: 100%;
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    z-index: 10;
  }
}
</style>