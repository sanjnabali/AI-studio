<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden">
    <div class="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col overflow-y-auto">
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
                  @click="showSettings = !showSettings; showUserMenu = false"
                  class="w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                  Settings
                </button>
                <button
                  @click="handleLogout"
                  class="w-full text-left px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                  </svg>
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

        <!-- Sessions Section -->
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-semibold text-gray-900 dark:text-white">Chat Sessions</h2>
            <button @click="createNewSession" class="text-blue-600 hover:text-blue-700">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          <div class="space-y-2">
            <div
              v-for="session in chatStore.sessions"
              :key="session.id"
              class="session-item"
              @click="selectSession(session.id)"
            >
              <div class="session-info">
                <p class="session-name">{{ session.name }}</p>
                <p class="session-meta">{{ new Date(session.created_at).toLocaleDateString() }}</p>
              </div>
              <button @click.stop="deleteSession(session.id)" class="text-gray-400 hover:text-red-500">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Documents Section -->
        <div class="p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-semibold text-gray-900 dark:text-white">Documents</h2>
            <FileLoader @upload-success="handleDocumentUpload" />
          </div>
          <div class="space-y-2">
            <div
              v-for="doc in documents"
              :key="doc.id"
              class="document-item"
            >
              <div class="document-info">
                <p class="document-name">{{ doc.filename }}</p>
                <p class="document-meta">{{ formatFileSize(doc.size) }}</p>
              </div>
              <button @click.stop="deleteDocument(doc.id)" class="text-gray-400 hover:text-red-500">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

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
import { ref, computed, onMounted } from 'vue'
import { useChatStore } from '@/store/chat'
import { useAuthStore } from '@/store/auth'
import { apiClient } from '@/api/client'
import ChatbotWindow from '@/components/chatbot_window.vue'
import CodeCanvas from '@/components/CodeCanvas.vue'
import FileLoader from '@/components/FileLoader.vue'

const chatStore = useChatStore()
const authStore = useAuthStore()
const activeTab = ref<'chat' | 'code'>('chat')
const showUserMenu = ref(false)
const showSettings = ref(false)
const documents = ref<any[]>([])

const userInitials = computed(() => {
  if (authStore.userName) {
    return authStore.userName.split(' ').map(n => n[0]).join('').toUpperCase()
  }
  return 'U'
})

const handleLogout = () => {
  authStore.logout()
  // Add navigation to login if needed
}

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