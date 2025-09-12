import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!user.value)

  const checkAuth = async () => {
    try {
      loading.value = true
      const response = await api.get('/auth/status')
      
      if (response.data.success) {
        user.value = response.data.user_info
      } else {
        user.value = null
      }
    } catch (err) {
      console.error('Auth check failed:', err)
      user.value = null
    } finally {
      loading.value = false
    }
  }

  const login = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post('/auth/login')
      
      if (response.data.success) {
        user.value = response.data.user_info
        return true
      } else {
        error.value = response.data.message || 'Login failed'
        return false
      }
    } catch (err) {
      console.error('Login failed:', err)
      error.value = err.response?.data?.detail || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      loading.value = true
      await api.post('/auth/logout')
    } catch (err) {
      console.error('Logout failed:', err)
    } finally {
      user.value = null
      loading.value = false
    }
  }

  const testConnection = async () => {
    try {
      const response = await api.get('/auth/test-connection')
      return response.data.success
    } catch (err) {
      console.error('Connection test failed:', err)
      return false
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    checkAuth,
    login,
    logout,
    testConnection
  }
})