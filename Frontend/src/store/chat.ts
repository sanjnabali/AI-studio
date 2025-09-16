// src/store/chat.ts - Enhanced version
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { apiClient } from '../api/client'
import type { Chat, Message, ModelConfig } from '../types'

const STORAGE_KEY = 'ai-studio-chats'

export const useChatStore = defineStore('chat', () => {
  const chats = ref<Chat[]>([])
  const activeChat = ref<Chat | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // System status
  const systemHealth = ref<any>(null)
  const modelStatus = ref<any>(null)
  const supportedLanguages = ref<string[]>(['python', 'javascript', 'bash'])

  const activeChatMessages = computed(() => activeChat.value?.messages || [])
  const isSystemReady = computed(() => systemHealth.value?.ready_for_chat || false)

  // Watch for changes and auto-save
  watch(() => chats.value, () => {
    saveToStorage()
  }, { deep: true })

  watch(() => activeChat.value, () => {
    saveToStorage()
  }, { deep: true })

  // Storage functions
  function saveToStorage() {
    try {
      const data = {
        chats: chats.value,
        activeChatId: activeChat.value?.id || null,
        timestamp: Date.now()
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    } catch (error) {
      console.warn('Failed to save chats to localStorage:', error)
    }
  }

  function loadFromStorage() {
    try {
      const data = localStorage.getItem(STORAGE_KEY)
      if (data) {
        const parsed = JSON.parse(data)
        chats.value = parsed.chats || []
        
        // Restore active chat
        if (parsed.activeChatId && chats.value.length > 0) {
          const foundChat = chats.value.find(c => c.id === parsed.activeChatId)
          activeChat.value = foundChat || chats.value[0]
        } else if (chats.value.length > 0) {
          activeChat.value = chats.value[0]
        }
        
        return true
      }
    } catch (error) {
      console.warn('Failed to load chats from localStorage:', error)
    }
    return false
  }

  // System monitoring
  async function checkSystemHealth() {
    try {
      systemHealth.value = await apiClient.checkHealth()
      return systemHealth.value
    } catch (err) {
      console.error('System health check failed:', err)
      systemHealth.value = { status: 'unhealthy', ready_for_chat: false }
      return systemHealth.value
    }
  }

  async function getModelStatus() {
    try {
      modelStatus.value = await apiClient.getModelStatus()
      return modelStatus.value
    } catch (err) {
      console.error('Model status check failed:', err)
      return null
    }
  }

  async function loadSupportedLanguages() {
    try {
      supportedLanguages.value = await apiClient.getSupportedLanguages()
    } catch (err) {
      console.warn('Failed to load supported languages:', err)
    }
  }

  function createChat(title: string = ''): Chat {
    const chat: Chat = {
      id: Date.now().toString(),
      title: title || `Chat ${chats.value.length + 1}`,
      messages: [],
      created: new Date(),
      updated: new Date(),
      modelConfig: {
        model: 'gemini-pro',
        temperature: 0.7,
        topK: 40,
        topP: 0.9,
        maxTokens: 1024,
        safetyLevel: 'medium'
      }
    }
    chats.value.unshift(chat)
    activeChat.value = chat
    return chat
  }

  function selectChat(chatId: string) {
    const chat = chats.value.find(c => c.id === chatId)
    if (chat) {
      activeChat.value = chat
      error.value = null
      return true
    }
    return false
  }

  function addMessage(message: Omit<Message, 'id' | 'timestamp'>) {
    if (!activeChat.value) {
      createChat()
    }
    
    const newMessage: Message = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date()
    }
    
    activeChat.value!.messages.push(newMessage)
    activeChat.value!.updated = new Date()
    
    // Auto-generate title from first user message
    if (activeChat.value!.messages.length === 1 && message.role === 'user') {
      const content = message.content.trim()
      activeChat.value!.title = content.length > 50 
        ? content.substring(0, 50) + '...' 
        : content
    }
    
    return newMessage
  }

  // Enhanced send message with backend integration
  async function sendMessage(content: string, config?: {
    domain?: string
    useRAG?: boolean
    temperature?: number
    maxTokens?: number
  }): Promise<Message | null> {
    if (!content.trim()) return null

    loading.value = true
    error.value = null

    try {
      // Add user message
      const userMessage = addMessage({
        role: 'user',
        content: content.trim(),
        type: 'text',
        metadata: {}
      })

      // Prepare messages for API
      const messages = activeChat.value!.messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      // Choose API endpoint based on RAG setting
      const response = config?.useRAG 
        ? await apiClient.sendRAGMessage({
            messages,
            domain: config?.domain || 'general',
            temperature: config?.temperature || activeChat.value!.modelConfig.temperature,
            max_new_tokens: config?.maxTokens || activeChat.value!.modelConfig.maxTokens,
            use_rag: true
          })
        : await apiClient.sendTextMessage({
            messages,
            domain: config?.domain || 'general',
            temperature: config?.temperature || activeChat.value!.modelConfig.temperature,
            max_new_tokens: config?.maxTokens || activeChat.value!.modelConfig.maxTokens
          })

      // Extract response content
      const responseContent = response.response || response.result || response.text || response.output

      if (!responseContent) {
        throw new Error('Empty response from AI')
      }

      // Add assistant message
      const assistantMessage = addMessage({
        role: 'assistant',
        content: responseContent,
        type: 'text',
        metadata: {
          latency: response.latency_ms,
          model_status: response.model_status,
          domain: response.domain,
          citations: response.citations,
          sources: response.sources
        }
      })

      return assistantMessage
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to send message'
      console.error('Send message error:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  // Code execution
  async function executeCode(code: string, language: string): Promise<{
    success: boolean
    output?: string
    error?: string
    executionTime?: number
  }> {
    loading.value = true
    error.value = null

    try {
      const result = await apiClient.executeCode({
        code,
        language,
        timeout: 30
      })

      return {
        success: true,
        output: result.output,
        error: result.error ?? undefined,   // ✅ fixes type mismatch
        executionTime: result.execution_time,
}
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Code execution failed'
      error.value = errorMessage
      return {
        success: false,
        error: errorMessage
      }
    } finally {
      loading.value = false
    }
  }

  // Voice transcription
  async function transcribeAudio(audioFile: File): Promise<{
    success: boolean
    transcription?: string
    confidence?: number
    error?: string
  }> {
    loading.value = true
    error.value = null

    try {
      const result = await apiClient.transcribeAudio(audioFile)
      
      return {
        success: result.status === 'success',
        transcription: result.transcription,
        confidence: result.confidence,
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Voice transcription failed'
      error.value = errorMessage
      return {
        success: false,
        error: errorMessage
      }
    } finally {
      loading.value = false
    }
  }

  // Document management
  async function uploadDocuments(files: File[]): Promise<{
    success: boolean
    message?: string
    uploadedFiles?: any[]
    error?: string
  }> {
    loading.value = true
    error.value = null

    try {
      const result = await apiClient.uploadDocuments(files)
      return {
        success: true,
        message: result.message,
        uploadedFiles: result.files
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Document upload failed'
      error.value = errorMessage
      return {
        success: false,
        error: errorMessage
      }
    } finally {
      loading.value = false
    }
  }

  async function getUploadedDocuments(): Promise<any[]> {
    try {
      return await apiClient.getDocuments()
    } catch (err) {
      console.error('Failed to get documents:', err)
      return []
    }
  }

  function updateMessage(messageId: string, updates: Partial<Message>) {
    if (!activeChat.value) return false
    
    const messageIndex = activeChat.value.messages.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return false
    
    activeChat.value.messages[messageIndex] = {
      ...activeChat.value.messages[messageIndex],
      ...updates
    }
    activeChat.value.updated = new Date()
    return true
  }

  function deleteMessage(messageId: string) {
    if (!activeChat.value) return false
    
    const messageIndex = activeChat.value.messages.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return false
    
    activeChat.value.messages.splice(messageIndex, 1)
    activeChat.value.updated = new Date()
    return true
  }

  function deleteChat(chatId: string) {
    const index = chats.value.findIndex(c => c.id === chatId)
    if (index === -1) return false
    
    chats.value.splice(index, 1)
    
    if (activeChat.value?.id === chatId) {
      activeChat.value = chats.value.length > 0 ? chats.value[0] : null
    }
    
    return true
  }

  function updateChatTitle(chatId: string, title: string) {
    const chat = chats.value.find(c => c.id === chatId)
    if (chat) {
      chat.title = title
      chat.updated = new Date()
      return true
    }
    return false
  }

  function duplicateChat(chatId: string) {
    const originalChat = chats.value.find(c => c.id === chatId)
    if (!originalChat) return null
    
    const duplicatedChat: Chat = {
      id: Date.now().toString(),
      title: `${originalChat.title} (Copy)`,
      messages: [...originalChat.messages],
      created: new Date(),
      updated: new Date(),
      modelConfig: { ...originalChat.modelConfig }
    }
    
    chats.value.unshift(duplicatedChat)
    activeChat.value = duplicatedChat
    return duplicatedChat
  }

  function clearAllChats() {
    chats.value = []
    activeChat.value = null
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch (error) {
      console.warn('Failed to clear localStorage:', error)
    }
  }

  function exportChats() {
    const data = {
      chats: chats.value,
      exported: new Date(),
      version: '1.0'
    }
    return JSON.stringify(data, null, 2)
  }

  function importChats(data: string) {
    try {
      const parsed = JSON.parse(data)
      if (parsed.chats && Array.isArray(parsed.chats)) {
        chats.value = parsed.chats
        activeChat.value = chats.value.length > 0 ? chats.value[0] : null
        return true
      }
    } catch (error) {
      console.error('Failed to import chats:', error)
    }
    return false
  }

  // Search functionality
  function searchChats(query: string) {
    const lowerQuery = query.toLowerCase()
    return chats.value.filter(chat => 
      chat.title.toLowerCase().includes(lowerQuery) ||
      chat.messages.some(msg => 
        msg.content.toLowerCase().includes(lowerQuery)
      )
    )
  }

  // Get chat statistics
  const chatStats = computed(() => {
    const totalChats = chats.value.length
    const totalMessages = chats.value.reduce((sum, chat) => sum + chat.messages.length, 0)
    const userMessages = chats.value.reduce((sum, chat) => 
      sum + chat.messages.filter(msg => msg.role === 'user').length, 0
    )
    const assistantMessages = totalMessages - userMessages
    
    return {
      totalChats,
      totalMessages,
      userMessages,
      assistantMessages
    }
  })

  // Clear error
  function clearError() {
    error.value = null
  }

  // Initialize store
  async function initialize() {
    const loaded = loadFromStorage()
    if (!loaded && chats.value.length === 0) {
      createChat('Welcome to AI Studio')
    }
    
    // Check system health
    await checkSystemHealth()
    await getModelStatus()
    await loadSupportedLanguages()
  }

  return {
    // State
    chats,
    activeChat,
    loading,
    error,
    systemHealth,
    modelStatus,
    supportedLanguages,
    activeChatMessages,
    chatStats,
    isSystemReady,
    
    // Actions
    createChat,
    selectChat,
    addMessage,
    sendMessage,
    executeCode,
    transcribeAudio,
    uploadDocuments,
    getUploadedDocuments,
    updateMessage,
    deleteMessage,
    deleteChat,
    updateChatTitle,
    duplicateChat,
    clearAllChats,
    exportChats,
    importChats,
    searchChats,
    checkSystemHealth,
    getModelStatus,
    loadSupportedLanguages,
    clearError,
    saveToStorage,
    loadFromStorage,
    initialize
  }
})