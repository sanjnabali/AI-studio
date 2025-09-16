// src/main.ts - Fixed Version
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './app.vue'  // Fixed: Capital 'A' in App.vue
import router from './router'
import { useAuthStore } from './store/auth'

// Import CSS
import './style.css'

const app = createApp(App)
const pinia = createPinia()

// Use plugins
app.use(pinia)
app.use(router)

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err)
  console.error('Vue component info:', info)
  
  // Send to logging service in production
  if (import.meta.env.PROD) {
    // TODO: Send to logging service
  }
}

// Global properties
app.config.globalProperties.$appName = 'AI Studio'
app.config.globalProperties.$version = '1.0.0'

// Mount app
app.mount('#app')

// Initialize auth after app is mounted
const authStore = useAuthStore()
authStore.initializeAuth()

// Service Worker registration (optional, for PWA)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration)
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}


declare global {
  interface Window {
    gtag: (...args: any[]) => void;
  }
}


// Global event handlers
window.addEventListener('auth-expired', () => {
  console.log('Auth token expired, redirecting to login')
  const authStore = useAuthStore()
  authStore.logout()
  router.push('/auth')
})

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', event => {
  console.error('Unhandled promise rejection:', event.reason)
  event.preventDefault()
})

// Debug info in development
if (import.meta.env.DEV) {
  console.log('🚀 AI Studio started in development mode')
  console.log('📊 Vue version:', app.version)
  console.log('🔗 API URL:', import.meta.env.VITE_API_BASE_URL)
}