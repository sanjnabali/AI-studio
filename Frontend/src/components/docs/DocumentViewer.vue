<template>
  <div class="document-viewer flex flex-col h-full">
    <div class="document-header p-4 border-b bg-white dark:bg-gray-800">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ currentDocument?.filename || 'Document Viewer' }}</h3>
          <span v-if="currentDocument" class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
            {{ currentDocument.type }}
          </span>
        </div>
        <div class="flex items-center space-x-2">
          <button @click="zoomIn" class="p-2 text-gray-500 hover:text-gray-700">
            <PlusIcon class="w-4 h-4" />
          </button>
          <button @click="zoomOut" class="p-2 text-gray-500 hover:text-gray-700">
            <MinusIcon class="w-4 h-4" />
          </button>
          <button @click="toggleFullscreen" class="p-2 text-gray-500 hover:text-gray-700">
            <ArrowsPointingOutIcon class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <div class="document-content flex-1 relative overflow-hidden">
      <div v-if="!currentDocument" class="h-full flex items-center justify-center">
        <div class="text-center text-gray-500 dark:text-gray-400">
          <DocumentIcon class="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p class="text-lg">No document selected</p>
          <p class="text-sm">Select a document from the sidebar to view it here</p>
        </div>
      </div>

      <div v-else class="h-full flex flex-col">
        <!-- Toolbar for document-specific controls -->
        <div class="document-toolbar p-2 bg-gray-50 dark:bg-gray-700 border-b flex items-center space-x-2">
          <button @click="previousPage" :disabled="currentPage === 1" class="p-1 text-gray-500 hover:text-gray-700 disabled:opacity-50">
            <ChevronLeftIcon class="w-5 h-5" />
          </button>
          <span class="text-sm text-gray-600">{{ currentPage }} / {{ totalPages }}</span>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="p-1 text-gray-500 hover:text-gray-700 disabled:opacity-50">
            <ChevronRightIcon class="w-5 h-5" />
          </button>
          <div class="flex-1 text-center">
            <span class="text-sm text-gray-600">Zoom: {{ zoomLevel }}%</span>
          </div>
        </div>

        <!-- Document Render Area -->
        <div class="document-render flex-1 overflow-auto p-4" :style="{ transform: `scale(${zoomLevel / 100})` }">
          <div v-if="documentType === 'pdf'" class="pdf-viewer">
            <!-- PDF rendering placeholder - in real app, use pdf.js -->
            <div class="pdf-page bg-white shadow-lg rounded-lg p-8 max-w-4xl mx-auto">
              <div class="pdf-content">
                <p class="text-gray-800 text-lg leading-relaxed">
                  PDF content would be rendered here using pdf.js or similar library.
                </p>
                <p class="text-gray-600 mt-4 italic">
                  Page {{ currentPage }} of {{ totalPages }}
                </p>
              </div>
            </div>
          </div>

          <div v-else-if="documentType === 'docx'" class="docx-viewer">
            <!-- DOCX rendering placeholder -->
            <div class="docx-content bg-white shadow-lg rounded-lg p-8 max-w-4xl mx-auto">
              <h1 class="text-2xl font-bold mb-4">Document Title</h1>
              <p class="text-gray-800 text-lg leading-relaxed mb-4">
                This is a sample DOCX document content. In a real application, this would be rendered using a library like mammoth.js.
              </p>
              <ul class="list-disc list-inside ml-4 mb-4">
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
              </ul>
              <p class="text-gray-600 italic">Page {{ currentPage }}</p>
            </div>
          </div>

          <div v-else-if="documentType === 'txt'" class="txt-viewer">
            <!-- Plain text rendering -->
            <pre class="bg-white shadow-lg rounded-lg p-8 max-w-4xl mx-auto text-sm font-mono whitespace-pre-wrap">
{{ currentDocument.content || 'Plain text content here...' }}
            </pre>
          </div>

          <div v-else class="generic-viewer">
            <div class="bg-white shadow-lg rounded-lg p-8 max-w-4xl mx-auto">
              <p class="text-gray-800">Unsupported document type: {{ documentType }}</p>
              <p class="text-gray-600 mt-2">Please upload supported formats (PDF, DOCX, TXT)</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  PlusIcon,
  MinusIcon,
  ArrowsPointingOutIcon,
  DocumentIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

interface Props {
  documents: any[]
  currentDocumentId?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  selectDocument: [documentId: string]
  pageChange: [page: number]
  zoomChange: [level: number]
}>()

const currentDocument = computed(() => {
  return props.documents.find(doc => doc.id === props.currentDocumentId) || null
})

const documentType = computed(() => {
  return currentDocument.value?.type || 'unknown'
})

const currentPage = ref(1)
const totalPages = computed(() => {
  // Simulate page count based on document type
  if (documentType.value === 'pdf') return 5
  if (documentType.value === 'docx') return 3
  return 1
})

const zoomLevel = ref(100)

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    emit('pageChange', currentPage.value)
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    emit('pageChange', currentPage.value)
  }
}

const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value + 25, 200)
  emit('zoomChange', zoomLevel.value)
}

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value - 25, 50)
  emit('zoomChange', zoomLevel.value)
}

const toggleFullscreen = () => {
  // Implement fullscreen toggle
  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    const container = document.querySelector('.document-viewer') as HTMLElement
    if (container) container.requestFullscreen()
  }
}
</script>

<style scoped>
.document-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
}

.document-content {
  position: relative;
  flex: 1;
  overflow: hidden;
}

.document-render {
  transform-origin: top left;
  transition: transform 0.2s ease;
}

.pdf-viewer,
.docx-viewer,
.txt-viewer,
.generic-viewer {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.document-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .document-toolbar {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
  }
  
  .document-toolbar > div {
    order: 2;
  }
  
  .document-toolbar > span {
    order: 1;
  }
}
</style>
