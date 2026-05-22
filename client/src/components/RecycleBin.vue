<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-2xl mx-auto">
      <button @click="$router.back()" class="text-blue-500 text-sm mb-4 inline-block">&larr; 返回</button>
      <h1 class="text-2xl font-bold text-gray-800 mb-4">回收站</h1>

      <div v-if="items.length === 0" class="text-gray-300 text-center py-16">回收站为空</div>
      <div v-else class="space-y-2">
        <div v-for="item in items" :key="item.type + item.id"
          class="bg-white rounded-lg p-3 border border-gray-100">
          <div class="flex items-center gap-2 mb-1">
            <span :class="typeBadge(item.type)" class="text-xs px-2 py-0.5 rounded-full font-medium">
              {{ typeLabel(item.type) }}
            </span>
            <span class="font-medium text-gray-800 text-sm truncate">{{ item.name }}</span>
          </div>
          <div class="text-xs text-gray-400 mb-1">{{ contextPath(item) }}</div>
          <div class="text-xs text-gray-400 mb-3">删除于 {{ item.deleted_at }}</div>
          <div class="flex gap-2">
            <button @click="restore(item)"
              class="flex-1 py-1.5 text-xs border border-blue-200 text-blue-500 rounded-lg hover:bg-blue-50 transition">
              恢复
            </button>
            <button @click="promptPermanentDelete(item)"
              class="flex-1 py-1.5 text-xs border border-red-200 text-red-400 rounded-lg hover:bg-red-50 transition">
              永久删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <ConfirmDialog
      v-if="permDeleteTarget"
      title="永久删除"
      :message="`确定永久删除「${permDeleteTarget.name}」？此操作不可撤销。`"
      confirm-text="永久删除"
      @confirm="confirmPermanentDelete"
      @cancel="permDeleteTarget = null"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api/client.js";
import { useToast } from "../composables/useToast.js";
import ConfirmDialog from "./ConfirmDialog.vue";

const route = useRoute();
const tripId = route.params.id;
const items = ref([]);
const permDeleteTarget = ref(null);
const { show: toast } = useToast();

const typeMap = {
  trip: "旅行",
  day: "天",
  activity: "活动",
  packing: "打包",
};

const badgeMap = {
  trip: "bg-red-100 text-red-700",
  day: "bg-blue-100 text-blue-700",
  activity: "bg-orange-100 text-orange-700",
  packing: "bg-green-100 text-green-700",
};

function typeLabel(t) {
  return typeMap[t] || t;
}

function typeBadge(t) {
  return badgeMap[t] || "";
}

function contextPath(item) {
  const parts = [];
  if (item.trip_title) parts.push(item.trip_title);
  if (item.day_number) parts.push(`Day ${item.day_number}`);
  if (item.day_date && item.type === "activity") parts.push(item.day_date);
  return parts.join(" · ") || "";
}

async function load() {
  items.value = await api.get(`/trips/${tripId}/recycle-bin`);
}

async function restore(item) {
  try {
    await api.post(`/recycle-bin/${item.type}/${item.id}/restore`);
    await load();
  } catch (e) {
    toast(e.message || "恢复失败");
    await load();
  }
}

function promptPermanentDelete(item) {
  permDeleteTarget.value = item;
}

async function confirmPermanentDelete() {
  const item = permDeleteTarget.value;
  permDeleteTarget.value = null;
  await api.delete(`/recycle-bin/${item.type}/${item.id}`);
  await load();
}

onMounted(load);
</script>
