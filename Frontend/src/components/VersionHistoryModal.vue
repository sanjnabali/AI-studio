<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden">
      <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          Version History ({{ versions.length }})
        </h3>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <div class="overflow-y-auto max-h-[calc(80vh-100px)]">
        <div v-if="versions.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
          No versions saved yet. Create your first version to start tracking changes.
        </div>
        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
          <div
            v-for="(version, index) in versions"
            :key="version.id"
            class="p-6 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                  <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="text-sm font-medium text-gray-900 dark:text-white">
                    Version {{ versions.length - index }}
                  </h4>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    {{ new Date(version.timestamp).toLocaleString() }}
                  </p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-xs text-gray-500 dark:text-gray-400">
                  {{ getFileCount(version.files) }} files
                </span>
                <button
                  @click="$emit('restore', version)"
                  class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded-lg transition-colors"
                >
                  Restore
                </button>
              </div>
            </div>

            <div v-if="version.message" class="text-sm text-gray-600 dark:text-gray-300 mb-3">
              {{ version.message }}
            </div>

            <div class="grid grid-cols-3 gap-4 text-sm">
              <div
                v-for="(file, fileIndex) in version.files.slice(0, 3)"
                :key="fileIndex"
                class="p-2 bg-gray-100 dark:bg-gray-700 rounded text-xs truncate"
              >
                {{ file.name }}
              </div>
              <div v-if="version.files.length > 3" class="p-2 bg-gray-100 dark:bg-gray-700 rounded text-xs text-gray-500 dark:text-gray-400">
                +{{ version.files.length - 3 }} more files
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  versions: any[]
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  restore: [version: any]
}>()

const getFileCount = (files: any[]) => {
  return files.length
}
</script>
