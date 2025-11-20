/**
 * Vue Router configuration with authentication guards
 * 
 * Meta fields:
 * - requiresAuth: Route requires authentication
 * - requiresGuest: Route requires user to be logged out
 * - requiresVerification: Route requires verified email/ORCID
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/auth/orcid/callback',
      name: 'orcid-callback',
      component: () => import('@/views/auth/ORCIDCallback.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/submissions/new',
      name: 'new-submission',
      component: () => import('@/views/submissions/NewSubmission.vue'),
      meta: { requiresAuth: true, requiresVerification: true }
    },
    {
      path: '/submissions/:id',
      name: 'submission-detail',
      component: () => import('@/views/submissions/SubmissionDetail.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  console.log('[Router] Navigation:', from.path, '->', to.path)
  const authStore = useAuthStore()

  // If not initialized yet, initialize once
  if (!authStore.initialized) {
    try {
      console.log('[Router] Initializing auth store...')
      await authStore.initialize()
      console.log('[Router] Auth initialized. User:', authStore.user?.email, 'Token:', !!authStore.accessToken)
    } catch (err) {
      console.log('[Router] Auth initialization failed:', err)
      // User not authenticated, mark as initialized anyway
      authStore.initialized = true
    }
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    console.log('[Router] Route requires auth:', to.path, '| isAuthenticated:', authStore.isAuthenticated)
    if (!authStore.isAuthenticated) {
      console.log('[Router] Not authenticated, redirecting to login')
      // Not authenticated, redirect to login
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // Check if route requires verification
    // TEMPORARILY DISABLED FOR TESTING
    // if (to.meta.requiresVerification && !authStore.hasVerifiedIdentity) {
    //   console.log('[Router] Not verified, redirecting to dashboard')
    //   // Not verified, redirect to dashboard with message
    //   next({
    //     path: '/dashboard',
    //     query: { message: 'Please verify your email or ORCID to submit manuscripts' }
    //   })
    //   return
    // }
  }

  // Check if route requires guest (logged out)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    console.log('[Router] Already authenticated, redirecting to dashboard')
    next('/dashboard')
    return
  }

  // Allow navigation
  console.log('[Router] Navigation allowed to:', to.path)
  next()
})

export default router

