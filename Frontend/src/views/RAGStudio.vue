<template>
  <div class="h-screen bg-[#0D1117] text-[#E6EDF3] grid" :class="collapsed ? 'grid-rows-[56px_1fr]' : 'grid-rows-[56px_1fr]'">
    <header class="h-14 border-b border-[#30363D] flex items-center justify-between px-4">
      <div class="flex items-center gap-3">
        <div class="text-[#00AEEF] font-semibold">RAG Studio</div>
      </div>
      <div class="flex items-center gap-2">
        <UserMenu />
      </div>
    </header>

    <div class="grid" :class="collapsed ? 'grid-cols-[64px_1fr_420px]' : 'grid-cols-[256px_1fr_420px]'">
      <SidebarNav :collapsed="collapsed" active="docs" @toggle="collapsed=!collapsed" @navigate="onNavigate" />
      <main class="min-h-0 overflow-hidden grid grid-cols-2 gap-4 p-4">
        <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4 flex flex-col">
          <h3 class="text-sm font-semibold mb-2">Documents</h3>
          <FileUploadZone class="mb-3" @upload="handleFileUpload" />
          <DocumentList :documents="documents" @select="selectDocument" @delete="deleteDocument" class="flex-1 overflow-auto" />
        </div>
        <div class="bg-[#161B22] border border-[#30363D] rounded-xl p-4 flex flex-col">
          <h3 class="text-sm font-semibold mb-2">Preview & Query</h3>
          <DocumentViewer :documents="selectedDocument ? [selectedDocument] : []" :current-document-id="selectedDocument?.id" class="flex-1 overflow-auto" />
          <div class="mt-3 flex items-center gap-2">
            <input v-model="query" class="flex-1 bg-[#0D1117] border border-[#30363D] rounded-lg p-2 text-sm" placeholder="Ask about the document..." />
            <button class="px-3 py-2 bg-[#00AEEF] rounded-lg" @click="runQuery">Run</button>
          </div>
        </div>
      </main>
      <aside class="h-full p-4 border-l border-[#30363D] bg-[#0D1117] hidden xl:block">
        <div class="text-sm text-gray-400 mb-2">Vector Stats</div>
        <div class="text-xs text-gray-500">Coming soon</div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import SidebarNav from '@/components/layout/SidebarNav.vue'
import UserMenu from '@/components/UserMenu.vue'
import FileUploadZone from '@/components/FileUploadZone.vue'
import DocumentList from '@/components/docs/DocumentList.vue'
import DocumentViewer from '@/components/docs/DocumentViewer.vue'
import { apiClient } from '@/api/client'

const router = useRouter()
const collapsed = ref(false)
const documents = ref<any[]>([])
const selectedDocument = ref<any>(null)
const query = ref('')

const onNavigate = (key: string) => {
  const map: Record<string,string> = { chat: '/playground', docs: '/rag', build: '/code-canvas', settings: '/settings' }
  router.push(map[key] || '/')
}

const handleFileUpload = async (files: FileList) => {
  for (const f of Array.from(files)) {
    await apiClient.uploadDocument(f)
  }
  documents.value = await apiClient.getDocuments()
}

const selectDocument = (doc: any) => { selectedDocument.value = doc }
const deleteDocument = async (id: number) => { await apiClient.deleteDocument(id); documents.value = await apiClient.getDocuments() }
const runQuery = async () => {
  if (!query.value) return
  await apiClient.queryDocuments(query.value, selectedDocument.value ? [selectedDocument.value.filename] : undefined)
}
</script>

<style scoped></style>
