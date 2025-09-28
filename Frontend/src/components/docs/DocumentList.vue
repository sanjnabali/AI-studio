<template>
  <div class="document-list">
    <h3 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Documents</h3>
    <div class="space-y-1">
      <!-- Placeholder for documents -->
      <div v-for="doc in documents" :key="doc.id" class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
        {{ doc.filename }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  documents: any[]
}

defineProps<Props>()

defineEmits<{
  select: [document: any]
  delete: [documentId: number]
}>()
</script>

<style scoped>
.document-list {
  /* Styles */
}
</style>
