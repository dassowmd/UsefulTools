<template>
  <div class="bg-white shadow-sm rounded-lg border border-gray-200">
    <!-- Table Header -->
    <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
        <div class="flex items-center space-x-4">
          <!-- Search -->
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
            </div>
            <input
              v-model="globalFilter"
              type="text"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
              :placeholder="`Search ${title.toLowerCase()}...`"
            >
          </div>
          
          <!-- Actions Slot -->
          <slot name="actions" />
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              v-for="header in table.getLeafHeaders()"
              :key="header.id"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              @click="header.column.getToggleSortingHandler()?.($event)"
            >
              <div class="flex items-center space-x-1">
                <span>{{ header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext()) }}</span>
                <template v-if="header.column.getIsSorted()">
                  <ChevronUpIcon v-if="header.column.getIsSorted() === 'asc'" class="w-4 h-4" />
                  <ChevronDownIcon v-else class="w-4 h-4" />
                </template>
              </div>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="row in table.getRowModel().rows"
            :key="row.id"
            class="hover:bg-gray-50"
          >
            <td
              v-for="cell in row.getVisibleCells()"
              :key="cell.id"
              class="px-6 py-4 whitespace-nowrap"
            >
              <component
                :is="flexRender(cell.column.columnDef.cell, cell.getContext())"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="showPagination" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-700">
          Showing {{ table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1 }} to 
          {{ Math.min((table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize, table.getFilteredRowModel().rows.length) }} 
          of {{ table.getFilteredRowModel().rows.length }} results
        </div>
        
        <div class="flex items-center space-x-2">
          <button
            @click="table.previousPage()"
            :disabled="!table.getCanPreviousPage()"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          
          <span class="text-sm text-gray-700">
            Page {{ table.getState().pagination.pageIndex + 1 }} of {{ table.getPageCount() }}
          </span>
          
          <button
            @click="table.nextPage()"
            :disabled="!table.getCanNextPage()"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="table.getFilteredRowModel().rows.length === 0" class="text-center py-12">
      <slot name="empty-state">
        <div class="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <component :is="emptyIcon" class="w-12 h-12 text-gray-400" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">{{ emptyTitle }}</h3>
        <p class="text-gray-600">{{ emptyDescription }}</p>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  useReactiveTable,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  flexRender
} from '@tanstack/vue-table'
import {
  MagnifyingGlassIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  TableCellsIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  title: {
    type: String,
    default: 'Data'
  },
  data: {
    type: Array,
    required: true
  },
  columns: {
    type: Array,
    required: true
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  pageSize: {
    type: Number,
    default: 10
  },
  emptyTitle: {
    type: String,
    default: 'No data found'
  },
  emptyDescription: {
    type: String,
    default: 'There are no items to display'
  },
  emptyIcon: {
    type: Object,
    default: () => TableCellsIcon
  }
})

const globalFilter = ref('')

const table = useReactiveTable({
  get data() {
    return props.data
  },
  get columns() {
    return props.columns
  },
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  getSortedRowModel: getSortedRowModel(),
  state: {
    get globalFilter() {
      return globalFilter.value
    },
    get pagination() {
      return {
        pageIndex: 0,
        pageSize: props.pageSize
      }
    }
  },
  onGlobalFilterChange: (updater) => {
    globalFilter.value = typeof updater === 'function' ? updater(globalFilter.value) : updater
  }
})
</script>