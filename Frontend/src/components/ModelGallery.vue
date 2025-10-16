<template>
  <div class="flex flex-col gap-4">
    <div class="flex items-center gap-2 text-sm text-gray-400">
      <button v-for="f in filters" :key="f" @click="currentFilter=f" :class="['px-3 py-1.5 rounded-full', currentFilter===f ? 'bg-white/10 text-white' : 'hover:bg-white/5']">{{ f }}</button>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <button v-for="m in visibleModels" :key="m.key" @click="$emit('select', m)" class="group text-left p-4 rounded-2xl border border-gray-800 bg-[#0f1317] hover:border-blue-600/60 hover:shadow-[0_0_0_1px_#2563eb] transition">
        <div class="flex items-center justify-between">
          <div class="text-white font-medium">{{ m.name }}</div>
          <span class="text-xs text-gray-500">{{ m.version }}</span>
        </div>
        <p class="mt-2 text-sm text-gray-400">{{ m.desc }}</p>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const filters = ['Featured','Gemini','Images','Audio','Video']
const currentFilter = ref('Featured')

const allModels = [
  { key: 'gemini-pro', name: 'Gemini 2.5 Pro', version: 'Latest', group: 'Gemini', desc: 'Powerful reasoning model for code and complex tasks.' },
  { key: 'gemini-flash', name: 'Gemini Flash', version: 'Latest', group: 'Gemini', desc: 'Fast hybrid model with large context.' },
  { key: 'nano-banana', name: 'Nano Banana', version: 'New', group: 'Images', desc: 'State-of-the-art image generation and editing.' },
]

const visibleModels = computed(() => {
  if (currentFilter.value==='Featured') return allModels
  return allModels.filter(m => m.group===currentFilter.value)
})
</script>

<style scoped>
</style>
