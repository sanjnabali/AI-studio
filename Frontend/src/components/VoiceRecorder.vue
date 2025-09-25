<!-- Frontend/src/components/VoiceRecorder.vue -->
<template>
  <div class="voice-recorder">
    <button 
      @click="toggleRecording"
      :class="['btn', isRecording ? 'btn-error' : 'btn-ghost', 'btn-sm']"
      :title="isRecording ? 'Stop recording' : 'Start voice recording'"
    >
      <svg v-if="!isRecording" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
      </svg>
       <svg v-else class="w-5 h-5 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
      </svg>
    </button>

    <!-- Recording indicator -->
    <div v-if="isRecording" class="recording-indicator">
      <div class="flex items-center space-x-2">
        <div class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
        <span class="text-sm text-red-600">Recording... {{ formatDuration(recordingDuration) }}</span>
      </div>
    </div>

    <!-- Processing indicator -->
    <div v-if="isProcessing" class="processing-indicator">
      <div class="flex items-center space-x-2">
        <div class="loading loading-spinner loading-sm"></div>
        <span class="text-sm text-blue-600">Processing audio...</span>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="error-message">
      <div class="alert alert-error alert-sm">
        <span>{{ error }}</span>
        <button @click="clearError" class="btn btn-ghost btn-xs">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { apiClient } from '../api/client'

const emit = defineEmits<{
  transcript: [text: string]
}>()

const isRecording = ref(false)
const isProcessing = ref(false)
const error = ref<string | null>(null)
const recordingDuration = ref(0)

let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
let recordingTimer: NodeJS.Timeout | null = null

onMounted(() => {
  checkMediaSupport()
})

onUnmounted(() => {
  if (recordingTimer) {
    clearInterval(recordingTimer)
  }
})

const checkMediaSupport = () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    error.value = 'Voice recording is not supported in this browser'
  }
}

const toggleRecording = async () => {
  if (isRecording.value) {
    await stopRecording()
  } else {
    await startRecording()
  }
}

const startRecording = async () => {
  try {
    error.value = null
    
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000
      }
    })

    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    })

    audioChunks = []
    recordingDuration.value = 0

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(track => track.stop())
      
      if (audioChunks.length > 0) {
        await processAudio()
      }
    }

    mediaRecorder.start()
    isRecording.value = true

    // Start timer
    recordingTimer = setInterval(() => {
      recordingDuration.value += 1
      
      // Auto-stop after 30 seconds
      if (recordingDuration.value >= 30) {
        stopRecording()
      }
    }, 1000)

  } catch (err: any) {
    error.value = `Failed to start recording: ${err.message}`
    console.error('Recording error:', err)
  }
}

const stopRecording = async () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
    
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }
  }
}

const processAudio = async () => {
  try {
    isProcessing.value = true

    // Create audio blob
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
    
    // Convert to File for API
    const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' })

    // Send to speech-to-text API
    const result = await apiClient.speechToText(audioFile)

    if (result.text && result.text !== '[No speech detected]') {
      emit('transcript', result.text)
    } else {
      error.value = 'No speech detected. Please try again.'
    }

  } catch (err: any) {
    error.value = `Speech processing failed: ${err.message}`
    console.error('Speech-to-text error:', err)
  } finally {
    isProcessing.value = false
    audioChunks = []
    recordingDuration.value = 0
  }
}

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const clearError = () => {
  error.value = null
}
</script>

<style scoped>
/* eslint-disable-next-line @tailwindcss/no-custom-classname */
.recording-indicator, .processing-indicator, .error-message {
  @apply absolute top-full left-0 mt-2 z-10;
}
</style>
