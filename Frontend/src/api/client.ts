class ApiClient {
  private baseURL: string

  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL
  }

  async sendMessage(message: string, config: any) {
    const response = await fetch(`${this.baseURL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message, config })
    })
    return response.json()
  }

  async uploadFile(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${this.baseURL}/api/upload`, {
      method: 'POST',
      body: formData
    })
    return response.json()
  }

  async generateImage(prompt: string) {
    const response = await fetch(`${this.baseURL}/api/image/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prompt })
    })
    return response.json()
  }

  async voiceToText(audioBlob: Blob) {
    const formData = new FormData()
    formData.append('audio', audioBlob)
    
    const response = await fetch(`${this.baseURL}/api/voice/transcribe`, {
      method: 'POST',
      body: formData
    })
    return response.json()
  }
}

export const apiClient = new ApiClient()
