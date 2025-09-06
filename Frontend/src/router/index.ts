// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import Studio from '../views/Studio.vue'
import Templates from '../views/Templates.vue'
import Settings from '../views/Settings.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'studio',
      component: Studio
    },
    {
      path: '/templates',
      name: 'templates',
      component: Templates
    },
    {
      path: '/settings',
      name: 'settings',
      component: Settings
    }
  ]
})

export default router
