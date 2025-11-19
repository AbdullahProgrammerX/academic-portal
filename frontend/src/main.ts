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

app.use(pinia)
app.use(router)

// Initialize auth store after pinia is set up
const authStore = useAuthStore()
authStore.initialize().catch(() => {
  // Silent fail - user just needs to login
  console.debug('No active session found')
})

app.mount('#app')

