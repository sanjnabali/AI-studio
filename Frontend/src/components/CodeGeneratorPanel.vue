<template>
  <div class="code-generator-panel bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-lg">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Generate Code</h3>
      <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Description
        </label>
        <textarea
          v-model="description"
          placeholder="Describe the code you want to generate..."
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
          rows="3"
        ></textarea>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Language
          </label>
          <select
            v-model="language"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
            <option value="csharp">C#</option>
            <option value="go">Go</option>
            <option value="rust">Rust</option>
            <option value="php">PHP</option>
            <option value="ruby">Ruby</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Framework
          </label>
          <select
            v-model="framework"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="none">None</option>
            <option value="react">React</option>
            <option value="vue">Vue.js</option>
            <option value="angular">Angular</option>
            <option value="express">Express</option>
            <option value="django">Django</option>
            <option value="flask">Flask</option>
            <option value="spring">Spring Boot</option>
          </select>
        </div>
      </div>

      <button
        @click="generate"
        :disabled="!description.trim()"
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
      >
        Generate Code
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const description = ref('')
const language = ref('javascript')
const framework = ref('none')

const emit = defineEmits<{
  close: []
  generate: [prompt: string, language: string, options: any]
}>()

const generate = () => {
  if (!description.value.trim()) return

  const options = {
    framework: framework.value,
    language: language.value
  }

  emit('generate', description.value, language.value, options)
}
</script>
