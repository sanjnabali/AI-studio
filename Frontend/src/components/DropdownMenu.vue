<template>
  <div class="dropdown-menu" ref="dropdownRef">
    <button
      @click="toggle"
      class="dropdown-trigger"
      :class="{ 'dropdown-trigger--open': isOpen }"
    >
      <slot name="trigger" />
    </button>

    <Transition name="dropdown">
      <div
        v-if="isOpen"
        class="dropdown-content"
        :class="position"
      >
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Props {
  position?: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right'
}

const props = defineProps<Props>()

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement>()

const toggle = () => {
  isOpen.value = !isOpen.value
}

const close = () => {
  isOpen.value = false
}

const handleClickOutside = (event: Event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.dropdown-menu {
  position: relative;
  display: inline-block;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  color: #374151;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.dropdown-trigger:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.dropdown-trigger--open {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.dropdown-content {
  position: absolute;
  z-index: 50;
  margin-top: 0.25rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  min-width: 12rem;
  padding: 0.25rem 0;
}

.dropdown-content.bottom-left {
  left: 0;
  top: 100%;
}

.dropdown-content.bottom-right {
  right: 0;
  top: 100%;
}

.dropdown-content.top-left {
  left: 0;
  bottom: 100%;
}

.dropdown-content.top-right {
  right: 0;
  bottom: 100%;
}

/* Transitions */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-0.5rem);
}
</style>
