// src/api/client.ts
import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'

interface ApiConfig {
  baseURL: string
  timeout: number
}

interface LoginCredentials {
  email: string
  password: string
}

interface RegisterCredentials extends LoginCredentials {
  name: string
  confirmPassword: string
}

interface AuthResponse {
  access_token: string
  refresh_token: string
  user: {
    id: string
    name: string
    email: string
  }
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

interface ChatRequest {
  messages: ChatMessage[]
  domain?: string
  temperature?: number
  max_new_tokens?: number
  use_rag?: boolean
}

interface ChatResponse {
  response: string
  result: string
  text: string
  output: string
  latency_ms: number
  model_status: string
  success: boolean
  domain: string
  citations?: string[]
  sources?: string[]
}

interface CodeExecutionRequest {
  code: string
  language: string
  timeout?: number
  args?: string[]
  stdin?: string
}

interface CodeExecutionResponse {
  output: string
  error: string | null
  execution_time: number
  success: boolean
  language: string
  exit_code: number
}

interface TranscriptionResponse {
  transcription: string
  confidence: number
  language_detected: string
  duration_seconds: number
  latency_ms: number
  status: string
}

interface HealthResponse {
  status: string
  models_status: string
  ready_for_chat: boolean
  performance_mode: boolean
}

class ApiClient {
  private client: AxiosInstance
  private token: string | null = null

  constructor(config: ApiConfig = { baseURL: '', timeout: 30000 }) {
    this.client = axios.create({
      baseURL: config.baseURL.endsWith('/api') ? config.baseURL.slice(0, -4) : config.baseURL,
      timeout: config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })

    // Load token from localStorage
    this.token = localStorage.getItem('auth_token')
    if (this.token) {
      this.setAuthHeader(this.token)
    }

    // Request interceptor for auth
    this.client.interceptors.request.use(
      (config) => {
        if (this.token && config.headers) {
          config.headers.Authorization = `Bearer ${this.token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearAuth()
          // Redirect to login or emit auth error
          window.dispatchEvent(new CustomEvent('auth-expired'))
        }
        return Promise.reject(this.handleApiError(error))
      }
    )
  }

  private setAuthHeader(token: string) {
    this.token = token
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`
    localStorage.setItem('auth_token', token)
  }

  private clearAuth() {
    this.token = null
    delete this.client.defaults.headers.common['Authorization']
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
  }

  private handleApiError(error: any): Error {
    if (error.response?.data?.error_code) {
      const { error_code, message } = error.response.data
      switch (error_code) {
        case 'RATE_LIMIT_EXCEEDED':
          return new Error('Too many requests. Please wait and try again.')
        case 'FILE_SIZE_EXCEEDED':
          return new Error('File is too large. Maximum size is 50MB.')
        case 'CODE_SECURITY_VIOLATION':
          return new Error('Code contains potentially dangerous operations.')
        case 'MODEL_NOT_LOADED':
          return new Error('AI model is loading. Please try again in a moment.')
        case 'AUTHENTICATION_REQUIRED':
          return new Error('Please log in to continue.')
        case 'INVALID_CREDENTIALS':
          return new Error('Invalid email or password.')
        default:
          return new Error(message || 'An error occurred')
      }
    }
    return new Error(error.message || 'Network error. Please check your connection.')
  }

  // Authentication Methods
    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        try {
            const response: AxiosResponse<AuthResponse> = await this.client.post('/api/auth/login', credentials)
            const { access_token, user } = response.data
            this.setAuthHeader(access_token)
            localStorage.setItem('user_data', JSON.stringify(user))
            return response.data
        } catch (error) {
            throw this.handleApiError(error)
        }
    }

    async register(credentials: RegisterCredentials): Promise<AuthResponse> {
        try {
            const response: AxiosResponse<AuthResponse> = await this.client.post('/api/auth/register', credentials)
            const { access_token, user } = response.data
            this.setAuthHeader(access_token)
            localStorage.setItem('user_data', JSON.stringify(user))
            return response.data
        } catch (error) {
            throw this.handleApiError(error)
        }
    }

    async logout(): Promise<void> {
        try {
            if (this.token) {
                await this.client.post('/api/auth/logout')
            }
        } catch (error) {
            console.warn('Logout error:', error)
        } finally {
            this.clearAuth()
        }
    }

    async refreshToken(): Promise<AuthResponse> {
        try {
            const refreshToken = localStorage.getItem('refresh_token')
            if (!refreshToken) {
                throw new Error('No refresh token available')
            }
            
            const response: AxiosResponse<AuthResponse> = await this.client.post('/api/auth/refresh', {
                refresh_token: refreshToken
            })
            
            const { access_token, user } = response.data
            this.setAuthHeader(access_token)
            localStorage.setItem('user_data', JSON.stringify(user))
            return response.data
        } catch (error) {
            this.clearAuth()
            throw this.handleApiError(error)
        }
    }

  // Chat Methods
  async sendTextMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response: AxiosResponse<ChatResponse> = await this.client.post('/api/chat-text/', request)
      return response.data
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  async sendRAGMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response: AxiosResponse<ChatResponse> = await this.client.post('/api/chat-rag/', request)
      return response.data
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  // Code Execution Methods
  async executeCode(request: CodeExecutionRequest): Promise<CodeExecutionResponse> {
    try {
      const response: AxiosResponse<CodeExecutionResponse> = await this.client.post('/api/code/execute', request)
      return response.data
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  async getSupportedLanguages(): Promise<string[]> {
    try {
      const response: AxiosResponse<{ languages: string[] }> = await this.client.get('/api/code/languages')
      return response.data.languages
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  async validateCode(code: string, language: string): Promise<{ valid: boolean; errors?: string[] }> {
    try {
      const response = await this.client.post('/api/code/validate', { code, language })
      return response.data
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  // Voice Processing Methods
  async transcribeAudio(audioFile: File, language: string = 'auto'): Promise<TranscriptionResponse> {
    try {
      const formData = new FormData()
      formData.append('file', audioFile)
      formData.append('language', language)
      
      const response: AxiosResponse<TranscriptionResponse> = await this.client.post('/api/voice/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  // Document Management Methods
  async uploadDocuments(files: File[]): Promise<{ message: string; files: any[] }> {
    try {
      const formData = new FormData()
      files.forEach(file => formData.append('files', file))
      
      const response = await this.client.post('/api/chat-rag/upload-documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  async getDocuments(): Promise<any[]> {
    try {
      const response = await this.client.get('/api/chat-rag/documents')
      return response.data.documents || []
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  async deleteDocument(docId: string): Promise<void> {
    try {
      await this.client.delete(`/api/chat-rag/documents/${docId}`)
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  async searchDocuments(query: string): Promise<any[]> {
    try {
      const response = await this.client.post('/api/chat-rag/search', { query })
      return response.data.results || []
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  // System Health Methods
  async checkHealth(): Promise<HealthResponse> {
    try {
      const response: AxiosResponse<HealthResponse> = await this.client.get('/health')
      return response.data
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  async getModelStatus(): Promise<{ status: string; models: any[] }> {
    try {
      const response = await this.client.get('/api/models/status/')
      return response.data
    } catch (error) {
      throw this.handleApiError(error)
    }
  }

  // Utility Methods
  isAuthenticated(): boolean {
    return !!this.token
  }

  getCurrentUser(): any {
    const userData = localStorage.getItem('user_data')
    return userData ? JSON.parse(userData) : null
  }

  getToken(): string | null {
    return this.token
  }

  // Update base URL (useful for different environments)
  updateBaseURL(newBaseURL: string): void {
    this.client.defaults.baseURL = newBaseURL
  }
}

// Create singleton instance
export const apiClient = new ApiClient({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 30000
})

export default ApiClient