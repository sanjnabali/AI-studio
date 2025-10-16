
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import compression from 'vite-plugin-compression'

export default defineConfig({
  plugins: [vue(), compression({ algorithm: 'gzip', threshold: 10240 })],
  resolve: {
    alias: {
       "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    target: 'es2020',
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['@vueuse/core'],
          'http-vendor': ['axios']
        }
      }
    }
  }
})