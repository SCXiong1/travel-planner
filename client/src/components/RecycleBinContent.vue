<template>
  <div>
    <div v-if="items.length === 0" class="text-gray-300 text-center py-16">回收站为空</div>
    <div v-else class="space-y-2">
      <div v-for="item in items" :key="`${item.type}-${item.id}`" data-testid="recycle-bin-item"
        class="bg-white rounded-lg p-3 border border-gray-100">
        <div class="flex items-center gap-2 mb-1">
          <span :class="ENTITY_TYPE_BADGE[item.type] || ''" class="text-xs px-2 py-0.5 rounded-full font-medium">
            {{ ENTITY_TYPE_LABEL[item.type] || item.type }}
          </span>
          <span class="font-medium text-gray-800 text-sm truncate">{{ item.name }}</span>
        </div>
        <div class="text-xs text-gray-400 mb-1">{{ contextPath(item) }}</div>
        <div class="text-xs text-gray-400 mb-3">删除于 {{ item.deleted_at }}</div>
        <div class="flex gap-2">
          <button @click="$emit('restore', item.type, item.id)" data-testid="restore-button"
            class="flex-1 py-1.5 text-xs border border-blue-200 text-blue-500 rounded-lg hover:bg-blue-50 transition">
            恢复
          </button>
          <button @click="promptPermanentDelete(item)" data-testid="permanent-delete-button"
            class="flex-1 py-1.5 text-xs border border-red-200 text-red-400 rounded-lg hover:bg-red-50 transition">
            永久删除
          </button>
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
import { ref } from "vue";
import { ENTITY_TYPE_LABEL, ENTITY_TYPE_BADGE } from "../constants.js";
import ConfirmDialog from "./ConfirmDialog.vue";

defineProps({
  items: { type: Array, required: true },
});

const emit = defineEmits(["restore", "permanentDelete"]);

const permDeleteTarget = ref(null);

function contextPath(item) {
  const parts = [];
  if (item.trip_title) parts.push(item.trip_title);
  if (item.day_number) parts.push(`Day ${item.day_number}`);
  if (item.day_date && item.type === "activity") parts.push(item.day_date);
  return parts.join(" · ") || "";
}

function promptPermanentDelete(item) {
  permDeleteTarget.value = item;
}

function confirmPermanentDelete() {
  const item = permDeleteTarget.value;
  permDeleteTarget.value = null;
  emit("permanentDelete", item.type, item.id);
}
</script>
