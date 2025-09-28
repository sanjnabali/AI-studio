<template>
  <div class="side-panel flex-1 overflow-y-auto">
    <!-- Mode Tabs -->
    <div class="mode-tabs mb-4">
      <div class="flex space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
        <button
          v-for="mode in workspaceModes"
          :key="mode.id"
          @click="activeMode = mode.id"
          :class="[
            'flex-1 flex items-center justify-center py-2 px-3 text-sm font-medium rounded-md transition-colors',
            activeMode === mode.id
              ? 'bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 shadow-sm'
              : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
          ]"
        >
          <component :is="mode.icon" class="w-4 h-4 mr-2" />
          {{ mode.name }}
        </button>
      </div>
    </div>

    <!-- Active Mode Content -->
    <div class="mode-content">
      <component :is="activeModeComponent" :key="activeMode" />
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
      <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Quick Actions</h4>
      <div class="grid grid-cols-2 gap-2">
        <button @click="createNewSession" class="p-2 text-xs text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-800 rounded">
          New Chat
        </button>
        <button @click="showTemplates = true" class="p-2 text-xs text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-800 rounded">
          Templates
        </button>
        <button @click="uploadFile" class="p-2 text-xs text-purple-600 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-800 rounded">
          Upload
        </button>
        <button @click="exportWorkspace" class="p-2 text-xs text-orange-600 dark:text-orange-400 hover:bg-orange-100 dark:hover:bg-orange-800 rounded">
          Export
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { 
  ChatBubbleLeftRightIcon, 
  CodeBracketIcon, 
  MicrophoneIcon, 
  DocumentTextIcon,
  PlusIcon 
} from '@heroicons/vue/24/outline'
import SessionList from './chat/SessionList.vue'
import ProjectList from './code/ProjectList.vue'
import RecordingList from './voice/RecordingList.vue'
import DocumentList from './docs/DocumentList.vue'
import FileUploadZone from './FileUploadZone.vue'
import StatusIndicator from './StatusIndicator.vue'
import EnhancedChatWindow from './chat/EnhancedChatWindow.vue'
import CodeCanvas from './code/CodeCanvas.vue'
import VoiceWorkspace from './voice/VoiceWorkspace.vue'
import DocumentViewer from './docs/DocumentViewer.vue'

interface WorkspaceMode {
  id: string
  name: string
  icon: any
  component: any
}

const props = defineProps<{
  activeMode?: string
}>()

const emit = defineEmits<{
  modeChange: [mode: string]
  createSession: []
  showTemplates: []
  uploadFile: [files: FileList]
  exportWorkspace: []
}>()

const activeMode = ref(props.activeMode || 'chat')

const workspaceModes: WorkspaceMode[] = [
  {
    id: 'chat',
    name: 'Chat',
    icon: ChatBubbleLeftRightIcon,
    component: EnhancedChatWindow
  },
  {
    id: 'code',
    name: 'Code',
    icon: CodeBracketIcon,
    component: CodeCanvas
  },
  {
    id: 'voice',
    name: 'Voice',
    icon: MicrophoneIcon,
    component: VoiceWorkspace
  },
  {
    id: 'docs',
    name: 'Documents',
    icon: DocumentTextIcon,
    component: DocumentViewer
  }
]

const activeModeComponent = computed(() => {
  const mode = workspaceModes.find(m => m.id === activeMode.value)
  return mode ? mode.component : EnhancedChatWindow
})

const createNewSession = () => {
  emit('createSession')
}

const showTemplates = ref(false)

const uploadFile = () => {
  // Trigger file upload
  const input = document.createElement('input')
  input.type = 'file'
  input.multiple = true
  input.onchange = (e) => {
    const files = (e.target as HTMLInputElement).files
    if (files) emit('uploadFile', files)
  }
  input.click()
}

const exportWorkspace = () => {
  emit('exportWorkspace')
}

watch(activeMode, (newMode: string) => {
  emit('modeChange', newMode)
})
</script>

<style scoped>
.side-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.mode-tabs {
  flex-shrink: 0;
}

.mode-content {
  flex: 1;
  overflow: hidden;
}

.quick-actions {
  flex-shrink: 0;
  border-top: 1px solid #e5e7eb;
  margin-top: 1rem;
  padding-top: 1rem;
}
</style>
