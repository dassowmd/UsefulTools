import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useProcessingStore = defineStore('processing', () => {
  const processingResults = ref([])
  const isProcessing = ref(false)
  const processingProgress = ref(0)
  const error = ref(null)

  const totalProcessed = computed(() => 
    processingResults.value.reduce((sum, result) => sum + result.processed_count, 0)
  )

  const totalSucceeded = computed(() => 
    processingResults.value.reduce((sum, result) => sum + result.success_count, 0)
  )

  const totalFailed = computed(() => 
    processingResults.value.reduce((sum, result) => sum + result.error_count, 0)
  )

  const successRate = computed(() => {
    const total = totalProcessed.value
    return total > 0 ? (totalSucceeded.value / total) * 100 : 0
  })

  const processRules = async (options = {}) => {
    try {
      isProcessing.value = true
      processingProgress.value = 0
      error.value = null
      
      const requestData = {
        rule_ids: options.ruleIds || null,
        dry_run: options.dryRun || false,
        max_messages_per_rule: options.maxMessages || null
      }

      const response = await api.post('/processing/rules/run', requestData)
      
      processingResults.value = response.data.results
      processingProgress.value = 100
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Processing failed'
      throw err
    } finally {
      isProcessing.value = false
    }
  }

  const validateRules = async (ruleIds = null) => {
    try {
      const response = await api.post('/processing/rules/validate', {
        rule_ids: ruleIds,
        dry_run: true
      })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Validation failed'
      throw err
    }
  }

  const batchOperation = async (messageIds, operation, parameters = {}) => {
    try {
      isProcessing.value = true
      
      const response = await api.post('/processing/batch', {
        message_ids: messageIds,
        operation,
        parameters
      })
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Batch operation failed'
      throw err
    } finally {
      isProcessing.value = false
    }
  }

  const clearResults = () => {
    processingResults.value = []
    error.value = null
    processingProgress.value = 0
  }

  return {
    processingResults,
    isProcessing,
    processingProgress,
    error,
    totalProcessed,
    totalSucceeded,
    totalFailed,
    successRate,
    processRules,
    validateRules,
    batchOperation,
    clearResults
  }
})