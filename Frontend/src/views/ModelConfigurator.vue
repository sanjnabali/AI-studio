<template>
  <div class="h-screen bg-[#0D1117] text-[#E6EDF3] grid" :class="collapsed ? 'grid-rows-[56px_1fr]' : 'grid-rows-[56px_1fr]'">
    <header class="h-14 border-b border-[#30363D] flex items-center justify-between px-4">
      <div class="text-[#00AEEF] font-semibold">Model Configurator</div>
      <UserMenu />
    </header>

    <div class="grid" :class="collapsed ? 'grid-cols-[64px_1fr]' : 'grid-cols-[256px_1fr]'">
      <SidebarNav :collapsed="collapsed" active="config" @toggle="collapsed=!collapsed" @navigate="onNavigate" />
      <main class="min-h-0 overflow-auto p-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
          <div class="text-sm font-semibold mb-3">Parameters</div>
          <div class="space-y-4">
            <div>
              <label class="text-xs text-gray-400">Model</label>
              <select v-model="model" class="mt-1 w-full bg-[#0D1117] border border-[#30363D] rounded-lg p-2 text-sm">
                <option value="chat">DialoGPT Medium</option>
                <option value="code">CodeGPT Small</option>
                <option value="summarizer">BART Large CNN</option>
              </select>
            </div>
            <div>
              <div class="flex items-center justify-between text-xs text-gray-400"><span>Temperature</span><span>{{ temperature.toFixed(2) }}</span></div>
              <input v-model.number="temperature" type="range" min="0" max="2" step="0.01" class="w-full" />
            </div>
            <div>
              <div class="flex items-center justify-between text-xs text-gray-400"><span>Top-p</span><span>{{ topP.toFixed(2) }}</span></div>
              <input v-model.number="topP" type="range" min="0" max="1" step="0.01" class="w-full" />
            </div>
            <div>
              <div class="flex items-center justify-between text-xs text-gray-400"><span>Max tokens</span><span>{{ maxTokens }}</span></div>
              <input v-model.number="maxTokens" type="range" min="50" max="4000" step="50" class="w-full" />
            </div>
            <button class="px-3 py-2 bg-[#00C853] rounded-lg text-black font-medium" @click="save">Save Preset</button>
          </div>
        </div>
        <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
          <div class="text-sm font-semibold mb-3">Current Preset</div>
          <pre class="text-xs whitespace-pre-wrap">{{ preset }}</pre>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import SidebarNav from '@/components/layout/SidebarNav.vue'
import UserMenu from '@/components/UserMenu.vue'

const collapsed = ref(false)
const router = useRouter()

const model = ref('chat')
const temperature = ref(1.0)
const topP = ref(0.9)
const maxTokens = ref(1000)
const preset = ref('{}')

const save = () => {
  preset.value = JSON.stringify({ model: model.value, temperature: temperature.value, top_p: topP.value, max_tokens: maxTokens.value }, null, 2)
}

const onNavigate = (key: string) => {
  const map: Record<string,string> = { chat: '/playground', build: '/code-canvas', docs: '/rag', settings: '/settings' }
  router.push(map[key] || '/')
}
</script>

<style scoped></style>
