<template>
  <aside class="h-full w-80 border-l border-gray-800/60 bg-[#0f1317] text-gray-300 p-4 hidden xl:flex xl:flex-col">
    <div class="text-sm font-medium text-gray-400 mb-3">Run settings</div>
    <div class="space-y-4">
      <div>
        <label class="text-xs text-gray-400">System instructions</label>
        <textarea v-model="sys" rows="4" placeholder="Optional tone and style instructions..."
                  class="mt-1 w-full bg-[#12171c] border border-gray-700 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500"></textarea>
      </div>
      <div class="flex items-center justify-between">
        <span class="text-xs text-gray-400">Temperature</span>
        <span class="text-xs text-gray-400">{{ temperature.toFixed(1) }}</span>
      </div>
      <input type="range" v-model.number="temperature" min="0" max="2" step="0.1" class="w-full" />
      <div>
        <label class="text-xs text-gray-400">Aspect ratio</label>
        <select v-model="aspect" class="mt-1 w-full bg-[#12171c] border border-gray-700 rounded-lg p-2 text-sm">
          <option>Auto</option>
          <option>1:1</option>
          <option>16:9</option>
          <option>9:16</option>
        </select>
      </div>
      <div class="flex items-center justify-between text-xs text-gray-400">
        <span>Advanced settings</span>
        <button class="px-2 py-1 rounded-md hover:bg-white/5">Show</button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const temperature = defineModel<number>('temperature', { default: 1.0 })
const sys = defineModel<string>('system', { default: '' })
const aspect = ref('Auto')
</script>

<style scoped>
</style>
