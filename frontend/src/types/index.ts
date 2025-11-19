/**
 * TypeScript type definitions for the Editorial System
 */

// User & Authentication Types
export interface User {
  id: string  // UUID
  email: string
  full_name: string
  affiliation?: string
  bio?: string
  orcid_id?: string
  role: 'author' | 'reviewer' | 'editor' | 'admin'
  is_active: boolean
  is_staff: boolean
  email_verified: boolean
  orcid_verified: boolean
  date_joined: string
  last_login?: string
  profile?: UserProfile
}

export interface UserProfile {
  phone?: string
  country?: string
  research_interests?: string[]
  expertise_areas?: string[]
  website?: string
  profile_completed?: boolean
  notification_preferences: {
    email_notifications: boolean
    submission_updates: boolean
    review_reminders: boolean
  }
}

// Profile completion response
export interface ProfileCompletionResponse {
  user: User
  completion_percentage: number
  missing_fields: string[]
  message?: string
}

// Manuscript Types
export interface Manuscript {
  id: number
  title: string
  abstract: string
  status: ManuscriptStatus
  submittedAt: string
  updatedAt: string
  authors: Author[]
  files: File[]
}

export type ManuscriptStatus = 
  | 'draft' 
  | 'submitted' 
  | 'under_review' 
  | 'revision_required' 
  | 'accepted' 
  | 'rejected'

export interface Author {
  id: number
  firstName: string
  lastName: string
  email: string
  orcid?: string
  affiliation?: string
  isCorresponding: boolean
}

// File Types
export interface File {
  id: number
  filename: string
  fileType: string
  fileSize: number
  uploadedAt: string
  s3Key: string
}

// API Response Types
export interface ApiResponse<T> {
  data: T
  message?: string
  error?: boolean
}

export interface PaginatedResponse<T> {
  results: T[]
  count: number
  next: string | null
  previous: string | null
}

