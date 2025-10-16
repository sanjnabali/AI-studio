<template>
  <aside :class="['h-full border-r border-gray-800/60 bg-[#111418] text-gray-300 transition-all duration-300', collapsed ? 'w-16' : 'w-64']">
    <div class="flex items-center justify-between px-4 py-4">
      <div class="text-sm font-semibold text-white" v-if="!collapsed">AI Studio</div>
      <button class="p-2 rounded-md hover:bg-white/5" @click="$emit('toggle')">
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 12h12"/><path d="M6 6h12"/><path d="M6 18h12"/></svg>
      </button>
    </div>

    <nav class="mt-2 space-y-1">
      <button v-for="item in items" :key="item.key" @click="$emit('navigate', item.key)"
              :class="['mx-2 flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/5', active===item.key ? 'bg-white/10 text-white' : 'text-gray-300']">
        <component :is="item.icon" class="w-5 h-5" />
        <span v-if="!collapsed" class="text-sm">{{ item.label }}</span>
      </button>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import { HomeIcon, ChatBubbleLeftRightIcon, BeakerIcon, ChartBarIcon, BookOpenIcon, Cog6ToothIcon } from '@heroicons/vue/24/outline'

interface Props {
  collapsed: boolean
  active: string
}

defineProps<Props>()

const items = [
  { key: 'home', label: 'Home', icon: HomeIcon },
  { key: 'chat', label: 'Chat', icon: ChatBubbleLeftRightIcon },
  { key: 'build', label: 'Build', icon: BeakerIcon },
  { key: 'dashboard', label: 'Dashboard', icon: ChartBarIcon },
  { key: 'docs', label: 'Documentation', icon: BookOpenIcon },
  { key: 'settings', label: 'Settings', icon: Cog6ToothIcon },
]
</script>

<style scoped>
</style>
