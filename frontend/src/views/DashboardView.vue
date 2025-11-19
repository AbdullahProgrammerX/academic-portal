<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <p>Welcome, {{ authStore.user?.email }}</p>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>
