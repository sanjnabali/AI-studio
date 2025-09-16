// src/api/client.ts - API Client
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

interface LoginResponse {
  user: {
    id: string
    name: string
    email: string
  }
  access_token: string
  refresh_token?: string
}

interface RegisterResponse extends LoginResponse {}

class ApiClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers || {}) as Record<string, string>)
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    console.log(`🌐 API Request: ${options.method || 'GET'} ${url}`)

    try {
      const response = await fetch(url, {
        ...options,
        headers
      })

      console.log(`📡 API Response: ${response.status} ${response.statusText}`)

      if (!response.ok) {
        const errorText = await response.text()
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`
        
        try {
          const errorData = JSON.parse(errorText)
          errorMessage = errorData.message || errorData.error || errorMessage
        } catch {
          errorMessage = errorText || errorMessage
        }
        
        throw new Error(errorMessage)
      }

      const data = await response.json()
      console.log('✅ API Success:', { endpoint, data: !!data })
      return data
    } catch (error) {
      console.error('❌ API Error:', { endpoint, error })
      throw error
    }
  }

  // Authentication endpoints
  async login(credentials: { email: string; password: string }): Promise<LoginResponse> {
    return this.request<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    })
  }

  async register(credentials: { 
    name: string; 
    email: string; 
    password: string; 
    confirmPassword: string 
  }): Promise<RegisterResponse> {
    return this.request<RegisterResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(credentials)
    })
  }

  async logout(): Promise<void> {
    return this.request<void>('/auth/logout', {
      method: 'POST'
    })
  }

  async refreshToken(): Promise<LoginResponse> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    return this.request<LoginResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken })
    })
  }

  async getCurrentUser(): Promise<{ user: { id: string; name: string; email: string } }> {
    return this.request<{ user: { id: string; name: string; email: string } }>('/auth/me')
  }

  // Chat endpoints
  async sendTextMessage(request: any): Promise<any> {
    return this.request<any>('/chat/text', {
      method: 'POST',
      body: JSON.stringify(request)
    })
  }

  async sendRAGMessage(request: any): Promise<any> {
    return this.request<any>('/chat/rag', {
      method: 'POST',
      body: JSON.stringify(request)
    })
  }

  async executeCode(request: any): Promise<any> {
    return this.request<any>('/code/execute', {
      method: 'POST',
      body: JSON.stringify(request)
    })
  }

  async transcribeAudio(audioFile: File): Promise<any> {
    const formData = new FormData()
    formData.append('audio', audioFile)

    return this.request<any>('/audio/transcribe', {
      method: 'POST',
      body: formData,
      headers: {} // Let browser set Content-Type for FormData
    })
  }

  async uploadDocuments(files: File[]): Promise<any> {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))

    return this.request<any>('/documents/upload', {
      method: 'POST',
      body: formData,
      headers: {} // Let browser set Content-Type for FormData
    })
  }

  // System endpoints
  async checkHealth(): Promise<any> {
    return this.request<any>('/health')
  }

  async getModelStatus(): Promise<any> {
    return this.request<any>('/models/status')
  }

  async getSupportedLanguages(): Promise<string[]> {
    const response = await this.request<{ languages: string[] }>('/code/languages')
    return response.languages || ['python', 'javascript', 'html', 'css']
  }
}

export const apiClient = new ApiClient()
export type { LoginResponse, RegisterResponse }