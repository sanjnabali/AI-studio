<template>
  <div class="flex items-center space-x-2">
    <button
      @click="toggleRecording"
      class="relative p-3 rounded-full transition-all duration-200"
      :class="{
        'bg-red-500 hover:bg-red-600 text-white animate-pulse': isRecording,
        'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300': !isRecording
      }"
    >
      <MicrophoneIcon class="w-5 h-5" />
      
      <!-- Recording indicator -->
      <div
        v-if="isRecording"
        class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-ping"
      ></div>
    </button>

    <!-- Recording duration -->
    <div v-if="isRecording" class="text-sm text-red-600 dark:text-red-400 font-mono">
      {{ formatDuration(recordingDuration) }}
    </div>

    <!-- Audio visualization -->
    <div v-if="isRecording" class="flex items-center space-x-1">
      <div
        v-for="i in 5"
        :key="i"
        class="w-1 bg-red-500 rounded-full animate-pulse"
        :style="{ height: `${Math.random() * 20 + 10}px`, animationDelay: `${i * 0.1}s` }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { MicrophoneIcon } from '@heroicons/vue/24/outline'
import { useVoice } from '../composables/usevoice'

interface Emits {
  (e: 'recordingComplete', audioBlob: Blob): void
  (e: 'recordingStart'): void
  (e: 'recordingStop'): void
}

const emit = defineEmits<Emits>()

const { isRecording, startRecording, stopRecording } = useVoice()
const recordingDuration = ref(0)
let durationInterval: ReturnType<typeof setInterval> | null = null

async function toggleRecording() {
  if (isRecording.value) {
    // Stop recording
    const audioBlob = await stopRecording()
    clearInterval(durationInterval!)
    recordingDuration.value = 0
    emit('recordingStop')
    emit('recordingComplete', audioBlob)
  } else {
    // Start recording
    await startRecording()
    emit('recordingStart')
    
    // Start duration timer
    recordingDuration.value = 0
    durationInterval = setInterval(() => {
      recordingDuration.value += 1
    }, 1000)
  }
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

onUnmounted(() => {
  if (durationInterval) {
    clearInterval(durationInterval)
  }
})
</script>
