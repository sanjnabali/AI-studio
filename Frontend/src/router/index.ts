// src/router/index.ts - Updated with authentication
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

// Lazy load components
const Studio = () => import('../views/Studio.vue')
const Templates = () => import('../views/Templates.vue')  
const Settings = () => import('../views/Settings.vue')
const Auth = () => import('../views/auth.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/auth',
      name: 'auth',
      component: Auth,
      meta: { 
        requiresGuest: true,
        title: 'Sign In - AI Studio'
      }
    },
    {
      path: '/',
      name: 'studio',
      component: Studio,
      meta: { 
        requiresAuth: true,
        title: 'AI Studio'
      }
    },
    {
      path: '/templates',
      name: 'templates', 
      component: Templates,
      meta: { 
        requiresAuth: true,
        title: 'Templates - AI Studio'
      }
    },
    {
      path: '/settings',
      name: 'settings',
      component: Settings,
      meta: { 
        requiresAuth: true,
        title: 'Settings - AI Studio'
      }
    },
    // Catch-all route for 404s
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth store if not already done
  if (!authStore.user && !authStore.isLoading) {
    authStore.initializeAuth()
  }
  
  // Set page title
  if (to.meta.title) {
    document.title = to.meta.title as string
  }
  
  // Check authentication requirements
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Try to refresh token if we have one
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          await authStore.refreshToken()
          if (authStore.isAuthenticated) {
            next()
            return
          }
        } catch (error) {
          console.warn('Token refresh failed:', error)
        }
      }
      
      // Redirect to auth page
      next({
        name: 'auth',
        query: { redirect: to.fullPath }
      })
      return
    }
  }
  
  // Check guest-only routes
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    const redirectPath = (to.query.redirect as string) || '/'
    next(redirectPath)
    return
  }
  
  next()
})

// After each navigation
router.afterEach((to) => {
  // You could add analytics tracking here
  console.log(`Navigated to: ${to.path}`)
})

export default router