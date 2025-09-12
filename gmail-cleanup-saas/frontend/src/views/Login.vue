<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Gmail Cleanup
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Modern email management and cleanup tool
        </p>
      </div>
      
      <div class="card p-8">
        <div class="space-y-6">
          <!-- Error message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
            <div class="flex">
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">
                  Authentication Error
                </h3>
                <div class="mt-2 text-sm text-red-700">
                  {{ error }}
                </div>
              </div>
            </div>
          </div>

          <!-- Login form -->
          <div>
            <div class="text-center mb-6">
              <p class="text-gray-600 mb-4">
                Sign in with your Google account to access Gmail Cleanup
              </p>
            </div>
            
            <button
              @click="handleLogin"
              :disabled="loading"
              class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span v-if="!loading" class="flex items-center">
                <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Sign in with Google
              </span>
              <span v-else class="flex items-center">
                <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Signing in...
              </span>
            </button>
          </div>

          <!-- Setup instructions -->
          <div class="text-sm text-gray-500">
            <details>
              <summary class="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                First time setup instructions
              </summary>
              <div class="mt-3 space-y-2">
                <p>1. Ensure you have Google OAuth2 credentials set up</p>
                <p>2. The Gmail API must be enabled in your Google Cloud Console</p>
                <p>3. Your OAuth2 client must be configured for this application</p>
                <p class="mt-3 text-xs text-gray-400">
                  If you're having trouble, check the documentation for setup instructions.
                </p>
              </div>
            </details>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const loading = computed(() => authStore.loading)
const error = computed(() => authStore.error)

const handleLogin = async () => {
  const success = await authStore.login()
  if (success) {
    router.push('/dashboard')
  }
}
</script>