<template>
  <PageLayout title="打包清单" :backTo="`/trips/${tripId}`">

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
        <div v-for="item in items" :key="item.id" data-testid="packing-item"
          class="bg-white rounded-lg p-3 border border-gray-100 flex items-center gap-3">
          <input type="checkbox" :checked="item.checked" @change="toggleCheck(item)" data-testid="packing-checkbox"
            class="w-5 h-5 rounded border-gray-300 text-green-500 focus:ring-green-500" />
          <div class="flex-1">
            <div :class="['text-sm font-medium', item.checked ? 'text-gray-400 line-through' : 'text-gray-800']">
              {{ item.name }}
            </div>
            <div class="text-xs text-gray-400">{{ item.category }}</div>
          </div>
          <span :class="item.assignee === 'sd' ? 'text-blue-500' : 'text-pink-500'" class="text-xs font-medium" data-testid="packing-assignee">
            {{ item.assignee }}
          </span>
          <button @click="deleteItem(item)" data-testid="packing-delete-button" class="text-gray-300 hover:text-red-500 text-sm">&times;</button>
        </div>
      </div>

      <!-- 添加物品 -->
      <form @submit.prevent="addItem" class="mt-4 flex gap-2">
        <input v-model="form.name" required placeholder="物品名称" data-testid="packing-form-name" class="flex-1 border rounded-lg px-3 py-2 text-sm text-gray-800" />
        <input v-model="form.category" required placeholder="分类" data-testid="packing-form-category" class="w-24 border rounded-lg px-3 py-2 text-sm text-gray-800" />
        <select v-model="form.assignee" data-testid="packing-form-assignee" class="w-16 border rounded-lg px-2 py-2 text-sm text-gray-800 bg-white">
          <option value="sd">sd</option>
          <option value="sg">sg</option>
        </select>
        <button type="submit" data-testid="packing-form-submit" class="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 transition">
          添加
        </button>
      </form>
  </PageLayout>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import * as packing from "../api/packing.js";
import { useTripWebSocket } from "../composables/useTripWebSocket.js";
import { useToast } from "../composables/useToast.js";
import PageLayout from "../components/PageLayout.vue";

const route = useRoute();
const tripId = route.params.id;
const items = ref([]);
const form = ref({ name: "", category: "", assignee: "sd" });
const { show: toast } = useToast();

const checkedCount = computed(() => items.value.filter(i => i.checked).length);
const progressPercent = computed(() => items.value.length ? Math.round((checkedCount.value / items.value.length) * 100) : 0);

async function load() {
  items.value = await packing.list(tripId);
}

async function addItem() {
  try {
    await packing.create(tripId, form.value);
    form.value = { name: "", category: form.value.category, assignee: form.value.assignee };
    await load();
  } catch (e) {
    toast(e.message || "操作失败", { type: "error" });
  }
}

async function toggleCheck(item) {
  await packing.toggleCheck(tripId, item.id);
  await load();
}

async function deleteItem(item) {
  await packing.remove(tripId, item.id);
  await load();
}

useTripWebSocket(tripId, (msg) => {
  if (msg.type.startsWith("packing_")) load();
});

onMounted(load);
</script>
