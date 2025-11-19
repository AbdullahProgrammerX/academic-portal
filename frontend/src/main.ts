/**
 * Frontend application entry point
 * 
 * Initializes:
 * - Pinia store
 * - Vue Router
 * - Auth store (attempt to restore session)
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue Error]', err)
  console.error('[Error Info]', info)
  console.error('[Component]', instance)
}

// Global warning handler
app.config.warnHandler = (msg, instance, trace) => {
  console.warn('[Vue Warning]', msg)
  console.warn('[Trace]', trace)
}

app.use(pinia)
app.use(router)

// DO NOT initialize auth store here - router guard will do it once
console.log('[Main] Mounting app...')
app.mount('#app')
console.log('[Main] App mounted successfully')

