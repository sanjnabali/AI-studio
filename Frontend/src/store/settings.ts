// Frontend/src/store/settings.ts - Enhanced settings store
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useAuthStore } from './auth'
import { apiClient } from '@/api/client'

export interface ModelSettings {
  model_name: string
  temperature: number
  max_tokens: number
  top_p: number
  top_k: number
  frequency_penalty: number
  presence_penalty: number
  use_rag: boolean
  generate_code: boolean
  system_prompt?: string
}

export interface VoiceSettings {
  voice_style: string
  speech_speed: number
  auto_play: boolean
  voice_language: string
  enable_voice_commands: boolean
}

export interface CodeSettings {
  default_language: string
  auto_execute: boolean
  show_line_numbers: boolean
  word_wrap: boolean
  font_size: number
  theme: string
  auto_save: boolean
  format_on_save: boolean
}

export interface UISettings {
  theme: 'light' | 'dark' | 'auto'
  language: string
  timezone: string
  date_format: string
  compact_mode: boolean
  show_timestamps: boolean
  enable_animations: boolean
  sidebar_collapsed: boolean
}

export interface ExperimentSettings {
  enable_beta_features: boolean
  enable_experimental_models: boolean
  enable_advanced_rag: boolean
  enable_multimodal: boolean
  debug_mode: boolean
}

export const useSettingsStore = defineStore('settings', () => {
  const authStore = useAuthStore()
  
  // Settings state
  const modelSettings = ref<ModelSettings>({
    model_name: 'microsoft/DialoGPT-medium',
    temperature: 0.7,
    max_tokens: 1000,
    top_p: 0.9,
    top_k: 50,
    frequency_penalty: 0.0,
    presence_penalty: 0.0,
    use_rag: false,
    generate_code: false,
    system_prompt: 'You are a helpful AI assistant.'
  })

  const voiceSettings = ref<VoiceSettings>({
    voice_style: 'neutral',
    speech_speed: 1.0,
    auto_play: false,
    voice_language: 'en-US',
    enable_voice_commands: true
  })

  const codeSettings = ref<CodeSettings>({
    default_language: 'python',
    auto_execute: false,
    show_line_numbers: true,
    word_wrap: true,
    font_size: 14,
    theme: 'dark',
    auto_save: true,
    format_on_save: true
  })

  const uiSettings = ref<UISettings>({
    theme: 'dark',
    language: 'en',
    timezone: 'UTC',
    date_format: 'MM/DD/YYYY',
    compact_mode: false,
    show_timestamps: true,
    enable_animations: true,
    sidebar_collapsed: false
  })

  const experimentSettings = ref<ExperimentSettings>({
    enable_beta_features: false,
    enable_experimental_models: false,
    enable_advanced_rag: false,
    enable_multimodal: true,
    debug_mode: false
  })

  // Computed properties
  const theme = computed(() => uiSettings.value.theme)
  const isDarkMode = computed(() => {
    if (uiSettings.value.theme === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return uiSettings.value.theme === 'dark'
  })

  const availableModels = computed(() => {
    const baseModels = [
      { 
        name: 'DialoGPT Medium', 
        value: 'microsoft/DialoGPT-medium',
        type: 'text',
        description: 'General purpose conversational model'
      },
      { 
        name: 'DialoGPT Small', 
        value: 'microsoft/DialoGPT-small',
        type: 'text',
        description: 'Faster, lightweight conversational model'
      },
      { 
        name: 'CodeBERT Base', 
        value: 'microsoft/CodeBERT-base',
        type: 'code',
        description: 'Specialized for code understanding and generation'
      },
      { 
        name: 'BART Large CNN', 
        value: 'facebook/bart-large-cnn',
        type: 'text',
        description: 'Excellent for summarization and text generation'
      }
    ]

    if (experimentSettings.value.enable_experimental_models) {
      baseModels.push(
        {
          name: 'GPT-2 Large',
          value: 'gpt2-large',
          type: 'text',
          description: 'Large language model for creative text generation'
        },
        {
          name: 'T5 Base',
          value: 't5-base',
          type: 'text',
          description: 'Text-to-text transformer for various tasks'
        }
      )
    }

    return baseModels
  })

  const availableLanguages = computed(() => [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'es', name: 'Spanish', flag: '🇪🇸' },
    { code: 'fr', name: 'French', flag: '🇫🇷' },
    { code: 'de', name: 'German', flag: '🇩🇪' },
    { code: 'it', name: 'Italian', flag: '🇮🇹' },
    { code: 'pt', name: 'Portuguese', flag: '🇵🇹' },
    { code: 'ru', name: 'Russian', flag: '🇷🇺' },
    { code: 'ja', name: 'Japanese', flag: '🇯🇵' },
    { code: 'ko', name: 'Korean', flag: '🇰🇷' },
    { code: 'zh', name: 'Chinese', flag: '🇨🇳' }
  ])

  const availableCodeLanguages = computed(() => [
    'python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'csharp',
    'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'r',
    'julia', 'matlab', 'sql', 'html', 'css', 'markdown'
  ])

  const availableVoices = computed(() => [
    { value: 'neutral', name: 'Neutral', description: 'Balanced and professional' },
    { value: 'friendly', name: 'Friendly', description: 'Warm and approachable' },
    { value: 'formal', name: 'Formal', description: 'Professional and authoritative' },
    { value: 'casual', name: 'Casual', description: 'Relaxed and conversational' }
  ])

  const availableThemes = computed(() => [
    { value: 'light', name: 'Light', icon: '☀️' },
    { value: 'dark', name: 'Dark', icon: '🌙' },
    { value: 'auto', name: 'Auto', icon: '🌓' }
  ])

  // Settings persistence
  const STORAGE_KEYS = {
    MODEL: 'ai-studio-model-settings',
    VOICE: 'ai-studio-voice-settings',
    CODE: 'ai-studio-code-settings',
    UI: 'ai-studio-ui-settings',
    EXPERIMENT: 'ai-studio-experiment-settings'
  }

  const applyTheme = (themeValue: string) => {
    const root = document.documentElement
    const body = document.body

    // Remove existing theme classes
    root.classList.remove('light', 'dark')
    body.classList.remove('light', 'dark')

    let appliedTheme = themeValue
    if (themeValue === 'auto') {
      appliedTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }

    // Apply theme classes
    root.classList.add(appliedTheme)
    body.classList.add(appliedTheme)
    root.setAttribute('data-theme', appliedTheme)

    // Update CSS custom properties for theme
    if (appliedTheme === 'dark') {
      root.style.setProperty('--color-primary', '59 130 246')
      root.style.setProperty('--color-background', '17 24 39')
      root.style.setProperty('--color-surface', '31 41 55')
      root.style.setProperty('--color-text', '249 250 251')
    } else {
      root.style.setProperty('--color-primary', '37 99 235')
      root.style.setProperty('--color-background', '249 250 251')
      root.style.setProperty('--color-surface', '255 255 255')
      root.style.setProperty('--color-text', '17 24 39')
    }

    console.log(`🎨 Theme applied: ${appliedTheme}`)
  }

  // Watch for auth store changes to load user preferences
  watch(
    () => authStore.user?.model_preferences,
    (preferences) => {
      if (preferences) {
        modelSettings.value = { ...modelSettings.value, ...preferences }
      }
    },
    { immediate: true }
  )

  // Watch for theme changes and apply to DOM
  watch(
    () => uiSettings.value.theme,
    (newTheme) => {
      applyTheme(newTheme)
    },
    { immediate: true }
  )

  // Watch for system theme changes when in auto mode
  if (typeof window !== 'undefined') {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addListener(() => {
      if (uiSettings.value.theme === 'auto') {
        applyTheme('auto')
      }
    })
  }

  // Methods
  const loadSettings = () => {
    try {
      // Load from localStorage
      const savedModel = localStorage.getItem(STORAGE_KEYS.MODEL)
      if (savedModel) {
        modelSettings.value = { ...modelSettings.value, ...JSON.parse(savedModel) }
      }

      const savedVoice = localStorage.getItem(STORAGE_KEYS.VOICE)
      if (savedVoice) {
        voiceSettings.value = { ...voiceSettings.value, ...JSON.parse(savedVoice) }
      }

      const savedCode = localStorage.getItem(STORAGE_KEYS.CODE)
      if (savedCode) {
        codeSettings.value = { ...codeSettings.value, ...JSON.parse(savedCode) }
      }

      const savedUI = localStorage.getItem(STORAGE_KEYS.UI)
      if (savedUI) {
        uiSettings.value = { ...uiSettings.value, ...JSON.parse(savedUI) }
      }

      const savedExperiment = localStorage.getItem(STORAGE_KEYS.EXPERIMENT)
      if (savedExperiment) {
        experimentSettings.value = { ...experimentSettings.value, ...JSON.parse(savedExperiment) }
      }

      // Apply theme immediately after loading
      applyTheme(uiSettings.value.theme)
      
      console.log('✅ Settings loaded from localStorage')
    } catch (error) {
      console.error('Failed to load settings from localStorage:', error)
    }
  }

  const saveSettings = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.MODEL, JSON.stringify(modelSettings.value))
      localStorage.setItem(STORAGE_KEYS.VOICE, JSON.stringify(voiceSettings.value))
      localStorage.setItem(STORAGE_KEYS.CODE, JSON.stringify(codeSettings.value))
      localStorage.setItem(STORAGE_KEYS.UI, JSON.stringify(uiSettings.value))
      localStorage.setItem(STORAGE_KEYS.EXPERIMENT, JSON.stringify(experimentSettings.value))
      console.log('✅ Settings saved to localStorage')
    } catch (error) {
      console.error('Failed to save settings to localStorage:', error)
    }
  }

  const loadUserPreferences = async () => {
    if (!authStore.isAuthenticated) return

    try {
      const preferences = await apiClient.getUserPreferences()
      if (preferences) {
        // Merge server preferences with local settings
        if (preferences.model_settings) {
          modelSettings.value = { ...modelSettings.value, ...preferences.model_settings }
        }
        if (preferences.voice_settings) {
          voiceSettings.value = { ...voiceSettings.value, ...preferences.voice_settings }
        }
        if (preferences.code_settings) {
          codeSettings.value = { ...codeSettings.value, ...preferences.code_settings }
        }
        if (preferences.ui_settings) {
          uiSettings.value = { ...uiSettings.value, ...preferences.ui_settings }
        }
        if (preferences.experiment_settings) {
          experimentSettings.value = { ...experimentSettings.value, ...preferences.experiment_settings }
        }
        
        console.log('✅ User preferences loaded from server')
        saveSettings() // Update localStorage with server data
      }
    } catch (error) {
      console.warn('Failed to load user preferences from server:', error)
    }
  }

  const saveUserPreferences = async () => {
    if (!authStore.isAuthenticated) return

    try {
      const preferences = {
        model_settings: modelSettings.value,
        voice_settings: voiceSettings.value,
        code_settings: codeSettings.value,
        ui_settings: uiSettings.value,
        experiment_settings: experimentSettings.value
      }

      await apiClient.saveUserPreferences(preferences)
      console.log('✅ User preferences saved to server')
    } catch (error) {
      console.error('Failed to save user preferences to server:', error)
      throw error
    }
  }

  // Update methods
  const updateModelSettings = async (newSettings: Partial<ModelSettings>) => {
    modelSettings.value = { ...modelSettings.value, ...newSettings }
    saveSettings()
    
    // Sync with server if authenticated
    if (authStore.isAuthenticated) {
      try {
        await authStore.updateModelPreferences(modelSettings.value)
      } catch (error) {
        console.error('Failed to sync model settings with server:', error)
      }
    }
  }

  const updateVoiceSettings = (newSettings: Partial<VoiceSettings>) => {
    voiceSettings.value = { ...voiceSettings.value, ...newSettings }
    saveSettings()
    
    // Sync with server if authenticated
    if (authStore.isAuthenticated) {
      saveUserPreferences().catch(console.error)
    }
  }

  const updateCodeSettings = (newSettings: Partial<CodeSettings>) => {
    codeSettings.value = { ...codeSettings.value, ...newSettings }
    saveSettings()
    
    // Sync with server if authenticated
    if (authStore.isAuthenticated) {
      saveUserPreferences().catch(console.error)
    }
  }

  const updateUISettings = (newSettings: Partial<UISettings>) => {
    uiSettings.value = { ...uiSettings.value, ...newSettings }
    
    // Apply theme immediately if it changed
    if (newSettings.theme) {
      applyTheme(newSettings.theme)
    }
    
    saveSettings()
    
    // Sync with server if authenticated
    if (authStore.isAuthenticated) {
      saveUserPreferences().catch(console.error)
    }
  }

  const updateExperimentSettings = (newSettings: Partial<ExperimentSettings>) => {
    experimentSettings.value = { ...experimentSettings.value, ...newSettings }
    saveSettings()
    
    // Sync with server if authenticated
    if (authStore.isAuthenticated) {
      saveUserPreferences().catch(console.error)
    }
  }

  // Bulk update method
  const updateSettings = async (settings: {
    model?: Partial<ModelSettings>
    voice?: Partial<VoiceSettings>
    code?: Partial<CodeSettings>
    ui?: Partial<UISettings>
    experiment?: Partial<ExperimentSettings>
  }) => {
    if (settings.model) {
      modelSettings.value = { ...modelSettings.value, ...settings.model }
    }
    if (settings.voice) {
      voiceSettings.value = { ...voiceSettings.value, ...settings.voice }
    }
    if (settings.code) {
      codeSettings.value = { ...codeSettings.value, ...settings.code }
    }
    if (settings.ui) {
      uiSettings.value = { ...uiSettings.value, ...settings.ui }
      if (settings.ui.theme) {
        applyTheme(settings.ui.theme)
      }
    }
    if (settings.experiment) {
      experimentSettings.value = { ...experimentSettings.value, ...settings.experiment }
    }

    saveSettings()
    
    // Sync with server if authenticated
    if (authStore.isAuthenticated) {
      try {
        await saveUserPreferences()
      } catch (error) {
        console.error('Failed to sync settings with server:', error)
        throw error
      }
    }
  }

  // Theme toggle methods
  const toggleTheme = () => {
    const themes: Array<'light' | 'dark' | 'auto'> = ['light', 'dark', 'auto']
    const currentIndex = themes.indexOf(uiSettings.value.theme)
    const nextIndex = (currentIndex + 1) % themes.length
    updateUISettings({ theme: themes[nextIndex] })
  }

  const setTheme = (theme: 'light' | 'dark' | 'auto') => {
    updateUISettings({ theme })
  }

  // Reset methods
  const resetModelSettings = () => {
    modelSettings.value = {
      model_name: 'microsoft/DialoGPT-medium',
      temperature: 0.7,
      max_tokens: 1000,
      top_p: 0.9,
      top_k: 50,
      frequency_penalty: 0.0,
      presence_penalty: 0.0,
      use_rag: false,
      generate_code: false,
      system_prompt: 'You are a helpful AI assistant.'
    }
    saveSettings()
  }

  const resetAllSettings = () => {
    // Reset to defaults
    resetModelSettings()
    
    voiceSettings.value = {
      voice_style: 'neutral',
      speech_speed: 1.0,
      auto_play: false,
      voice_language: 'en-US',
      enable_voice_commands: true
    }

    codeSettings.value = {
      default_language: 'python',
      auto_execute: false,
      show_line_numbers: true,
      word_wrap: true,
      font_size: 14,
      theme: 'dark',
      auto_save: true,
      format_on_save: true
    }

    uiSettings.value = {
      theme: 'dark',
      language: 'en',
      timezone: 'UTC',
      date_format: 'MM/DD/YYYY',
      compact_mode: false,
      show_timestamps: true,
      enable_animations: true,
      sidebar_collapsed: false
    }

    experimentSettings.value = {
      enable_beta_features: false,
      enable_experimental_models: false,
      enable_advanced_rag: false,
      enable_multimodal: true,
      debug_mode: false
    }

    applyTheme(uiSettings.value.theme)
    saveSettings()
  }

  // Export/Import methods
  const exportSettings = () => {
    const settingsData = {
      model: modelSettings.value,
      voice: voiceSettings.value,
      code: codeSettings.value,
      ui: uiSettings.value,
      experiment: experimentSettings.value,
      exportDate: new Date().toISOString(),
      version: '1.0'
    }

    const blob = new Blob([JSON.stringify(settingsData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ai-studio-settings-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const importSettings = async (file: File) => {
    try {
      const text = await file.text()
      const settingsData = JSON.parse(text)

      if (settingsData.version !== '1.0') {
        throw new Error('Incompatible settings file version')
      }

      // Validate and import settings
      if (settingsData.model) {
        modelSettings.value = { ...modelSettings.value, ...settingsData.model }
      }
      if (settingsData.voice) {
        voiceSettings.value = { ...voiceSettings.value, ...settingsData.voice }
      }
      if (settingsData.code) {
        codeSettings.value = { ...codeSettings.value, ...settingsData.code }
      }
      if (settingsData.ui) {
        uiSettings.value = { ...uiSettings.value, ...settingsData.ui }
        applyTheme(uiSettings.value.theme)
      }
      if (settingsData.experiment) {
        experimentSettings.value = { ...experimentSettings.value, ...settingsData.experiment }
      }

      saveSettings()
      
      // Sync with server if authenticated
      if (authStore.isAuthenticated) {
        await saveUserPreferences()
      }

      return true
    } catch (error) {
      console.error('Failed to import settings:', error)
      throw error
    }
  }

  // Initialize settings on store creation
  loadSettings()

  return {
    // State
    modelSettings,
    voiceSettings,
    codeSettings,
    uiSettings,
    experimentSettings,

    // Computed
    theme,
    isDarkMode,
    availableModels,
    availableLanguages,
    availableCodeLanguages,
    availableVoices,
    availableThemes,

    // Methods
    loadSettings,
    saveSettings,
    loadUserPreferences,
    saveUserPreferences,
    updateModelSettings,
    updateVoiceSettings,
    updateCodeSettings,
    updateUISettings,
    updateExperimentSettings,
    updateSettings,
    toggleTheme,
    setTheme,
    resetModelSettings,
    resetAllSettings,
    exportSettings,
    importSettings
  }
})