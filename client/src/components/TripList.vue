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
                  @click="openEditDialog(trip); closeMenu()"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >编辑</button>
                <button
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
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="block text-sm font-medium text-gray-600 mb-1">标题</label>
            <input v-model="form.title" required class="w-full border rounded-lg px-3 py-2 text-gray-800" />
          </div>
          <div class="mb-3">
            <label class="block text-sm font-medium text-gray-600 mb-1">目的地</label>
            <input v-model="form.destination" required class="w-full border rounded-lg px-3 py-2 text-gray-800" />
          </div>
          <div class="flex flex-col sm:flex-row gap-3 mb-4">
            <div class="flex-1 min-w-0">
              <label class="block text-sm font-medium text-gray-600 mb-1">开始日期</label>
              <input v-model="form.start_date" type="date" required class="w-full border rounded-lg px-3 py-2 text-gray-800" />
            </div>
            <div class="flex-1 min-w-0">
              <label class="block text-sm font-medium text-gray-600 mb-1">结束日期</label>
              <input v-model="form.end_date" type="date" required class="w-full border rounded-lg px-3 py-2 text-gray-800" />
            </div>
          </div>
          <div class="flex gap-3">
            <button type="button" @click="showDialog = false"
              class="flex-1 py-2 border rounded-xl text-gray-600 hover:bg-gray-50 transition">
              取消
            </button>
            <button type="submit"
              class="flex-1 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition">
              保存
            </button>
          </div>
        </form>
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
import { ref, onMounted, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useUser } from "../composables/useUser.js";
import { useToast } from "../composables/useToast.js";
import { api } from "../api/client.js";
import ContextMenu from "./ContextMenu.vue";
import ConfirmDialog from "./ConfirmDialog.vue";
import RecycleBinDrawer from "./RecycleBinDrawer.vue";

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

const form = ref({ title: "", destination: "", start_date: "", end_date: "" });

// ---- 拖拽排序 ----
const cardRefs = {};
let dragIndex = -1;
let dragGripEl = null;
const dropBefore = ref(-1);
const dragging = ref(false);
let dragJustEnded = false;

function setCardRef(idx, el) {
  if (el) cardRefs[idx] = el;
}

function onDragStart(idx, event) {
  dragIndex = idx;
  dragging.value = true;
  dragGripEl = event.currentTarget;
  dragGripEl.setPointerCapture(event.pointerId);
  dragGripEl.addEventListener("pointermove", onDragMove);
  dragGripEl.addEventListener("pointerup", onDragEnd);
  dragGripEl.addEventListener("pointercancel", onDragEnd);
}

function onDragMove(event) {
  const y = event.clientY;
  let ins = trips.value.length;
  for (let i = 0; i < trips.value.length; i++) {
    const rect = cardRefs[i]?.getBoundingClientRect();
    if (rect && y < rect.top + rect.height / 2) {
      ins = i;
      break;
    }
  }
  dropBefore.value = ins;
}

function onDragEnd() {
  if (dragGripEl) {
    dragGripEl.removeEventListener("pointermove", onDragMove);
    dragGripEl.removeEventListener("pointerup", onDragEnd);
    dragGripEl.removeEventListener("pointercancel", onDragEnd);
    dragGripEl = null;
  }

  if (
    dropBefore.value !== -1 &&
    dropBefore.value !== dragIndex &&
    dropBefore.value !== dragIndex + 1
  ) {
    performReorder();
  } else {
    dragIndex = -1;
    dropBefore.value = -1;
    dragging.value = false;
  }

  dragJustEnded = true;
  nextTick(() => { dragJustEnded = false; });
}

function onCardClick(trip) {
  if (dragJustEnded) return;
  openTrip(trip.id);
}

async function performReorder() {
  const arr = [...trips.value];
  const [moved] = arr.splice(dragIndex, 1);
  const newIdx = dropBefore.value < dragIndex ? dropBefore.value : dropBefore.value - 1;
  arr.splice(newIdx, 0, moved);

  const orders = arr.map((t, i) => ({ id: t.id, sort_order: i }));
  await api.put("/trips/reorder", orders);
  dragIndex = -1;
  dropBefore.value = -1;
  dragging.value = false;
  await loadTrips();
}

async function loadTrips() {
  trips.value = await api.get("/trips");
}

function openCreateDialog() {
  editingTrip.value = null;
  form.value = { title: "", destination: "", start_date: "", end_date: "" };
  showDialog.value = true;
}

function openEditDialog(trip) {
  editingTrip.value = trip;
  form.value = {
    title: trip.title,
    destination: trip.destination,
    start_date: trip.start_date,
    end_date: trip.end_date,
  };
  showDialog.value = true;
}

async function submit() {
  if (form.value.start_date > form.value.end_date) {
    toast("开始日期不能晚于结束日期", { type: "error" });
    return;
  }
  if (editingTrip.value) {
    await api.put(`/trips/${editingTrip.value.id}`, form.value);
  } else {
    await api.post("/trips", form.value);
  }
  showDialog.value = false;
  await loadTrips();
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
  await api.delete(`/trips/${trip.id}`);
  await loadTrips();
}

onMounted(loadTrips);
</script>
