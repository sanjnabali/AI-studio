<!-- Frontend/src/components/CodeCanvas.vue -->
<template>
  <div class="code-canvas">
    <!-- Header -->
    <div class="canvas-header">
      <div class="flex items-center space-x-4">
        <h2 class="text-xl font-semibold">Code Canvas</h2>
        <select 
          v-model="selectedLanguage" 
          class="select select-bordered select-sm"
          @change="updateLanguage"
        >
          <option v-for="lang in supportedLanguages" :key="lang.code" :value="lang.code">
            {{ lang.name }}
          </option>
        </select>
      </div>
      
      <div class="flex items-center space-x-2">
        <button 
          @click="generateCode" 
          class="btn btn-primary btn-sm"
          :disabled="!codePrompt.trim() || generating"
        >
          <svg v-if="!generating" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span v-else class="loading loading-spinner loading-sm"></span>
          Generate
        </button>
        
        <button 
          @click="executeCode" 
          class="btn btn-success btn-sm"
          :disabled="!code.trim() || executing"
        >
          <svg v-if="!executing" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1M9 16a5 5 0 006 0" />
          </svg>
          <span v-else class="loading loading-spinner loading-sm"></span>
          Run
        </button>
        
        <button 
          @click="analyzeCode" 
          class="btn btn-outline btn-sm"
          :disabled="!code.trim() || analyzing"
        >
          <svg v-if="!analyzing" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span v-else class="loading loading-spinner loading-sm"></span>
          Analyze
        </button>
        
        <button @click="clearCode" class="btn btn-ghost btn-sm">
          Clear
        </button>
      </div>
    </div>

    <!-- Code Generation Prompt -->
    <div class="prompt-section">
      <textarea
        v-model="codePrompt"
        placeholder="Describe what you want to build... (e.g., 'Create a function to calculate fibonacci numbers')"
        class="textarea textarea-bordered w-full"
        rows="2"
      ></textarea>
      
      <div class="flex items-center space-x-4 mt-2">
        <label class="flex items-center">
          <input 
            v-model="includeTests" 
            type="checkbox" 
            class="checkbox checkbox-sm" 
          />
          <span class="ml-2 text-sm">Include tests</span>
        </label>
        
        <select v-model="complexity" class="select select-bordered select-sm">
          <option value="simple">Simple</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="canvas-content">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 h-full">
        <!-- Code Editor -->
        <div class="code-editor-panel">
          <div class="panel-header">
            <h3 class="font-medium">Code Editor</h3>
            <div class="text-sm text-gray-500">
              Lines: {{ lineCount }} | Characters: {{ code.length }}
            </div>
          </div>
          
          <div class="editor-container">
            <textarea
              v-model="code"
              class="code-textarea"
              placeholder="Write your code here..."
              spellcheck="false"
              @keydown="handleKeyDown"
            ></textarea>
          </div>
        </div>

        <!-- Output/Results Panel -->
        <div class="output-panel">
          <div class="panel-header">
            <h3 class="font-medium">Output</h3>
            <div class="tabs tabs-boxed tabs-sm">
              <button 
                :class="['tab', { 'tab-active': activeTab === 'output' }]"
                @click="activeTab = 'output'"
              >
                Console
              </button>
              <button 
                :class="['tab', { 'tab-active': activeTab === 'analysis' }]"
                @click="activeTab = 'analysis'"
              >
                Analysis
              </button>
              <button 
                :class="['tab', { 'tab-active': activeTab === 'history' }]"
                @click="activeTab = 'history'"
              >
                History
              </button>
            </div>
          </div>

          <div class="output-content">
            <!-- Console Output -->
            <div v-if="activeTab === 'output'" class="console-output">
              <div v-if="executionResult" class="execution-result">
                <div class="result-header">
                  <span :class="['status-badge', executionResult.status]">
                    {{ executionResult.status.toUpperCase() }}
                  </span>
                  <span class="execution-time">
                    {{ executionResult.execution_time }}ms
                  </span>
                </div>
                
                <div v-if="executionResult.output" class="output-text">
                  <h4 class="text-sm font-medium mb-2">Output:</h4>
                  <pre class="console-text">{{ executionResult.output }}</pre>
                </div>
                
                <div v-if="executionResult.error" class="error-text">
                  <h4 class="text-sm font-medium mb-2 text-red-600">Error:</h4>
                  <pre class="console-text error">{{ executionResult.error }}</pre>
                </div>
              </div>
              
              <div v-else class="empty-console">
                <p class="text-gray-500">No output yet. Run your code to see results here.</p>
              </div>
            </div>

            <!-- Analysis Tab -->
            <div v-if="activeTab === 'analysis'" class="analysis-output">
              <div v-if="analysisResult" class="analysis-content">
                <div class="complexity-score mb-4">
                  <h4 class="font-medium mb-2">Complexity Score</h4>
                  <div class="flex items-center space-x-2">
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        class="bg-gradient-to-r from-green-400 to-red-500 h-2 rounded-full transition-all"
                        :style="{ width: `${(analysisResult.complexity_score / 10) * 100}%` }"
                      ></div>
                    </div>
                    <span class="text-sm font-medium">{{ analysisResult.complexity_score }}/10</span>
                  </div>
                </div>

                <div class="suggestions mb-4">
                  <h4 class="font-medium mb-2">Suggestions</h4>
                  <ul class="space-y-2">
                    <li v-for="suggestion in analysisResult.suggestions" :key="suggestion" 
                        class="flex items-start space-x-2">
                      <svg class="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span class="text-sm">{{ suggestion }}</span>
                    </li>
                  </ul>
                </div>

                <div v-if="analysisResult.issues.length > 0" class="issues">
                  <h4 class="font-medium mb-2">Issues</h4>
                  <div class="space-y-2">
                    <div v-for="issue in analysisResult.issues" :key="issue.message" 
                         :class="['issue-item', `severity-${issue.severity}`]">
                      <div class="flex items-center space-x-2">
                        <span :class="['issue-type', issue.severity]">{{ issue.type }}</span>
                        <span class="issue-message">{{ issue.message }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="analysis-text mt-4">
                  <h4 class="font-medium mb-2">Detailed Analysis</h4>
                  <div class="prose prose-sm">
                    <p class="whitespace-pre-wrap">{{ analysisResult.analysis }}</p>
                  </div>
                </div>
              </div>
              
              <div v-else class="empty-analysis">
                <p class="text-gray-500">No analysis yet. Analyze your code to see insights here.</p>
              </div>
            </div>

            <!-- History Tab -->
            <div v-if="activeTab === 'history'" class="history-output">
              <div v-if="executionHistory.length > 0" class="space-y-2">
                <div v-for="execution in executionHistory.slice(0, 10)" :key="execution.id" 
                     class="history-item">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                      <span :class="['status-dot', execution.status]"></span>
                      <span class="text-sm font-mono">{{ execution.language }}</span>
                      <span class="text-xs text-gray-500">
                        {{ new Date(execution.created_at).toLocaleTimeString() }}
                      </span>
                    </div>
                    <span class="text-xs text-gray-500">{{ execution.execution_time }}ms</span>
                  </div>
                  <p class="text-sm text-gray-600 truncate mt-1">{{ execution.code_preview }}</p>
                </div>
              </div>
              
              <div v-else class="empty-history">
                <p class="text-gray-500">No execution history yet.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiClient } from '@/api/client'

const selectedLanguage = ref('python')
const code = ref('')
const codePrompt = ref('')
const includeTests = ref(false)
const complexity = ref<'simple' | 'intermediate' | 'advanced'>('simple')
const activeTab = ref<'output' | 'analysis' | 'history'>('output')

const generating = ref(false)
const executing = ref(false)
const analyzing = ref(false)

const executionResult = ref<any>(null)
const analysisResult = ref<any>(null)
const executionHistory = ref<any[]>([])
const supportedLanguages = ref<any[]>([])

const lineCount = computed(() => code.value.split('\n').length)

onMounted(async () => {
  try {
    const languagesResponse = await apiClient.getSupportedLanguages()
    supportedLanguages.value = languagesResponse.supported_languages
    
    const historyResponse = await apiClient.getCodeExecutions()
    executionHistory.value = historyResponse
  } catch (error) {
    console.error('Failed to load initial data:', error)
  }
})

const updateLanguage = () => {
  // Clear results when switching languages
  executionResult.value = null
  analysisResult.value = null
}

const generateCode = async () => {
  if (!codePrompt.value.trim()) return

  generating.value = true
  try {
    const response = await apiClient.generateCode(
      codePrompt.value,
      selectedLanguage.value,
      complexity.value,
      includeTests.value
    )
    
    code.value = response.code
    
    // Show generation info in console
    executionResult.value = {
      status: 'generated',
      output: `Code generated successfully!\n\nExplanation:\n${response.explanation}`,
      execution_time: Math.round(response.processing_time * 1000)
    }
    
    activeTab.value = 'output'
  } catch (error: any) {
    executionResult.value = {
      status: 'error',
      error: `Code generation failed: ${error.message}`,
      execution_time: 0
    }
  } finally {
    generating.value = false
  }
}

const executeCode = async () => {
  if (!code.value.trim()) return

  executing.value = true
  try {
    const response = await apiClient.executeCode(
      code.value,
      selectedLanguage.value,
      10,
      []
    )
    
    executionResult.value = response
    activeTab.value = 'output'
    
    // Refresh history
    const historyResponse = await apiClient.getCodeExecutions(10)
    executionHistory.value = historyResponse
    
  } catch (error: any) {
    executionResult.value = {
      status: 'error',
      error: `Execution failed: ${error.message}`,
      execution_time: 0
    }
  } finally {
    executing.value = false
  }
}

const analyzeCode = async () => {
  if (!code.value.trim()) return

  analyzing.value = true
  try {
    const response = await apiClient.analyzeCode(
      code.value,
      selectedLanguage.value,
      'full'
    )
    
    analysisResult.value = response
    activeTab.value = 'analysis'
  } catch (error: any) {
    analysisResult.value = {
      analysis: `Analysis failed: ${error.message}`,
      suggestions: [],
      complexity_score: 0,
      issues: []
    }
  } finally {
    analyzing.value = false
  }
}

const clearCode = () => {
  code.value = ''
  codePrompt.value = ''
  executionResult.value = null
  analysisResult.value = null
}

const handleKeyDown = (event: KeyboardEvent) => {
  // Handle tab key for indentation
  if (event.key === 'Tab') {
    event.preventDefault()
    const textarea = event.target as HTMLTextAreaElement
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    
    // Insert tab character
    const newValue = code.value.substring(0, start) + '  ' + code.value.substring(end)
    code.value = newValue
    
    // Restore cursor position
    setTimeout(() => {
      textarea.selectionStart = textarea.selectionEnd = start + 2
    })
  }
}
</script>

<style scoped>
.code-canvas {
  @apply flex flex-col h-full bg-white dark:bg-gray-900;
}

.canvas-header {
  @apply flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700;
}

.prompt-section {
  @apply p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800;
}

.canvas-content {
  @apply flex-1 p-4 overflow-hidden;
}

.code-editor-panel, .output-panel {
  @apply bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden;
}

.panel-header {
  @apply flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700;
}

.editor-container {
  @apply h-full;
}

.code-textarea {
  @apply w-full h-full p-4 font-mono text-sm resize-none border-0 bg-transparent focus:outline-none;
  min-height: 400px;
  line-height: 1.5;
}

.output-content {
  @apply p-4 h-full overflow-y-auto;
  max-height: 400px;
}

.console-output, .analysis-output, .history-output {
  @apply h-full;
}

.console-text {
  @apply font-mono text-sm bg-gray-100 dark:bg-gray-900 p-3 rounded overflow-x-auto;
}

.console-text.error {
  @apply bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300;
}

.result-header {
  @apply flex items-center justify-between mb-3;
}

.status-badge {
  @apply px-2 py-1 text-xs font-medium rounded;
}

.status-badge.success {
  @apply bg-green-100 text-green-800;
}

.status-badge.error {
  @apply bg-red-100 text-red-800;
}

.status-badge.timeout {
  @apply bg-yellow-100 text-yellow-800;
}

.status-badge.generated {
  @apply bg-blue-100 text-blue-800;
}

.execution-time {
  @apply text-sm text-gray-500;
}

.issue-item {
  @apply p-2 rounded border-l-4;
}

.issue-item.severity-high {
  @apply border-red-500 bg-red-50 dark:bg-red-900/20;
}

.issue-item.severity-medium {
  @apply border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20;
}

.issue-item.severity-low {
  @apply border-blue-500 bg-blue-50 dark:bg-blue-900/20;
}

.issue-type {
  @apply px-2 py-1 text-xs font-medium rounded uppercase;
}

.issue-type.high {
  @apply bg-red-200 text-red-800;
}

.issue-type.medium {
  @apply bg-yellow-200 text-yellow-800;
}

.issue-type.low {
  @apply bg-blue-200 text-blue-800;
}

.history-item {
  @apply p-3 border border-gray-200 dark:border-gray-700 rounded;
}

.status-dot {
  @apply w-2 h-2 rounded-full;
}

.status-dot.success {
  @apply bg-green-500;
}

.status-dot.error {
  @apply bg-red-500;
}

.status-dot.timeout {
  @apply bg-yellow-500;
}

.empty-console, .empty-analysis, .empty-history {
  @apply flex items-center justify-center h-32 text-center;
}

</style>