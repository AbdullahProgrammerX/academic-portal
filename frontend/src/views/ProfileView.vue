<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getProfile, updateProfile } from '@/api/profile'
import type { ProfileCompletionResponse, User } from '@/types'

const authStore = useAuthStore()
const profileData = ref<ProfileCompletionResponse | null>(null)
const loading = ref(true)
const saving = ref(false)
const saveMessage = ref('')
const saveTimeout = ref<number | null>(null)

// Form data
const formData = ref<Partial<User>>({
  full_name: '',
  affiliation: '',
  bio: '',
  profile: {
    phone: '',
    country: '',
    research_interests: [],
    expertise_areas: [],
    notification_preferences: {
      email_notifications: true,
      submission_updates: true,
      review_reminders: true
    }
  }
})

// New research interest input
const newInterest = ref('')

onMounted(async () => {
  await loadProfile()
})

async function loadProfile() {
  try {
    loading.value = true
    profileData.value = await getProfile()
    
    // Populate form with current data
    if (profileData.value.user) {
      formData.value = {
        full_name: profileData.value.user.full_name || '',
        affiliation: profileData.value.user.affiliation || '',
        bio: profileData.value.user.bio || '',
        profile: {
          phone: profileData.value.user.profile?.phone || '',
          country: profileData.value.user.profile?.country || '',
          research_interests: profileData.value.user.profile?.research_interests || [],
          expertise_areas: profileData.value.user.profile?.expertise_areas || [],
          notification_preferences: profileData.value.user.profile?.notification_preferences || {
            email_notifications: true,
            submission_updates: true,
            review_reminders: true
          }
        }
      }
    }
  } catch (err) {
    console.error('[Profile] Failed to load:', err)
    saveMessage.value = 'Failed to load profile'
  } finally {
    loading.value = false
  }
}

// Autosave with debounce (3 seconds)
watch(formData, () => {
  if (saveTimeout.value) {
    clearTimeout(saveTimeout.value)
  }
  
  saveTimeout.value = window.setTimeout(() => {
    saveProfile()
  }, 3000)
}, { deep: true })

async function saveProfile() {
  if (saving.value) return
  
  try {
    saving.value = true
    saveMessage.value = 'Saving...'
    
    profileData.value = await updateProfile(formData.value)
    
    saveMessage.value = 'Saved ✓'
    setTimeout(() => {
      saveMessage.value = ''
    }, 2000)
  } catch (err: any) {
    console.error('[Profile] Save failed:', err)
    saveMessage.value = 'Save failed'
    setTimeout(() => {
      saveMessage.value = ''
    }, 3000)
  } finally {
    saving.value = false
  }
}

function addResearchInterest() {
  if (newInterest.value.trim() && formData.value.profile) {
    if (!formData.value.profile.research_interests) {
      formData.value.profile.research_interests = []
    }
    formData.value.profile.research_interests.push(newInterest.value.trim())
    newInterest.value = ''
  }
}

function removeResearchInterest(index: number) {
  if (formData.value.profile?.research_interests) {
    formData.value.profile.research_interests.splice(index, 1)
  }
}

function connectORCID() {
  // ORCID connection will be implemented in next phase
  alert('ORCID connection will be available soon')
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Profile</h1>
          <p class="text-gray-600 mt-2">Manage your account information</p>
        </div>
        
        <!-- Save Indicator -->
        <div v-if="saveMessage" 
             :class="saveMessage.includes('failed') ? 'text-red-600' : 'text-green-600'"
             class="text-sm font-medium">
          {{ saveMessage }}
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-lg shadow p-6 animate-pulse space-y-4">
        <div class="h-4 bg-gray-200 rounded w-1/4"></div>
        <div class="h-10 bg-gray-200 rounded"></div>
        <div class="h-4 bg-gray-200 rounded w-1/4"></div>
        <div class="h-10 bg-gray-200 rounded"></div>
      </div>

      <!-- Profile Form -->
      <div v-else class="space-y-6">
        <!-- Completion Progress -->
        <div v-if="profileData" class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Profile Completion</h2>
            <span class="text-2xl font-bold text-indigo-600">
              {{ profileData.completion_percentage }}%
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-3">
            <div 
              class="bg-indigo-600 h-3 rounded-full transition-all duration-500"
              :style="{ width: `${profileData.completion_percentage}%` }"
            ></div>
          </div>
        </div>

        <!-- Basic Information -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Basic Information</h2>
          
          <div class="space-y-4">
            <!-- Full Name -->
            <div>
              <label for="full_name" class="block text-sm font-medium text-gray-700 mb-1">
                Full Name *
              </label>
              <input 
                id="full_name"
                v-model="formData.full_name"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="John Doe"
              />
            </div>

            <!-- Email (read-only) -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input 
                id="email"
                :value="authStore.user?.email"
                type="email"
                disabled
                class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
              />
            </div>

            <!-- Affiliation -->
            <div>
              <label for="affiliation" class="block text-sm font-medium text-gray-700 mb-1">
                Affiliation *
              </label>
              <input 
                id="affiliation"
                v-model="formData.affiliation"
                type="text"
                maxlength="255"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="University of Example"
              />
            </div>

            <!-- Country -->
            <div>
              <label for="country" class="block text-sm font-medium text-gray-700 mb-1">
                Country *
              </label>
              <input 
                id="country"
                v-model="formData.profile!.country"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="United States"
              />
            </div>

            <!-- Bio -->
            <div>
              <label for="bio" class="block text-sm font-medium text-gray-700 mb-1">
                Bio * (min 50 characters)
              </label>
              <textarea 
                id="bio"
                v-model="formData.bio"
                rows="4"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Brief description of your research background and interests..."
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">
                {{ formData.bio?.length || 0 }} / 50 minimum
              </p>
            </div>
          </div>
        </div>

        <!-- Research Information -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Research Information</h2>
          
          <div class="space-y-4">
            <!-- Research Interests -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Research Interests * (at least 1)
              </label>
              
              <!-- Interest Tags -->
              <div v-if="formData.profile?.research_interests && formData.profile.research_interests.length > 0" 
                   class="flex flex-wrap gap-2 mb-3">
                <span 
                  v-for="(interest, index) in formData.profile.research_interests" 
                  :key="index"
                  class="inline-flex items-center bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm"
                >
                  {{ interest }}
                  <button 
                    @click="removeResearchInterest(index)"
                    class="ml-2 text-indigo-600 hover:text-indigo-800"
                    aria-label="Remove interest"
                  >
                    ×
                  </button>
                </span>
              </div>

              <!-- Add New Interest -->
              <div class="flex gap-2">
                <input 
                  v-model="newInterest"
                  type="text"
                  @keyup.enter="addResearchInterest"
                  class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="e.g., Machine Learning, Bioinformatics"
                />
                <button 
                  @click="addResearchInterest"
                  class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Add
                </button>
              </div>
            </div>

            <!-- ORCID -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                ORCID iD *
              </label>
              <div v-if="authStore.user?.orcid_id" class="flex items-center gap-2">
                <input 
                  :value="authStore.user.orcid_id"
                  type="text"
                  disabled
                  class="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                />
                <span class="text-green-600 font-medium">✓ Connected</span>
              </div>
              <button 
                v-else
                @click="connectORCID"
                class="bg-white hover:bg-gray-50 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors inline-flex items-center"
              >
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 7.885c.614 0 1.107.494 1.107 1.108 0 .613-.493 1.107-1.107 1.107-.614 0-1.108-.494-1.108-1.107 0-.614.494-1.108 1.108-1.108zm-.738 3.231h1.477v7.877H6.631v-7.877zm4.862 0h1.415v1.077h.02c.197-.373.681-1.077 1.402-1.077 1.5 0 1.777 1.123 1.777 2.585v4.292h-1.477v-3.808c0-.55-.011-1.258-.767-1.258-.769 0-.887.6-.887 1.219v3.847h-1.477v-7.877h-.006z"/>
                </svg>
                Connect ORCID
              </button>
            </div>
          </div>
        </div>

        <!-- Contact & Privacy -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Contact & Privacy</h2>
          
          <div class="space-y-4">
            <!-- Phone -->
            <div>
              <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">
                Phone (optional)
              </label>
              <input 
                id="phone"
                v-model="formData.profile!.phone"
                type="tel"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <!-- Notification Preferences -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Email Notifications
              </label>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input 
                    v-model="formData.profile!.notification_preferences.email_notifications"
                    type="checkbox"
                    class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">General email notifications</span>
                </label>
                <label class="flex items-center">
                  <input 
                    v-model="formData.profile!.notification_preferences.submission_updates"
                    type="checkbox"
                    class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Submission status updates</span>
                </label>
                <label class="flex items-center">
                  <input 
                    v-model="formData.profile!.notification_preferences.review_reminders"
                    type="checkbox"
                    class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Review reminders</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Auto-save Notice -->
        <div class="text-center text-sm text-gray-500">
          Changes are automatically saved
        </div>
      </div>
    </div>
  </div>
</template>
