<template>
  <div class="recording-list">
    <h3 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Voice Recordings</h3>
    <div class="space-y-1">
      <!-- Placeholder for recordings -->
      <div v-for="recording in recordings" :key="recording.id" class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
        {{ recording.name }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  recordings: any[]
}

defineProps<Props>()

defineEmits<{
  play: [recording: any]
  delete: [recordingId: string]
}>()
</script>

<style scoped>
.recording-list {
  /* Styles */
}
</style>
