<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav v-if="isAuthenticated" class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <h1 class="text-xl font-bold text-gray-900">Gmail Cleanup</h1>
            </div>
            <div class="hidden sm:ml-8 sm:flex sm:space-x-8">
              <router-link
                to="/dashboard"
                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors"
                active-class="border-primary-500 text-primary-600"
              >
                Dashboard
              </router-link>
              <router-link
                to="/analysis"
                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors"
                active-class="border-primary-500 text-primary-600"
              >
                Analysis
              </router-link>
              <router-link
                to="/rules"
                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors"
                active-class="border-primary-500 text-primary-600"
              >
                Rules
              </router-link>
              <router-link
                to="/processing"
                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors"
                active-class="border-primary-500 text-primary-600"
              >
                Processing
              </router-link>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">{{ user?.email }}</span>
            <button
              @click="handleLogout"
              class="btn btn-secondary text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main content -->
    <main>
      <router-view />
    </main>

    <!-- Loading overlay -->
    <div
      v-if="authLoading"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
        <span>Loading...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)
const authLoading = computed(() => authStore.loading)

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  // Check authentication status on app load
  authStore.checkAuth()
})
</script>