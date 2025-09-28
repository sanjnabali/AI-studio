// src/router/index.ts - Fixed Version
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../store/auth'

// Type declarations for Google Analytics gtag
declare global {
  interface Window {
    gtag?: (...args: any[]) => void
  }
}

// Lazy load components with proper error handling
const Studio = () => import('../views/Studio.vue').catch(err => {
  console.error('Failed to load Studio component:', err)
  return import('../views/fallback/ComponentError.vue').catch(() => null)
})

const Templates = () => import('../views/Templates.vue').catch(err => {
  console.error('Failed to load Templates component:', err)
  return import('../views/fallback/ComponentError.vue').catch(() => null)
})

const Settings = () => import('../views/Settings.vue').catch(err => {
  console.error('Failed to load Settings component:', err)
  return import('../views/fallback/ComponentError.vue').catch(() => null)
})

const Auth = () => import('../views/auth.vue').catch(err => {
  console.error('Failed to load Auth component:', err)
  return import('../views/fallback/ComponentError.vue').catch(() => null)
})

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
    redirect: '/auth'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0, behavior: 'smooth' }
  }
})

let isInitialLoad = true;

// Global navigation guards
router.beforeEach(async (to, from) => {
  console.log(`🧭 Router: Navigating from ${from.path} to ${to.path}`)

  // Prevent infinite loops (skip for initial load where from.name is null)
  if (to.path === from.path && from.name !== null) {
    console.warn('⚠️ Router: Navigation loop detected, aborting')
    return false
  }

  try {
    const authStore = useAuthStore()

    // Wait for auth initialization if needed
    if (!authStore.isInitialized) {
      console.log('⏳ Router: Waiting for auth initialization...')
      await authStore.initializeAuth()
    }

    // If token exists but user is missing, fetch user info
    if (authStore.token && !authStore.user) {
      console.log('⏳ Router: Token present but user missing, fetching user info...')
      // Call fetchUser() to fetch user info from backend
      await authStore.fetchUser()
    }

    console.log('🔐 Router: Auth state:', {
      isAuthenticated: authStore.isAuthenticated,
      hasUser: !!authStore.user,
      hasToken: !!authStore.token,
      isInitialized: authStore.isInitialized,
      targetRequiresAuth: !!to.meta.requiresAuth,
      targetRequiresGuest: !!to.meta.requiresGuest
    })

    // Set page title
    if (to.meta.title) {
      document.title = to.meta.title as string
    }

    // Handle protected routes
    if (to.meta.requiresAuth) {
      if (!authStore.isAuthenticated) {
        if (to.path === '/auth') {
          console.log('⚠️ Router: Already on /auth, not redirecting to avoid loop')
          return true
        }
        console.log('❌ Router: Protected route accessed without auth, redirecting to /auth')
        return {
          name: 'auth',
          query: { redirect: to.fullPath }
        }
      }
      console.log('✅ Router: Auth verified for protected route')
    }

    // Handle guest-only routes (like auth page)
    if (to.meta.requiresGuest) {
      if (authStore.isAuthenticated) {
        console.log('🔀 Router: Authenticated user accessing guest route, redirecting')
        const redirectPath = (to.query.redirect as string) || '/'
        return redirectPath
      }
      console.log('✅ Router: Guest access verified')
    }

    // Mark initial load as complete after first successful navigation
    if (isInitialLoad) {
      isInitialLoad = false
    }

    console.log('✅ Router: Navigation approved')
    return true

  } catch (error) {
    console.error('❌ Router: Navigation error:', error)
    return { name: 'auth' } // Fallback to auth on error
  }
})

// After each navigation
router.afterEach((to, from, failure) => {
  if (failure) {
    console.error('❌ Router: Navigation failed:', failure)
    return
  }
  
  console.log(`✅ Router: Successfully navigated to: ${to.path}`)
  
  // Track page views (analytics)
  if (import.meta.env.PROD && window.gtag) {
    window.gtag('config', 'GA_TRACKING_ID', {
      page_path: to.path
    })
  }
  
  // Log navigation in development
  if (import.meta.env.DEV) {
    console.log(`📍 Router: Current route:`, {
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
  console.error('🚨 Router: Router error:', error)
  
  // Try to recover by going to auth page
  router.push('/auth').catch(err => {
    console.error('❌ Router: Failed to navigate to auth page:', err)
    // Last resort: reload the page
    window.location.href = '/auth'
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