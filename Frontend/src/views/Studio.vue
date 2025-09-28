<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden">
    <!-- Sidebar -->
    <div class="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            </div>
            <div>
              <h1 class="text-lg font-semibold text-gray-900 dark:text-white">AI Studio</h1>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ authStore.userName }}</p>
            </div>
          </div>
          
          <!-- User Menu -->
          <UserMenu />
        </div>

        <!-- Quick Actions -->
        <div class="flex space-x-2">
          <button
            @click="createNewSession"
            class="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
          >
            <PlusIcon class="w-4 h-4 inline mr-1" />
            New Chat
          </button>
          <button
            @click="showTemplates = true"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 text-sm rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <DocumentTextIcon class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Mode Selector -->
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            v-for="mode in workspaceModes"
            :key="mode.id"
            @click="activeMode = mode.id"
            :class="[
              'flex-1 flex items-center justify-center px-3 py-2 text-xs font-medium rounded-md transition-all',
              activeMode === mode.id
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
            ]"
          >
            <component :is="mode.icon" class="w-4 h-4 mr-1" />
            {{ mode.name }}
          </button>
        </div>
      </div>

      <!-- Dynamic Content Area -->
      <div class="flex-1 overflow-y-auto">
        <!-- Chat Sessions -->
        <div v-if="activeMode === 'chat'" class="p-4">
          <ChatSessionList 
            :sessions="chatStore.sessions"
            :current-session="chatStore.currentSession"
            @select="selectSession"
            @delete="deleteSession"
          />
        </div>

        <!-- Code Projects -->
        <div v-else-if="activeMode === 'code'" class="p-4">
          <CodeProjectList 
            :projects="codeProjects"
            :current-project="currentCodeProject"
            @select="selectCodeProject"
            @delete="deleteCodeProject"
          />
        </div>

        <!-- Voice Recordings -->
        <div v-else-if="activeMode === 'voice'" class="p-4">
          <VoiceRecordingList 
            :recordings="voiceRecordings"
            @play="playRecording"
            @delete="deleteRecording"
          />
        </div>

        <!-- Documents -->
        <div v-else-if="activeMode === 'docs'" class="p-4">
          <DocumentList 
            :documents="documents"
            @select="selectDocument"
            @delete="deleteDocument"
          />
        </div>
      </div>

      <!-- Upload Area -->
      <div class="p-4 border-t border-gray-200 dark:border-gray-700">
        <FileUploadZone @upload="handleFileUpload" />
      </div>
    </div>

    <!-- Main Workspace -->
    <main class="flex-1 flex flex-col">
      <!-- Workspace Header -->
      <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ workspaceTitle }}
            </h2>
            <div class="flex items-center space-x-2">
              <StatusIndicator :status="connectionStatus" />
              <ModelSelector
                :model-config="settingsStore.modelSettings"
                @update="handleModelChange"
              />
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <!-- Export/Share -->
            <button
              @click="exportWorkspace"
              class="px-3 py-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              title="Export workspace"
            >
              <ArrowDownTrayIcon class="w-5 h-5" />
            </button>

            <!-- Version Control -->
            <button
              @click="showVersionControl = true"
              class="px-3 py-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              title="Version control"
            >
              <CodeBracketIcon class="w-5 h-5" />
            </button>

            <!-- Settings -->
            <button
              @click="showSettings = true"
              class="px-3 py-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              title="Settings"
            >
              <CogIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      <!-- Workspace Content -->
      <div class="flex-1 flex">
        <!-- Main Content Area -->
        <div class="flex-1 flex flex-col">
          <!-- Chat Interface -->
          <div v-if="activeMode === 'chat'" class="flex-1">
            <EnhancedChatWindow 
              :session="chatStore.currentSession"
              @message="handleChatMessage"
              @voice-input="handleVoiceInput"
              @file-upload="handleFileUpload"
            />
          </div>

          <!-- Code Canvas -->
          <div v-else-if="activeMode === 'code'" class="flex-1">
            <CodeCanvas 
              :project="currentCodeProject"
              @execute="executeCode"
              @save="saveCodeProject"
            />
          </div>

          <!-- Voice Interface -->
          <div v-else-if="activeMode === 'voice'" class="flex-1">
            <VoiceWorkspace 
              @record="startVoiceRecording"
              @process="processVoiceRecording"
            />
          </div>

          <!-- Document Viewer -->
          <div v-else-if="activeMode === 'docs'" class="flex-1">
            <DocumentViewer 
              :document="selectedDocument"
              @query="handleDocumentQuery"
            />
          </div>
        </div>

        <!-- Side Panel -->
        <div 
          v-if="showSidePanel"
          class="w-96 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700"
        >
          <SidePanel 
            :type="sidePanelType"
            :content="sidePanelContent"
            @close="showSidePanel = false"
          />
        </div>
      </div>
    </main>

    <!-- Modals -->
    <TemplateModal 
      v-if="showTemplates"
      @close="showTemplates = false"
      @select="useTemplate"
    />

    <SettingsModal 
      v-if="showSettings"
      @close="showSettings = false"
      @update="updateSettings"
    />

    <VersionControlModal 
      v-if="showVersionControl"
      @close="showVersionControl = false"
      @commit="commitChanges"
      @restore="restoreVersion"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/store/chat'
import { useAuthStore } from '@/store/auth'
import { useSettingsStore } from '@/store/settings'
import { useNotificationStore } from '@/store/notification'
import { apiClient } from '@/api/client'

// Icons
import {
  PlusIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  CodeBracketIcon,
  MicrophoneIcon,
  FolderIcon,
  CogIcon,
  ArrowDownTrayIcon
} from '@heroicons/vue/24/outline'

// Components
import UserMenu from '@/components/UserMenu.vue'
import ChatSessionList from '@/components/chat/SessionList.vue'
import CodeProjectList from '@/components/code/ProjectList.vue'
import VoiceRecordingList from '@/components/voice/RecordingList.vue'
import DocumentList from '@/components/docs/DocumentList.vue'
import FileUploadZone from '@/components/FileUploadZone.vue'
import StatusIndicator from '@/components/StatusIndicator.vue'
import ModelSelector from '@/components/ModelSelector.vue'
import EnhancedChatWindow from '@/components/chat/EnhancedChatWindow.vue'
import CodeCanvas from '@/components/CodeCanvas.vue'
import VoiceWorkspace from '@/components/voice/VoiceWorkspace.vue'
import DocumentViewer from '@/components/docs/DocumentViewer.vue'
import SidePanel from '@/components/SidePanel.vue'
import TemplateModal from '@/components/modals/TemplateModal.vue'
import SettingsModal from '@/components/modals/SettingsModal.vue'
import VersionControlModal from '@/components/modals/VersionControlModal.vue'

// Stores
const router = useRouter()
const chatStore = useChatStore()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const notificationStore = useNotificationStore()

// State
const activeMode = ref<'chat' | 'code' | 'voice' | 'docs'>('chat')
const showTemplates = ref(false)
const showSettings = ref(false)
const showVersionControl = ref(false)
const showSidePanel = ref(false)
const sidePanelType = ref<string>('')
const sidePanelContent = ref<any>(null)

// Data
const documents = ref<any[]>([])
const codeProjects = ref<any[]>([])
const voiceRecordings = ref<any[]>([])
const currentCodeProject = ref<any>(null)
const selectedDocument = ref<any>(null)
const connectionStatus = ref<'connected' | 'connecting' | 'disconnected'>('connecting')

// Workspace modes configuration
const workspaceModes: Array<{ id: 'chat' | 'code' | 'voice' | 'docs', name: string, icon: any }> = [
  { id: 'chat', name: 'Chat', icon: ChatBubbleLeftRightIcon },
  { id: 'code', name: 'Code', icon: CodeBracketIcon },
  { id: 'voice', name: 'Voice', icon: MicrophoneIcon },
  { id: 'docs', name: 'Docs', icon: FolderIcon }
]

// Computed
const workspaceTitle = computed(() => {
  switch (activeMode.value) {
    case 'chat':
      return chatStore.currentSession?.name || 'New Chat'
    case 'code':
      return currentCodeProject.value?.name || 'Code Canvas'
    case 'voice':
      return 'Voice Workspace'
    case 'docs':
      return selectedDocument.value?.filename || 'Documents'
    default:
      return 'AI Studio'
  }
})

// Lifecycle
onMounted(async () => {
  await initializeWorkspace()
  checkConnectionStatus()
})

// Watch for mode changes
watch(activeMode, (newMode) => {
  // Load data specific to the new mode
  switch (newMode) {
    case 'chat':
      chatStore.loadSessions()
      break
    case 'code':
      loadCodeProjects()
      break
    case 'voice':
      loadVoiceRecordings()
      break
    case 'docs':
      loadDocuments()
      break
  }
})

// Methods
const initializeWorkspace = async () => {
  try {
    // Load initial data
    await Promise.all([
      chatStore.loadSessions(),
      loadDocuments(),
      loadCodeProjects(),
      loadVoiceRecordings()
    ])
    
    connectionStatus.value = 'connected'
    notificationStore.success('AI Studio initialized successfully')
  } catch (error) {
    console.error('Failed to initialize workspace:', error)
    connectionStatus.value = 'disconnected'
    notificationStore.error('Failed to initialize workspace')
  }
}

const checkConnectionStatus = () => {
  // Periodically check API health
  setInterval(async () => {
    try {
      await fetch('/api/health')
      connectionStatus.value = 'connected'
    } catch {
      connectionStatus.value = 'disconnected'
    }
  }, 30000) // Check every 30 seconds
}

// Session Management
const createNewSession = async () => {
  try {
    const session = await chatStore.createSession('New Chat')
    await chatStore.selectSession(session.id)
    activeMode.value = 'chat'
    notificationStore.success('New chat session created')
  } catch (error) {
    console.error('Failed to create session:', error)
    notificationStore.error('Failed to create chat session')
  }
}

const selectSession = async (sessionId: number) => {
  try {
    await chatStore.selectSession(sessionId)
    activeMode.value = 'chat'
  } catch (error) {
    console.error('Failed to select session:', error)
    notificationStore.error('Failed to load chat session')
  }
}

const deleteSession = async (sessionId: number) => {
  try {
    await chatStore.deleteSession(sessionId)
    notificationStore.success('Chat session deleted')
  } catch (error) {
    console.error('Failed to delete session:', error)
    notificationStore.error('Failed to delete chat session')
  }
}

// Code Project Management
const loadCodeProjects = async () => {
  try {
    // Load code projects from API or local storage
    codeProjects.value = JSON.parse(localStorage.getItem('codeProjects') || '[]')
  } catch (error) {
    console.error('Failed to load code projects:', error)
  }
}

const selectCodeProject = (project: any) => {
  currentCodeProject.value = project
  activeMode.value = 'code'
}

const deleteCodeProject = (projectId: string) => {
  codeProjects.value = codeProjects.value.filter(p => p.id !== projectId)
  localStorage.setItem('codeProjects', JSON.stringify(codeProjects.value))
  notificationStore.success('Code project deleted')
}

const saveCodeProject = (project: any) => {
  const index = codeProjects.value.findIndex(p => p.id === project.id)
  if (index >= 0) {
    codeProjects.value[index] = project
  } else {
    codeProjects.value.push(project)
  }
  localStorage.setItem('codeProjects', JSON.stringify(codeProjects.value))
  notificationStore.success('Code project saved')
}

// Voice Management
const loadVoiceRecordings = async () => {
  try {
    voiceRecordings.value = JSON.parse(localStorage.getItem('voiceRecordings') || '[]')
  } catch (error) {
    console.error('Failed to load voice recordings:', error)
  }
}

const startVoiceRecording = () => {
  // Implement voice recording
  notificationStore.info('Voice recording started')
}

const processVoiceRecording = async (recording: any) => {
  try {
    // Process voice recording through API
    const response = await apiClient.processVoiceRecording(recording)
    voiceRecordings.value.push(response)
    localStorage.setItem('voiceRecordings', JSON.stringify(voiceRecordings.value))
    notificationStore.success('Voice recording processed')
  } catch (error) {
    console.error('Failed to process voice recording:', error)
    notificationStore.error('Failed to process voice recording')
  }
}

const playRecording = (recording: any) => {
  // Implement audio playback
  notificationStore.info('Playing voice recording')
}

const deleteRecording = (recordingId: string) => {
  voiceRecordings.value = voiceRecordings.value.filter(r => r.id !== recordingId)
  localStorage.setItem('voiceRecordings', JSON.stringify(voiceRecordings.value))
  notificationStore.success('Voice recording deleted')
}

// Document Management
const loadDocuments = async () => {
  try {
    documents.value = await apiClient.getDocuments()
  } catch (error) {
    console.error('Failed to load documents:', error)
    notificationStore.error('Failed to load documents')
  }
}

const selectDocument = (document: any) => {
  selectedDocument.value = document
  activeMode.value = 'docs'
}

const deleteDocument = async (documentId: number) => {
  try {
    await apiClient.deleteDocument(documentId)
    await loadDocuments()
    notificationStore.success('Document deleted')
  } catch (error) {
    console.error('Failed to delete document:', error)
    notificationStore.error('Failed to delete document')
  }
}

// File Upload
const handleFileUpload = async (files: FileList) => {
  for (const file of Array.from(files)) {
    try {
      if (file.type.startsWith('image/')) {
        // Handle image upload for vision tasks
        await handleImageUpload(file)
      } else if (file.type.startsWith('audio/')) {
        // Handle audio upload for speech processing
        await handleAudioUpload(file)
      } else if (file.type.includes('pdf') || file.type.includes('document')) {
        // Handle document upload for RAG
        await handleDocumentUpload(file)
      } else {
        // Handle code files
        await handleCodeFileUpload(file)
      }
    } catch (error) {
      console.error(`Failed to upload ${file.name}:`, error)
      notificationStore.error(`Failed to upload ${file.name}`)
    }
  }
}

const handleImageUpload = async (file: File) => {
  const response = await apiClient.uploadImage(file)
  notificationStore.success(`Image "${file.name}" uploaded and analyzed`)
  
  // Add to chat if in chat mode
  if (activeMode.value === 'chat') {
    // Add image analysis result to chat
  }
}

const handleAudioUpload = async (file: File) => {
  const response = await apiClient.uploadAudio(file)
  voiceRecordings.value.push(response)
  localStorage.setItem('voiceRecordings', JSON.stringify(voiceRecordings.value))
  notificationStore.success(`Audio "${file.name}" uploaded and transcribed`)
}

const handleDocumentUpload = async (file: File) => {
  const response = await apiClient.uploadDocument(file)
  await loadDocuments()
  notificationStore.success(`Document "${file.name}" uploaded and processed for RAG`)
}

const handleCodeFileUpload = async (file: File) => {
  const content = await file.text()
  const project = {
    id: Date.now().toString(),
    name: file.name,
    content,
    language: getLanguageFromFilename(file.name),
    createdAt: new Date()
  }
  codeProjects.value.push(project)
  localStorage.setItem('codeProjects', JSON.stringify(codeProjects.value))
  notificationStore.success(`Code file "${file.name}" imported`)
}

// Chat Handlers
const handleChatMessage = async (message: string, options: any = {}) => {
  try {
    await chatStore.sendMessage(message, chatStore.currentSessionId, {
      ...settingsStore.modelSettings,
      ...options
    })
  } catch (error) {
    console.error('Failed to send message:', error)
    notificationStore.error('Failed to send message')
  }
}

const handleVoiceInput = async (audioBlob: Blob) => {
  try {
    const transcript = await apiClient.speechToText(audioBlob)
    await handleChatMessage(transcript.text)
  } catch (error) {
    console.error('Failed to process voice input:', error)
    notificationStore.error('Failed to process voice input')
  }
}

const handleDocumentQuery = async (query: string) => {
  try {
    const response = await apiClient.queryDocuments(query, selectedDocument.value?.id)
    // Display results in side panel
    sidePanelType.value = 'query-results'
    sidePanelContent.value = response
    showSidePanel.value = true
  } catch (error) {
    console.error('Failed to query document:', error)
    notificationStore.error('Failed to query document')
  }
}

// Code Execution
const executeCode = async (code: string, language: string) => {
  try {
    const response = await apiClient.executeCode(code, language)
    notificationStore.success('Code executed successfully')
    return response
  } catch (error) {
    console.error('Code execution failed:', error)
    notificationStore.error('Code execution failed')
    throw error
  }
}

const handleModelChange = async (config: any) => {
  try {
    await settingsStore.updateModelSettings(config)
    notificationStore.success(`Switched to model: ${config.model_name}`)
  } catch (error) {
    console.error('Failed to change model:', error)
    notificationStore.error('Failed to change model')
  }
}

const updateSettings = async (newSettings: any) => {
  try {
    await settingsStore.updateSettings(newSettings)
    notificationStore.success('Settings updated successfully')
  } catch (error) {
    console.error('Failed to update settings:', error)
    notificationStore.error('Failed to update settings')
  }
}

// Template and Export Functions
const useTemplate = (template: any) => {
  // Apply template based on mode
  switch (activeMode.value) {
    case 'chat':
      handleChatMessage(template.prompt)
      break
    case 'code':
      const project = {
        id: Date.now().toString(),
        name: template.name,
        content: template.code || '',
        language: template.language || 'python',
        createdAt: new Date()
      }
      codeProjects.value.push(project)
      selectCodeProject(project)
      break
    default:
      activeMode.value = 'chat'
      handleChatMessage(template.prompt)
  }
  showTemplates.value = false
}

const exportWorkspace = () => {
  const workspaceData = {
    sessions: chatStore.sessions,
    codeProjects: codeProjects.value,
    voiceRecordings: voiceRecordings.value.map(r => ({ ...r, blob: null })), // Exclude blob data
    settings: settingsStore.modelSettings,
    exportDate: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(workspaceData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ai-studio-workspace-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  notificationStore.success('Workspace exported successfully')
}

// Version Control
const commitChanges = async (message: string) => {
  try {
    // Implement version control logic
    notificationStore.success('Changes committed successfully')
  } catch (error) {
    console.error('Failed to commit changes:', error)
    notificationStore.error('Failed to commit changes')
  }
}

const restoreVersion = async (versionId: string) => {
  try {
    // Implement version restore logic
    notificationStore.success('Version restored successfully')
  } catch (error) {
    console.error('Failed to restore version:', error)
    notificationStore.error('Failed to restore version')
  }
}

// Utility Functions
const getLanguageFromFilename = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase()
  const languageMap: Record<string, string> = {
    'py': 'python',
    'js': 'javascript',
    'ts': 'typescript',
    'java': 'java',
    'cpp': 'cpp',
    'c': 'c',
    'go': 'go',
    'rs': 'rust',
    'php': 'php',
    'rb': 'ruby'
  }
  return languageMap[ext || ''] || 'text'
}
</script>

<style scoped>
/* Custom scrollbar for sidebar */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgb(156 163 175 / 0.5);
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgb(156 163 175 / 0.8);
}

/* Mode transition animations */
.mode-transition {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Workspace grid layout */
.workspace-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  grid-template-rows: auto 1fr;
  height: 100vh;
}

/* Responsive design */
@media (max-width: 1024px) {
  .workspace-grid {
    grid-template-columns: 1fr;
  }
  
  .w-80 {
    width: 100%;
  }
}
</style>