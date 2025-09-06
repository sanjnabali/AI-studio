import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ModelConfig, Agent } from '../types'

export const useSettingsStore = defineStore('settings', () => {
  const modelConfig = ref<ModelConfig>({
    model: 'gemini-pro',
    temperature: 0.7,
    topK: 40,
    topP: 0.9,
    maxTokens: 1024,
    safetyLevel: 'medium'
  })

  const agents = ref<Agent[]>([
    {
      id: 'code-agent',
      name: 'Code Assistant',
      description: 'Specialized in code generation and debugging',
      type: 'code',
      status: 'idle'
    },
    {
      id: 'text-agent',
      name: 'Text Assistant',
      description: 'General text processing and analysis',
      type: 'text',
      status: 'idle'
    }
  ])

  const domainProfiles = ref([
    { id: 'coding', name: 'Software Development', active: false },
    { id: 'marketing', name: 'Marketing & Content', active: false },
    { id: 'legal', name: 'Legal Analysis', active: false },
    { id: 'research', name: 'Research & Analysis', active: false }
  ])

  function updateModelConfig(config: Partial<ModelConfig>) {
    modelConfig.value = { ...modelConfig.value, ...config }
  }

  function toggleDomainProfile(id: string) {
    const profile = domainProfiles.value.find(p => p.id === id)
    if (profile) {
      profile.active = !profile.active
    }
  }

  return {
    modelConfig,
    agents,
    domainProfiles,
    updateModelConfig,
    toggleDomainProfile
  }
})
