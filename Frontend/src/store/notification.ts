// Frontend/src/store/notifications.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  duration?: number // 0 = persistent
  action?: {
    label: string
    handler: () => void
  }
  timestamp: Date
}

export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref<Notification[]>([])
  const maxNotifications = 5

  const add = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newNotification: Notification = {
      id,
      timestamp: new Date(),
      duration: notification.duration ?? 5000,
      ...notification
    }

    notifications.value.unshift(newNotification)

    // Limit number of notifications
    if (notifications.value.length > maxNotifications) {
      notifications.value = notifications.value.slice(0, maxNotifications)
    }

    // Auto-remove if duration is set
    if (newNotification.duration && newNotification.duration > 0) {
      setTimeout(() => {
        remove(id)
      }, newNotification.duration)
    }

    return id
  }

  const remove = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clear = () => {
    notifications.value = []
  }

  // Convenience methods
  const success = (message: string, options?: Partial<Notification>) => {
    return add({ type: 'success', message, ...options })
  }

  const error = (message: string, options?: Partial<Notification>) => {
    return add({ type: 'error', message, duration: 0, ...options })
  }

  const warning = (message: string, options?: Partial<Notification>) => {
    return add({ type: 'warning', message, ...options })
  }

  const info = (message: string, options?: Partial<Notification>) => {
    return add({ type: 'info', message, ...options })
  }

  return {
    notifications,
    add,
    remove,
    clear,
    success,
    error,
    warning,
    info
  }
})