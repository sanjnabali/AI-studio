<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Settings</h2>
        <button
          @click="$emit('close')"
          class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded"
        >
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>

      <div class="p-6 space-y-6">
        <!-- Model Settings -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">AI Model</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Model
              </label>
              <select class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option>GPT-4</option>
                <option>GPT-3.5</option>
                <option>Claude</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Temperature
              </label>
              <input type="range" min="0" max="2" step="0.1" class="w-full" />
            </div>
          </div>
        </div>

        <!-- Code Settings -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Code Editor</h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">Auto-save</span>
              <input type="checkbox" class="rounded" />
            </div>

            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">Line numbers</span>
              <input type="checkbox" checked class="rounded" />
            </div>

            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">Word wrap</span>
              <input type="checkbox" class="rounded" />
            </div>
          </div>
        </div>

        <!-- Theme -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Appearance</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Theme
              </label>
              <select class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option>Light</option>
                <option>Dark</option>
                <option>System</option>
              </select>
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
          @click="$emit('update', {})"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Save Changes
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { XMarkIcon } from '@heroicons/vue/24/outline'

defineEmits<{
  close: []
  update: [settings: any]
}>()
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
