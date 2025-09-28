<template>
  <div class="project-list">
    <h3 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Code Projects</h3>
    <div class="space-y-1">
      <!-- Placeholder for projects -->
      <div v-for="project in projects" :key="project.id" class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
        {{ project.name }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  projects: any[]
  currentProject: any
}

defineProps<Props>()

defineEmits<{
  select: [project: any]
  delete: [projectId: string]
}>()
</script>

<style scoped>
.project-list {
  /* Styles */
}
</style>
