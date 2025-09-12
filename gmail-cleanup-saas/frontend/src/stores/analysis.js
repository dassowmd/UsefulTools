import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useAnalysisStore = defineStore('analysis', () => {
  const mailboxStats = ref(null)
  const analysis = ref(null)
  const messages = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Filtering and grouping state
  const filters = ref({
    sender: '',
    subject: '',
    hasAttachment: null,
    sizeMin: null,
    sizeMax: null,
    dateRange: null,
    labels: []
  })

  const groupBy = ref('sender') // 'sender', 'date', 'size', 'labels'
  const sortBy = ref('date')
  const sortOrder = ref('desc')

  const filteredMessages = computed(() => {
    let filtered = [...messages.value]

    // Apply filters
    if (filters.value.sender) {
      const senderFilter = filters.value.sender.toLowerCase()
      filtered = filtered.filter(msg => 
        msg.sender.toLowerCase().includes(senderFilter)
      )
    }

    if (filters.value.subject) {
      const subjectFilter = filters.value.subject.toLowerCase()
      filtered = filtered.filter(msg => 
        msg.subject.toLowerCase().includes(subjectFilter)
      )
    }

    if (filters.value.hasAttachment !== null) {
      filtered = filtered.filter(msg => 
        msg.has_attachment === filters.value.hasAttachment
      )
    }

    if (filters.value.sizeMin) {
      filtered = filtered.filter(msg => 
        msg.size >= filters.value.sizeMin
      )
    }

    if (filters.value.sizeMax) {
      filtered = filtered.filter(msg => 
        msg.size <= filters.value.sizeMax
      )
    }

    // Sort
    filtered.sort((a, b) => {
      let aVal, bVal
      
      switch (sortBy.value) {
        case 'date':
          aVal = new Date(a.date)
          bVal = new Date(b.date)
          break
        case 'size':
          aVal = a.size || 0
          bVal = b.size || 0
          break
        case 'sender':
          aVal = a.sender.toLowerCase()
          bVal = b.sender.toLowerCase()
          break
        case 'subject':
          aVal = a.subject.toLowerCase()
          bVal = b.subject.toLowerCase()
          break
        default:
          return 0
      }

      if (sortOrder.value === 'desc') {
        return aVal > bVal ? -1 : aVal < bVal ? 1 : 0
      } else {
        return aVal < bVal ? -1 : aVal > bVal ? 1 : 0
      }
    })

    return filtered
  })

  const groupedMessages = computed(() => {
    const groups = {}
    
    filteredMessages.value.forEach(message => {
      let groupKey
      
      switch (groupBy.value) {
        case 'sender':
          groupKey = message.sender.includes('@') 
            ? message.sender.split('@')[1] 
            : message.sender
          break
        case 'date':
          groupKey = new Date(message.date).toISOString().split('T')[0]
          break
        case 'size':
          const size = message.size || 0
          if (size < 1024) groupKey = 'Small (< 1KB)'
          else if (size < 1024 * 1024) groupKey = 'Medium (< 1MB)'
          else if (size < 10 * 1024 * 1024) groupKey = 'Large (< 10MB)'
          else groupKey = 'Very Large (> 10MB)'
          break
        case 'labels':
          groupKey = message.labels?.[0] || 'No Labels'
          break
        default:
          groupKey = 'All'
      }

      if (!groups[groupKey]) {
        groups[groupKey] = []
      }
      groups[groupKey].push(message)
    })

    // Sort groups by count
    return Object.entries(groups)
      .map(([key, messages]) => ({
        key,
        messages,
        count: messages.length,
        totalSize: messages.reduce((sum, msg) => sum + (msg.size || 0), 0)
      }))
      .sort((a, b) => b.count - a.count)
  })

  const getMailboxStats = async () => {
    try {
      loading.value = true
      const response = await api.get('/analysis/stats')
      mailboxStats.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to get mailbox stats'
    } finally {
      loading.value = false
    }
  }

  const analyzeMailbox = async (maxMessages = 1000) => {
    try {
      loading.value = true
      const response = await api.post('/analysis/mailbox', {
        max_messages: maxMessages,
        include_suggestions: true
      })
      analysis.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Analysis failed'
    } finally {
      loading.value = false
    }
  }

  const searchMessages = async (criteria) => {
    try {
      loading.value = true
      const response = await api.post('/analysis/search', {
        criteria,
        max_results: 500
      })
      messages.value = response.data.messages
    } catch (err) {
      error.value = err.response?.data?.detail || 'Search failed'
    } finally {
      loading.value = false
    }
  }

  const previewRule = async (ruleData) => {
    try {
      const response = await api.post('/analysis/preview-rule', ruleData, {
        params: { max_results: 100 }
      })
      return response.data
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Rule preview failed')
    }
  }

  const updateFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const clearFilters = () => {
    filters.value = {
      sender: '',
      subject: '',
      hasAttachment: null,
      sizeMin: null,
      sizeMax: null,
      dateRange: null,
      labels: []
    }
  }

  return {
    mailboxStats,
    analysis,
    messages,
    loading,
    error,
    filters,
    groupBy,
    sortBy,
    sortOrder,
    filteredMessages,
    groupedMessages,
    getMailboxStats,
    analyzeMailbox,
    searchMessages,
    previewRule,
    updateFilters,
    clearFilters
  }
})