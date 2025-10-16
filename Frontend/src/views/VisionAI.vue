<template>
  <div class="h-screen bg-[#0D1117] text-[#E6EDF3] grid" :class="collapsed ? 'grid-rows-[56px_1fr]' : 'grid-rows-[56px_1fr]'">
    <header class="h-14 border-b border-[#30363D] flex items-center justify-between px-4">
      <div class="text-[#00AEEF] font-semibold">Vision AI</div>
      <UserMenu />
    </header>

    <div class="grid" :class="collapsed ? 'grid-cols-[64px_1fr]' : 'grid-cols-[256px_1fr]'">
      <SidebarNav :collapsed="collapsed" active="vision" @toggle="collapsed=!collapsed" @navigate="onNavigate" />
      <main class="min-h-0 overflow-hidden p-4 space-y-4">
        <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
          <div class="text-sm font-semibold mb-2">Image Analysis</div>
          <FileUploadZone @upload="onUpload" />
        </div>
        <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4">
          <div class="text-sm text-gray-400">Results</div>
          <pre class="text-xs mt-2">{{ result }}</pre>
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
import FileUploadZone from '@/components/FileUploadZone.vue'
import { apiClient } from '@/api/client'

const collapsed = ref(false)
const router = useRouter()
const result = ref('')

const onNavigate = (key: string) => {
  const map: Record<string,string> = { chat: '/playground', build: '/code-canvas', docs: '/rag', settings: '/settings' }
  router.push(map[key] || '/')
}

const onUpload = async (files: FileList) => {
  const file = files.item(0)
  if (!file) return
  const res = await apiClient.uploadImage(file)
  result.value = JSON.stringify(res, null, 2)
}
</script>

<style scoped></style>
