<template>
  <div class="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="close">
    <div class="modal-content bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
      <div class="modal-header p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Select Template</h2>
          <button @click="close" class="text-gray-400 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-200">
            <XMarkIcon class="w-6 h-6" />
          </button>
        </div>
      </div>

      <div class="modal-body p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="template in templates"
            :key="template.id"
            class="template-card p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
            @click="selectTemplate(template)"
          >
            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0">
                <component :is="template.icon" class="w-8 h-8 text-blue-500" />
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-sm font-medium text-gray-900 dark:text-white mb-1">{{ template.name }}</h3>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ template.description }}</p>
                <div class="mt-2 flex items-center space-x-2 text-xs">
                  <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full">{{ template.category }}</span>
                  <span class="text-gray-400">{{ template.useCases.length }} use cases</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Search and Filters -->
        <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div class="flex flex-col sm:flex-row gap-3">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search templates..."
              class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
            />
            <select
              v-model="selectedCategory"
              class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
            >
              <option value="">All Categories</option>
              <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
            </select>
          </div>
        </div>
      </div>

      <div class="modal-footer p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50">
        <div class="flex justify-between items-center">
          <button
            @click="close"
            class="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            Cancel
          </button>
          <div class="flex space-x-3">
            <button
              @click="loadRecent"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
            >
              Recent
            </button>
            <button
              @click="loadFavorites"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Favorites
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import {
  ChatBubbleLeftRightIcon,
  CodeBracketIcon,
  DocumentMagnifyingGlassIcon,
  LightBulbIcon,
  SparklesIcon
} from '@heroicons/vue/24/outline'

interface Template {
  id: string
  name: string
  description: string
  category: string
  icon: any
  useCases: string[]
  tags: string[]
  isFavorite: boolean
  preview?: string
}

const emit = defineEmits<{
  select: [template: Template]
  close: []
}>()

const props = defineProps<{
  visible: boolean
}>()

const searchQuery = ref('')
const selectedCategory = ref('')

const templates: Template[] = [
  {
    id: 'chat-assistant',
    name: 'AI Assistant',
    description: 'Create a conversational AI assistant for customer support',
    category: 'Chat',
    icon: ChatBubbleLeftRightIcon,
    useCases: ['Customer Support', 'FAQ Bot', 'Internal Helpdesk'],
    tags: ['conversational', 'support', 'automation'],
    isFavorite: false
  },
  {
    id: 'code-review',
    name: 'Code Review Bot',
    description: 'Automated code review and suggestions using AI',
    category: 'Code',
    icon: CodeBracketIcon,
    useCases: ['Code Quality', 'Bug Detection', 'Best Practices'],
    tags: ['code', 'review', 'quality'],
    isFavorite: true
  },
  {
    id: 'document-summarizer',
    name: 'Document Summarizer',
    description: 'Extract key insights and summaries from documents',
    category: 'Documents',
    icon: DocumentMagnifyingGlassIcon,
    useCases: ['Research', 'Legal Review', 'Content Analysis'],
    tags: ['documents', 'summary', 'analysis'],
    isFavorite: false
  },
  {
    id: 'idea-generator',
    name: 'Idea Generator',
    description: 'Generate creative ideas and brainstorming sessions',
    category: 'Creative',
    icon: LightBulbIcon,
    useCases: ['Marketing', 'Product Development', 'Content Creation'],
    tags: ['creative', 'brainstorming', 'innovation'],
    isFavorite: true
  },
  {
    id: 'voice-transcriber',
    name: 'Voice Transcriber',
    description: 'Convert speech to text with high accuracy',
    category: 'Voice',
    icon: SparklesIcon,
    useCases: ['Meetings', 'Interviews', 'Podcasts'],
    tags: ['voice', 'transcription', 'speech'],
    isFavorite: false
  }
]

const categories = computed(() => [...new Set(templates.map(t => t.category))])

const filteredTemplates = computed(() => {
  return templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = !selectedCategory.value || template.category === selectedCategory.value
    return matchesSearch && matchesCategory
  })
})

const selectTemplate = (template: Template) => {
  emit('select', template)
  close()
}

const close = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  emit('close')
}

const loadRecent = () => {
  // Load recent templates logic
  console.log('Loading recent templates')
}

const loadFavorites = () => {
  // Load favorites logic
  console.log('Loading favorite templates')
}

watch(() => props.visible, (visible: boolean) => {
  if (!visible) {
    searchQuery.value = ''
    selectedCategory.value = ''
  }
})
</script>

<style scoped>
.modal-overlay {
  backdrop-filter: blur(4px);
}

.template-card {
  transition: all 0.2s ease-in-out;
}

.template-card:hover {
  transform: translateY(-1px);
}

.modal-content {
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
