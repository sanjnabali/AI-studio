// src/main.ts - Updated
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './app.vue'
import router from './router'
import { useAuthStore } from './store/auth'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err)
  console.error('Component info:', info)
  // You could send this to a logging service
}

app.mount('#app')

// Service Worker registration (optional)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  navigator.serviceWorker.register('/sw.js').catch((error) => {
    console.log('SW registration failed:', error)
  })
}

// Handle auth token expiration globally
window.addEventListener('auth-expired', () => {
  // This will be triggered by the API client when a 401 is received
  const authStore = useAuthStore()
  authStore.logout()
  router.push('/auth')
})