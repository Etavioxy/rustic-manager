<template>
  <div class="date-range-picker">
    <select :value="modelValue" @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)">
      <option value="1d">今天</option>
      <option value="7d">7天</option>
      <option value="30d">30天</option>
      <option value="90d">90天</option>
    </select>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();
</script>

<style scoped>
.date-range-picker select {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  font-size: 14px;
  cursor: pointer;
}

.date-range-picker select:focus {
  outline: none;
  border-color: #4a90d9;
}
</style>
