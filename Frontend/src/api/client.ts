import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosError } from 'axios';


export interface ApiResponse<T = any> {
  data: T
  status: number
  message?: string
}

export interface ChatMessage {
  id?: number
  role: 'user' | 'assistant' | 'system'
  content: string
  message_type?: 'text' | 'code' | 'image' | 'audio' | 'file'
  metadata?: Record<string, any>
  timestamp?: string
  token_count?: number
}

export interface ChatSession {
  id: number
  name: string
  created_at: string
  updated_at: string
  message_count: number
  model_config: Record<string, any>
}

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  api_key?: string
  model_preferences: ModelConfig
  usage_stats: {
    total_requests: number
    total_tokens: number
    last_request?: number
  }
}

export interface ModelConfig {
  default_model: string
  temperature: number
  max_tokens: number
  top_p: number
  top_k: number
  frequency_penalty?: number
  presence_penalty?: number
}

export interface Document {
  id: number
  filename: string
  original_filename: string
  file_size: number
  file_type: string
  processed: boolean
  created_at: string
  chunk_count: number
}

export interface CodeExecutionResult {
  id: number
  output?: string
  error?: string
  execution_time: number
  status: 'success' | 'error' | 'timeout'
  language: string
  memory_used?: number
}

export interface VoiceResult {
  text: string
  confidence: number
  duration: number
  language: string
  processing_time: number
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

class ApiClient {
  private client: AxiosInstance
  private accessToken: string | null = null
  private refreshToken: string | null = null

  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Load tokens from localStorage
    this.accessToken = localStorage.getItem('access_token')
    this.refreshToken = localStorage.getItem('refresh_token')

    // Request interceptor to add auth header
    this.client.interceptors.request.use(
      (config) => {
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401 && this.refreshToken) {
          try {
            const refreshResponse = await this.client.post('/api/auth/refresh', {
              refresh_token: this.refreshToken
            })
            
            const { access_token, refresh_token } = refreshResponse.data
            this.setTokens(access_token, refresh_token)
            
            // Retry original request
            if (error.config) {
              error.config.headers.Authorization = `Bearer ${access_token}`
              return this.client.request(error.config)
            }
          } catch (refreshError) {
            this.clearTokens()
            window.location.href = '/auth'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  private setTokens(accessToken: string, refreshToken: string): void {
    this.accessToken = accessToken
    this.refreshToken = refreshToken
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
  }

  private clearTokens(): void {
    this.accessToken = null
    this.refreshToken = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/api/auth/login', credentials)
    this.setTokens(response.data.access_token, response.data.refresh_token)
    return response.data
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/api/auth/register', userData)
    this.setTokens(response.data.access_token, response.data.refresh_token)
    return response.data
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/api/auth/logout')
    } finally {
      this.clearTokens()
    }
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/api/auth/me')
    return response.data
  }

  async updateModelPreferences(preferences: ModelConfig): Promise<void> {
    await this.client.put('/api/auth/preferences', preferences)
  }

  async updateProfile(profileData: { name: string; email: string }): Promise<{ user: User }> {
    const response = await this.client.put<{ user: User }>('/api/auth/profile', profileData)
    return response.data
  }

  async changePassword(passwordData: { currentPassword: string; newPassword: string }): Promise<void> {
    await this.client.put('/api/auth/change-password', passwordData)
  }

  // Chat endpoints
  async getChatSessions(): Promise<ChatSession[]> {
    const response = await this.client.get<ChatSession[]>('/api/chat/sessions')
    return response.data
  }

  async createChatSession(name?: string, modelConfig?: Record<string, any>): Promise<ChatSession> {
    const response = await this.client.post<ChatSession>('/api/chat/sessions', {
      name,
      model_config: modelConfig
    })
    return response.data
  }

  async getSessionMessages(sessionId: number): Promise<ChatMessage[]> {
    const response = await this.client.get<ChatMessage[]>(`/api/chat/sessions/${sessionId}/messages`)
    return response.data
  }

  async sendChatMessage(message: string, sessionId?: number, modelConfig?: Record<string, any>): Promise<{
    message: string
    session_id: number
    message_id: number
    model_used: string
    token_count: number
    processing_time: number
  }> {
    const response = await this.client.post('/api/chat/chat', {
      message,
      session_id: sessionId,
      model_config: modelConfig
    })
    return response.data
  }

  async deleteChatSession(sessionId: number): Promise<void> {
    await this.client.delete(`/api/chat/sessions/${sessionId}`)
  }

  // RAG endpoints
  async uploadDocument(file: File): Promise<{
    status: string
    document_id: number
    filename: string
    chunks_processed: number
    message: string
  }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await this.client.post('/api/rag/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }

  async getDocuments(): Promise<Document[]> {
    const response = await this.client.get<Document[]>('/api/rag/documents')
    return response.data
  }

  async queryDocuments(
    query: string, 
    documentNames?: string[], 
    modelConfig?: Record<string, any>
  ): Promise<{
    response: string
    sources: Array<{
      document: string
      chunk_id: string
      similarity: number
    }>
    model_used: string
    processing_time: number
    token_count: number
    context_used: number
  }> {
    const response = await this.client.post('/api/rag/query', {
      query,
      document_names: documentNames,
      model_config: modelConfig
    })
    return response.data
  }

  async deleteDocument(documentId: number): Promise<void> {
    await this.client.delete(`/api/rag/documents/${documentId}`)
  }

  // Voice endpoints
  async speechToText(audioFile: File): Promise<VoiceResult> {
    const formData = new FormData()
    formData.append('audio', audioFile)
    
    const response = await this.client.post<VoiceResult>('/api/voice/speech-to-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }

  async textToSpeech(text: string, voiceStyle?: string, speed?: number): Promise<{
    audio_data: string
    duration: number
    processing_time: number
    text: string
  }> {
    const response = await this.client.post('/api/voice/text-to-speech', {
      text,
      voice_style: voiceStyle,
      speed
    })
    return response.data
  }

  // Code execution endpoints
  async executeCode(
    code: string, 
    language: string, 
    timeout?: number, 
    inputs?: string[]
  ): Promise<CodeExecutionResult> {
    const response = await this.client.post<CodeExecutionResult>('/api/code/execute', {
      code,
      language,
      timeout,
      inputs
    })
    return response.data
  }

  async generateCode(
    prompt: string, 
    language: string = 'python', 
    complexity: string = 'simple',
    includeTests: boolean = false,
    modelConfig?: Record<string, any>
  ): Promise<{
    code: string
    explanation: string
    language: string
    model_used: string
    processing_time: number
    tests?: string
  }> {
    const response = await this.client.post('/api/code/generate', {
      prompt,
      language,
      complexity,
      include_tests: includeTests,
      model_config: modelConfig
    })
    return response.data
  }

  async analyzeCode(
    code: string, 
    language: string, 
    analysisType: string = 'full'
  ): Promise<{
    analysis: string
    suggestions: string[]
    complexity_score: number
    issues: Array<{
      type: string
      message: string
      severity: string
    }>
    processing_time: number
  }> {
    const response = await this.client.post('/api/code/analyze', {
      code,
      language,
      analysis_type: analysisType
    })
    return response.data
  }

  async getCodeExecutions(limit: number = 20): Promise<Array<{
    id: number
    language: string
    code_preview: string
    status: string
    execution_time: number
    created_at: string
    has_output: boolean
    has_error: boolean
  }>> {
    const response = await this.client.get(`/api/code/executions?limit=${limit}`)
    return response.data
  }

  // Image endpoints
  async generateImage(
    prompt: string,
    width: number = 512,
    height: number = 512,
    style: string = 'realistic'
  ): Promise<{
    image_data: string
    prompt: string
    width: number
    height: number
    processing_time: number
  }> {
    const response = await this.client.post('/api/image/generate', {
      prompt,
      width,
      height,
      style
    })
    return response.data
  }

  async analyzeImage(imageData: string, prompt: string = 'Describe this image'): Promise<{
    analysis: string
    prompt: string
    image_dimensions: { width: number, height: number }
    confidence: number
  }> {
    const response = await this.client.post('/api/image/analyze', {
      image_data: imageData,
      prompt
    })
    return response.data
  }

  // Health check
  async healthCheck(): Promise<{ status: string, version: string, service: string }> {
    const response = await this.client.get('/health')
    return response.data
  }

  // Get supported languages for code execution
  async getSupportedLanguages(): Promise<{
    supported_languages: Array<{
      name: string
      code: string
      version: string
      features: string[]
      libraries: string[]
    }>
    execution_limits: {
      max_execution_time: number
      max_code_size: string
      max_memory: string
    }
  }> {
    const response = await this.client.get('/api/code/languages')
    return response.data
  }

  // Get voice supported formats
  async getVoiceSupportedFormats(): Promise<{
    input_formats: string[]
    output_format: string
    max_file_size: string
    max_duration: string
    sample_rate: string
    channels: string
  }> {
    const response = await this.client.get('/api/voice/supported-formats')
    return response.data
  }
}

// Create singleton instance
export const apiClient = new ApiClient()
export default apiClient