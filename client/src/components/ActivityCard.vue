<template>
  <div class="p-3 pl-8" data-testid="activity-card">
    <div class="flex items-center gap-2 pr-6">
      <span :class="ACTIVITY_TYPE_BADGE[activity.type] || ''" class="text-xs px-2 py-0.5 rounded-full font-medium">
        {{ ACTIVITY_TYPE_LABEL[activity.type] || activity.type }}
      </span>
      <span class="text-sm text-gray-500">{{ activity.start_time }} - {{ activity.end_time }}</span>
      <span v-if="activity.need_reservation" class="text-xs text-orange-500">📋</span>
    </div>
    <div class="font-medium text-gray-800 mt-1">{{ activity.name }}</div>
    <div v-if="activity.location" class="text-xs text-gray-400 mt-0.5">{{ activity.location }}</div>
    <div v-if="activity.expense_total" class="text-xs text-gray-500 mt-1">
      ¥{{ activity.expense_total }}
      <span v-if="activity.expense_items?.length">（{{ activity.expense_items.length }}笔）</span>
    </div>
    <div v-if="activity.sd_review || activity.sg_review" class="text-xs text-gray-400 mt-1 space-y-0.5">
      <div v-if="activity.sd_review" class="italic">
        <span class="text-blue-500 not-italic font-medium">sd:</span> "{{ truncate(activity.sd_review) }}"
      </div>
      <div v-if="activity.sg_review" class="italic">
        <span class="text-pink-500 not-italic font-medium">sg:</span> "{{ truncate(activity.sg_review) }}"
      </div>
    </div>
    <button
      @click.stop="$emit('delete', activity.id)"
      data-testid="delete-activity-button"
      class="absolute top-2 right-2 w-6 h-6 flex items-center justify-center rounded-full text-gray-300 hover:text-red-500 hover:bg-red-50 transition"
      title="删除活动"
    >&times;</button>
  </div>
</template>

<script setup>
import { ACTIVITY_TYPE_LABEL, ACTIVITY_TYPE_BADGE } from "../constants.js";

defineProps({
  activity: { type: Object, required: true },
});

defineEmits(["edit", "delete"]);

function truncate(text) {
  return text.length > 30 ? text.slice(0, 30) + "..." : text;
}
</script>
