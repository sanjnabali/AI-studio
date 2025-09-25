// Frontend/src/types/index.ts
export interface Message {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  type: 'text' | 'code' | 'image' | 'audio' | 'file'
  metadata?: {
    model_used?: string
    processing_time?: number
    token_count?: number
    sources?: Array<{
      document: string
      similarity: number
    }>
  }
}

export interface ChatSession {
  id: number
  name: string
  messages: Message[]
  created_at: Date
  updated_at: Date
  model_config: ModelSettings
}

export interface ModelSettings {
  model_name: string
  temperature: number
  max_tokens: number
  top_p: number
  top_k: number
  frequency_penalty: number
  presence_penalty: number
}

export interface Document {
  id: number
  name: string
  size: number
  type: string
  uploaded_at: Date
  processed: boolean
  chunk_count: number
}

export interface ExecutionResult {
  id: number
  code: string
  language: string
  output?: string
  error?: string
  execution_time: number
  status: 'success' | 'error' | 'timeout'
  timestamp: Date
}

export interface VoiceRecording {
  id: string
  duration: number
  blob: Blob
  transcript?: string
  processing: boolean
}
