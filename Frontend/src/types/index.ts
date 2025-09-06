export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  type: 'text' | 'image' | 'audio' | 'code'
  metadata?: Record<string, any>
}

export interface Chat {
  id: string
  title: string
  messages: Message[]
  created: Date
  updated: Date
  modelConfig: ModelConfig
}

export interface ModelConfig {
  model: string
  temperature: number
  topK: number
  topP: number
  maxTokens: number
  safetyLevel: string
}

export interface Agent {
  id: string
  name: string
  description: string
  type: 'code' | 'text' | 'multimodal' | 'voice'
  status: 'idle' | 'busy' | 'error'
}

export interface Template {
  id: string
  name: string
  description: string
  category: string
  prompt: string
  config: ModelConfig
}
