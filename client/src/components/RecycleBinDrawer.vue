<template>
  <div class="fixed inset-0 z-50">
    <div class="absolute inset-0 bg-black/40" @click="$emit('close')" />
    <div class="absolute right-0 top-0 h-full w-full max-w-md bg-white shadow-xl flex flex-col">
      <div class="flex items-center justify-between px-4 py-3 border-b">
        <h2 class="text-lg font-bold text-gray-800">回收站</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
      </div>
      <div class="flex-1 overflow-y-auto p-4">
        <RecycleBinContent
          :items="items"
          @restore="handleRestore"
          @permanent-delete="handlePermanentDelete"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import * as recycleBin from "../api/recycleBin.js";
import { useToast } from "../composables/useToast.js";
import RecycleBinContent from "./RecycleBinContent.vue";

defineEmits(["close"]);

const items = ref([]);
const { show: toast } = useToast();

async function load() {
  items.value = await recycleBin.listGlobal();
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
