<template>
  <div
    @drop="handleDrop"
    @dragover.prevent
    @dragenter.prevent
    class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-gray-400 dark:hover:border-gray-500 transition-colors"
    :class="{ 'border-blue-500 bg-blue-50 dark:bg-blue-900/20': isDragging }"
  >
    <input
      ref="fileInput"
      type="file"
      multiple
      :accept="acceptedTypes"
      class="hidden"
      @change="handleFileInput"
    />
    
    <div class="space-y-2">
      <DocumentArrowUpIcon class="mx-auto h-12 w-12 text-gray-400" />
      <div>
        <button
          @click="triggerFileInput"
          class="text-blue-600 dark:text-blue-400 hover:text-blue-500 font-medium"
        >
          Choose files
        </button>
        <span class="text-gray-500 dark:text-gray-400"> or drag and drop</span>
      </div>
      <p class="text-sm text-gray-500 dark:text-gray-400">
        {{ acceptedTypesText }}
      </p>
    </div>

    <!-- File List -->
    <div v-if="uploadedFiles.length" class="mt-4 space-y-2">
      <div
        v-for="file in uploadedFiles"
        :key="file.id"
        class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded"
      >
        <div class="flex items-center space-x-2">
          <component :is="getFileIcon(file.type)" class="w-4 h-4 text-gray-500" />
          <span class="text-sm text-gray-700 dark:text-gray-300">{{ file.name }}</span>
          <span class="text-xs text-gray-500 dark:text-gray-400">({{ formatFileSize(file.size) }})</span>
        </div>
        <button
          @click="removeFile(file.id)"
          class="text-red-500 hover:text-red-700 p-1"
        >
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  DocumentArrowUpIcon,
  DocumentTextIcon,
  PhotoIcon,
  FilmIcon,
  MusicalNoteIcon,
  DocumentIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
  file: File
}

interface Props {
  acceptedTypes?: string
  maxSize?: number
}

interface Emits {
  (e: 'filesUploaded', files: File[]): void
  (e: 'fileRemoved', fileId: string): void
}

const props = withDefaults(defineProps<Props>(), {
  acceptedTypes: 'image/*,.pdf,.docx,.txt,.mp3,.mp4',
  maxSize: 10 * 1024 * 1024 // 10MB
})

const emit = defineEmits<Emits>()

const fileInput = ref<HTMLInputElement>()
const uploadedFiles = ref<UploadedFile[]>([])
const isDragging = ref(false)

const acceptedTypesText = computed(() => {
  return 'Images, PDFs, Documents, Audio, Video (max 10MB)'
})

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileInput(event: Event) {
  const files = (event.target as HTMLInputElement).files
  if (files) {
    processFiles(Array.from(files))
  }
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  isDragging.value = false
  
  const files = event.dataTransfer?.files
  if (files) {
    processFiles(Array.from(files))
  }
}

function processFiles(files: File[]) {
  const validFiles = files.filter(file => file.size <= props.maxSize)
  
  const newFiles: UploadedFile[] = validFiles.map(file => ({
    id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
    name: file.name,
    size: file.size,
    type: file.type,
    file
  }))
  
  uploadedFiles.value.push(...newFiles)
  emit('filesUploaded', validFiles)
}

function removeFile(fileId: string) {
  const index = uploadedFiles.value.findIndex(f => f.id === fileId)
  if (index > -1) {
    uploadedFiles.value.splice(index, 1)
    emit('fileRemoved', fileId)
  }
}

function getFileIcon(type: string) {
  if (type.startsWith('image/')) return PhotoIcon
  if (type.startsWith('audio/')) return MusicalNoteIcon
  if (type.startsWith('video/')) return FilmIcon
  if (type.includes('pdf') || type.includes('document')) return DocumentTextIcon
  return DocumentIcon
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>