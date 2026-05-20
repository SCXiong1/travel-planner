<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-2xl mx-auto">
      <button @click="$router.back()" class="text-blue-500 text-sm mb-4 inline-block">&larr; 返回</button>
      <h1 class="text-2xl font-bold text-gray-800 mb-4">回收站</h1>

      <div v-if="items.length === 0" class="text-gray-300 text-center py-16">回收站为空</div>
      <div v-else class="space-y-2">
        <div v-for="item in items" :key="item.type + item.id"
          class="bg-white rounded-lg p-3 border border-gray-100 flex items-center justify-between">
          <div>
            <span :class="item.type === 'activity' ? 'text-orange-500' : 'text-blue-500'"
              class="text-xs px-2 py-0.5 rounded-full bg-gray-100 font-medium">
              {{ item.type === 'activity' ? '活动' : '打包' }}
            </span>
            <span class="font-medium text-gray-800 ml-2">{{ item.name }}</span>
            <div class="text-xs text-gray-400 mt-0.5">删除于 {{ item.deleted_at }}</div>
          </div>
          <button @click="restore(item)"
            class="px-3 py-1.5 text-sm text-blue-500 border border-blue-300 rounded-lg hover:bg-blue-50 transition">
            恢复
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api/client.js";

const route = useRoute();
const tripId = route.params.id;
const items = ref([]);

async function load() {
  items.value = await api.get(`/trips/${tripId}/recycle-bin`);
}

async function restore(item) {
  await api.post(`/recycle-bin/${item.type}/${item.id}/restore`);
  await load();
}

onMounted(load);
</script>
