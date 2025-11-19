<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getProfile } from '@/api/profile'
import type { ProfileCompletionResponse } from '@/types'

const authStore = useAuthStore()
const router = useRouter()
const profileData = ref<ProfileCompletionResponse | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    profileData.value = await getProfile()
  } catch (err) {
    console.error('[Dashboard] Failed to load profile:', err)
  } finally {
    loading.value = false
  }
})

function navigateToNewSubmission() {
  router.push('/submissions/new')
}

function navigateToProfile() {
  router.push('/profile')
}

function getCompletionColor(percentage: number): string {
  if (percentage === 100) return 'bg-green-500'
  if (percentage >= 70) return 'bg-yellow-500'
  return 'bg-red-500'
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-gray-600 mt-2">Welcome, {{ authStore.user?.email }}</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="space-y-4">
        <div class="bg-white rounded-lg shadow p-6 animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div class="h-8 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>

      <!-- Profile Completion Widget (Progressive Disclosure) -->
      <div v-else-if="profileData && profileData.completion_percentage < 100" 
           class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h2 class="text-lg font-semibold text-blue-900 mb-2">
              Complete Your Profile
            </h2>
            <p class="text-blue-700 text-sm mb-4">
              {{ profileData.completion_percentage }}% complete. Add more information to improve your profile visibility.
            </p>
            
            <!-- Progress Bar -->
            <div class="w-full bg-blue-100 rounded-full h-2 mb-4">
              <div 
                :class="getCompletionColor(profileData.completion_percentage)"
                class="h-2 rounded-full transition-all duration-300"
                :style="{ width: `${profileData.completion_percentage}%` }"
              ></div>
            </div>

            <!-- Missing Fields -->
            <div v-if="profileData.missing_fields.length > 0" class="mb-4">
              <p class="text-sm text-blue-800 font-medium mb-2">Missing information:</p>
              <ul class="text-sm text-blue-700 space-y-1">
                <li v-for="field in profileData.missing_fields" :key="field" class="flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd"/>
                  </svg>
                  {{ field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) }}
                </li>
              </ul>
            </div>

            <button 
              @click="navigateToProfile"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              aria-label="Complete your profile"
            >
              Complete Profile
            </button>
          </div>
        </div>
      </div>

      <!-- Main CTA: New Submission -->
      <div class="bg-white rounded-lg shadow-md p-8 mb-6 text-center">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">
          Ready to submit your manuscript?
        </h2>
        <p class="text-gray-600 mb-6">
          Start a new submission and track its progress through the review process.
        </p>
        
        <!-- Show verification warning if not verified -->
        <div v-if="!authStore.hasVerifiedIdentity" 
             class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4 text-left">
          <p class="text-yellow-800 text-sm">
            <strong>⚠️ Verification Required:</strong> Please verify your email or connect your ORCID to submit manuscripts.
          </p>
        </div>
        
        <button 
          @click="navigateToNewSubmission"
          :disabled="!authStore.hasVerifiedIdentity"
          :class="authStore.hasVerifiedIdentity 
            ? 'bg-indigo-600 hover:bg-indigo-700' 
            : 'bg-gray-400 cursor-not-allowed'"
          class="text-white px-8 py-3 rounded-lg font-semibold text-lg transition-colors inline-flex items-center"
          :aria-label="authStore.hasVerifiedIdentity ? 'Create new manuscript submission' : 'Verification required to submit'"
        >
          <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          New Manuscript Submission
        </button>
      </div>

      <!-- Recent Submissions -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Your Submissions</h2>
        
        <!-- Empty State -->
        <div class="text-center py-12">
          <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <p class="text-gray-500 text-lg mb-2">No submissions yet</p>
          <p class="text-gray-400 text-sm">Your manuscript submissions will appear here</p>
        </div>
      </div>
    </div>
  </div>
</template>

