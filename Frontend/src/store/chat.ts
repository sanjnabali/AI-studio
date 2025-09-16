// src/store/chat.ts - Fixed Chat Store
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '../api/client'

// Interfaces
interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  type: 'text' | 'image' | 'voice' | 'file'
  metadata: {
    model?: string
    latency?: number
    sources?: string[]
    citations?: string[]
    [key: string]: any
  }
}

interface Chat {
  id: string
  title: string
  messages: ChatMessage[]
  created: Date
  updated: Date
  settings: {
    model: string
    temperature: number
    maxTokens: number
    domain: string
  }
}

interface ChatRequest {
  domain?: string
  useRAG?: boolean
  temperature?: number
  maxTokens?: number
}

interface SystemHealth {
  status: string
  models_status: string
  ready_for_chat: boolean
  performance_mode: boolean
}

export const useChatStore = defineStore('chat', () => {
  // State
  const chats = ref<Chat[]>([])
  const activeChat = ref<Chat | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const systemHealth = ref<SystemHealth | null>(null)
  const supportedLanguages = ref<string[]>(['python', 'javascript', 'html', 'css', 'java', 'cpp'])
  const modelStatus = ref<any>(null)

  // Computed
  const activeChatMessages = computed(() => activeChat.value?.messages || [])
  const isSystemReady = computed(() => systemHealth.value?.ready_for_chat || false)

  // Actions
  function createChat(title?: string): Chat {
    const chat: Chat = {
      id: generateId(),
      title: title || 'New Chat',
      messages: [],
      created: new Date(),
      updated: new Date(),
      settings: {
        model: 'gemini-pro',
        temperature: 0.7,
        maxTokens: 1024,
        domain: 'general'
      }
    }

    chats.value.unshift(chat)
    activeChat.value = chat
    return chat
  }

  function selectChat(chatId: string): void {
    const chat = chats.value.find(c => c.id === chatId)
    if (chat) {
      activeChat.value = chat
    }
  }

  function deleteChat(chatId: string): void {
    const index = chats.value.findIndex(c => c.id === chatId)
    if (index > -1) {
      chats.value.splice(index, 1)
      
      // If deleted chat was active, select another or create new
      if (activeChat.value?.id === chatId) {
        if (chats.value.length > 0) {
          activeChat.value = chats.value[0]
        } else {
          createChat()
        }
      }
    }
  }

  function updateChatTitle(chatId: string, title: string): void {
    const chat = chats.value.find(c => c.id === chatId)
    if (chat) {
      chat.title = title
      chat.updated = new Date()
    }
  }

  async function sendMessage(content: string, options: ChatRequest = {}): Promise<void> {
    if (!activeChat.value) {
      createChat()
    }

    if (!activeChat.value) return

    loading.value = true
    error.value = null

    // Add user message
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date(),
      type: 'text',
      metadata: {}
    }

    activeChat.value.messages.push(userMessage)
    activeChat.value.updated = new Date()

    // Auto-generate title for first message
    if (activeChat.value.messages.length === 1) {
      activeChat.value.title = content.slice(0, 50) + (content.length > 50 ? '...' : '')
    }

    try {
      // Prepare request
      const requestMessages = activeChat.value.messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      const request = {
        messages: requestMessages,
        domain: options.domain || activeChat.value.settings.domain,
        temperature: options.temperature || activeChat.value.settings.temperature,
        max_new_tokens: options.maxTokens || activeChat.value.settings.maxTokens,
        use_rag: options.useRAG || false
      }

      // Send to appropriate endpoint
      const response = options.useRAG 
        ? await apiClient.sendRAGMessage(request)
        : await apiClient.sendTextMessage(request)

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: response.response || response.result || response.text || response.output || 'No response',
        timestamp: new Date(),
        type: 'text',
        metadata: {
          model: activeChat.value.settings.model,
          latency: response.latency_ms,
          sources: response.sources,
          citations: response.citations
        }
      }

      activeChat.value.messages.push(assistantMessage)
      activeChat.value.updated = new Date()

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to send message'
      console.error('Send message error:', err)
    } finally {
      loading.value = false
    }
  }

  async function executeCode(code: string, language: string = 'python'): Promise<any> {
    try {
      const response = await apiClient.executeCode({
        code,
        language,
        timeout: 30000
      })
      return response
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : 'Code execution failed',
        output: '',
        executionTime: 0
      }
    }
  }

  async function transcribeAudio(audioFile: File): Promise<any> {
    try {
      const response = await apiClient.transcribeAudio(audioFile)
      return {
        success: true,
        transcription: response.transcription
      }
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : 'Transcription failed'
      }
    }
  }

  async function uploadDocuments(files: File[]): Promise<any> {
    try {
      const response = await apiClient.uploadDocuments(files)
      return {
        success: true,
        files: response.files
      }
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : 'Upload failed'
      }
    }
  }

  async function checkSystemHealth(): Promise<void> {
    try {
      const health = await apiClient.checkHealth()
      systemHealth.value = health
    } catch (err) {
      console.warn('Health check failed:', err)
      systemHealth.value = {
        status: 'error',
        models_status: 'offline',
        ready_for_chat: false,
        performance_mode: false
      }
    }
  }

  async function getModelStatus(): Promise<void> {
    try {
      const status = await apiClient.getModelStatus()
      modelStatus.value = status
    } catch (err) {
      console.warn('Model status check failed:', err)
    }
  }

  async function getSupportedLanguages(): Promise<void> {
    try {
      const languages = await apiClient.getSupportedLanguages()
      supportedLanguages.value = languages
    } catch (err) {
      console.warn('Failed to get supported languages:', err)
    }
  }

  function clearError(): void {
    error.value = null
  }

  function clearChats(): void {
    chats.value = []
    activeChat.value = null
  }

  async function initialize(): Promise<void> {
    try {
      // Load chats from localStorage
      const savedChats = localStorage.getItem('ai_studio_chats')
      if (savedChats) {
        const parsedChats = JSON.parse(savedChats)
        chats.value = parsedChats.map((chat: any) => ({
          ...chat,
          created: new Date(chat.created),
          updated: new Date(chat.updated),
          messages: chat.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
        }))

        if (chats.value.length > 0) {
          activeChat.value = chats.value[0]
        }
      }

      // Initialize system
      await Promise.all([
        checkSystemHealth(),
        getModelStatus(),
        getSupportedLanguages()
      ])

      // Create first chat if none exist
      if (chats.value.length === 0) {
        createChat()
      }

    } catch (err) {
      console.error('Initialization error:', err)
    }
  }

  // Save chats to localStorage whenever they change
  function saveChats(): void {
    try {
      localStorage.setItem('ai_studio_chats', JSON.stringify(chats.value))
    } catch (err) {
      console.warn('Failed to save chats:', err)
    }
  }

  // Utility functions
  function generateId(): string {
    return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substr(2, 9)
  }

  // Watch for changes and save
  chats.value && saveChats()

  return {
    // State
    chats,
    activeChat,
    loading,
    error,
    systemHealth,
    supportedLanguages,
    modelStatus,

    // Computed
    activeChatMessages,
    isSystemReady,

    // Actions
    createChat,
    selectChat,
    deleteChat,
    updateChatTitle,
    sendMessage,
    executeCode,
    transcribeAudio,
    uploadDocuments,
    checkSystemHealth,
    getModelStatus,
    getSupportedLanguages,
    clearError,
    clearChats,
    initialize,
    saveChats
  }
})