import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useRulesStore = defineStore('rules', () => {
  const rules = ref([])
  const templates = ref([])
  const loading = ref(false)
  const error = ref(null)

  const enabledRules = computed(() => 
    rules.value.filter(rule => rule.enabled)
  )

  const rulesByPriority = computed(() => 
    [...rules.value].sort((a, b) => b.priority - a.priority)
  )

  const fetchRules = async () => {
    try {
      loading.value = true
      const response = await api.get('/rules/')
      rules.value = response.data.rules
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch rules'
    } finally {
      loading.value = false
    }
  }

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/rules/templates/')
      templates.value = response.data.templates
    } catch (err) {
      console.error('Failed to fetch templates:', err)
    }
  }

  const createRule = async (ruleData) => {
    try {
      loading.value = true
      const response = await api.post('/rules/', ruleData)
      rules.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create rule'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateRule = async (ruleId, ruleData) => {
    try {
      loading.value = true
      const response = await api.put(`/rules/${ruleId}`, ruleData)
      const index = rules.value.findIndex(r => r.id === ruleId)
      if (index !== -1) {
        rules.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update rule'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteRule = async (ruleId) => {
    try {
      loading.value = true
      await api.delete(`/rules/${ruleId}`)
      rules.value = rules.value.filter(r => r.id !== ruleId)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete rule'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createRuleFromTemplate = async (templateId, customizations = {}) => {
    try {
      loading.value = true
      const response = await api.post(`/rules/templates/${templateId}`, {
        customizations
      })
      rules.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create rule from template'
      throw err
    } finally {
      loading.value = false
    }
  }

  const toggleRule = async (ruleId) => {
    const rule = rules.value.find(r => r.id === ruleId)
    if (!rule) return

    try {
      await updateRule(ruleId, { enabled: !rule.enabled })
    } catch (err) {
      console.error('Failed to toggle rule:', err)
    }
  }

  return {
    rules,
    templates,
    loading,
    error,
    enabledRules,
    rulesByPriority,
    fetchRules,
    fetchTemplates,
    createRule,
    updateRule,
    deleteRule,
    createRuleFromTemplate,
    toggleRule
  }
})