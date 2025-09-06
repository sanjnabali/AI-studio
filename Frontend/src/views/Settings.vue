<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-4xl mx-auto px-4 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Settings</h1>
        <p class="text-gray-600 dark:text-gray-400">Customize your AI Studio experience</p>
      </div>

      <div class="space-y-8">
        <!-- Model Configuration -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">Model Configuration</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Default Model -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Default Model</label>
              <select
                v-model="settingsStore.modelConfig.model"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="gemini-pro">Gemini Pro</option>
                <option value="gemini-pro-vision">Gemini Pro Vision</option>
                <option value="claude-3">Claude 3</option>
                <option value="gpt-4">GPT-4</option>
              </select>
            </div>

            <!-- Max Tokens -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Tokens: {{ settingsStore.modelConfig.maxTokens }}
              </label>
              <input
                v-model.number="settingsStore.modelConfig.maxTokens"
                type="range"
                min="256"
                max="4096"
                step="256"
                class="w-full"
              />
            </div>

            <!-- Temperature -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Temperature: {{ settingsStore.modelConfig.temperature }}
              </label>
              <input
                v-model.number="settingsStore.modelConfig.temperature"
                type="range"
                min="0"
                max="2"
                step="0.1"
                class="w-full"
              />
              <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span>Conservative</span>
                <span>Creative</span>
              </div>
            </div>

            <!-- Safety Level -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Safety Level</label>
              <select
                v-model="settingsStore.modelConfig.safetyLevel"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Domain Profiles -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">Domain Specialization</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="profile in settingsStore.domainProfiles"
              :key="profile.id"
              class="p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
              :class="{
                'bg-blue-50 dark:bg-blue-900/20 border-blue-500': profile.active
              }"
            >
              <label class="flex items-center cursor-pointer">
                <input
                  v-model="profile.active"
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-3"
                />
                <div>
                  <div class="font-medium text-gray-900 dark:text-white">{{ profile.name }}</div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">
                    Optimized for {{ profile.id }} tasks
                  </div>
                </div>
              </label>
            </div>
          </div>
        </div>

        <!-- Agent Management -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">Agent Management</h2>
          
          <div class="space-y-4">
            <div
              v-for="agent in settingsStore.agents"
              :key="agent.id"
              class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
            >
              <div class="flex items-center space-x-3">
                <div
                  class="w-3 h-3 rounded-full"
                  :class="{
                    'bg-green-500': agent.status === 'idle',
                    'bg-yellow-500': agent.status === 'busy',
                    'bg-red-500': agent.status === 'error'
                  }"
                ></div>
                <div>
                  <div class="font-medium text-gray-900 dark:text-white">{{ agent.name }}</div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">{{ agent.description }}</div>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-xs bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 px-2 py-1 rounded capitalize">
                  {{ agent.type }}
                </span>
                <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                  <CogIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Interface Preferences -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">Interface Preferences</h2>
          
          <div class="space-y-6">
            <!-- Theme -->
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-gray-900 dark:text-white">Dark Mode</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">Use dark theme for better low-light experience</div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="darkMode"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <!-- Auto-save -->
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-gray-900 dark:text-white">Auto-save Conversations</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">Automatically save your chat history</div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="autoSave"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <!-- Voice Input -->
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-gray-900 dark:text-white">Voice Input</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">Enable voice-to-text functionality</div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="voiceInput"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        <!-- Export/Import -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">Data Management</h2>
          
          <div class="flex flex-col sm:flex-row gap-4">
            <button
              @click="exportSettings"
              class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium"
            >
              Export Settings
            </button>
            <button
              @click="importSettings"
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium"
            >
              Import Settings
            </button>
            <button
              @click="clearAllData"
              class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium"
            >
              Clear All Data
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useSettingsStore } from '../store/settings'
import { useChatStore } from '../store/chat'
import { CogIcon } from '@heroicons/vue/24/outline'

const settingsStore = useSettingsStore()
const chatStore = useChatStore()

const darkMode = ref(false)
const autoSave = ref(true)
const voiceInput = ref(true)

// Watch for dark mode changes
watch(darkMode, (newValue) => {
  if (newValue) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})

function exportSettings() {
  const settings = {
    modelConfig: settingsStore.modelConfig,
    domainProfiles: settingsStore.domainProfiles,
    preferences: {
      darkMode: darkMode.value,
      autoSave: autoSave.value,
      voiceInput: voiceInput.value
    }
  }
  
  const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'ai-studio-settings.json'
  a.click()
  URL.revokeObjectURL(url)
}

function importSettings() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (event) => {
    const file = (event.target as HTMLInputElement).files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const settings = JSON.parse(e.target?.result as string)
          if (settings.modelConfig) {
            settingsStore.updateModelConfig(settings.modelConfig)
          }
          if (settings.preferences) {
            darkMode.value = settings.preferences.darkMode
            autoSave.value = settings.preferences.autoSave
            voiceInput.value = settings.preferences.voiceInput
          }
        } catch (error) {
          console.error('Error importing settings:', error)
        }
      }
      reader.readAsText(file)
    }
  }
  input.click()
}

function clearAllData() {
  if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
    // Clear chats
    chatStore.chats.splice(0)
    chatStore.activeChat = null
    
    // Reset settings
    settingsStore.updateModelConfig({
      model: 'gemini-pro',
      temperature: 0.7,
      topK: 40,
      topP: 0.9,
      maxTokens: 1024,
      safetyLevel: 'medium'
    })
    
    // Reset preferences
    darkMode.value = false
    autoSave.value = true
    voiceInput.value = true
  }
}
</script>