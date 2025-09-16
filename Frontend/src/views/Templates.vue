<!-- src/views/Templates.vue -->
<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <Navbar />
    
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Templates</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Pre-built templates to get you started quickly
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="template in templates"
          :key="template.id"
          class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow cursor-pointer"
          @click="useTemplate(template)"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <component :is="template.icon" class="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 class="font-medium text-gray-900 dark:text-white">{{ template.name }}</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ template.category }}</p>
              </div>
            </div>
          </div>
          
          <p class="mt-3 text-sm text-gray-600 dark:text-gray-300">{{ template.description }}</p>
          
          <div class="mt-4 flex items-center justify-between">
            <div class="flex flex-wrap gap-1">
              <span
                v-for="tag in template.tags"
                :key="tag"
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200"
              >
                {{ tag }}
              </span>
            </div>
            
            <button class="text-blue-600 dark:text-blue-400 text-sm font-medium hover:text-blue-800 dark:hover:text-blue-300">
              Use Template
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../composables/Navbar.vue'
import {
  CodeBracketIcon,
  PencilIcon,
  ChartBarIcon,
  DocumentTextIcon,
  AcademicCapIcon,
  BriefcaseIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()

const templates = ref([
  {
    id: 1,
    name: 'Code Review',
    category: 'Development',
    description: 'Get detailed code reviews and suggestions for improvement',
    icon: CodeBracketIcon,
    tags: ['code', 'review', 'development'],
    prompt: 'Please review this code and provide detailed feedback on:\n1. Code quality and best practices\n2. Potential bugs or issues\n3. Performance optimizations\n4. Suggestions for improvement\n\n```\n[Your code here]\n```'
  },
  {
    id: 2,
    name: 'Creative Writing',
    category: 'Writing',
    description: 'Generate creative stories, poems, and narrative content',
    icon: PencilIcon,
    tags: ['creative', 'writing', 'story'],
    prompt: 'Help me write a creative piece. Please specify:\n- Genre (e.g., fantasy, sci-fi, mystery)\n- Setting and time period\n- Main character details\n- Plot elements or themes\n\nThen I\'ll create an engaging narrative for you.'
  },
  {
    id: 3,
    name: 'Data Analysis',
    category: 'Analytics',
    description: 'Analyze data, create visualizations, and generate insights',
    icon: ChartBarIcon,
    tags: ['data', 'analysis', 'visualization'],
    prompt: 'I need help analyzing data. Please provide:\n1. Your dataset (CSV, JSON, or describe the data)\n2. What insights you\'re looking for\n3. Any specific questions about the data\n4. Preferred visualization types\n\nI\'ll help you analyze the data and create meaningful insights.'
  },
  {
    id: 4,
    name: 'Technical Documentation',
    category: 'Documentation',
    description: 'Create comprehensive technical documentation',
    icon: DocumentTextIcon,
    tags: ['documentation', 'technical', 'API'],
    prompt: 'Help me create technical documentation. Please specify:\n- Project/API/system to document\n- Target audience (developers, users, etc.)\n- Specific sections needed\n- Existing code or specs\n\nI\'ll create clear, comprehensive documentation.'
  },
  {
    id: 5,
    name: 'Research Assistant',
    category: 'Research',
    description: 'Research topics, summarize findings, and cite sources',
    icon: AcademicCapIcon,
    tags: ['research', 'academic', 'summary'],
    prompt: 'I need research assistance on [TOPIC]. Please help me:\n1. Find key information and current developments\n2. Summarize main points and findings\n3. Identify reliable sources\n4. Provide citations where applicable\n\nWhat specific topic would you like me to research?'
  },
  {
    id: 6,
    name: 'Business Analysis',
    category: 'Business',
    description: 'Analyze business problems and provide strategic insights',
    icon: BriefcaseIcon,
    tags: ['business', 'strategy', 'analysis'],
    prompt: 'Help me with business analysis. Please provide:\n- Business context or industry\n- Specific problem or opportunity\n- Available data or constraints\n- Strategic objectives\n\nI\'ll provide analysis, recommendations, and actionable insights.'
  }
])

function useTemplate(template: any) {
  // Navigate to studio with the template prompt
  router.push({
    name: 'studio',
    query: { template: template.prompt }
  })
}
</script>