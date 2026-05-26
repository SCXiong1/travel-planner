<template>
  <div class="md:w-48 bg-white md:border-r md:min-h-[calc(100vh-80px)] p-3 flex-shrink-0">
    <div class="flex md:flex-col gap-1 overflow-x-auto pb-2 md:pb-0">
      <div
        v-for="day in days"
        :key="day.id"
        @click="$emit('select', day.id)"
        :class="[
          'px-3 py-2 rounded-lg cursor-pointer text-sm transition flex-shrink-0 flex items-center justify-between gap-1',
          selectedId === day.id ? 'bg-blue-500 text-white' : 'text-gray-700 hover:bg-gray-100',
        ]"
      >
        <div class="min-w-0">
          <div class="font-medium whitespace-nowrap">Day {{ day.day_number }}</div>
          <div class="text-xs opacity-70 whitespace-nowrap">{{ day.date }}</div>
        </div>
        <ContextMenu @click.stop>
          <template #default="{ close: closeMenu }">
            <button
              @click="$emit('delete', day); closeMenu()"
              class="block w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50"
            >删除</button>
          </template>
        </ContextMenu>
      </div>
    </div>
    <button @click="$emit('add')"
      class="mt-2 w-full py-2 text-sm text-blue-500 border border-dashed border-blue-300 rounded-lg hover:bg-blue-50 transition flex-shrink-0">
      + 添加天
    </button>
  </div>
</template>

<script setup>
import ContextMenu from "./ContextMenu.vue";

defineProps({
  days: { type: Array, required: true },
  selectedId: { type: [Number, null], default: null },
});

defineEmits(["select", "add", "delete"]);
</script>
