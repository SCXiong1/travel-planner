<template>
  <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="$emit('cancel')">
    <div class="bg-white rounded-2xl p-6 w-full max-w-sm shadow-xl">
      <h3 class="text-lg font-bold text-gray-800 mb-2">{{ title }}</h3>
      <p class="text-sm text-gray-500 mb-6">{{ message }}</p>
      <div class="flex gap-3">
        <button
          @click="$emit('cancel')"
          class="flex-1 py-2 border rounded-xl text-gray-600 hover:bg-gray-50 transition"
        >取消</button>
        <button
          @click="$emit('confirm')"
          class="flex-1 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition"
        >{{ confirmText }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  message: { type: String, default: "" },
  confirmText: { type: String, default: "删除" },
});

defineEmits(["confirm", "cancel"]);
</script>
