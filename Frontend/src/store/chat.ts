import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { Chat, Message, ModelConfig } from '../types'

const STORAGE_KEY = 'ai-studio-chats'
const SETTINGS_KEY = 'ai-studio-settings'

export const useChatStore = defineStore('chat', () => {
  const chats = ref<Chat[]>([])
  const activeChat = ref<Chat | null>(null)
  const loading = ref(false)

  const activeChatMessages = computed(() => activeChat.value?.messages || [])

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

  // Initialize store
  function initialize() {
    const loaded = loadFromStorage()
    if (!loaded && chats.value.length === 0) {
      createChat('Welcome to AI Studio')
    }
  }

  return {
    // State
    chats,
    activeChat,
    loading,
    activeChatMessages,
    chatStats,
    
    // Actions
    createChat,
    selectChat,
    addMessage,
    updateMessage,
    deleteMessage,
    deleteChat,
    updateChatTitle,
    duplicateChat,
    clearAllChats,
    exportChats,
    importChats,
    searchChats,
    saveToStorage,
    loadFromStorage,
    initialize
  }
})