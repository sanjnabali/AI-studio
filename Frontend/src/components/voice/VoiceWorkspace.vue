<template>
  <div class="voice-workspace flex flex-col h-full">
    <div class="voice-header p-4 border-b bg-white dark:bg-gray-800">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Voice Workspace</h3>
        <div class="flex items-center space-x-3">
          <StatusIndicator :status="connectionStatus" />
          <button @click="toggleRecording" :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            isRecording ? 'bg-red-500 text-white' : 'bg-blue-600 text-white hover:bg-blue-700'
          ]">
            {{ isRecording ? 'Stop Recording' : 'Start Recording' }}
          </button>
        </div>
      </div>
    </div>

    <div class="voice-content flex-1 flex flex-col overflow-hidden">
      <!-- Waveform/Visualization Area -->
      <div class="voice-visualization flex-1 p-4">
        <div v-if="!isRecording" class="h-full flex items-center justify-center">
          <div class="text-center text-gray-500 dark:text-gray-400">
            <MicrophoneIcon class="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p class="text-lg">Ready to record</p>
            <p class="text-sm">Click 'Start Recording' to begin</p>
          </div>
        </div>
        
        <div v-else class="h-full relative">
          <!-- Audio visualization placeholder -->
          <div class="waveform-placeholder h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <div class="waveform-bars flex space-x-1">
              <div v-for="n in 20" :key="n" class="w-1 bg-white rounded opacity-75" :style="{ height: `${Math.random() * 100}%` }"></div>
            </div>
            <p class="text-white ml-4 text-sm font-medium">Recording...</p>
          </div>
        </div>
      </div>

      <!-- Controls and Transcript -->
      <div class="voice-controls p-4 border-t bg-gray-50 dark:bg-gray-700">
        <div class="flex flex-col space-y-3">
          <!-- Transcript Display -->
          <div class="transcript-section">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Live Transcript</label>
            <div class="transcript-content p-3 bg-white dark:bg-gray-800 border rounded-lg max-h-32 overflow-y-auto">
              <p v-if="!transcript" class="text-gray-500 italic">Transcript will appear here...</p>
              <p v-else class="text-sm">{{ transcript }}</p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex space-x-2">
            <button @click="processAudio" :disabled="!hasRecording" class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              <CheckIcon v-if="hasRecording" class="w-4 h-4 mr-2" />
              Process Audio
            </button>
            <button @click="clearRecording" :disabled="!hasRecording" class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              Clear
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { MicrophoneIcon, CheckIcon } from '@heroicons/vue/24/outline'
import StatusIndicator from '../StatusIndicator.vue'

interface Props {
  initialTranscript?: string
}

const props = withDefaults(defineProps<Props>(), {
  initialTranscript: ''
})

const emit = defineEmits<{
  startRecording: []
  stopRecording: []
  processAudio: [audioBlob: Blob]
  clear: []
}>()

const isRecording = ref(false)
const transcript = ref(props.initialTranscript)
const connectionStatus = ref<'connected' | 'connecting' | 'disconnected'>('connected')
const hasRecording = computed(() => isRecording.value || transcript.value.length > 0)

const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = () => {
  isRecording.value = true
  emit('startRecording')
  // Simulate connection status change
  connectionStatus.value = 'connected'
}

const stopRecording = () => {
  isRecording.value = false
  emit('stopRecording')
}

const processAudio = () => {
  // Simulate audio processing
  emit('processAudio', new Blob([])) // Empty blob for demo
}

const clearRecording = () => {
  transcript.value = ''
  emit('clear')
}

const simulateTranscript = () => {
  if (isRecording.value) {
    // Add random words to simulate speech-to-text
    const words = ['Hello', 'this', 'is', 'a', 'test', 'of', 'voice', 'recording']
    transcript.value += ' ' + words[Math.floor(Math.random() * words.length)]
    setTimeout(simulateTranscript, 1000)
  }
}

watch(isRecording, (newVal: boolean) => {
  if (newVal) {
    simulateTranscript()
  }
})
</script>

<style scoped>
.voice-workspace {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.waveform-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.waveform-bars {
  display: flex;
  align-items: end;
  height: 60px;
  padding: 1rem;
}

.transcript-content {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.5;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.waveform-bars .w-1 {
  animation: pulse 1.5s ease-in-out infinite;
  animation-delay: calc(var(--index) * 0.1s);
}
</style>
