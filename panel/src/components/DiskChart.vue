<template>
  <div class="disk-chart">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { Chart } from 'chart.js';
import { diskChartOptions } from '../utils/chart';

const props = defineProps<{
  dateRange: string;
}>();

const chartCanvas = ref<HTMLCanvasElement | null>(null);
let chart: Chart | null = null;

async function loadData() {
  const paths = await window.api.getPaths();
  if (!paths.length) return;

  const path = paths[0];
  const limit = getLimitFromDateRange(props.dateRange);
  const data = await window.api.getDiskUsage(path.disk_table_name, limit);
  
  return data.reverse().map((item: any) => ({
    x: new Date(item.timestamp),
    y: item.used_bytes
  }));
}

function getLimitFromDateRange(range: string): number {
  const map: Record<string, number> = {
    '1d': 24,
    '7d': 168,
    '30d': 720,
    '90d': 2160
  };
  return map[range] || 168;
}

async function renderChart() {
  if (!chartCanvas.value) return;
  
  const data = await loadData();
  
  if (chart) {
    chart.destroy();
  }
  
  chart = new Chart(chartCanvas.value, {
    type: 'bar',
    data: {
      datasets: [{
        label: '已用空间',
        data: data || [],
        backgroundColor: 'rgba(74, 144, 217, 0.8)',
        borderRadius: 6,
        borderSkipped: false
      }]
    },
    options: diskChartOptions
  });
}

onMounted(renderChart);

watch(() => props.dateRange, renderChart);
</script>

<style scoped>
.disk-chart {
  height: 400px;
}
</style>
