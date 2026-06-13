<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-2xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-gray-800">我的旅行</h1>
        <div class="flex items-center gap-2">
          <button
            @click="showDrawer = true"
            class="text-sm text-gray-400 bg-white px-3 py-1 rounded-full border hover:bg-gray-100 transition"
          >回收站</button>
          <button
            @click="handleSwitchUser"
            class="text-sm text-gray-400 bg-white px-3 py-1 rounded-full border hover:text-blue-500 hover:border-blue-300 transition cursor-pointer"
            title="切换用户"
          >
            {{ currentUser }}
          </button>
        </div>
      </div>

      <!-- 空 -->
      <p v-if="trips.length === 0" class="text-gray-400 text-center py-12">
        还没有旅行计划，点击下方按钮创建
      </p>

      <!-- 旅行卡片 -->
      <div v-else>
        <template v-for="(trip, idx) in trips" :key="trip.id">
          <!-- 拖拽插入线 -->
          <div :class="[
            'h-1 mx-2 rounded transition-colors',
            dragging && dropBefore === idx && idx !== dragIndex && idx !== dragIndex + 1
              ? 'bg-blue-500' : 'bg-transparent'
          ]" />
          <div
            :ref="el => setCardRef(idx, el)"
            data-testid="trip-card"
            class="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition flex items-center"
            :class="{
              'cursor-pointer': !dragging,
              'opacity-50': dragging && idx === dragIndex,
            }"
            @click="onCardClick(trip)"
          >
            <!-- 拖拽手柄 -->
            <div
              v-if="trips.length >= 2"
              data-testid="trip-drag-handle"
              class="w-9 flex items-center justify-center text-gray-300 hover:text-gray-500 select-none self-stretch rounded-l-xl"
              :class="dragging && idx === dragIndex ? 'cursor-grabbing bg-blue-50' : 'cursor-grab'"
              style="touch-action: none;"
              @pointerdown.prevent="onDragStart(idx, $event)"
              @touchstart.prevent
            >⋮</div>
            <div class="flex-1 min-w-0 py-4 pr-4" :class="{ 'pl-4': trips.length < 2 }">
              <h2 class="text-lg font-semibold text-gray-800 truncate">{{ trip.title }}</h2>
              <p class="text-sm text-gray-500 mt-1">{{ trip.destination }} · {{ trip.start_date }} ~ {{ trip.end_date }}</p>
            </div>
            <ContextMenu @click.stop>
              <template #default="{ close: closeMenu }">
                <button
                  data-testid="edit-trip-button"
                  @click="openEditDialog(trip); closeMenu()"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >编辑</button>
                <button
                  data-testid="delete-trip-button"
                  @click="promptDelete(trip); closeMenu()"
                  class="block w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50"
                >删除</button>
              </template>
            </ContextMenu>
          </div>
        </template>
        <!-- 末尾插入线 -->
        <div :class="[
          'h-1 mx-2 rounded transition-colors',
          dragging && dropBefore === trips.length && trips.length !== dragIndex && trips.length !== dragIndex + 1
            ? 'bg-blue-500' : 'bg-transparent'
        ]" />
      </div>

      <!-- 新建按钮 -->
      <button
        data-testid="create-trip-button"
        @click="openCreateDialog"
        class="mt-6 w-full py-3 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600 active:scale-[0.98] transition"
      >
        + 新建旅行
      </button>
    </div>

    <!-- 新建/编辑弹窗 -->
    <div v-if="showDialog" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl" @click.stop>
        <h2 class="text-xl font-bold mb-4 text-gray-800">{{ editingTrip ? '编辑旅行' : '新建旅行' }}</h2>
        <TripForm :initial="editingTrip || undefined" @submit="onFormSubmit" @cancel="showDialog = false" />
      </div>
    </div>

    <!-- 删除确认 -->
    <ConfirmDialog
      v-if="deleteTarget"
      title="删除旅行"
      :message="`确定删除「${deleteTarget.title}」？删除后可到回收站恢复。`"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />

    <!-- 回收站抽屉 -->
    <RecycleBinDrawer
      v-if="showDrawer"
      @close="showDrawer = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUser } from "../composables/useUser.js";
import { useToast } from "../composables/useToast.js";
import * as tripsApi from "../api/trips.js";
import { useDragReorder } from "../composables/useDragReorder.js";
import ContextMenu from "../components/ContextMenu.vue";
import ConfirmDialog from "../components/ConfirmDialog.vue";
import RecycleBinDrawer from "../components/RecycleBinDrawer.vue";
import TripForm from "../components/TripForm.vue";

const { current: currentUser, switchUser } = useUser();
const { show: toast } = useToast();
const router = useRouter();

function handleSwitchUser() {
  switchUser();
  toast("切换成功", { type: "info" });
}

const trips = ref([]);
const showDialog = ref(false);
const editingTrip = ref(null);
const deleteTarget = ref(null);
const showDrawer = ref(false);

// ---- 拖拽排序 ----
const {
  setCardRef, onDragStart, onDragMove, onDragEnd, onCardClick,
  dragging, dragJustEnded, dropBefore, dragIndex,
} = useDragReorder({
  items: trips,
  onReorder: async (orders) => {
    await tripsApi.reorder(orders);
    await loadTrips();
  },
  onClick: (trip) => openTrip(trip.id),
});

async function loadTrips() {
  trips.value = await tripsApi.list();
}

function openCreateDialog() {
  editingTrip.value = null;
  showDialog.value = true;
}

function openEditDialog(trip) {
  editingTrip.value = trip;
  showDialog.value = true;
}

async function onFormSubmit(formData) {
  if (formData.start_date > formData.end_date) {
    toast("开始日期不能晚于结束日期", { type: "error" });
    return;
  }
  try {
    if (editingTrip.value) {
      await tripsApi.update(editingTrip.value.id, formData);
    } else {
      await tripsApi.create(formData);
    }
    showDialog.value = false;
    await loadTrips();
  } catch (e) {
    toast(e.message || "操作失败", { type: "error" });
  }
}

function openTrip(id) {
  router.push(`/trips/${id}`);
}

function promptDelete(trip) {
  deleteTarget.value = trip;
}

async function confirmDelete() {
  const trip = deleteTarget.value;
  deleteTarget.value = null;
  await tripsApi.remove(trip.id);
  await loadTrips();
}

onMounted(loadTrips);
</script>
