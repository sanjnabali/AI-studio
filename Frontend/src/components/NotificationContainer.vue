<template>
  <div class="notification-container">
    <TransitionGroup name="notification" tag="div">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'notification',
          `notification-${notification.type}`
        ]"
      >
        <div class="notification-content">
          <div class="notification-icon">
            <CheckCircleIcon v-if="notification.type === 'success'" class="w-5 h-5" />
            <ExclamationTriangleIcon v-else-if="notification.type === 'warning'" class="w-5 h-5" />
            <XCircleIcon v-else-if="notification.type === 'error'" class="w-5 h-5" />
            <InformationCircleIcon v-else class="w-5 h-5" />
          </div>
          <div class="notification-text">
            <p class="notification-title">{{ notification.title }}</p>
            <p v-if="notification.message" class="notification-message">{{ notification.message }}</p>
          </div>
        </div>
        <button @click="remove(notification.id)" class="notification-close">
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useNotificationStore } from '@/store/notification'
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const notificationStore = useNotificationStore()

const notifications = computed(() => notificationStore.notifications)

const remove = (id: string) => {
  notificationStore.remove(id)
}
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  max-width: 400px;
}

.notification {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border-left: 4px solid;
}

.notification-success {
  background: white;
  border-left-color: #10b981;
}

.notification-warning {
  background: white;
  border-left-color: #f59e0b;
}

.notification-error {
  background: white;
  border-left-color: #ef4444;
}

.notification-info {
  background: white;
  border-left-color: #3b82f6;
}

.notification-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  flex: 1;
}

.notification-icon {
  flex-shrink: 0;
}

.notification-success .notification-icon {
  color: #10b981;
}

.notification-warning .notification-icon {
  color: #f59e0b;
}

.notification-error .notification-icon {
  color: #ef4444;
}

.notification-info .notification-icon {
  color: #3b82f6;
}

.notification-text {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  font-size: 0.875rem;
  color: #111827;
  margin: 0;
}

.notification-message {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0.25rem 0 0 0;
}

.notification-close {
  flex-shrink: 0;
  color: #6b7280;
  padding: 0.125rem;
  border-radius: 0.25rem;
}

.notification-close:hover {
  color: #374151;
  background: #f3f4f6;
}

/* Transitions */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notification-move {
  transition: transform 0.3s ease;
}
</style>
