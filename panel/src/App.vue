<template>
  <div class="app" :class="{ dark: isDark }">
    <header class="header">
      <h1>Rustic Manager</h1>
      <div class="header-actions">
        <button class="theme-toggle" @click="toggleTheme">
          {{ isDark ? '☀️' : '🌙' }}
        </button>
        <DateRangePicker v-model="dateRange" />
      </div>
    </header>
    
    <div class="tabs">
      <button 
        :class="{ active: activeTab === 'disk' }" 
        @click="activeTab = 'disk'"
      >
        磁盘空间
      </button>
      <button 
        :class="{ active: activeTab === 'backup' }" 
        @click="activeTab = 'backup'"
      >
        备份历史
      </button>
    </div>
    
    <main class="content">
      <DiskChart v-if="activeTab === 'disk'" :date-range="dateRange" :is-dark="isDark" />
      <BackupChart v-if="activeTab === 'backup'" :date-range="dateRange" :is-dark="isDark" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DiskChart from './components/DiskChart.vue';
import BackupChart from './components/BackupChart.vue';
import DateRangePicker from './components/DateRangePicker.vue';

const activeTab = ref('disk');
const dateRange = ref('7d');
const isDark = ref(false);

onMounted(() => {
  const saved = localStorage.getItem('theme');
  if (saved === 'dark') {
    isDark.value = true;
  }
});

function toggleTheme() {
  isDark.value = !isDark.value;
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f5f5;
  color: #333;
  transition: background 0.3s, color 0.3s;
}

.app.dark body,
.app.dark {
  background: #1a1a1a;
  color: #e5e5e5;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.theme-toggle {
  padding: 8px 12px;
  border: none;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.app.dark .theme-toggle {
  background: #2a2a2a;
}

.theme-toggle:hover {
  transform: scale(1.1);
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.app.dark .tabs button {
  background: #2a2a2a;
  color: #e5e5e5;
}

.tabs button.active {
  background: #4a90d9;
  color: #fff;
}

.tabs button:hover:not(.active) {
  background: #e5e5e5;
}

.app.dark .tabs button:hover:not(.active) {
  background: #3a3a3a;
}

.content {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: background 0.3s;
}

.app.dark .content {
  background: #2a2a2a;
}
</style>
