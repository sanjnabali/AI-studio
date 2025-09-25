
// Frontend/src/store/chat.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient, type ChatSession, type ChatMessage } from '@/api/client'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<ChatSession[]>([])
  const currentSession = ref<ChatSession | null>(null)
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isTyping = ref(false)

  const currentSessionId = computed(() => currentSession.value?.id)
  const hasMessages = computed(() => messages.value.length > 0)

  // Alias for sessions to match component expectations
  const chats = computed(() => sessions.value)

  async function loadSessions(): Promise<void> {
    loading.value = true
    try {
      sessions.value = await apiClient.getChatSessions()
    } catch (err: any) {
      error.value = 'Failed to load chat sessions'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function createSession(name?: string, modelConfig?: Record<string, any>): Promise<ChatSession> {
    try {
      const session = await apiClient.createChatSession(name, modelConfig)
      sessions.value.unshift(session)
      return session
    } catch (err: any) {
      error.value = 'Failed to create chat session'
      throw err
    }
  }

  async function selectSession(sessionId: number): Promise<void> {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      currentSession.value = session
      await loadMessages(sessionId)
    }
  }

  async function loadMessages(sessionId: number): Promise<void> {
    loading.value = true
    try {
      messages.value = await apiClient.getSessionMessages(sessionId)
    } catch (err: any) {
      error.value = 'Failed to load messages'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function sendMessage(
    content: string, 
    sessionId?: number, 
    modelConfig?: Record<string, any>
  ): Promise<void> {
    isTyping.value = true
    
    // Add user message immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content,
      message_type: 'text',
      timestamp: new Date().toISOString()
    }
    messages.value.push(userMessage)

    try {
      const response = await apiClient.sendChatMessage(content, sessionId, modelConfig)
      
      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: response.message_id,
        role: 'assistant',
        content: response.message,
        message_type: 'text',
        timestamp: new Date().toISOString(),
        metadata: {
          model_used: response.model_used,
          processing_time: response.processing_time,
          token_count: response.token_count
        }
      }
      messages.value.push(assistantMessage)

      // Update current session if needed
      if (!currentSession.value && response.session_id) {
        await loadSessions()
        const session = sessions.value.find(s => s.id === response.session_id)
        if (session) {
          currentSession.value = session
        }
      }

    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to send message'
      console.error(err)
      
      // Add error message
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        message_type: 'text',
        timestamp: new Date().toISOString()
      }
      messages.value.push(errorMessage)
    } finally {
      isTyping.value = false
    }
  }

  async function deleteSession(sessionId: number): Promise<void> {
    try {
      await apiClient.deleteChatSession(sessionId)
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null
        messages.value = []
      }
    } catch (err: any) {
      error.value = 'Failed to delete session'
      throw err
    }
  }

  function clearMessages(): void {
    messages.value = []
  }

  function clearError(): void {
    error.value = null
  }

  function clearChats(): void {
    sessions.value = []
    currentSession.value = null
    messages.value = []
  }

  return {
    sessions,
    chats,
    currentSession,
    messages,
    loading,
    error,
    isTyping,
    currentSessionId,
    hasMessages,
    loadSessions,
    createSession,
    selectSession,
    loadMessages,
    sendMessage,
    deleteSession,
    clearMessages,
    clearChats,
    clearError
  }
})