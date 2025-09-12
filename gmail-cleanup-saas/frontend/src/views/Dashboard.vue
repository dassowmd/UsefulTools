<template>
  <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p class="mt-2 text-gray-600">Overview of your Gmail cleanup activities</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="card p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"></path>
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"></path>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Messages</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ formatNumber(mailboxStats?.total_messages || 0) }}
            </p>
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2L3 7v11a2 2 0 002 2h10a2 2 0 002-2V7l-7-5zM8 15a1 1 0 11-2 0 1 1 0 012 0zm4 0a1 1 0 11-2 0 1 1 0 012 0zm2-8H6V6h8v1z"></path>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Unread Messages</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ formatNumber(mailboxStats?.unread_messages || 0) }}
            </p>
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"></path>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Active Rules</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ enabledRules.length }}
            </p>
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Last Processing</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ totalProcessed || 0 }}
            </p>
            <p class="text-xs text-gray-500">messages processed</p>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Recent Rules -->
      <div class="card">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Recent Rules</h3>
        </div>
        <div class="p-6">
          <div v-if="rules.length === 0" class="text-center py-8">
            <p class="text-gray-500">No rules created yet</p>
            <router-link to="/rules" class="text-primary-600 hover:text-primary-800 font-medium">
              Create your first rule
            </router-link>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="rule in rules.slice(0, 5)"
              :key="rule.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div>
                <p class="font-medium text-gray-900">{{ rule.name }}</p>
                <p class="text-sm text-gray-600">{{ rule.action.type }}</p>
              </div>
              <div class="flex items-center space-x-2">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full',
                    rule.enabled
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  ]"
                >
                  {{ rule.enabled ? 'Enabled' : 'Disabled' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="card">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Quick Actions</h3>
        </div>
        <div class="p-6">
          <div class="space-y-4">
            <router-link
              to="/analysis"
              class="block p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
                <div class="ml-4">
                  <h4 class="text-lg font-medium text-gray-900">Analyze Mailbox</h4>
                  <p class="text-gray-600">Get insights about your email patterns</p>
                </div>
              </div>
            </router-link>

            <router-link
              to="/rules"
              class="block p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"></path>
                  </svg>
                </div>
                <div class="ml-4">
                  <h4 class="text-lg font-medium text-gray-900">Manage Rules</h4>
                  <p class="text-gray-600">Create and edit cleanup rules</p>
                </div>
              </div>
            </router-link>

            <router-link
              to="/processing"
              class="block p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m4-10V8a2 2 0 01-2 2H8a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2z"></path>
                  </svg>
                </div>
                <div class="ml-4">
                  <h4 class="text-lg font-medium text-gray-900">Run Processing</h4>
                  <p class="text-gray-600">Execute your cleanup rules</p>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Processing Results -->
    <div v-if="processingResults.length > 0" class="mt-8">
      <div class="card">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Latest Processing Results</h3>
        </div>
        <div class="p-6">
          <div class="space-y-4">
            <div
              v-for="result in processingResults.slice(0, 3)"
              :key="result.rule_id"
              class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
            >
              <div>
                <p class="font-medium text-gray-900">{{ result.rule_name }}</p>
                <p class="text-sm text-gray-600">
                  {{ result.success_count }} of {{ result.processed_count }} processed successfully
                </p>
              </div>
              <div class="text-right">
                <p class="text-sm font-medium text-green-600">
                  {{ formatPercentage(result.success_count, result.processed_count) }}
                </p>
                <p class="text-xs text-gray-500">success rate</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useAnalysisStore } from '../stores/analysis'
import { useRulesStore } from '../stores/rules'
import { useProcessingStore } from '../stores/processing'
import { formatNumber, formatPercentage } from '../utils/formatters'

const authStore = useAuthStore()
const analysisStore = useAnalysisStore()
const rulesStore = useRulesStore()
const processingStore = useProcessingStore()

const mailboxStats = computed(() => analysisStore.mailboxStats)
const rules = computed(() => rulesStore.rules)
const enabledRules = computed(() => rulesStore.enabledRules)
const processingResults = computed(() => processingStore.processingResults)
const totalProcessed = computed(() => processingStore.totalProcessed)

onMounted(async () => {
  // Load dashboard data
  await Promise.all([
    analysisStore.getMailboxStats(),
    rulesStore.fetchRules()
  ])
})
</script>