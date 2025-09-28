// Frontend/src/main.ts - Enhanced application bootstrap
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './app.vue'
import './style.css'

// Import global components for registration
import LoadingSpinner from './components/LoadingSpinner.vue'
import DropdownMenu from './components/DropdownMenu.vue'
import Modal from './components/Modal.vue'

// Type declarations
declare global {
  interface Window {
    showNotification?: (type: 'success' | 'error' | 'warning' | 'info', message: string, timeout?: number) => void
    gtag?: (...args: any[]) => void
    monaco?: any
    fs?: {
      readFile: (path: string, options?: { encoding?: string }) => Promise<Uint8Array | string>
    }
  }
}

// Error tracking configuration
interface ErrorReport {
  message: string
  stack?: string
  url: string
  userAgent: string
  timestamp: string
  userId?: string
  sessionId: string
}

// Create Vue app
const app = createApp(App)

// Create Pinia store
const pinia = createPinia()

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global Vue Error:', err)
  console.error('Component Info:', info)
  
  // Report error
  reportError({
    message: err?.toString() || 'Unknown Vue error',
    stack: (err as Error)?.stack || '',
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString(),
    sessionId: getSessionId()
  })

  // Show user-friendly error message
  if (window.showNotification) {
    window.showNotification('error', 'An unexpected error occurred. Please refresh the page if the problem persists.')
  }
}

// Global properties
app.config.globalProperties.$apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
app.config.globalProperties.$version = import.meta.env.VITE_APP_VERSION || '1.0.0'
app.config.globalProperties.$isDev = import.meta.env.DEV

// Register global components
app.component('LoadingSpinner', LoadingSpinner)
app.component('DropdownMenu', DropdownMenu)
app.component('Modal', Modal)

// Performance monitoring
if (import.meta.env.PROD) {
  // Mark app start time
  performance.mark('app-start')
  
  // Monitor Core Web Vitals
  // @ts-ignore
  import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
    getCLS(console.log)
    getFID(console.log)
    getFCP(console.log)
    getLCP(console.log)
    getTTFB(console.log)
  }).catch(console.warn)
}

// Service Worker registration
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered:', registration)
      })
      .catch((registrationError) => {
        console.log('SW registration failed:', registrationError)
      })
  })
}

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled Promise Rejection:', event.reason)
  
  // Report error
  reportError({
    message: `Unhandled Promise Rejection: ${event.reason?.toString() || 'Unknown error'}`,
    stack: (event.reason as Error)?.stack || '',
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString(),
    sessionId: getSessionId()
  })
  
  // Prevent the default browser behavior
  event.preventDefault()
})

// Global error handler for network errors
window.addEventListener('error', (event) => {
  if (event.target !== window && event.target instanceof HTMLElement) {
    // Resource loading error
    console.error('Resource Error:', event.target.tagName, event.target)
    
    reportError({
      message: `Resource loading error: ${event.target.tagName} - ${(event.target as any).src || (event.target as any).href}`,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString(),
      sessionId: getSessionId()
    })
  }
})

const initializeApp = async () => {
  try {
    console.log('Initializing AI Studio...')

    console.log('🔍 Starting browser compatibility check...')
    checkBrowserCompatibility()
    console.log('✅ Browser compatibility check passed')

    console.log('🎨 Starting theme initialization...')
    initializeTheme()
    console.log('✅ Theme initialization complete')

    console.log('📁 Starting file system initialization...')
    initializeFileSystem()
    console.log('✅ File system initialization complete')

    console.log('⚙️ Starting environment config load...')
    await loadEnvironmentConfig()
    console.log('✅ Environment config loaded')

    if (import.meta.env.PROD) {
      console.log('📊 Starting analytics initialization...')
      initializeAnalytics()
      console.log('✅ Analytics initialized')
    }

    console.log('AI Studio initialization complete')
    
  } catch (error) {
    console.error('❌ Failed to initialize AI Studio at step:', error)
    
    // Show fallback error message
    const errorDiv = document.createElement('div')
    errorDiv.innerHTML = `
      <div style="position: fixed; inset: 0; background: white; display: flex; align-items: center; justify-content: center; z-index: 9999;">
        <div style="text-align: center; padding: 2rem;">
          <h1 style="color: #dc2626; font-size: 1.5rem; margin-bottom: 1rem;">AI Studio Failed to Load</h1>
          <p style="color: #6b7280; margin-bottom: 1rem;">There was an error initializing the application.</p>
          <button onclick="window.location.reload()" style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border: none; border-radius: 0.375rem; cursor: pointer;">
            Reload Page
          </button>
        </div>
      </div>
    `
    document.body.appendChild(errorDiv)
  }
}

const checkBrowserCompatibility = () => {
  // Check window properties
  const windowFeatures = ['Promise', 'fetch', 'localStorage']
  const missingWindowFeatures = windowFeatures.filter(feature => !(feature in window))
  
  // Check document methods
  const documentMethods = ['querySelector', 'addEventListener']
  const missingDocumentFeatures = documentMethods.filter(method => {
    const docMethod = (document as any)[method]
    return typeof docMethod !== 'function'
  })
  
  const unsupportedFeatures = [...missingWindowFeatures, ...missingDocumentFeatures]
  
  if (unsupportedFeatures.length > 0) {
    console.warn(`⚠️ Browser compatibility warning: Missing features: ${unsupportedFeatures.join(', ')}`)
    // Don't throw in dev; log and continue
    if (import.meta.env.PROD) {
      throw new Error(`Browser not supported. Missing features: ${unsupportedFeatures.join(', ')}`)
    }
  }
  
  // Check for modern browser features with error handling
  const modernFeatures: Record<string, boolean> = {}
  try {
    modernFeatures['ES6 Modules'] = 'noModule' in HTMLScriptElement.prototype
  } catch (e) {
    console.warn('ES6 Modules check failed:', e)
    modernFeatures['ES6 Modules'] = false
  }
  
  try {
    modernFeatures['CSS Grid'] = CSS.supports('display', 'grid')
  } catch (e) {
    console.warn('CSS Grid check failed:', e)
    modernFeatures['CSS Grid'] = false
  }
  
  try {
    modernFeatures['WebGL'] = !!document.createElement('canvas').getContext('webgl')
  } catch (e) {
    console.warn('WebGL check failed:', e)
    modernFeatures['WebGL'] = false
  }
  
  console.log('🔍 Browser Feature Check:', modernFeatures)
}

// Theme initialization
const initializeTheme = () => {
  const savedTheme = localStorage.getItem('ai-studio-ui-settings')
  let theme = 'dark' // Default theme
  
  if (savedTheme) {
    try {
      const settings = JSON.parse(savedTheme)
      theme = settings.theme || 'dark'
    } catch (error) {
      console.warn('Failed to parse saved theme settings:', error)
    }
  }
  
  // Apply theme immediately to prevent flash
  if (theme === 'auto') {
    theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  
  document.documentElement.classList.add(theme)
  document.documentElement.setAttribute('data-theme', theme)
  
  console.log(`Initial theme applied: ${theme}`)
}

// File system API initialization
const initializeFileSystem = () => {
  if ('showOpenFilePicker' in window) {
    // Native File System API is available
    window.fs = {
      readFile: async (path: string, options = {}) => {
        // Implement file reading using File System Access API
        throw new Error('File System Access API implementation needed')
      }
    }
    console.log('File System Access API available')
  } else {
    // Fallback for older browsers
    window.fs = {
      readFile: async (path: string, options = {}) => {
        throw new Error('File System Access API not available')
      }
    }
    console.log('File System Access API not available, using fallback')
  }
}

// Environment configuration
const loadEnvironmentConfig = async () => {
  try {
    // Load configuration from API or environment
    const config = {
      apiUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
      version: import.meta.env.VITE_APP_VERSION || '1.0.0',
      environment: import.meta.env.MODE,
      features: {
        codeExecution: import.meta.env.VITE_ENABLE_CODE_EXECUTION !== 'false',
        voiceInput: import.meta.env.VITE_ENABLE_VOICE_INPUT !== 'false',
        imageGeneration: import.meta.env.VITE_ENABLE_IMAGE_GENERATION !== 'false',
        rag: import.meta.env.VITE_ENABLE_RAG !== 'false'
      }
    }
    
    // Store config globally
    app.config.globalProperties.$config = config
    
    console.log('Environment configuration loaded:', config)
  } catch (error) {
    console.warn('Failed to load environment configuration:', error)
  }
}

// Analytics initialization
const initializeAnalytics = () => {
  const trackingId = import.meta.env.VITE_GA_TRACKING_ID
  
  if (trackingId) {
    // Load Google Analytics
    const script = document.createElement('script')
    script.src = `https://www.googletagmanager.com/gtag/js?id=${trackingId}`
    script.async = true
    document.head.appendChild(script)
    
    script.onload = () => {
      window.gtag = function() {
        (window as any).dataLayer = (window as any).dataLayer || []
        ;(window as any).dataLayer.push(arguments)
      }
      
      window.gtag('js', new Date())
      window.gtag('config', trackingId, {
        page_title: 'AI Studio',
        custom_map: { 'custom_parameter': 'value' }
      })
      
      console.log('✅ Analytics initialized')
    }
  }
}

// Error reporting
const reportError = (error: ErrorReport) => {
  if (import.meta.env.DEV) {
    console.log('Error Report (DEV):', error)
    return
  }
  
  // In production, send to error tracking service
  try {
    fetch('/api/errors', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(error)
    }).catch(() => {
      // Fallback: log to console if error reporting fails
      console.error('Failed to report error to server:', error)
    })
  } catch (reportingError) {
    console.error('Error reporting system failed:', reportingError)
  }
}

// Session ID generation
const getSessionId = (): string => {
  let sessionId = sessionStorage.getItem('ai-studio-session-id')
  
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    sessionStorage.setItem('ai-studio-session-id', sessionId)
  }
  
  return sessionId
}

// Register plugins
app.use(pinia)
app.use(router)

// Initialize and mount app
initializeApp().then(() => {
  app.mount('#app')
  
  // Mark app as fully loaded
  if (import.meta.env.PROD && 'performance' in window) {
    performance.mark('app-ready')
    performance.measure('app-load-time', 'app-start', 'app-ready')
    
    const measure = performance.getEntriesByName('app-load-time')[0]
    console.log(`App load time: ${measure.duration.toFixed(2)}ms`)
  }
  
  console.log('🎉 AI Studio mounted successfully!')
}).catch((error) => {
  console.error('Failed to mount AI Studio:', error)
})

// Hot Module Replacement (HMR) for development
if (import.meta.hot) {
  import.meta.hot.accept()
}

