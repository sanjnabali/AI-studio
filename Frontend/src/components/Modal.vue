<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click="closeOnBackdrop && $emit('close')">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">{{ title }}</h3>
            <button @click="$emit('close')" class="modal-close">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          <div class="modal-body">
            <slot />
          </div>
          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { XMarkIcon } from '@heroicons/vue/24/outline'

interface Props {
  isOpen: boolean
  title: string
  closeOnBackdrop?: boolean
}

const props = defineProps<Props>()

defineEmits<{
  close: []
}>()
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 106, 26, 0.1);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-content {
  background: rgba(255, 244, 232, 0.85);
  border: 1px solid #ffd6b5;
  border-radius: 1rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(255, 106, 26, 0.12);
  backdrop-filter: blur(12px);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #ffd6b5;
  background: rgba(255, 214, 181, 0.3);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #b34713;
  text-shadow: 0 1px 4px rgba(255, 106, 26, 0.1);
}

.modal-close {
  color: #b34713;
  transition: color 0.2s;
}

.modal-close:hover {
  color: #ff6a1a;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #ffd6b5;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  background: rgba(255, 214, 181, 0.3);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.95);
}
</style>
