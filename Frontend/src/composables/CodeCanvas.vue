<template>
  <div class="h-full flex flex-col">
    <!-- Canvas Header -->
    <div class="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center space-x-2">
        <CodeBracketIcon class="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <span class="font-medium text-gray-900 dark:text-white">Code Canvas</span>
      </div>
      
      <div class="flex items-center space-x-2">
        <button
          @click="runCode"
          :disabled="!canRun"
          class="px-3 py-1 text-sm bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white rounded"
        >
          Run
        </button>
        
        <button
          @click="exportCode"
          class="px-3 py-1 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded"
        >
          Export
        </button>
        
        <select
          v-model="selectedLanguage"
          class="text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="javascript">JavaScript</option>
          <option value="python">Python</option>
          <option value="html">HTML</option>
          <option value="css">CSS</option>
        </select>
      </div>
    </div>

    <!-- Code Editor -->
    <div class="flex-1 flex">
      <div class="flex-1 relative">
        <textarea
          v-model="code"
          class="w-full h-full p-4 font-mono text-sm bg-gray-900 text-green-400 border-none outline-none resize-none"
          placeholder="// Start typing your code here..."
          @keydown="handleKeyDown"
        ></textarea>
        
        <!-- Line numbers -->
        <div class="absolute left-0 top-0 p-4 text-gray-500 text-sm font-mono pointer-events-none">
          <div v-for="(line, index) in codeLines" :key="index" class="h-5 leading-5">
            {{ index + 1 }}
          </div>
        </div>
      </div>

      <!-- Preview Panel -->
      <div
        v-if="showPreview"
        class="w-1/2 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
      >
        <div class="p-3 border-b border-gray-200 dark:border-gray-700">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Preview</span>
        </div>
        
        <div class="p-4">
          <iframe
            v-if="selectedLanguage === 'html'"
            ref="previewFrame"
            class="w-full h-full border border-gray-300 dark:border-gray-600 rounded"
            :srcdoc="code"
          ></iframe>
          
          <div v-else-if="selectedLanguage === 'javascript'" class="space-y-2">
            <div class="text-sm text-gray-600 dark:text-gray-400">Console Output:</div>
            <div class="bg-gray-100 dark:bg-gray-700 p-3 rounded font-mono text-sm">
              <div v-for="(output, index) in consoleOutput" :key="index" class="mb-1">
                <span class="text-gray-500">&gt;</span> {{ output }}
              </div>
            </div>
          </div>
          
          <div v-else class="text-sm text-gray-500 dark:text-gray-400">
            Preview not available for {{ selectedLanguage }}
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-between p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
      <div class="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
        <span>Lines: {{ codeLines.length }}</span>
        <span>Characters: {{ code.length }}</span>
        <span>Language: {{ selectedLanguage }}</span>
      </div>
      
      <button
        @click="showPreview = !showPreview"
        class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
      >
        {{ showPreview ? 'Hide' : 'Show' }} Preview
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { CodeBracketIcon } from '@heroicons/vue/24/outline'

const code = ref('')
const selectedLanguage = ref('javascript')
const showPreview = ref(true)
const consoleOutput = ref<string[]>([])
const previewFrame = ref<HTMLIFrameElement>()

const codeLines = computed(() => code.value.split('\n'))

const canRun = computed(() => {
  return ['javascript', 'html'].includes(selectedLanguage.value) && code.value.trim().length > 0
})

function handleKeyDown(event: KeyboardEvent) {
  // Handle tab indentation
  if (event.key === 'Tab') {
    event.preventDefault()
    const textarea = event.target as HTMLTextAreaElement
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    
    textarea.value = textarea.value.substring(0, start) + '  ' + textarea.value.substring(end)
    textarea.selectionStart = textarea.selectionEnd = start + 2
    code.value = textarea.value
  }
}

function runCode() {
  if (selectedLanguage.value === 'javascript') {
    consoleOutput.value = []
    
    try {
      // Create a custom console for capturing output
      const customConsole = {
        log: (...args: any[]) => {
          consoleOutput.value.push(args.join(' '))
        },
        error: (...args: any[]) => {
          consoleOutput.value.push(`Error: ${args.join(' ')}`)
        }
      }
      
      // Execute the code with custom console
      const func = new Function('console', code.value)
      func(customConsole)
    } catch (error) {
      consoleOutput.value.push(`Error: ${error}`)
    }
  }
}

function exportCode() {
  const blob = new Blob([code.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `code.${getFileExtension(selectedLanguage.value)}`
  a.click()
  URL.revokeObjectURL(url)
}

function getFileExtension(language: string): string {
  const extensions: Record<string, string> = {
    javascript: 'js',
    python: 'py',
    html: 'html',
    css: 'css'
  }
  return extensions[language] || 'txt'
}

// Watch for language changes to update preview
watch(selectedLanguage, (newLang) => {
  if (newLang === 'html') {
    showPreview.value = true
  }
})

// Auto-run for HTML
watch(code, () => {
  if (selectedLanguage.value === 'html' && showPreview.value) {
    // The iframe will automatically update with the new srcdoc
  }
})
</script>