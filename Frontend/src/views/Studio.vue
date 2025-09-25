// Frontend/src/views/studio.vue
<template>
  <div class="studio-layout">
    <!-- Sidebar -->
    <aside class="studio-sidebar">
      <div class="sidebar-content">
        <!-- Chat Sessions -->
        <div class="session-section">
          <div class="section-header">
            <h3 class="section-title">Chat Sessions</h3>
            <button @click="createNewSession" class="btn btn-primary btn-sm">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              New
            </button>
          </div>
          
          <div class="session-list">
            <div v-if="chatStore.sessions.length === 0" class="empty-state">
              <p class="text-sm text-gray-500">No sessions yet</p>
            </div>
            
            <div v-for="session in chatStore.sessions" :key="session.id" 
                 :class="['session-item', { active: session.id === chatStore.currentSessionId }]"
                 @click="selectSession(session.id)">
              <div class="session-info">
                <h4 class="session-name">{{ session.name }}</h4>
                <p class="session-meta">{{ session.message_count }} messages</p>
              </div>
              
              <div class="session-actions">
                <button @click.stop="deleteSession(session.id)" class="btn btn-ghost btn-xs text-red-500">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Documents -->
        <div class="documents-section">
          <div class="section-header">
            <h3 class="section-title">Documents</h3>
            <FileLoader @uploaded="handleDocumentUpload" />
          </div>
          
          <div class="documents-list">
            <div v-if="documents.length === 0" class="empty-state">
              <p class="text-sm text-gray-500">No documents uploaded</p>
            </div>
            
            <div v-for="doc in documents" :key="doc.id" class="document-item">
              <div class="document-info">
                <h4 class="document-name">{{ doc.filename }}</h4>
                <p class="document-meta">
                  {{ formatFileSize(doc.file_size) }} • 
                  {{ doc.processed ? `${doc.chunk_count} chunks` : 'Processing...' }}
                </p>
              </div>
              
              <div class="document-actions">
                <button @click="deleteDocument(doc.id)" class="btn btn-ghost btn-xs text-red-500">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="studio-main">
      <div class="tabs tabs-lifted">
        <button 
          :class="['tab tab-lg', { 'tab-active': activeTab === 'chat' }]"
          @click="activeTab = 'chat'"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          Chat
        </button>
        
        <button 
          :class="['tab tab-lg', { 'tab-active': activeTab === 'code' }]"
          @click="activeTab = 'code'"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
          Code Canvas
        </button>
      </div>

      <div class="tab-content">
        <div v-show="activeTab === 'chat'" class="tab-pane">
          <ChatbotWindow />
        </div>
        
        <div v-show="activeTab === 'code'" class="tab-pane">
          <CodeCanvas />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useChatStore } from '@/store/chat'
import { apiClient } from '@/api/client'
import ChatbotWindow from '@/components/chatbot_window.vue'
import CodeCanvas from '@/components/CodeCanvas.vue'
import FileLoader from '@/components/FileLoader.vue'

const chatStore = useChatStore()
const activeTab = ref<'chat' | 'code'>('chat')
const documents = ref<any[]>([])

onMounted(async () => {
  await Promise.all([
    chatStore.loadSessions(),
    loadDocuments()
  ])
})

const createNewSession = async () => {
  try {
    const session = await chatStore.createSession('New Chat')
    await chatStore.selectSession(session.id)
    activeTab.value = 'chat'
  } catch (error) {
    console.error('Failed to create session:', error)
  }
}

const selectSession = async (sessionId: number) => {
  try {
    await chatStore.selectSession(sessionId)
    activeTab.value = 'chat'
  } catch (error) {
    console.error('Failed to select session:', error)
  }
}

const deleteSession = async (sessionId: number) => {
  if (confirm('Are you sure you want to delete this chat session?')) {
    try {
      await chatStore.deleteSession(sessionId)
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }
}

const loadDocuments = async () => {
  try {
    documents.value = await apiClient.getDocuments()
  } catch (error) {
    console.error('Failed to load documents:', error)
  }
}

const handleDocumentUpload = async (result: any) => {
  await loadDocuments()
  if (window.showNotification) {
    window.showNotification('success', `Document "${result.filename}" uploaded successfully!`)
  }
}

const deleteDocument = async (documentId: number) => {
  if (confirm('Are you sure you want to delete this document?')) {
    try {
      await apiClient.deleteDocument(documentId)
      await loadDocuments()
      if (window.showNotification) {
        window.showNotification('success', 'Document deleted successfully')
      }
    } catch (error) {
      console.error('Failed to delete document:', error)
      if (window.showNotification) {
        window.showNotification('error', 'Failed to delete document')
      }
    }
  }
}

const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Bytes'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
.studio-layout {
  @apply flex h-screen;
}

.studio-sidebar {
  @apply w-80 bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto;
}

.sidebar-content {
  @apply p-4 space-y-6;
}

.section-header {
  @apply flex items-center justify-between mb-3;
}

.section-title {
  @apply text-lg font-semibold;
}

.session-item, .document-item {
  @apply flex items-center justify-between p-3 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors;
}

.session-item.active {
  @apply bg-blue-100 dark:bg-blue-900 border-blue-500;
}

.session-info, .document-info {
  @apply flex-1 min-w-0;
}

.session-name, .document-name {
  @apply text-sm font-medium truncate;
}

.session-meta, .document-meta {
  @apply text-xs text-gray-500 mt-1;
}

.studio-main {
  @apply flex-1 flex flex-col;
}

.tabs {
  @apply border-b border-gray-200 dark:border-gray-700;
}

.tab-content {
  @apply flex-1;
}

.tab-pane {
  @apply h-full;
}
</style>