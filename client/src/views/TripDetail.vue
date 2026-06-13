<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部 -->
    <div class="bg-white border-b px-4 py-3 flex items-center justify-between">
      <div>
        <button @click="$router.push('/trips')" class="text-blue-500 text-sm">&larr; 返回</button>
        <h1 class="text-xl font-bold text-gray-800">{{ trip.title }}</h1>
        <p class="text-sm text-gray-500">{{ trip.destination }} · {{ trip.start_date }} ~ {{ trip.end_date }}</p>
      </div>
      <div class="flex gap-2">
        <button @click="$router.push(`/trips/${trip.id}/packing`)"
          class="px-3 py-1.5 text-xs border rounded-lg text-gray-500 hover:bg-gray-100">打包</button>
        <button @click="$router.push(`/trips/${trip.id}/settlement`)"
          class="px-3 py-1.5 text-xs border rounded-lg text-gray-500 hover:bg-gray-100">结算</button>
        <button @click="$router.push(`/trips/${trip.id}/recycle-bin`)"
          class="px-3 py-1.5 text-xs border rounded-lg text-gray-400 hover:bg-gray-100">回收站</button>
      </div>
    </div>

    <!-- 主体 -->
    <div class="flex flex-col md:flex-row">
      <!-- 天列表：手机横滑，桌面竖排 -->
      <DaySidebar
        :days="days"
        :selected-id="selectedDay"
        @select="selectDay"
        @add="addDay"
        @delete="promptDeleteDay"
      />

      <!-- 右侧活动区 -->
      <div class="flex-1 p-4">
        <p v-if="!selectedDay" class="text-gray-300 text-center py-20">选择左侧的一天</p>
        <div v-else>
          <div v-if="activities.length === 0" class="text-gray-300 text-center py-20">还没有活动，点击下方添加</div>
          <div v-else class="flex flex-col">
            <template v-for="(act, idx) in activities" :key="act.id">
              <!-- 拖拽插入线 -->
              <div :class="[
                'h-1 mx-2 rounded transition-colors',
                dragging && dropBefore === idx && idx !== dragIndex && idx !== dragIndex + 1
                  ? 'bg-blue-500' : 'bg-transparent'
              ]" />
              <div
                :ref="el => setCardRef(idx, el)"
                class="bg-white rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition relative"
                :class="{ 'cursor-pointer': !dragging, 'opacity-50': dragging && idx === dragIndex }"
                @click="onCardClick(act)"
              >
                <!-- 拖拽手柄 -->
                <div v-if="activities.length >= 2"
                  data-testid="activity-drag-handle"
                  class="absolute left-1 top-0 bottom-0 w-7 flex items-center justify-center text-gray-300 hover:text-gray-500 select-none"
                  :class="dragging && idx === dragIndex ? 'cursor-grabbing' : 'cursor-grab'"
                  style="touch-action: none;"
                  @pointerdown.prevent="onDragStart(idx, $event)"
                  @touchstart.prevent
                >⋮</div>
                <ActivityCard :activity="act" @delete="deleteActivity" />
              </div>
            </template>
            <!-- 末尾插入线 -->
            <div :class="[
              'h-1 mx-2 rounded transition-colors',
              dragging && dropBefore === activities.length && activities.length !== dragIndex && activities.length !== dragIndex + 1
                ? 'bg-blue-500' : 'bg-transparent'
            ]" />
          </div>

          <button @click="openCreateDialog" data-testid="add-activity-button"
            class="mt-4 w-full py-2.5 bg-blue-500 text-white rounded-xl text-sm font-medium hover:bg-blue-600 active:scale-[0.98] transition">
            + 添加活动
          </button>

          <!-- Day 删除确认 -->
          <ConfirmDialog
            v-if="deleteTargetDay"
            title="删除天"
            :message="`确定删除 Day ${deleteTargetDay.day_number}（${deleteTargetDay.date}）？该天下的活动也将不可见。`"
            @confirm="confirmDeleteDay"
            @cancel="deleteTargetDay = null"
          />

          <ActivityForm v-if="showDialog" :initial="editingAct" @submit="submitActivity" @cancel="showDialog = false" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRoute } from "vue-router";
import { useTripData } from "../composables/useTripData.js";
import { useTripWebSocket } from "../composables/useTripWebSocket.js";
import { useDragReorder } from "../composables/useDragReorder.js";
import * as activitiesApi from "../api/activities.js";
import ConfirmDialog from "../components/ConfirmDialog.vue";
import ActivityCard from "../components/ActivityCard.vue";
import ActivityForm from "../components/ActivityForm.vue";
import DaySidebar from "../components/DaySidebar.vue";

const route = useRoute();
const tripId = route.params.id;

const {
  trip, days, activities, selectedDay,
  loadAll, selectDay, addDay, deleteDay: deleteDayApi,
  addActivity, updateActivity, deleteActivity,
} = useTripData(tripId);

useTripWebSocket(tripId, (msg) => {
  if (msg.type.startsWith("activity_") || msg.type === "activities_reordered") {
    if (selectedDay.value) selectDay(selectedDay.value);
  }
});

// ---- 拖拽排序 ----
const {
  setCardRef, onDragStart, onDragMove, onDragEnd, onCardClick,
  dragging, dragJustEnded, dropBefore, dragIndex,
} = useDragReorder({
  items: activities,
  onReorder: async (orders) => {
    await activitiesApi.reorder(tripId, selectedDay.value, orders);
    await selectDay(selectedDay.value);
  },
  onClick: (act) => openEditDialog(act),
});

// ---- 表单 ----
const showDialog = ref(false);
const editingAct = ref(null);

function openCreateDialog() {
  editingAct.value = null;
  showDialog.value = true;
}

function openEditDialog(act) {
  editingAct.value = act;
  showDialog.value = true;
}

async function submitActivity(data) {
  if (editingAct.value) {
    await updateActivity(editingAct.value.id, data);
  } else {
    await addActivity(data);
  }
  showDialog.value = false;
}

const deleteTargetDay = ref(null);

function promptDeleteDay(day) {
  deleteTargetDay.value = day;
}

async function confirmDeleteDay() {
  const day = deleteTargetDay.value;
  deleteTargetDay.value = null;
  await deleteDayApi(day.id);
}

import { onMounted } from "vue";
onMounted(loadAll);
</script>
