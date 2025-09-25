// Frontend/src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './app.vue'
import './style.css'

// Extend Window interface to include showNotification
declare global {
  interface Window {
    showNotification?: (type: 'success' | 'error' | 'warning' | 'info', message: string, timeout?: number) => void;
  }
}

// Create Vue app
const app = createApp(App)

// Add global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error handler:', err, info)

  // Show user-friendly error message
  if (window.showNotification) {
    window.showNotification('error', 'An unexpected error occurred')
  }
}

// Configure global properties
app.config.globalProperties.$apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Use plugins
app.use(createPinia())
app.use(router)

// Mount app
app.mount('#app')


