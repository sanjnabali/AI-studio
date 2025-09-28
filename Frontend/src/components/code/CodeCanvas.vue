<template>
  <div class="code-canvas">
    <div class="code-header flex justify-between items-center p-4 border-b">
      <div class="flex items-center space-x-2">
        <div class="w-3 h-3 bg-red-500 rounded-full"></div>
        <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
        <div class="w-3 h-3 bg-green-500 rounded-full"></div>
      </div>
      <div class="flex items-center space-x-4">
        <button class="text-gray-500 hover:text-gray-700">
          <PlayIcon class="w-4 h-4" />
        </button>
        <select class="text-sm border rounded px-2 py-1">
          <option>Python</option>
          <option>JavaScript</option>
          <option>TypeScript</option>
        </select>
      </div>
    </div>
    <div class="code-editor flex-1 relative">
      <textarea
        ref="codeEditor"
        v-model="code"
        :class="languageClass"
        placeholder="Write your code here..."
        @keydown="handleKeydown"
      ></textarea>
    </div>
    <div class="code-footer p-4 border-t bg-gray-50">
      <div class="flex justify-between items-center">
        <span class="text-sm text-gray-600">{{ lines }} lines</span>
        <div class="flex space-x-2">
          <button @click="formatCode" class="text-sm text-blue-600 hover:underline">Format</button>
          <button @click="runCode" class="px-3 py-1 bg-blue-600 text-white rounded text-sm">Run</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { PlayIcon } from '@heroicons/vue/24/outline'

interface Props {
  initialCode?: string
  language?: 'python' | 'javascript' | 'typescript' | 'java' | 'cpp'
  theme?: 'light' | 'dark'
}

const props = withDefaults(defineProps<Props>(), {
  initialCode: '// Start coding...',
  language: 'python',
  theme: 'light'
})

const emit = defineEmits<{
  run: [code: string, language: string]
  change: [code: string]
  format: [code: string]
}>()

const codeEditor = ref<HTMLTextAreaElement>()
const code = ref(props.initialCode)

const lines = computed(() => code.value.split('\n').length)
const languageClass = computed(() => `language-${props.language}`)

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Tab') {
    event.preventDefault()
    const target = event.target as HTMLTextAreaElement
    const start = target.selectionStart
    const end = target.selectionEnd
    code.value = code.value.substring(0, start) + '  ' + code.value.substring(end)
    // Move cursor
    nextTick(() => {
      if (codeEditor.value) {
        codeEditor.value.selectionStart = codeEditor.value.selectionEnd = start + 2
      }
    })
  }
}

const formatCode = () => {
  // Simple formatting - in real app, use prettier or similar
  emit('format', code.value)
}

const runCode = () => {
  emit('run', code.value, props.language)
}

watch(() => props.initialCode, (newCode: string) => {
  if (newCode !== undefined) code.value = newCode
})

watch(code, (newCode: string) => {
  emit('change', newCode)
})
</script>

<style scoped>
.code-canvas {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.code-editor {
  position: relative;
  flex: 1;
  min-height: 300px;
}

.code-editor textarea {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  padding: 1rem;
  font-size: 0.875rem;
  line-height: 1.5;
  resize: none;
  background: transparent;
  color: #111827;
}

.code-editor textarea:focus {
  box-shadow: none;
}

.language-python {
  /* Python specific styling if needed */
}

.language-javascript,
.language-typescript {
  /* JS/TS specific */
}

.code-footer {
  border-top: 1px solid #e5e7eb;
}
</style>
