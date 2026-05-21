<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-2xl mx-auto">
      <button @click="$router.push(`/trips/${tripId}`)" class="text-blue-500 text-sm mb-4 inline-block">&larr; 返回行程</button>
      <h1 class="text-2xl font-bold text-gray-800 mb-1">打包清单</h1>

      <!-- 进度条 -->
      <div v-if="items.length > 0" class="mt-3 mb-4">
        <div class="flex justify-between text-sm text-gray-500 mb-1">
          <span>已打包 {{ checkedCount }} / {{ items.length }}</span>
          <span>{{ progressPercent }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-green-500 h-2 rounded-full transition-all" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>

      <!-- 物品列表 -->
      <div v-if="items.length === 0" class="text-gray-300 text-center py-16">
        还没有物品，点击下方添加
      </div>
      <div v-else class="space-y-1">
        <div v-for="item in items" :key="item.id"
          class="bg-white rounded-lg p-3 border border-gray-100 flex items-center gap-3">
          <input type="checkbox" :checked="item.checked" @change="toggleCheck(item)"
            class="w-5 h-5 rounded border-gray-300 text-green-500 focus:ring-green-500" />
          <div class="flex-1">
            <div :class="['text-sm font-medium', item.checked ? 'text-gray-400 line-through' : 'text-gray-800']">
              {{ item.name }}
            </div>
            <div class="text-xs text-gray-400">{{ item.category }}</div>
          </div>
          <span :class="item.assignee === 'sd' ? 'text-blue-500' : 'text-pink-500'" class="text-xs font-medium">
            {{ item.assignee }}
          </span>
          <button @click="deleteItem(item)" class="text-gray-300 hover:text-red-500 text-sm">&times;</button>
        </div>
      </div>

      <!-- 添加物品 -->
      <form @submit.prevent="addItem" class="mt-4 flex gap-2">
        <input v-model="form.name" required placeholder="物品名称" class="flex-1 border rounded-lg px-3 py-2 text-sm text-gray-800" />
        <input v-model="form.category" required placeholder="分类" class="w-24 border rounded-lg px-3 py-2 text-sm text-gray-800" />
        <select v-model="form.assignee" class="w-16 border rounded-lg px-2 py-2 text-sm text-gray-800 bg-white">
          <option value="sd">sd</option>
          <option value="sg">sg</option>
        </select>
        <button type="submit" class="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 transition">
          添加
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api/client.js";
import { useUser } from "../composables/useUser.js";
import { useWebSocket } from "../composables/useWebSocket.js";

const route = useRoute();
const tripId = route.params.id;
const items = ref([]);
const form = ref({ name: "", category: "", assignee: "sd" });
const { current: currentUser } = useUser();
const ws = useWebSocket();

const checkedCount = computed(() => items.value.filter(i => i.checked).length);
const progressPercent = computed(() => items.value.length ? Math.round((checkedCount.value / items.value.length) * 100) : 0);

async function load() {
  items.value = await api.get(`/trips/${tripId}/packing`);
}

async function addItem() {
  await api.post(`/trips/${tripId}/packing`, form.value);
  form.value = { name: "", category: form.value.category, assignee: form.value.assignee };
  await load();
}

async function toggleCheck(item) {
  await api.put(`/trips/${tripId}/packing/${item.id}/check`);
  await load();
}

async function deleteItem(item) {
  await api.delete(`/trips/${tripId}/packing/${item.id}`);
  await load();
}

function onWsMessage(msg) {
  if (msg.type.startsWith("packing_")) load();
}

onMounted(() => {
  load();
  ws.connect(tripId, currentUser.value, onWsMessage);
});

watch(currentUser, () => {
  ws.disconnect();
  ws.connect(tripId, currentUser.value, onWsMessage);
});

onUnmounted(() => {
  ws.disconnect();
});
</script>
