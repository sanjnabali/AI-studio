<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Version Control</h2>
        <button
          @click="$emit('close')"
          class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded"
        >
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>

      <div class="p-6">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Commit Message
            </label>
            <textarea
              v-model="commitMessage"
              rows="3"
              class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="Describe your changes..."
            ></textarea>
          </div>

          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-700 dark:text-gray-300">Auto-commit on save</span>
            <input type="checkbox" v-model="autoCommit" class="rounded" />
          </div>
        </div>

        <!-- Version History -->
        <div class="mt-6">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Version History</h3>
          <div class="space-y-3 max-h-60 overflow-y-auto">
            <div
              v-for="version in versions"
              :key="version.id"
              class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="font-medium text-gray-900 dark:text-white">{{ version.message }}</span>
                <button
                  @click="$emit('restore', version.id)"
                  class="px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded hover:bg-blue-200 dark:hover:bg-blue-800"
                >
                  Restore
                </button>
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatDate(version.timestamp) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          Cancel
        </button>
        <button
          @click="handleCommit"
          :disabled="!commitMessage.trim()"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          Commit Changes
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

interface Props {
  versions: any[]
}

const props = defineProps<Props>()

defineEmits<{
  close: []
  commit: [message: string]
  restore: [versionId: string]
}>()

const commitMessage = ref('')
const autoCommit = ref(false)

const handleCommit = () => {
  if (commitMessage.value.trim()) {
    // emit commit event
    commitMessage.value = ''
  }
}

const formatDate = (timestamp: string) => {
  return new Date(timestamp).toLocaleString()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}
</style>
