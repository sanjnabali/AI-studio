<template>
  <nav class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <router-link to="/" class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <SparklesIcon class="w-5 h-5 text-white" />
            </div>
            <span class="text-xl font-bold text-gray-900 dark:text-white">AI Studio</span>
          </router-link>
        </div>

        <div class="flex items-center space-x-1">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.path"
            class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
            :class="{ 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white': $route.path === item.path }"
          >
            <component :is="item.icon" class="w-4 h-4 inline-block mr-2" />
            {{ item.name }}
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import {
  SparklesIcon,
  ChatBubbleLeftRightIcon,
  DocumentDuplicateIcon,
  CogIcon
} from '@heroicons/vue/24/outline'

const navigation = [
  { name: 'Studio', path: '/', icon: ChatBubbleLeftRightIcon },
  { name: 'Templates', path: '/templates', icon: DocumentDuplicateIcon },
  { name: 'Settings', path: '/settings', icon: CogIcon }
]
</script>
