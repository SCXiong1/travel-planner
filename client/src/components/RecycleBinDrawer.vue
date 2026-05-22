<template>
  <div class="fixed inset-0 z-50">
    <!-- 背景遮罩 -->
    <div class="absolute inset-0 bg-black/40" @click="$emit('close')" />

    <!-- 抽屉 -->
    <div class="absolute right-0 top-0 h-full w-full max-w-md bg-white shadow-xl flex flex-col">
      <!-- 头部 -->
      <div class="flex items-center justify-between px-4 py-3 border-b">
        <h2 class="text-lg font-bold text-gray-800">回收站</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
      </div>

      <!-- 内容 -->
      <div class="flex-1 overflow-y-auto p-4">
        <p v-if="items.length === 0" class="text-gray-300 text-center py-16">回收站为空</p>

        <div v-else class="space-y-2">
          <div
            v-for="item in items"
            :key="`${item.type}-${item.id}`"
            class="bg-gray-50 rounded-lg p-3 border border-gray-100"
          >
            <div class="flex items-center gap-2 mb-1">
              <span :class="typeBadge(item.type)" class="text-xs px-2 py-0.5 rounded-full font-medium">
                {{ typeLabel(item.type) }}
              </span>
              <span class="text-sm font-medium text-gray-800 truncate">{{ item.name }}</span>
            </div>

            <div class="text-xs text-gray-400 mb-2">{{ contextPath(item) }}</div>

            <div class="text-xs text-gray-400 mb-3">{{ item.deleted_at }} 删除</div>

            <div class="flex gap-2">
              <button
                @click="restore(item)"
                class="flex-1 py-1.5 text-xs border border-blue-200 text-blue-500 rounded-lg hover:bg-blue-50 transition"
              >恢复</button>
              <button
                @click="promptPermanentDelete(item)"
                class="flex-1 py-1.5 text-xs border border-red-200 text-red-400 rounded-lg hover:bg-red-50 transition"
              >永久删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 永久删除确认 -->
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
import { api } from "../api/client.js";
import { useToast } from "../composables/useToast.js";
import ConfirmDialog from "./ConfirmDialog.vue";

defineEmits(["close"]);

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
  if (item.day_date) parts.push(item.day_date);
  return parts.join(" · ") || "";
}

async function load() {
  items.value = await api.get("/recycle-bin");
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
