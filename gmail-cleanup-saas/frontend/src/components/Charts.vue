<template>
  <div>
    <!-- Chart Container -->
    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 v-if="title" class="text-lg font-medium text-gray-900 mb-4">{{ title }}</h3>
      
      <div class="relative">
        <component
          :is="chartComponent"
          :data="chartData"
          :options="chartOptions"
          :height="height"
        />
      </div>
      
      <!-- Legend (if custom) -->
      <div v-if="showCustomLegend" class="mt-4 flex flex-wrap gap-4">
        <div
          v-for="(item, index) in legendItems"
          :key="index"
          class="flex items-center"
        >
          <div
            class="w-3 h-3 rounded-full mr-2"
            :style="{ backgroundColor: item.color }"
          ></div>
          <span class="text-sm text-gray-600">{{ item.label }} ({{ item.value }})</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler
} from 'chart.js'
import { Bar, Doughnut, Line } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler
)

const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (value) => ['bar', 'doughnut', 'line'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  data: {
    type: Object,
    required: true
  },
  options: {
    type: Object,
    default: () => ({})
  },
  height: {
    type: Number,
    default: 300
  },
  showCustomLegend: {
    type: Boolean,
    default: false
  }
})

const chartComponent = computed(() => {
  const components = {
    bar: Bar,
    doughnut: Doughnut,
    line: Line
  }
  return components[props.type]
})

const chartData = computed(() => props.data)

const chartOptions = computed(() => {
  const baseOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: !props.showCustomLegend,
        position: 'bottom',
        labels: {
          boxWidth: 12,
          padding: 20
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        padding: 12
      }
    }
  }

  // Type-specific options
  if (props.type === 'bar') {
    baseOptions.scales = {
      x: {
        grid: {
          display: false
        },
        ticks: {
          maxRotation: 45
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      }
    }
  }

  if (props.type === 'line') {
    baseOptions.scales = {
      x: {
        grid: {
          display: false
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      }
    }
  }

  if (props.type === 'doughnut') {
    baseOptions.cutout = '60%'
    baseOptions.plugins.legend.position = 'right'
  }

  // Merge with custom options
  return { ...baseOptions, ...props.options }
})

const legendItems = computed(() => {
  if (!props.showCustomLegend || !props.data.datasets?.[0]) return []
  
  const dataset = props.data.datasets[0]
  return props.data.labels?.map((label, index) => ({
    label,
    value: dataset.data[index],
    color: dataset.backgroundColor?.[index] || dataset.backgroundColor
  })) || []
})
</script>