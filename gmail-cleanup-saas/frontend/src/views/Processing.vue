<template>
  <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Email Processing</h1>
      <p class="mt-2 text-gray-600">Execute your cleanup rules and monitor progress</p>
    </div>

    <!-- Processing Controls -->
    <div class="card p-6 mb-8">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
        <h3 class="text-lg font-medium text-gray-900">Processing Controls</h3>
        <div class="mt-4 lg:mt-0 flex flex-wrap gap-3">
          <button
            @click="runValidation"
            :disabled="isProcessing || rules.length === 0"
            class="btn btn-secondary"
          >
            Validate Rules
          </button>
          <button
            @click="runDryRun"
            :disabled="isProcessing || rules.length === 0"
            class="btn btn-primary"
          >
            <span v-if="!isProcessing">Dry Run</span>
            <span v-else class="flex items-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Processing...
            </span>
          </button>
          <button
            @click="runProcessing"
            :disabled="isProcessing || rules.length === 0"
            class="btn btn-success"
          >
            Execute Rules
          </button>
          <button
            @click="clearResults"
            :disabled="isProcessing"
            class="btn btn-secondary"
          >
            Clear Results
          </button>
        </div>
      </div>

      <!-- Processing Options -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Max Messages Per Rule</label>
          <input
            v-model.number="processingOptions.maxMessages"
            type="number"
            min="1"
            max="10000"
            class="input"
            placeholder="Leave empty for no limit"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Rules to Process</label>
          <select v-model="processingOptions.selectedRules" class="select" multiple>
            <option value="">All Enabled Rules</option>
            <option
              v-for="rule in enabledRules"
              :key="rule.id"
              :value="rule.id"
            >
              {{ rule.name }}
            </option>
          </select>
        </div>
        <div class="flex items-end">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Safety Mode</label>
            <div class="flex items-center space-x-4">
              <label class="flex items-center">
                <input
                  v-model="processingOptions.dryRun"
                  type="checkbox"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                >
                <span class="ml-2 text-sm text-gray-900">Dry Run Only</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Progress Bar -->
    <div v-if="isProcessing" class="card p-6 mb-8">
      <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700">Processing Progress</span>
          <span class="text-sm text-gray-600">{{ processingProgress }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div
            class="bg-primary-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${processingProgress}%` }"
          ></div>
        </div>
      </div>
      <div class="text-center">
        <p class="text-sm text-gray-600">Processing your email cleanup rules...</p>
      </div>
    </div>

    <!-- Processing Summary -->
    <div v-if="processingResults.length > 0" class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="card p-6">
        <div class="text-center">
          <div class="text-3xl font-bold text-gray-900">{{ totalProcessed }}</div>
          <div class="text-sm text-gray-600">Total Processed</div>
        </div>
      </div>
      <div class="card p-6">
        <div class="text-center">
          <div class="text-3xl font-bold text-green-600">{{ totalSucceeded }}</div>
          <div class="text-sm text-gray-600">Succeeded</div>
        </div>
      </div>
      <div class="card p-6">
        <div class="text-center">
          <div class="text-3xl font-bold text-red-600">{{ totalFailed }}</div>
          <div class="text-sm text-gray-600">Failed</div>
        </div>
      </div>
      <div class="card p-6">
        <div class="text-center">
          <div class="text-3xl font-bold text-primary-600">{{ successRate.toFixed(1) }}%</div>
          <div class="text-sm text-gray-600">Success Rate</div>
        </div>
      </div>
    </div>

    <!-- Processing Results -->
    <div v-if="processingResults.length > 0" class="card">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Processing Results</h3>
        <p class="text-sm text-gray-600">{{ processingResults.length }} rules processed</p>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rule
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Matched
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Processed
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Success Rate
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Duration
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="result in processingResults"
              :key="result.rule_id"
              class="hover:bg-gray-50"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ result.rule_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatNumber(result.matched_count) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatNumber(result.processed_count) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-1">
                    <div class="text-sm font-medium text-gray-900">
                      {{ ((result.success_count / result.processed_count) * 100).toFixed(1) }}%
                    </div>
                    <div class="w-16 bg-gray-200 rounded-full h-2 mt-1">
                      <div
                        class="bg-green-600 h-2 rounded-full"
                        :style="{ width: `${(result.success_count / result.processed_count) * 100}%` }"
                      ></div>
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ result.execution_time ? formatDuration(result.execution_time) : '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    result.error_count === 0
                      ? 'bg-green-100 text-green-800'
                      : result.success_count > 0
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  ]"
                >
                  {{ result.error_count === 0 ? 'Success' : result.success_count > 0 ? 'Partial' : 'Failed' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Error Details -->
      <div v-if="hasErrors" class="border-t border-gray-200 p-6">
        <h4 class="text-sm font-medium text-gray-900 mb-3">Error Details</h4>
        <div class="space-y-2">
          <div
            v-for="result in processingResults.filter(r => r.errors.length > 0)"
            :key="result.rule_id"
            class="bg-red-50 border border-red-200 rounded-md p-3"
          >
            <p class="text-sm font-medium text-red-800">{{ result.rule_name }}</p>
            <ul class="mt-1 text-sm text-red-700">
              <li v-for="error in result.errors" :key="error">• {{ error }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Rules Status -->
    <div v-if="!isProcessing && rules.length === 0" class="card p-8 text-center">
      <div class="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
        <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"></path>
        </svg>
      </div>
      <h4 class="text-lg font-medium text-gray-900 mb-2">No rules to process</h4>
      <p class="text-gray-600 mb-6">Create some email cleanup rules before running processing</p>
      <router-link to="/rules" class="btn btn-primary">
        Create Rules
      </router-link>
    </div>

    <div v-else-if="!isProcessing && enabledRules.length === 0" class="card p-8 text-center">
      <div class="mx-auto w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mb-4">
        <svg class="w-12 h-12 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
        </svg>
      </div>
      <h4 class="text-lg font-medium text-gray-900 mb-2">No enabled rules</h4>
      <p class="text-gray-600 mb-6">You have {{ rules.length }} rules, but none are enabled</p>
      <router-link to="/rules" class="btn btn-primary">
        Enable Rules
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProcessingStore } from '../stores/processing'
import { useRulesStore } from '../stores/rules'
import { formatNumber, formatDuration } from '../utils/formatters'

const processingStore = useProcessingStore()
const rulesStore = useRulesStore()

const processingOptions = ref({
  maxMessages: null,
  selectedRules: [],
  dryRun: true
})

const isProcessing = computed(() => processingStore.isProcessing)
const processingProgress = computed(() => processingStore.processingProgress)
const processingResults = computed(() => processingStore.processingResults)
const totalProcessed = computed(() => processingStore.totalProcessed)
const totalSucceeded = computed(() => processingStore.totalSucceeded)
const totalFailed = computed(() => processingStore.totalFailed)
const successRate = computed(() => processingStore.successRate)

const rules = computed(() => rulesStore.rules)
const enabledRules = computed(() => rulesStore.enabledRules)

const hasErrors = computed(() => 
  processingResults.value.some(result => result.errors && result.errors.length > 0)
)

const runValidation = async () => {
  try {
    const result = await processingStore.validateRules(
      processingOptions.value.selectedRules.length > 0 
        ? processingOptions.value.selectedRules 
        : null
    )
    
    // Show validation results (could be a modal or notification)
    console.log('Validation results:', result)
  } catch (error) {
    console.error('Validation failed:', error)
  }
}

const runDryRun = async () => {
  try {
    await processingStore.processRules({
      ruleIds: processingOptions.value.selectedRules.length > 0 
        ? processingOptions.value.selectedRules 
        : null,
      dryRun: true,
      maxMessages: processingOptions.value.maxMessages
    })
  } catch (error) {
    console.error('Dry run failed:', error)
  }
}

const runProcessing = async () => {
  if (!confirm('This will execute your cleanup rules and make actual changes to your emails. Continue?')) {
    return
  }

  try {
    await processingStore.processRules({
      ruleIds: processingOptions.value.selectedRules.length > 0 
        ? processingOptions.value.selectedRules 
        : null,
      dryRun: false,
      maxMessages: processingOptions.value.maxMessages
    })
  } catch (error) {
    console.error('Processing failed:', error)
  }
}

const clearResults = () => {
  processingStore.clearResults()
}

onMounted(async () => {
  await rulesStore.fetchRules()
})
</script>