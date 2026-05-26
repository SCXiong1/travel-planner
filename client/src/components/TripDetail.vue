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
        @reorder="reorderDays"
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

          <button @click="openCreateDialog"
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
import { ref, watch, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import * as trips from "../api/trips.js";
import * as daysApi from "../api/days.js";
import * as activitiesApi from "../api/activities.js";
import { useDragReorder } from "../composables/useDragReorder.js";
import { useUser } from "../composables/useUser.js";
import { useWebSocket } from "../composables/useWebSocket.js";
import { useToast } from "../composables/useToast.js";
import ConfirmDialog from "./ConfirmDialog.vue";
import ActivityCard from "./ActivityCard.vue";
import ActivityForm from "./ActivityForm.vue";
import DaySidebar from "./DaySidebar.vue";

const route = useRoute();
const trip = ref({});
const days = ref([]);
const selectedDay = ref(null);
const activities = ref([]);
const showDialog = ref(false);
const editingAct = ref(null);
const { current: currentUser } = useUser();
const ws = useWebSocket();
const { show: toast } = useToast();

// ---- 拖拽排序 ----
const {
  setCardRef, onDragStart, onDragMove, onDragEnd, onCardClick,
  dragging, dragJustEnded, dropBefore, dragIndex,
} = useDragReorder({
  items: activities,
  onReorder: async (orders) => {
    await activitiesApi.reorder(route.params.id, selectedDay.value, orders);
    await selectDay(selectedDay.value);
  },
  onClick: (act) => openEditDialog(act),
});

// ---- 表单 ----
function openCreateDialog() {
  editingAct.value = null;
  showDialog.value = true;
}

function openEditDialog(act) {
  editingAct.value = act;
  showDialog.value = true;
}

async function submitActivity(data) {
  try {
    if (editingAct.value) {
      await activitiesApi.update(route.params.id, selectedDay.value, editingAct.value.id, data);
    } else {
      await activitiesApi.create(route.params.id, selectedDay.value, data);
    }
    showDialog.value = false;
    await selectDay(selectedDay.value);
  } catch (e) {
    toast(e.message || "操作失败", { type: "error" });
  }
}

async function loadTrip() {
  trip.value = await trips.get(route.params.id);
  days.value = await daysApi.list(route.params.id);
  if (days.value.length > 0 && !selectedDay.value) {
    await selectDay(days.value[0].id);
  }
}

async function selectDay(dayId) {
  selectedDay.value = dayId;
  activities.value = await activitiesApi.list(route.params.id, dayId);
}

async function addDay() {
  let nextDate;
  if (days.value.length > 0) {
    const lastDate = days.value[days.value.length - 1].date;
    nextDate = new Date(lastDate + 'T00:00:00');
    nextDate.setDate(nextDate.getDate() + 1);
  } else {
    nextDate = new Date(trip.value.start_date + 'T00:00:00');
  }

  const endDate = trip.value.end_date;
  while (true) {
    const dateStr = `${nextDate.getFullYear()}-${String(nextDate.getMonth() + 1).padStart(2, '0')}-${String(nextDate.getDate()).padStart(2, '0')}`;

    if (dateStr > endDate) {
      const start = new Date(trip.value.start_date + 'T00:00:00');
      const end = new Date(trip.value.end_date + 'T00:00:00');
      const totalDays = Math.round((end - start) / (1000 * 60 * 60 * 24)) + 1;
      if (days.value.length < totalDays) {
        toast('之前删过中间的天，有日期缺口，请从回收站恢复', { type: 'info' });
      } else {
        toast('已超过旅行结束日期，无法再添加天', { type: 'info' });
      }
      return;
    }

    try {
      const r = await daysApi.create(route.params.id, { date: dateStr });
      await loadTrip();
      await selectDay(r.id);
      return;
    } catch (e) {
      if (e.status === 409) {
        nextDate.setDate(nextDate.getDate() + 1);
        continue;
      }
      throw e;
    }
  }
}

const deleteTargetDay = ref(null);

function promptDeleteDay(day) {
  deleteTargetDay.value = day;
}

async function confirmDeleteDay() {
  const day = deleteTargetDay.value;
  deleteTargetDay.value = null;
  await daysApi.remove(route.params.id, day.id);
  await loadTrip();
  if (selectedDay.value === day.id) {
    selectedDay.value = null;
    activities.value = [];
  }
}

async function reorderDays(orders) {
  await daysApi.reorder(route.params.id, orders);
  await loadTrip();
}

async function deleteActivity(actId) {
  if (!selectedDay.value) return;
  await activitiesApi.remove(route.params.id, selectedDay.value, actId);
  await selectDay(selectedDay.value);
}

function onWsMessage(msg) {
  if (msg.type.startsWith("activity_") || msg.type === "activities_reordered") {
    if (selectedDay.value) selectDay(selectedDay.value);
  }
}

onMounted(() => {
  loadTrip();
  ws.connect(route.params.id, currentUser.value, onWsMessage);
});

watch(currentUser, () => {
  ws.disconnect();
  ws.connect(route.params.id, currentUser.value, onWsMessage);
});

onUnmounted(() => {
  ws.disconnect();
});
</script>
