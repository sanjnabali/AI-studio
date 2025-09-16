// src/router/index.ts - Fixed Version
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../store/auth'

// Lazy load components with proper error handling
const Studio = () => import('../views/Studio.vue').catch(err => {
  console.error('Failed to load Studio component:', err)
  return import('../views/fallback/ComponentError.vue')
})

const Templates = () => import('../views/Templates.vue').catch(err => {
  console.error('Failed to load Templates component:', err)
  return import('../views/fallback/ComponentError.vue')
})

const Settings = () => import('../views/Settings.vue').catch(err => {
  console.error('Failed to load Settings component:', err)
  return import('../views/fallback/ComponentError.vue')
})

const Auth = () => import('../views/auth.vue').catch(err => {
  console.error('Failed to load Auth component:', err)
  return import('../views/fallback/ComponentError.vue')
})

// Fallback component for errors
const ComponentError = () => import('../views/fallback/ComponentError.vue')

const routes: Array<RouteRecordRaw> = [
  {
    path: '/auth',
    name: 'auth',
    component: Auth,
    meta: { 
      requiresGuest: true,
      title: 'Sign In - AI Studio',
      description: 'Sign in to your AI Studio account'
    }
  },
  {
    path: '/',
    name: 'studio',
    component: Studio,
    meta: { 
      requiresAuth: true,
      title: 'AI Studio - Your AI Workspace',
      description: 'Multimodal AI workspace for coding, analysis, and creative writing'
    }
  },
  {
    path: '/templates',
    name: 'templates', 
    component: Templates,
    meta: { 
      requiresAuth: true,
      title: 'Templates - AI Studio',
      description: 'Pre-built templates to get you started quickly'
    }
  },
  {
    path: '/settings',
    name: 'settings',
    component: Settings,
    meta: { 
      requiresAuth: true,
      title: 'Settings - AI Studio',
      description: 'Manage your account and application preferences'
    }
  },
  // Error routes
  {
    path: '/error',
    name: 'error',
    component: ComponentError,
    props: route => ({ 
      error: route.query.error || 'An error occurred',
      code: route.query.code || '500'
    }),
    meta: {
      title: 'Error - AI Studio'
    }
  },
  // Redirect old routes
  {
    path: '/login',
    redirect: '/auth'
  },
  {
    path: '/register',
    redirect: '/auth'
  },
  {
    path: '/home',
    redirect: '/'
  },
  // Catch-all route for 404s
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/fallback/NotFound.vue').catch(() => ComponentError),
    meta: {
      title: 'Page Not Found - AI Studio'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Return to saved position if available (back/forward)
    if (savedPosition) {
      return savedPosition
    }
    // Scroll to anchor if present
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    // Otherwise scroll to top
    return { top: 0, behavior: 'smooth' }
  }
})

// Global navigation guards
router.beforeEach(async (to, from) => {
  console.log(`🧭 Navigating from ${from.path} to ${to.path}`)

  // Prevent navigation loops
  if (to.path === from.path) {
    console.warn('⚠️ Navigation loop detected, aborting')
    return false
  }

  try {
    const authStore = useAuthStore()

    // Initialize auth store if not already done
    if (!authStore.user && !authStore.isLoading) {
      console.log('🔐 Initializing auth store...')
      await authStore.initializeAuth()
    }

    // Set page title and meta
    if (to.meta.title) {
      document.title = to.meta.title as string
    }

    if (to.meta.description) {
      let metaDescription = document.querySelector('meta[name="description"]')
      if (!metaDescription) {
        metaDescription = document.createElement('meta')
        metaDescription.setAttribute('name', 'description')
        document.head.appendChild(metaDescription)
      }
      metaDescription.setAttribute('content', to.meta.description as string)
    }

    // Check authentication requirements
    if (to.meta.requiresAuth) {
      console.log('🔒 Route requires authentication')
      console.log('Current auth state:', {
        isAuthenticated: authStore.isAuthenticated,
        user: !!authStore.user,
        token: !!authStore.token,
        loading: authStore.isLoading,
        localStorage: {
          token: !!localStorage.getItem('auth_token'),
          user: !!localStorage.getItem('user_data')
        }
      })

      // Check both store and localStorage
      const hasToken = !!authStore.token || !!localStorage.getItem('auth_token')
      const hasUser = !!authStore.user || !!localStorage.getItem('user_data')

      if (!hasToken || !hasUser) {
        console.log('❌ User not authenticated')

        // Try to refresh token if we have one
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken && !authStore.isLoading) {
          try {
            console.log('🔄 Attempting token refresh...')
            await authStore.refreshToken()

            if (authStore.isAuthenticated) {
              console.log('✅ Token refresh successful')
              return true // allow navigation
            }
          } catch (error) {
            console.warn('⚠️ Token refresh failed:', error)
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('auth_token')
            localStorage.removeItem('user_data')
          }
        }

        // Redirect to auth page
        console.log('🔀 Redirecting to auth page')
        return {
          name: 'auth',
          query: { redirect: to.fullPath }
        }
      }

      console.log('✅ User is authenticated, allowing navigation')
    }

    // Guest-only routes
    if (to.meta.requiresGuest && authStore.isAuthenticated) {
      console.log('🔀 Authenticated user accessing guest page, redirecting')
      const redirectPath = (to.query.redirect as string) || '/'
      return redirectPath
    }

    // All checks passed
    console.log('✅ Navigation approved')
    return true

  } catch (error) {
    console.error('❌ Router navigation error:', error)

    // Redirect to error page
    return {
      name: 'error',
      query: {
        error: 'Navigation failed',
        code: '500'
      }
    }
  }
})

// After each navigation
router.afterEach((to, from, failure) => {
  if (failure) {
    console.error('❌ Navigation failed:', failure)
    return
  }
  
  console.log(`✅ Successfully navigated to: ${to.path}`)
  
  // Track page views (analytics)
  if (import.meta.env.PROD && window.gtag) {
    window.gtag('config', 'GA_TRACKING_ID', {
      page_path: to.path
    })
  }
  
  // Log navigation in development
  if (import.meta.env.DEV) {
    console.log(`📍 Current route:`, {
      name: to.name,
      path: to.path,
      params: to.params,
      query: to.query,
      meta: to.meta
    })
  }
})

// Handle router errors
router.onError((error) => {
  console.error('🚨 Router error:', error)
  
  // Try to recover by going to error page
  router.push({
    name: 'error',
    query: {
      error: error.message,
      code: '500'
    }
  }).catch(err => {
    console.error('Failed to navigate to error page:', err)
    // Last resort: reload the page
    window.location.href = '/error'
  })
})

export default router

// Type augmentation for custom route meta
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    requiresGuest?: boolean
    title?: string
    description?: string
  }
}