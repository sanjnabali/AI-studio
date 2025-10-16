<template>
  <div class="loading-spinner" :class="{ 'inline': inline }">
    <div class="spinner" :style="{ width: size, height: size }"></div>
    <span v-if="text" class="spinner-text">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: string
  text?: string
  inline?: boolean
}

defineProps<Props>()
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.loading-spinner.inline {
  flex-direction: row;
  display: inline-flex;
}

.spinner {
  border: 2px solid rgba(255, 214, 181, 0.5);
  border-top: 2px solid #ff6a1a;
  border-radius: 50%;
  filter: drop-shadow(0 0 8px rgba(255, 106, 26, 0.2));
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.spinner-text {
  font-size: 0.875rem;
  color: #b34713;
  text-shadow: 0 1px 4px rgba(255, 106, 26, 0.1);
}
</style>
