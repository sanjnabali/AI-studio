import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Chat, Message, ModelConfig } from '../types'

export const useChatStore = defineStore('chat', () => {
  const chats = ref<Chat[]>([])
  const activeChat = ref<Chat | null>(null)
  const loading = ref(false)

  const activeChatMessages = computed(() => activeChat.value?.messages || [])

  function createChat(title: string = 'New Chat'): Chat {
    const chat: Chat = {
      id: Date.now().toString(),
      title,
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
    chats.value.push(chat)
    activeChat.value = chat
    return chat
  }

  function selectChat(chatId: string) {
    const chat = chats.value.find(c => c.id === chatId)
    if (chat) {
      activeChat.value = chat
    }
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
  }

  function deleteChat(chatId: string) {
    const index = chats.value.findIndex(c => c.id === chatId)
    if (index > -1) {
      chats.value.splice(index, 1)
      if (activeChat.value?.id === chatId) {
        activeChat.value = chats.value[0] || null
      }
    }
  }

  return {
    chats,
    activeChat,
    loading,
    activeChatMessages,
    createChat,
    selectChat,
    addMessage,
    deleteChat
  }
})