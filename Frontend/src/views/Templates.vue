<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Template Library</h1>
        <p class="text-gray-600 dark:text-gray-400">Discover pre-built prompts and configurations for common tasks</p>
      </div>

      <!-- Search and Filters -->
      <div class="mb-8 flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search templates..."
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
        <select
          v-model="selectedCategory"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        >
          <option value="">All Categories</option>
          <option value="coding">Coding</option>
          <option value="writing">Writing</option>
          <option value="analysis">Analysis</option>
          <option value="creative">Creative</option>
        </select>
      </div>

      <!-- Template Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer"
          @click="useTemplate(template)"
        >
          <div class="p-6">
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center space-x-2">
                <div class="w-10 h-10 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                  <component :is="getTemplateIcon(template.category)" class="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 class="font-semibold text-gray-900 dark:text-white">{{ template.name }}</h3>
                  <span class="text-xs text-gray-500 dark:text-gray-400 capitalize">{{ template.category }}</span>
                </div>
              </div>
            </div>
            <p class="text-gray-600 dark:text-gray-400 text-sm mb-4">{{ template.description }}</p>
            <div class="flex items-center justify-between">
              <span class="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded">
                {{ template.config.model }}
              </span>
              <ChevronRightIcon class="w-4 h-4 text-gray-400" />
            </div>
          </div>
        </div>
      </div>

      <!-- Create Custom Template -->
      <div class="mt-12 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Create Custom Template</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Template Name</label>
            <input
              v-model="newTemplate.name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Category</label>
            <select
              v-model="newTemplate.category"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="coding">Coding</option>
              <option value="writing">Writing</option>
              <option value="analysis">Analysis</option>
              <option value="creative">Creative</option>
            </select>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
            <input
              v-model="newTemplate.description"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Prompt Template</label>
            <textarea
              v-model="newTemplate.prompt"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="Enter your prompt template here..."
            ></textarea>
          </div>
          <div class="md:col-span-2">
            <button
              @click="saveTemplate"
              class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium"
            >
              Save Template
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '../store/chat'
import type { Template } from '../types'
import {
  ChevronRightIcon,
  CodeBracketIcon,
  DocumentTextIcon,
  ChartBarIcon,
  SparklesIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const chatStore = useChatStore()

const searchQuery = ref('')
const selectedCategory = ref('')

const templates = ref<Template[]>([
  {
    id: '1',
    name: 'Python Code Generator',
    description: 'Generate clean, well-documented Python code for various tasks',
    category: 'coding',
    prompt: 'Write a Python function that {task}. Include docstrings, type hints, and error handling.',
    config: {
      model: 'gemini-pro',
      temperature: 0.2,
      topK: 40,
      topP: 0.9,
      maxTokens: 1024,
      safetyLevel: 'medium'
    }
  },
  {
    id: '2',
    name: 'Content Writer',
    description: 'Create engaging content for blogs, social media, and marketing',
    category: 'writing',
    prompt: 'Write a {type} about {topic}. Make it engaging, informative, and appropriate for {audience}.',
    config: {
      model: 'gemini-pro',
      temperature: 0.8,
      topK: 40,
      topP: 0.9,
      maxTokens: 1024,
      safetyLevel: 'medium'
    }
  },
  {
    id: '3',
    name: 'Data Analyst',
    description: 'Analyze data patterns and provide actionable insights',
    category: 'analysis',
    prompt: 'Analyze this data: {data}. Identify key patterns, trends, and provide actionable recommendations.',
    config: {
      model: 'gemini-pro',
      temperature: 0.3,
      topK: 40,
      topP: 0.9,
      maxTokens: 1024,
      safetyLevel: 'medium'
    }
  },
  {
    id: '4',
    name: 'Creative Story Writer',
    description: 'Generate creative stories, poems, and fictional content',
    category: 'creative',
    prompt: 'Write a {genre} story about {theme}. Make it {tone} and approximately {length} words long.',
    config: {
      model: 'gemini-pro',
      temperature: 0.9,
      topK: 40,
      topP: 0.9,
      maxTokens: 1024,
      safetyLevel: 'medium'
    }
  }
])

const newTemplate = ref<Partial<Template>>({
  name: '',
  description: '',
  category: 'coding',
  prompt: '',
  config: {
    model: 'gemini-pro',
    temperature: 0.7,
    topK: 40,
    topP: 0.9,
    maxTokens: 1024,
    safetyLevel: 'medium'
  }
})

const filteredTemplates = computed(() => {
  return templates.value.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = !selectedCategory.value || template.category === selectedCategory.value
    return matchesSearch && matchesCategory
  })
})

function getTemplateIcon(category: string) {
  const icons = {
    coding: CodeBracketIcon,
    writing: DocumentTextIcon,
    analysis: ChartBarIcon,
    creative: SparklesIcon
  }
  return icons[category as keyof typeof icons] || CodeBracketIcon
}

function useTemplate(template: Template) {
  const chat = chatStore.createChat(template.name)
  chat.modelConfig = { ...template.config }
  router.push('/')
}

function saveTemplate() {
  if (newTemplate.value.name && newTemplate.value.prompt) {
    templates.value.push({
      id: Date.now().toString(),
      name: newTemplate.value.name,
      description: newTemplate.value.description || '',
      category: newTemplate.value.category || 'coding',
      prompt: newTemplate.value.prompt,
      config: newTemplate.value.config || {
        model: 'gemini-pro',
        temperature: 0.7,
        topK: 40,
        topP: 0.9,
        maxTokens: 1024,
        safetyLevel: 'medium'
      }
    })
    
    // Reset form
    newTemplate.value = {
      name: '',
      description: '',
      category: 'coding',
      prompt: '',
      config: {
        model: 'gemini-pro',
        temperature: 0.7,
        topK: 40,
        topP: 0.9,
        maxTokens: 1024,
        safetyLevel: 'medium'
      }
    }
  }
}
</script>
