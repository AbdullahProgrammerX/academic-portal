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
  const authStore = useAuthStore()

  // If not initialized yet, try to fetch current user
  if (!authStore.user && !authStore.loading) {
    try {
      await authStore.initialize()
    } catch (err) {
      // User not authenticated, continue with guard logic
    }
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Not authenticated, redirect to login
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // Check if route requires verification
    if (to.meta.requiresVerification && !authStore.hasVerifiedIdentity) {
      // Not verified, redirect to dashboard with message
      next({
        path: '/dashboard',
        query: { message: 'Please verify your email or ORCID to submit manuscripts' }
      })
      return
    }
  }

  // Check if route requires guest (logged out)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/dashboard')
    return
  }

  // Allow navigation
  next()
})

export default router

