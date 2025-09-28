<template>
  <div class="session-list">
    <h3 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Chat Sessions</h3>
    <div class="space-y-1">
      <!-- Placeholder for sessions -->
      <div v-for="session in sessions" :key="session.id" class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
        {{ session.name }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  sessions: any[]
  currentSession: any
}

defineProps<Props>()

defineEmits<{
  select: [sessionId: number]
  delete: [sessionId: number]
}>()
</script>

<style scoped>
.session-list {
  /* Styles */
}
</style>
