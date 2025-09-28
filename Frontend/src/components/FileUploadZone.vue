<template>
  <div class="file-upload-zone">
    <input type="file" multiple @change="handleFiles" class="hidden" ref="fileInput" />
    <button @click="openFileDialog" class="w-full p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-gray-400 dark:hover:border-gray-500 transition-colors">
      <div class="text-center">
        <svg class="w-8 h-8 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p class="text-sm text-gray-600 dark:text-gray-400">Drop files here or click to upload</p>
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const fileInput = ref<HTMLInputElement>()

const emit = defineEmits<{
  upload: [files: FileList]
}>()

const handleFiles = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    emit('upload', target.files)
  }
}

const openFileDialog = () => {
  fileInput.value?.click()
}
</script>

<style scoped>
.file-upload-zone {
  /* Styles */
}
</style>
