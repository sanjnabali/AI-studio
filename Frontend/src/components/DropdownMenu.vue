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
import { ref, onMounted, onUnmounted, defineComponent } from 'vue'



interface Props {
  position?: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right'
}

const props = withDefaults(defineProps<Props>(), {
  position: 'bottom-left'
})

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
  border: 1px solid #ffd6b5;
  border-radius: 0.75rem;
  background: rgba(255, 244, 232, 0.7);
  color: #b34713;
  font-size: 0.875rem;
  box-shadow: 0 2px 8px #ffd6b5;
  backdrop-filter: blur(8px);
  transition: all 0.2s;
}

.dropdown-trigger:hover {
  background: rgba(255, 214, 181, 0.3);
  border-color: #ff6a1a;
}

.dropdown-trigger--open {
  border-color: #ff6a1a;
  box-shadow: 0 0 0 3px rgba(255, 106, 26, 0.1);
}

.dropdown-content {
  position: absolute;
  z-index: 50;
  margin-top: 0.25rem;
  background: rgba(255, 244, 232, 0.85);
  border: 1px solid #ffd6b5;
  border-radius: 0.75rem;
  box-shadow: 0 8px 32px rgba(255, 106, 26, 0.12);
  backdrop-filter: blur(12px);
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
