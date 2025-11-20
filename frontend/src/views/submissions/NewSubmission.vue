<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">New Manuscript Submission</h1>
      <p class="mt-2 text-gray-600">Upload your manuscript and we'll extract metadata automatically</p>
    </div>

    <!-- Step Indicator -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div v-for="(step, index) in steps" :key="index" class="flex-1">
          <div class="flex items-center">
            <div 
              :class="[
                'w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium',
                currentStep >= index + 1 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-600'
              ]"
            >
              {{ index + 1 }}
            </div>
            <div v-if="index < steps.length - 1" class="flex-1 h-1 mx-2 bg-gray-200">
              <div 
                :class="['h-full bg-blue-600 transition-all duration-300']"
                :style="{ width: currentStep > index + 1 ? '100%' : '0%' }"
              ></div>
            </div>
          </div>
          <div class="mt-2 text-sm font-medium text-gray-900">{{ step }}</div>
        </div>
      </div>
    </div>

    <!-- Step 1: File Upload -->
    <div v-if="currentStep === 1" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 class="text-xl font-semibold mb-4">Upload Manuscript</h2>
      
      <div class="space-y-4">
        <!-- Manuscript Type Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Manuscript Type</label>
          <select 
            v-model="manuscriptType" 
            class="w-full border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="RESEARCH_ARTICLE">Research Article</option>
            <option value="REVIEW_ARTICLE">Review Article</option>
            <option value="SHORT_COMMUNICATION">Short Communication</option>
            <option value="CASE_REPORT">Case Report</option>
            <option value="EDITORIAL">Editorial</option>
            <option value="LETTER">Letter to Editor</option>
          </select>
        </div>

        <!-- File Upload Area -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Manuscript File (.docx)</label>
          <div 
            @dragover.prevent="dragOver = true"
            @dragleave.prevent="dragOver = false"
            @drop.prevent="handleFileDrop"
            :class="[
              'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
              dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'
            ]"
          >
            <input 
              ref="fileInput"
              type="file" 
              accept=".docx"
              @change="handleFileSelect"
              class="hidden"
            />
            
            <div v-if="!selectedFile">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="mt-2 text-sm text-gray-600">
                Drag and drop your .docx file here, or
                <button @click="$refs.fileInput.click()" class="text-blue-600 hover:text-blue-500 font-medium">
                  browse
                </button>
              </p>
              <p class="mt-1 text-xs text-gray-500">Maximum file size: 50MB</p>
            </div>
            
            <div v-else class="space-y-2">
              <svg class="mx-auto h-12 w-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</p>
              <p class="text-xs text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
              <button 
                @click="selectedFile = null" 
                class="text-sm text-red-600 hover:text-red-500"
              >
                Remove
              </button>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end gap-3 pt-4">
          <button 
            @click="$router.push('/dashboard')" 
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button 
            @click="uploadAndExtract" 
            :disabled="!selectedFile || uploading"
            class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ uploading ? 'Uploading...' : 'Upload & Extract Metadata' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Step 2: Extraction Progress -->
    <div v-if="currentStep === 2" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 class="text-xl font-semibold mb-4">Extracting Metadata</h2>
      
      <div class="space-y-4">
        <div class="flex items-center justify-center py-8">
          <div class="text-center">
            <div class="inline-block animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent"></div>
            <p class="mt-4 text-gray-600">{{ extractionMessage }}</p>
          </div>
        </div>

        <div v-if="extractionWarnings.length > 0" class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <h3 class="text-sm font-medium text-yellow-800 mb-2">Warnings</h3>
          <ul class="list-disc list-inside text-sm text-yellow-700 space-y-1">
            <li v-for="(warning, index) in extractionWarnings" :key="index">{{ warning }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Step 3: Review & Edit -->
    <div v-if="currentStep === 3" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 class="text-xl font-semibold mb-4">Review & Edit Metadata</h2>
      
      <!-- Extraction Errors/Warnings -->
      <div v-if="extractionErrors.length > 0" class="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
        <h3 class="text-sm font-medium text-red-800 mb-2">⚠️ Extraction Issues</h3>
        <div class="space-y-2">
          <div v-for="error in extractionErrors" :key="error" class="text-sm text-red-700">
            {{ getErrorMessage(error) }}
          </div>
        </div>
      </div>

      <form @submit.prevent="submitManuscript" class="space-y-6">
        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Title *
            <span v-if="!submission.title" class="text-red-600">(Required - please add manually)</span>
          </label>
          <input 
            v-model="submission.title" 
            type="text"
            required
            placeholder="Enter manuscript title"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :class="{ 'border-red-500': !submission.title }"
          />
        </div>

        <!-- Abstract -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Abstract *
            <span v-if="!submission.abstract" class="text-red-600">(Required - please add manually)</span>
          </label>
          <textarea 
            v-model="submission.abstract"
            required
            rows="6"
            placeholder="Enter abstract"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :class="{ 'border-red-500': !submission.abstract }"
          ></textarea>
        </div>

        <!-- Keywords -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Keywords</label>
          <div class="flex gap-2 mb-2">
            <input 
              v-model="newKeyword"
              type="text"
              placeholder="Add keyword"
              @keypress.enter.prevent="addKeyword"
              class="flex-1 border border-gray-300 rounded-md px-3 py-2"
            />
            <button 
              type="button"
              @click="addKeyword"
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
            >
              Add
            </button>
          </div>
          <div class="flex flex-wrap gap-2">
            <span 
              v-for="(keyword, index) in keywords" 
              :key="index"
              class="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
            >
              {{ keyword }}
              <button 
                type="button"
                @click="removeKeyword(index)" 
                class="text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          </div>
        </div>

        <!-- Authors -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Authors *</label>
          <div class="space-y-3">
            <div 
              v-for="(author, index) in authors" 
              :key="index"
              class="border border-gray-200 rounded-md p-4"
            >
              <div class="grid grid-cols-2 gap-3">
                <input 
                  v-model="author.name"
                  placeholder="Author name"
                  class="border border-gray-300 rounded-md px-3 py-2"
                />
                <input 
                  v-model="author.email"
                  type="email"
                  placeholder="Email"
                  class="border border-gray-300 rounded-md px-3 py-2"
                />
                <input 
                  v-model="author.affiliation"
                  placeholder="Affiliation"
                  class="col-span-2 border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div class="mt-2 flex justify-between items-center">
                <label class="flex items-center text-sm text-gray-600">
                  <input 
                    v-model="author.is_corresponding" 
                    type="checkbox"
                    class="mr-2"
                  />
                  Corresponding author
                </label>
                <button 
                  v-if="authors.length > 1"
                  type="button"
                  @click="removeAuthor(index)"
                  class="text-sm text-red-600 hover:text-red-500"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
          <button 
            type="button"
            @click="addAuthor"
            class="mt-3 text-sm text-blue-600 hover:text-blue-500 font-medium"
          >
            + Add Author
          </button>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-between pt-4 border-t">
          <button 
            type="button"
            @click="saveDraft"
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Save as Draft
          </button>
          <div class="flex gap-3">
            <button 
              type="button"
              @click="currentStep = 1"
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Back
            </button>
            <button 
              type="submit"
              :disabled="!canSubmit || submitting"
              class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ submitting ? 'Submitting...' : 'Submit Manuscript' }}
            </button>
          </div>
        </div>
      </form>
    </div>

    <!-- Success Message -->
    <div v-if="currentStep === 4" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
      <svg class="mx-auto h-16 w-16 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h2 class="mt-4 text-2xl font-semibold text-gray-900">Submission Successful!</h2>
      <p class="mt-2 text-gray-600">Your manuscript has been submitted successfully.</p>
      <div class="mt-6 flex justify-center gap-3">
        <button 
          @click="$router.push('/dashboard')" 
          class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Go to Dashboard
        </button>
        <button 
          @click="resetForm" 
          class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          Submit Another
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { submissionsApi, type Submission, type Author } from '@/api/submissions'

const router = useRouter()

// Steps
const steps = ['Upload', 'Extract', 'Review', 'Complete']
const currentStep = ref(1)

// Step 1: File Upload
const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const manuscriptType = ref('RESEARCH_ARTICLE')
const dragOver = ref(false)
const uploading = ref(false)

// Step 2: Extraction
const extractionMessage = ref('Analyzing your manuscript...')
const extractionWarnings = ref<string[]>([])
const extractionErrors = ref<string[]>([])

// Step 3: Submission Data
const submission = ref<Partial<Submission>>({
  title: '',
  abstract: '',
  manuscript_type: 'RESEARCH_ARTICLE'
})
const submissionId = ref<string>('')
const keywords = ref<string[]>([])
const newKeyword = ref('')
const authors = ref<Array<{
  name: string
  email: string
  affiliation: string
  is_corresponding: boolean
}>>([{
  name: '',
  email: '',
  affiliation: '',
  is_corresponding: true
}])
const submitting = ref(false)

// Computed
const canSubmit = computed(() => {
  return submission.value.title && 
         submission.value.abstract && 
         authors.value.some(a => a.name && a.email)
})

// File Handling
function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

function handleFileDrop(event: DragEvent) {
  dragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    selectedFile.value = event.dataTransfer.files[0]
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Upload & Extract
async function uploadAndExtract() {
  if (!selectedFile.value) return
  
  uploading.value = true
  currentStep.value = 2
  
  try {
    // Start submission with file upload
    const result = await submissionsApi.startSubmission(selectedFile.value, manuscriptType.value)
    submissionId.value = result.submission_id
    
    if (result.task_id) {
      // Wait for extraction to complete
      extractionMessage.value = 'Extracting metadata from your manuscript...'
      
      const extractionResult = await submissionsApi.waitForExtraction(
        result.task_id,
        (status) => {
          if (status.state === 'PENDING') {
            extractionMessage.value = 'Processing... This may take a moment.'
          }
        }
      )
      
      // Update form with extracted data
      if (extractionResult.extracted) {
        submission.value.title = extractionResult.extracted.title || ''
        submission.value.abstract = extractionResult.extracted.abstract || ''
        keywords.value = extractionResult.extracted.keywords || []
        
        if (extractionResult.extracted.authors && extractionResult.extracted.authors.length > 0) {
          authors.value = extractionResult.extracted.authors.map((a, idx) => ({
            name: a.name || '',
            email: a.email || '',
            affiliation: a.affiliation || '',
            is_corresponding: idx === 0
          }))
        }
      }
      
      extractionErrors.value = extractionResult.errors || []
      extractionWarnings.value = extractionResult.warnings || []
    }
    
    submission.value.manuscript_type = manuscriptType.value
    currentStep.value = 3
    
  } catch (error) {
    console.error('Upload/extraction failed:', error)
    alert('Failed to upload and extract metadata. Please try again.')
    currentStep.value = 1
  } finally {
    uploading.value = false
  }
}

// Keywords
function addKeyword() {
  if (newKeyword.value.trim()) {
    keywords.value.push(newKeyword.value.trim())
    newKeyword.value = ''
  }
}

function removeKeyword(index: number) {
  keywords.value.splice(index, 1)
}

// Authors
function addAuthor() {
  authors.value.push({
    name: '',
    email: '',
    affiliation: '',
    is_corresponding: false
  })
}

function removeAuthor(index: number) {
  authors.value.splice(index, 1)
}

// Error Messages
function getErrorMessage(errorCode: string): string {
  const messages: Record<string, string> = {
    'EXTRACT_NO_TITLE': '⚠️ No title found. Please add it manually. Tip: Use "Heading 1" style in Word.',
    'EXTRACT_NO_ABSTRACT': '⚠️ No abstract found. Please add it manually. Tip: Add an "Abstract" section heading.',
    'EXTRACT_NO_KEYWORDS': 'ℹ️ No keywords found. You can add them manually below.',
    'EXTRACT_NO_AUTHORS': 'ℹ️ No authors detected. Please add authors manually.',
    'EXTRACT_INVALID_FORMAT': '❌ Invalid file format. Please upload a valid .docx file.'
  }
  return messages[errorCode] || `⚠️ ${errorCode}`
}

// Save & Submit
async function saveDraft() {
  if (!submissionId.value) return
  
  try {
    await submissionsApi.updateSubmission(submissionId.value, {
      title: submission.value.title,
      abstract: submission.value.abstract,
      manuscript_type: submission.value.manuscript_type
    })
    
    alert('Draft saved successfully!')
    router.push('/dashboard')
  } catch (error) {
    console.error('Failed to save draft:', error)
    alert('Failed to save draft. Please try again.')
  }
}

async function submitManuscript() {
  if (!submissionId.value || !canSubmit.value) return
  
  submitting.value = true
  
  try {
    // Update submission
    await submissionsApi.updateSubmission(submissionId.value, {
      title: submission.value.title,
      abstract: submission.value.abstract,
      manuscript_type: submission.value.manuscript_type
    })
    
    // Add authors (if not already added by extraction)
    for (const author of authors.value) {
      if (author.name && author.email) {
        await submissionsApi.addAuthor(submissionId.value, {
          external_author_name: author.name,
          external_author_email: author.email,
          affiliation: author.affiliation,
          is_corresponding: author.is_corresponding,
          author_order: 0 // Backend will set correct order
        })
      }
    }
    
    // Submit the draft
    await submissionsApi.submitDraft(submissionId.value)
    
    currentStep.value = 4
  } catch (error) {
    console.error('Submission failed:', error)
    alert('Failed to submit manuscript. Please try again.')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  currentStep.value = 1
  selectedFile.value = null
  submission.value = {
    title: '',
    abstract: '',
    manuscript_type: 'RESEARCH_ARTICLE'
  }
  submissionId.value = ''
  keywords.value = []
  authors.value = [{
    name: '',
    email: '',
    affiliation: '',
    is_corresponding: true
  }]
  extractionErrors.value = []
  extractionWarnings.value = []
}
</script>
