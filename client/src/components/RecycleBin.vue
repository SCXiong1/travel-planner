<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-2xl mx-auto">
      <button @click="$router.back()" class="text-blue-500 text-sm mb-4 inline-block">&larr; 返回</button>
      <h1 class="text-2xl font-bold text-gray-800 mb-4">回收站</h1>
      <RecycleBinContent
        :items="items"
        @restore="handleRestore"
        @permanent-delete="handlePermanentDelete"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import * as recycleBin from "../api/recycleBin.js";
import { useToast } from "../composables/useToast.js";
import RecycleBinContent from "./RecycleBinContent.vue";

const route = useRoute();
const tripId = route.params.id;
const items = ref([]);
const { show: toast } = useToast();

async function load() {
  items.value = await recycleBin.listByTrip(tripId);
}

async function handleRestore(type, id) {
  try {
    await recycleBin.restore(type, id);
    await load();
  } catch (e) {
    toast(e.message || "恢复失败");
    await load();
  }
}

async function handlePermanentDelete(type, id) {
  await recycleBin.permanentDelete(type, id);
  await load();
}

onMounted(load);
</script>
