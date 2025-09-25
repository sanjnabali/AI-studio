// Frontend/src/store/settings.ts
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useAuthStore } from './auth'
import type { ModelSettings } from '@/types'

export const useSettingsStore = defineStore('settings', () => {
  const authStore = useAuthStore()
  
  const modelSettings = ref<ModelSettings>({
    model_name: 'microsoft/DialoGPT-medium',
    temperature: 0.7,
    max_tokens: 1000,
    top_p: 0.9,
    top_k: 50,
    frequency_penalty: 0.0,
    presence_penalty: 0.0
  })

  const theme = ref<'light' | 'dark'>('light')
  const language = ref('en')
  const voiceSettings = ref({
    voice_style: 'neutral',
    speech_speed: 1.0,
    auto_play: false
  })

  const codeSettings = ref({
    default_language: 'python',
    auto_execute: false,
    show_line_numbers: true,
    word_wrap: true,
    font_size: 14
  })

  // Computed properties
  const isDarkMode = computed(() => theme.value === 'dark')
  const availableModels = computed(() => [
    { name: 'DialoGPT Medium', value: 'microsoft/DialoGPT-medium' },
    { name: 'DialoGPT Small', value: 'microsoft/DialoGPT-small' },
    { name: 'CodeBERT', value: 'microsoft/CodeBERT-base' },
    { name: 'BART CNN', value: 'facebook/bart-large-cnn' }
  ])

  const availableLanguages = computed(() => [
    'python', 'javascript', 'java', 'cpp', 'c', 'go', 'rust', 'php', 'ruby'
  ])

  // Watch for auth store changes
  watch(
    () => authStore.user?.model_preferences,
    (preferences) => {
      if (preferences) {
        modelSettings.value = { ...modelSettings.value, ...preferences }
      }
    },
    { immediate: true }
  )

  // Load settings from localStorage
  function loadSettings(): void {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      theme.value = savedTheme as 'light' | 'dark'
    }

    const savedLang = localStorage.getItem('language')
    if (savedLang) {
      language.value = savedLang
    }

    const savedVoice = localStorage.getItem('voiceSettings')
    if (savedVoice) {
      voiceSettings.value = JSON.parse(savedVoice)
    }

    const savedCode = localStorage.getItem('codeSettings')
    if (savedCode) {
      codeSettings.value = JSON.parse(savedCode)
    }

    // Apply theme
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  // Save settings to localStorage
  function saveSettings(): void {
    localStorage.setItem('theme', theme.value)
    localStorage.setItem('language', language.value)
    localStorage.setItem('voiceSettings', JSON.stringify(voiceSettings.value))
    localStorage.setItem('codeSettings', JSON.stringify(codeSettings.value))
  }

  // Update model settings
  async function updateModelSettings(newSettings: Partial<ModelSettings>): Promise<void> {
    modelSettings.value = { ...modelSettings.value, ...newSettings }
    
    try {
      await authStore.updateModelPreferences(modelSettings.value)
    } catch (err) {
      console.error('Failed to update model settings:', err)
      throw err
    }
  }

  // Toggle theme
  function toggleTheme(): void {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', theme.value)
    saveSettings()
  }

  // Update voice settings
  function updateVoiceSettings(newSettings: Partial<typeof voiceSettings.value>): void {
    voiceSettings.value = { ...voiceSettings.value, ...newSettings }
    saveSettings()
  }

  // Update code settings
  function updateCodeSettings(newSettings: Partial<typeof codeSettings.value>): void {
    codeSettings.value = { ...codeSettings.value, ...newSettings }
    saveSettings()
  }

  // Reset all settings
  function resetSettings(): void {
    modelSettings.value = {
      model_name: 'microsoft/DialoGPT-medium',
      temperature: 0.7,
      max_tokens: 1000,
      top_p: 0.9,
      top_k: 50,
      frequency_penalty: 0.0,
      presence_penalty: 0.0
    }
    
    theme.value = 'light'
    language.value = 'en'
    
    voiceSettings.value = {
      voice_style: 'neutral',
      speech_speed: 1.0,
      auto_play: false
    }
    
    codeSettings.value = {
      default_language: 'python',
      auto_execute: false,
      show_line_numbers: true,
      word_wrap: true,
      font_size: 14
    }
    
    saveSettings()
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  // Initialize settings
  loadSettings()

  return {
    modelSettings,
    theme,
    language,
    voiceSettings,
    codeSettings,
    isDarkMode,
    availableModels,
    availableLanguages,
    loadSettings,
    updateModelSettings,
    toggleTheme,
    updateVoiceSettings,
    updateCodeSettings,
    resetSettings,
    saveSettings
  }
})