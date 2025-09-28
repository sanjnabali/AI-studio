<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
      <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          Create New File
        </h3>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <div class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            File Name
          </label>
          <input
            v-model="filename"
            @keydown.enter="create"
            placeholder="e.g., main.py, app.js, index.html"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            ref="filenameInput"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Language
          </label>
          <select
            v-model="language"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="python">Python (.py)</option>
            <option value="javascript">JavaScript (.js)</option>
            <option value="typescript">TypeScript (.ts)</option>
            <option value="java">Java (.java)</option>
            <option value="cpp">C++ (.cpp)</option>
            <option value="c">C (.c)</option>
            <option value="go">Go (.go)</option>
            <option value="rust">Rust (.rs)</option>
            <option value="php">PHP (.php)</option>
            <option value="ruby">Ruby (.rb)</option>
            <option value="html">HTML (.html)</option>
            <option value="css">CSS (.css)</option>
            <option value="json">JSON (.json)</option>
            <option value="xml">XML (.xml)</option>
            <option value="yaml">YAML (.yaml)</option>
            <option value="markdown">Markdown (.md)</option>
            <option value="sql">SQL (.sql)</option>
            <option value="shell">Shell Script (.sh)</option>
          </select>
        </div>

        <div class="flex justify-end space-x-3 pt-4">
          <button
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="create"
            :disabled="!isValid"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
          >
            Create File
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const filename = ref('')
const language = ref('python')
const filenameInput = ref<HTMLInputElement>()

const emit = defineEmits<{
  close: []
  create: [filename: string, language: string]
}>()

const isValid = computed(() => {
  return filename.value.trim().length > 0 && filename.value.includes('.')
})

const create = () => {
  if (!isValid.value) return

  emit('create', filename.value.trim(), language.value)
}

onMounted(() => {
  filenameInput.value?.focus()
})
</script>
