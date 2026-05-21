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
          <span class="text-sm text-gray-400 bg-white px-3 py-1 rounded-full border">
            {{ currentUser }}
          </span>
        </div>
      </div>

      <!-- 空 -->
      <p v-if="trips.length === 0" class="text-gray-400 text-center py-12">
        还没有旅行计划，点击下方按钮创建
      </p>

      <!-- 旅行卡片 -->
      <div v-else class="space-y-3">
        <div
          v-for="trip in trips"
          :key="trip.id"
          class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 cursor-pointer hover:shadow-md transition flex items-center"
          @click="openTrip(trip.id)"
        >
          <div class="flex-1 min-w-0">
            <h2 class="text-lg font-semibold text-gray-800 truncate">{{ trip.title }}</h2>
            <p class="text-sm text-gray-500 mt-1">{{ trip.destination }} · {{ trip.start_date }} ~ {{ trip.end_date }}</p>
          </div>
          <ContextMenu @click.stop>
            <template #default="{ close: closeMenu }">
              <button
                @click="promptDelete(trip); closeMenu()"
                class="block w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50"
              >删除</button>
            </template>
          </ContextMenu>
        </div>
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
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUser } from "../composables/useUser.js";
import { api } from "../api/client.js";
import ContextMenu from "./ContextMenu.vue";
import ConfirmDialog from "./ConfirmDialog.vue";
import RecycleBinDrawer from "./RecycleBinDrawer.vue";

const { current: currentUser } = useUser();
const router = useRouter();

const trips = ref([]);
const showDialog = ref(false);
const editingTrip = ref(null);
const deleteTarget = ref(null);
const showDrawer = ref(false);

const form = ref({ title: "", destination: "", start_date: "", end_date: "" });

async function loadTrips() {
  trips.value = await api.get("/trips");
}

function openCreateDialog() {
  editingTrip.value = null;
  form.value = { title: "", destination: "", start_date: "", end_date: "" };
  showDialog.value = true;
}

async function submit() {
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
