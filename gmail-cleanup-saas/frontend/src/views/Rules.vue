<template>
  <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
    <div class="mb-8 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Rules Management</h1>
        <p class="mt-2 text-gray-600">Create and manage email cleanup rules</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="btn btn-primary"
      >
        Create Rule
      </button>
    </div>

    <!-- Rules Table -->
    <div class="card">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">
            Your Rules ({{ rules.length }})
          </h3>
          <div class="flex items-center space-x-3">
            <span class="text-sm text-gray-600">{{ enabledRules.length }} enabled</span>
            <button
              @click="fetchRules"
              :disabled="loading"
              class="btn btn-secondary btn-sm"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div v-if="rules.length === 0" class="p-8 text-center">
        <div class="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"></path>
          </svg>
        </div>
        <h4 class="text-lg font-medium text-gray-900 mb-2">No rules created yet</h4>
        <p class="text-gray-600 mb-6">Get started by creating your first email cleanup rule</p>
        <button
          @click="showCreateModal = true"
          class="btn btn-primary"
        >
          Create Your First Rule
        </button>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rule
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Action
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Priority
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Run
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="rule in rulesByPriority" :key="rule.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div>
                  <div class="text-sm font-medium text-gray-900">{{ rule.name }}</div>
                  <div class="text-sm text-gray-500">{{ truncateText(rule.description, 60) }}</div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getActionBadgeClass(rule.action.type)">
                  {{ rule.action.type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  @click="toggleRule(rule.id)"
                  :class="[
                    'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium cursor-pointer',
                    rule.enabled
                      ? 'bg-green-100 text-green-800 hover:bg-green-200'
                      : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                  ]"
                >
                  {{ rule.enabled ? 'Enabled' : 'Disabled' }}
                </button>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ rule.priority }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ rule.last_run_at ? formatDate(rule.last_run_at) : 'Never' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end space-x-2">
                  <button
                    @click="editRule(rule)"
                    class="text-primary-600 hover:text-primary-900"
                  >
                    Edit
                  </button>
                  <button
                    @click="deleteRule(rule.id)"
                    class="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Rule Templates -->
    <div v-if="templates.length > 0" class="mt-8 card">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Rule Templates</h3>
        <p class="text-sm text-gray-600">Quick start with pre-built rule templates</p>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="template in templates.slice(0, 6)"
            :key="template.id"
            class="border border-gray-200 rounded-lg p-4 hover:border-primary-300 hover:bg-primary-50 cursor-pointer transition-colors"
            @click="createFromTemplate(template)"
          >
            <div class="flex items-start justify-between">
              <div>
                <h4 class="font-medium text-gray-900">{{ template.name }}</h4>
                <p class="text-sm text-gray-600 mt-1">{{ truncateText(template.description, 80) }}</p>
                <div class="mt-2 flex items-center space-x-2">
                  <span class="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full">
                    {{ template.category }}
                  </span>
                  <span
                    :class="[
                      'text-xs px-2 py-1 rounded-full',
                      template.risk_level === 'low' ? 'bg-green-100 text-green-700' :
                      template.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    ]"
                  >
                    {{ template.risk_level }} risk
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Rule Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="showCreateModal = false"
    >
      <div
        class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white"
        @click.stop
      >
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ editingRule ? 'Edit Rule' : 'Create New Rule' }}
          </h3>
          
          <!-- Rule form would go here -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Rule Name</label>
              <input
                v-model="ruleForm.name"
                type="text"
                class="input"
                placeholder="Enter rule name..."
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="ruleForm.description"
                class="input"
                rows="3"
                placeholder="Describe what this rule does..."
              ></textarea>
            </div>

            <!-- Simplified criteria for demo -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Sender Contains</label>
              <input
                v-model="ruleForm.criteria.from"
                type="text"
                class="input"
                placeholder="e.g., @example.com"
              >
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Action</label>
              <select v-model="ruleForm.action.type" class="select">
                <option value="delete">Delete</option>
                <option value="mark_read">Mark as Read</option>
                <option value="add_label">Add Label</option>
                <option value="archive">Archive</option>
              </select>
            </div>

            <div class="flex items-center">
              <input
                v-model="ruleForm.enabled"
                type="checkbox"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              >
              <label class="ml-2 block text-sm text-gray-900">
                Enable this rule
              </label>
            </div>
          </div>

          <div class="flex items-center justify-end space-x-3 mt-6">
            <button
              @click="showCreateModal = false"
              class="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              @click="saveRule"
              class="btn btn-primary"
            >
              {{ editingRule ? 'Update Rule' : 'Create Rule' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRulesStore } from '../stores/rules'
import { formatDate, truncateText } from '../utils/formatters'

const rulesStore = useRulesStore()

const loading = computed(() => rulesStore.loading)
const rules = computed(() => rulesStore.rules)
const enabledRules = computed(() => rulesStore.enabledRules)
const rulesByPriority = computed(() => rulesStore.rulesByPriority)
const templates = computed(() => rulesStore.templates)

const showCreateModal = ref(false)
const editingRule = ref(null)
const ruleForm = ref({
  name: '',
  description: '',
  criteria: {
    from: ''
  },
  action: {
    type: 'delete'
  },
  enabled: true,
  priority: 0
})

const fetchRules = async () => {
  await rulesStore.fetchRules()
}

const toggleRule = async (ruleId) => {
  await rulesStore.toggleRule(ruleId)
}

const editRule = (rule) => {
  editingRule.value = rule
  ruleForm.value = {
    name: rule.name,
    description: rule.description,
    criteria: { ...rule.criteria },
    action: { ...rule.action },
    enabled: rule.enabled,
    priority: rule.priority
  }
  showCreateModal.value = true
}

const deleteRule = async (ruleId) => {
  if (confirm('Are you sure you want to delete this rule?')) {
    try {
      await rulesStore.deleteRule(ruleId)
    } catch (error) {
      console.error('Failed to delete rule:', error)
    }
  }
}

const createFromTemplate = async (template) => {
  try {
    await rulesStore.createRuleFromTemplate(template.id)
  } catch (error) {
    console.error('Failed to create rule from template:', error)
  }
}

const saveRule = async () => {
  try {
    if (editingRule.value) {
      await rulesStore.updateRule(editingRule.value.id, ruleForm.value)
    } else {
      await rulesStore.createRule(ruleForm.value)
    }
    
    showCreateModal.value = false
    resetForm()
  } catch (error) {
    console.error('Failed to save rule:', error)
  }
}

const resetForm = () => {
  editingRule.value = null
  ruleForm.value = {
    name: '',
    description: '',
    criteria: {
      from: ''
    },
    action: {
      type: 'delete'
    },
    enabled: true,
    priority: 0
  }
}

const getActionBadgeClass = (actionType) => {
  const classes = {
    delete: 'bg-red-100 text-red-800',
    mark_read: 'bg-blue-100 text-blue-800',
    add_label: 'bg-green-100 text-green-800',
    archive: 'bg-yellow-100 text-yellow-800'
  }
  return classes[actionType] || 'bg-gray-100 text-gray-800'
}

onMounted(async () => {
  await Promise.all([
    rulesStore.fetchRules(),
    rulesStore.fetchTemplates()
  ])
})
</script>

<style scoped>
.btn-sm {
  @apply px-3 py-1 text-sm;
}
</style>