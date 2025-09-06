<template>
  <div class="relative">
    <button
      @click="isOpen = !isOpen"
      class="flex items-center space-x-2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600"
    >
      <div class="w-2 h-2 rounded-full" :class="getModelStatusColor(selectedModel)"></div>
      <span>{{ getModelDisplayName(selectedModel) }}</span>
      <ChevronDownIcon class="w-4 h-4" />
    </button>

    <div
      v-if="isOpen"
      class="absolute top-full left-0 mt-1 w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50"
    >
      <div class="p-2">
        <div
          v-for="model in availableModels"
          :key="model.id"
          @click="selectModel(model)"
          class="flex items-start space-x-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg cursor-pointer"
        >
          <div class="w-2 h-2 rounded-full mt-2" :class="getModelStatusColor(model.id)"></div>
          <div class="flex-1">
            <div class="font-medium text-gray-900 dark:text-white">{{ model.name }}</div>
            <div class="text-sm text-gray-500 dark:text-gray-400">{{ model.description }}</div>
            <div class="flex items-center space-x-2 mt-1">
              <span class="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-0.5 rounded">
                {{ model.contextWindow }}
              </span>
              <span class="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-0.5 rounded">
                {{ model.capabilities.join(', ') }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

interface Model {
  id: string
  name: string
  description: string
  contextWindow: string
  capabilities: string[]
  status: 'available' | 'busy' | 'offline'
}

interface Props {
  selectedModel: string
}

interface Emits {
  (e: 'update:selectedModel', value: string): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const isOpen = ref(false)

const availableModels: Model[] = [
  {
    id: 'gemini-pro',
    name: 'Gemini Pro',
    description: 'Google\'s most capable model for complex tasks',
    contextWindow: '1M tokens',
    capabilities: ['Text', 'Code', 'Reasoning'],
    status: 'available'
  },
  {
    id: 'gemini-pro-vision',
    name: 'Gemini Pro Vision',
    description: 'Multimodal model with vision capabilities',
    contextWindow: '1M tokens',
    capabilities: ['Text', 'Images', 'Vision'],
    status: 'available'
  },
  {
    id: 'claude-3',
    name: 'Claude 3 Sonnet',
    description: 'Anthropic\'s balanced model for various tasks',
    contextWindow: '200K tokens',
    capabilities: ['Text', 'Code', 'Analysis'],
    status: 'available'
  },
  {
    id: 'gpt-4',
    name: 'GPT-4',
    description: 'OpenAI\'s most advanced language model',
    contextWindow: '128K tokens',
    capabilities: ['Text', 'Code', 'Reasoning'],
    status: 'available'
  }
]

function selectModel(model: Model) {
  emit('update:selectedModel', model.id)
  isOpen.value = false
}

function getModelDisplayName(modelId: string): string {
  const model = availableModels.find(m => m.id === modelId)
  return model?.name || modelId
}

function getModelStatusColor(modelId: string): string {
  const model = availableModels.find(m => m.id === modelId)
  switch (model?.status) {
    case 'available': return 'bg-green-500'
    case 'busy': return 'bg-yellow-500'
    case 'offline': return 'bg-red-500'
    default: return 'bg-gray-500'
  }
}
</script>
