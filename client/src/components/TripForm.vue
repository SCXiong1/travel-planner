<template>
  <form @submit.prevent="handleSubmit">
    <div class="mb-3">
      <label class="block text-sm font-medium text-gray-600 mb-1">标题</label>
      <input data-testid="trip-form-title" v-model="form.title" required class="w-full border rounded-lg px-3 py-2 text-gray-800" />
    </div>
    <div class="mb-3">
      <label class="block text-sm font-medium text-gray-600 mb-1">目的地</label>
      <input data-testid="trip-form-destination" v-model="form.destination" required class="w-full border rounded-lg px-3 py-2 text-gray-800" />
    </div>
    <div class="flex flex-col sm:flex-row gap-3 mb-4">
      <div class="flex-1 min-w-0">
        <label class="block text-sm font-medium text-gray-600 mb-1">开始日期</label>
        <input data-testid="trip-form-start-date" v-model="form.start_date" type="date" required class="w-full border rounded-lg px-3 py-2 text-gray-800" />
      </div>
      <div class="flex-1 min-w-0">
        <label class="block text-sm font-medium text-gray-600 mb-1">结束日期</label>
        <input data-testid="trip-form-end-date" v-model="form.end_date" type="date" required class="w-full border rounded-lg px-3 py-2 text-gray-800" />
      </div>
    </div>
    <div class="flex gap-3">
      <button type="button" @click="$emit('cancel')"
        class="flex-1 py-2 border rounded-xl text-gray-600 hover:bg-gray-50 transition">
        取消
      </button>
      <button type="submit"
        data-testid="trip-form-submit"
        class="flex-1 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition">
        保存
      </button>
    </div>
  </form>
</template>

<script setup>
import { reactive, watch } from "vue";

const props = defineProps({
  initial: { type: Object, default: null },
});

const emit = defineEmits(["submit", "cancel"]);

const defaultForm = { title: "", destination: "", start_date: "", end_date: "" };
const form = reactive({ ...defaultForm });

watch(() => props.initial, (val) => {
  Object.assign(form, val || defaultForm);
}, { immediate: true });

function handleSubmit() {
  emit("submit", { ...form });
}
</script>
