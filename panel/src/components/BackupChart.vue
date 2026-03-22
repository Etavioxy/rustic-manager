<template>
  <div class="backup-chart">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { Chart } from 'chart.js';
import { backupChartOptions } from '../utils/chart';

const props = defineProps<{
  dateRange: string;
}>();

const chartCanvas = ref<HTMLCanvasElement | null>(null);
let chart: Chart | null = null;

async function loadData() {
  const paths = await window.api.getPaths();
  if (!paths.length) return { backups: [], frequency: [] };

  const path = paths[0];
  const limit = getLimitFromDateRange(props.dateRange);
  const data = await window.api.getBackupHistory(path.backup_table_name, limit);
  
  const backups = data.reverse().map((item: any) => ({
    x: new Date(item.timestamp),
    y: item.space_change_bytes
  }));
  
  const frequency = calculateFrequency(data);
  
  return { backups, frequency };
}

function getLimitFromDateRange(range: string): number {
  const map: Record<string, number> = {
    '1d': 50,
    '7d': 200,
    '30d': 500,
    '90d': 1000
  };
  return map[range] || 200;
}

function calculateFrequency(data: any[]): { x: Date; y: number }[] {
  const hourlyCount: Record<string, number> = {};
  
  data.forEach((item: any) => {
    const date = new Date(item.timestamp);
    const hourKey = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}`;
    hourlyCount[hourKey] = (hourlyCount[hourKey] || 0) + 1;
  });
  
  return Object.entries(hourlyCount).map(([key, count]) => {
    const [year, month, day, hour] = key.split('-').map(Number);
    return {
      x: new Date(year, month, day, hour),
      y: count
    };
  }).sort((a, b) => a.x.getTime() - b.x.getTime());
}

async function renderChart() {
  if (!chartCanvas.value) return;
  
  const { backups, frequency } = await loadData();
  
  if (chart) {
    chart.destroy();
  }
  
  chart = new Chart(chartCanvas.value, {
    type: 'bar',
    data: {
      datasets: [
        {
          type: 'bar',
          label: '空间变化',
          data: backups,
          backgroundColor: backups.map((d: any) => 
            d.y >= 0 ? 'rgba(239, 68, 68, 0.8)' : 'rgba(34, 197, 94, 0.8)'
          ),
          borderRadius: 6,
          borderSkipped: false,
          yAxisID: 'y'
        },
        {
          type: 'line',
          label: '备份频率',
          data: frequency,
          borderColor: 'rgba(147, 51, 234, 1)',
          backgroundColor: 'rgba(147, 51, 234, 0.1)',
          fill: true,
          tension: 0.4,
          yAxisID: 'y1'
        }
      ]
    },
    options: backupChartOptions
  });
}

onMounted(renderChart);

watch(() => props.dateRange, renderChart);
</script>

<style scoped>
.backup-chart {
  height: 400px;
}
</style>
