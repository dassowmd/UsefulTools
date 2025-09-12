<template>
  <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Mailbox Analysis</h1>
      <p class="mt-2 text-gray-600">Deep insights into your email patterns with advanced filtering and grouping</p>
    </div>

    <!-- Analysis Controls -->
    <div class="card p-6 mb-8">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
        <h3 class="text-lg font-medium text-gray-900">Analysis Controls</h3>
        <div class="mt-4 lg:mt-0 flex space-x-3">
          <button
            @click="runAnalysis"
            :disabled="loading"
            class="btn btn-primary"
          >
            <span v-if="!loading">Run Analysis</span>
            <span v-else class="flex items-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Analyzing...
            </span>
          </button>
          <button
            @click="searchMessages"
            :disabled="loading"
            class="btn btn-secondary"
          >
            Search Messages
          </button>
        </div>
      </div>

      <!-- Search and Filter Controls -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sender</label>
          <input
            v-model="filters.sender"
            type="text"
            placeholder="Filter by sender..."
            class="input"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Subject</label>
          <input
            v-model="filters.subject"
            type="text"
            placeholder="Filter by subject..."
            class="input"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Has Attachment</label>
          <select v-model="filters.hasAttachment" class="select">
            <option :value="null">Any</option>
            <option :value="true">With Attachments</option>
            <option :value="false">Without Attachments</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Size Range</label>
          <div class="flex space-x-2">
            <input
              v-model.number="filters.sizeMin"
              type="number"
              placeholder="Min KB"
              class="input"
            >
            <input
              v-model.number="filters.sizeMax"
              type="number"
              placeholder="Max KB"
              class="input"
            >
          </div>
        </div>
      </div>

      <div class="mt-4 flex flex-wrap items-center gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Group By</label>
          <select v-model="groupBy" class="select">
            <option value="sender">Sender Domain</option>
            <option value="date">Date</option>
            <option value="size">Message Size</option>
            <option value="labels">Labels</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
          <select v-model="sortBy" class="select">
            <option value="date">Date</option>
            <option value="sender">Sender</option>
            <option value="subject">Subject</option>
            <option value="size">Size</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Order</label>
          <select v-model="sortOrder" class="select">
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="clearFilters"
            class="btn btn-secondary"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Analysis Overview -->
    <div v-if="analysis" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="card p-6">
        <h4 class="text-lg font-semibold text-gray-900">{{ formatNumber(analysis.total_messages) }}</h4>
        <p class="text-sm text-gray-600">Messages Analyzed</p>
      </div>
      <div class="card p-6">
        <h4 class="text-lg font-semibold text-gray-900">{{ formatNumber(analysis.unread_messages) }}</h4>
        <p class="text-sm text-gray-600">Unread Messages</p>
      </div>
      <div class="card p-6">
        <h4 class="text-lg font-semibold text-gray-900">{{ formatNumber(analysis.old_messages) }}</h4>
        <p class="text-sm text-gray-600">Old Messages (>1 year)</p>
      </div>
      <div class="card p-6">
        <h4 class="text-lg font-semibold text-gray-900">{{ formatNumber(analysis.unique_senders) }}</h4>
        <p class="text-sm text-gray-600">Unique Senders</p>
      </div>
    </div>

    <!-- Grouped Results -->
    <div v-if="groupedMessages.length > 0" class="card mb-8">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">
          Grouped by {{ groupByLabel }} ({{ groupedMessages.length }} groups)
        </h3>
        <p class="text-sm text-gray-600">{{ filteredMessages.length }} total messages</p>
      </div>
      <div class="divide-y divide-gray-200">
        <div
          v-for="group in groupedMessages.slice(0, showAllGroups ? undefined : 10)"
          :key="group.key"
          class="p-6"
        >
          <div class="flex items-center justify-between mb-3">
            <div>
              <h4 class="text-lg font-medium text-gray-900">{{ group.key }}</h4>
              <p class="text-sm text-gray-600">
                {{ group.count }} messages • {{ formatFileSize(group.totalSize) }} total
              </p>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="toggleGroupExpanded(group.key)"
                class="btn btn-secondary btn-sm"
              >
                {{ expandedGroups.has(group.key) ? 'Hide' : 'Show' }} Messages
              </button>
              <button
                @click="selectGroupForProcessing(group)"
                class="btn btn-primary btn-sm"
              >
                Create Rule
              </button>
            </div>
          </div>

          <!-- Progress bar showing relative size -->
          <div class="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div
              class="bg-primary-600 h-2 rounded-full"
              :style="{ width: `${(group.count / filteredMessages.length) * 100}%` }"
            ></div>
          </div>

          <!-- Expanded message list -->
          <div v-if="expandedGroups.has(group.key)" class="space-y-2">
            <div
              v-for="message in group.messages.slice(0, 20)"
              :key="message.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-sm"
            >
              <div class="flex-1 min-w-0">
                <p class="font-medium text-gray-900 truncate">{{ message.sender }}</p>
                <p class="text-gray-600 truncate">{{ truncateText(message.subject, 60) }}</p>
              </div>
              <div class="flex items-center space-x-4 text-xs text-gray-500">
                <span>{{ formatDate(message.date) }}</span>
                <span v-if="message.size">{{ formatFileSize(message.size) }}</span>
                <span v-if="message.is_unread" class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full">
                  Unread
                </span>
              </div>
            </div>
            <div v-if="group.messages.length > 20" class="text-center py-2">
              <span class="text-sm text-gray-500">... and {{ group.messages.length - 20 }} more messages</span>
            </div>
          </div>
        </div>
      </div>
      <div v-if="groupedMessages.length > 10" class="px-6 py-4 border-t border-gray-200">
        <button
          @click="showAllGroups = !showAllGroups"
          class="text-primary-600 hover:text-primary-800 font-medium"
        >
          {{ showAllGroups ? 'Show Less' : `Show All ${groupedMessages.length} Groups` }}
        </button>
      </div>
    </div>

    <!-- Top Sender Domains Chart -->
    <div v-if="analysis?.top_sender_domains?.length" class="card mb-8">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Top Sender Domains</h3>
      </div>
      <div class="p-6">
        <div class="space-y-4">
          <div
            v-for="domain in analysis.top_sender_domains.slice(0, 15)"
            :key="domain.domain"
            class="flex items-center justify-between"
          >
            <div class="flex-1">
              <div class="flex items-center justify-between mb-1">
                <span class="font-medium text-gray-900">{{ domain.domain }}</span>
                <span class="text-sm text-gray-600">{{ domain.count }} messages ({{ domain.percentage }}%)</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-primary-600 h-2 rounded-full"
                  :style="{ width: `${domain.percentage}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Cleanup Suggestions -->
    <div v-if="analysis?.suggestions?.length" class="card">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Cleanup Suggestions</h3>
      </div>
      <div class="divide-y divide-gray-200">
        <div
          v-for="suggestion in analysis.suggestions"
          :key="suggestion.title"
          class="p-6"
        >
          <div class="flex items-start justify-between">
            <div>
              <h4 class="text-lg font-medium text-gray-900">{{ suggestion.title }}</h4>
              <p class="text-gray-600 mt-1">{{ suggestion.description }}</p>
            </div>
            <button
              v-if="suggestion.rule"
              @click="createRuleFromSuggestion(suggestion)"
              class="btn btn-primary btn-sm"
            >
              Create Rule
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAnalysisStore } from '../stores/analysis'
import { useRulesStore } from '../stores/rules'
import { formatNumber, formatFileSize, formatDate, formatPercentage, truncateText } from '../utils/formatters'

const analysisStore = useAnalysisStore()
const rulesStore = useRulesStore()

const loading = computed(() => analysisStore.loading)
const analysis = computed(() => analysisStore.analysis)
const filteredMessages = computed(() => analysisStore.filteredMessages)
const groupedMessages = computed(() => analysisStore.groupedMessages)

const filters = computed({
  get: () => analysisStore.filters,
  set: (value) => analysisStore.updateFilters(value)
})

const groupBy = computed({
  get: () => analysisStore.groupBy,
  set: (value) => analysisStore.groupBy = value
})

const sortBy = computed({
  get: () => analysisStore.sortBy,
  set: (value) => analysisStore.sortBy = value
})

const sortOrder = computed({
  get: () => analysisStore.sortOrder,
  set: (value) => analysisStore.sortOrder = value
})

const showAllGroups = ref(false)
const expandedGroups = ref(new Set())

const groupByLabel = computed(() => {
  const labels = {
    sender: 'Sender Domain',
    date: 'Date',
    size: 'Message Size',
    labels: 'Labels'
  }
  return labels[groupBy.value] || 'Group'
})

const runAnalysis = async () => {
  await analysisStore.analyzeMailbox(1000)
}

const searchMessages = async () => {
  const criteria = {}
  
  if (filters.value.sender) criteria.from = filters.value.sender
  if (filters.value.subject) criteria.subject_contains = filters.value.subject
  if (filters.value.hasAttachment !== null) criteria.has_attachment = filters.value.hasAttachment
  if (filters.value.sizeMin) criteria.size_larger_than = filters.value.sizeMin * 1024
  if (filters.value.sizeMax) criteria.size_smaller_than = filters.value.sizeMax * 1024

  await analysisStore.searchMessages(criteria)
}

const clearFilters = () => {
  analysisStore.clearFilters()
}

const toggleGroupExpanded = (groupKey) => {
  if (expandedGroups.value.has(groupKey)) {
    expandedGroups.value.delete(groupKey)
  } else {
    expandedGroups.value.add(groupKey)
  }
}

const selectGroupForProcessing = (group) => {
  // Create rule criteria based on the group
  let criteria = {}
  
  switch (groupBy.value) {
    case 'sender':
      criteria.from_domain = group.key
      break
    case 'size':
      // Set size criteria based on group
      if (group.key.includes('Small')) {
        criteria.size_smaller_than = 1024
      } else if (group.key.includes('Medium')) {
        criteria.size_larger_than = 1024
        criteria.size_smaller_than = 1024 * 1024
      }
      break
    case 'labels':
      if (group.key !== 'No Labels') {
        criteria.labels = [group.key]
      }
      break
  }

  // Navigate to rules page with pre-filled criteria
  // This would be implemented with router.push and state sharing
  console.log('Create rule with criteria:', criteria)
}

const createRuleFromSuggestion = async (suggestion) => {
  try {
    if (suggestion.rule) {
      await rulesStore.createRule(suggestion.rule)
      // Show success message
    }
  } catch (error) {
    console.error('Failed to create rule from suggestion:', error)
  }
}

// Watch for filter changes to trigger live updates
watch([filters, groupBy, sortBy, sortOrder], () => {
  // The computed properties will automatically update
}, { deep: true })

onMounted(() => {
  // Load initial analysis if not already loaded
  if (!analysis.value) {
    runAnalysis()
  }
})
</script>

<style scoped>
.btn-sm {
  @apply px-3 py-1 text-sm;
}
</style>