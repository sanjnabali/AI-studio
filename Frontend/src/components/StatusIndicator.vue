<template>
  <div class="status-indicator flex items-center space-x-2">
    <div
      :class="[
        'w-2 h-2 rounded-full',
        status === 'connected' ? 'bg-green-500' :
        status === 'connecting' ? 'bg-yellow-500' :
        'bg-red-500'
      ]"
    ></div>
    <span class="text-xs text-gray-500 dark:text-gray-400 capitalize">{{ status }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  status: 'connected' | 'connecting' | 'disconnected'
}

defineProps<Props>()
</script>

<style scoped>
.status-indicator {
  /* Styles */
}
</style>
