import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  TimeScale,
  BarElement,
  LineElement,
  PointElement,
  LineController,
  BarController,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  BarElement,
  LineElement,
  PointElement,
  LineController,
  BarController,
  Title,
  Tooltip,
  Legend,
  Filler
);

export const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 500,
    easing: 'easeOutQuart'
  },
  plugins: {
    legend: {
      position: 'top' as const
    },
    tooltip: {
      mode: 'index' as const,
      intersect: false,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 12,
      cornerRadius: 8
    }
  },
  scales: {
    x: {
      type: 'time' as const,
      time: {
        unit: 'day' as const,
        displayFormats: {
          day: 'MM-dd'
        }
      },
      grid: {
        display: false
      }
    }
  }
};

export const diskChartOptions = {
  ...chartOptions,
  plugins: {
    ...chartOptions.plugins,
    title: {
      display: true,
      text: '磁盘空间使用趋势'
    }
  },
  scales: {
    ...chartOptions.scales,
    y: {
      beginAtZero: false,
      ticks: {
        callback: function(value: number) {
          return (value / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
        }
      }
    }
  }
};

export const backupChartOptions = {
  ...chartOptions,
  plugins: {
    ...chartOptions.plugins,
    title: {
      display: true,
      text: '备份历史统计'
    }
  },
  scales: {
    ...chartOptions.scales,
    y: {
      type: 'linear' as const,
      position: 'left' as const,
      ticks: {
        callback: function(value: number) {
          return (value / (1024 * 1024)).toFixed(1) + ' MB';
        }
      }
    },
    y1: {
      type: 'linear' as const,
      position: 'right' as const,
      grid: {
        drawOnChartArea: false
      },
      ticks: {
        callback: function(value: number) {
          return value + ' 次/h';
        }
      }
    }
  }
};

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function getChartColors(isDark: boolean) {
  if (isDark) {
    return {
      primary: 'rgba(74, 144, 217, 0.8)',
      danger: 'rgba(239, 68, 68, 0.8)',
      success: 'rgba(34, 197, 94, 0.8)',
      purple: 'rgba(147, 51, 234, 1)',
      purpleLight: 'rgba(147, 51, 234, 0.1)',
      text: '#e5e5e5',
      grid: 'rgba(255, 255, 255, 0.1)'
    };
  }
  return {
    primary: 'rgba(74, 144, 217, 0.8)',
    danger: 'rgba(239, 68, 68, 0.8)',
    success: 'rgba(34, 197, 94, 0.8)',
    purple: 'rgba(147, 51, 234, 1)',
    purpleLight: 'rgba(147, 51, 234, 0.1)',
    text: '#333333',
    grid: 'rgba(0, 0, 0, 0.1)'
  };
}
