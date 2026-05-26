<template>
  <div class="md:w-48 bg-white md:border-r md:min-h-[calc(100vh-80px)] p-3 flex-shrink-0">
    <div class="flex md:flex-col gap-1 overflow-x-auto pb-2 md:pb-0">
      <template v-for="(day, idx) in days" :key="day.id">
        <!-- 拖拽插入线 -->
        <div :class="[
          'h-1 mx-2 rounded transition-colors md:h-0.5',
          dragging && dropBefore === idx && idx !== dragIndex && idx !== dragIndex + 1
            ? 'bg-blue-500' : 'bg-transparent'
        ]" />
        <div
          :ref="el => setCardRef(idx, el)"
          @click="onCardClick(day)"
          :class="[
            'px-3 py-2 rounded-lg cursor-pointer text-sm transition flex-shrink-0 flex items-center justify-between gap-1',
            selectedId === day.id ? 'bg-blue-500 text-white' : 'text-gray-700 hover:bg-gray-100',
            { 'opacity-50': dragging && idx === dragIndex }
          ]"
        >
          <!-- 拖拽手柄 -->
          <div v-if="days.length >= 2"
            class="flex-shrink-0 w-5 h-5 flex items-center justify-center text-gray-300 hover:text-gray-500 select-none"
            :class="dragging && idx === dragIndex ? 'cursor-grabbing' : 'cursor-grab'"
            style="touch-action: none;"
            @pointerdown.prevent="onDragStart(idx, $event)"
            @touchstart.prevent
          >⋮</div>
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
      </template>
      <!-- 末尾插入线 -->
      <div :class="[
        'h-1 mx-2 rounded transition-colors md:h-0.5',
        dragging && dropBefore === days.length && days.length !== dragIndex && days.length !== dragIndex + 1
          ? 'bg-blue-500' : 'bg-transparent'
      ]" />
    </div>
    <button @click="$emit('add')"
      class="mt-2 w-full py-2 text-sm text-blue-500 border border-dashed border-blue-300 rounded-lg hover:bg-blue-50 transition flex-shrink-0">
      + 添加天
    </button>
  </div>
</template>

<script setup>
import { toRef } from "vue";
import { useDragReorder } from "../composables/useDragReorder.js";
import ContextMenu from "./ContextMenu.vue";

const props = defineProps({
  days: { type: Array, required: true },
  selectedId: { type: [Number, null], default: null },
});

const emit = defineEmits(["select", "add", "delete", "reorder"]);

const {
  setCardRef, onDragStart, onDragEnd, onCardClick,
  dragging, dropBefore, dragIndex,
} = useDragReorder({
  items: toRef(props, "days"),
  onReorder: (orders) => emit("reorder", orders),
  onClick: (day) => emit("select", day.id),
});
</script>
