<template>
  <div class="relative">
    <button
      @click.stop="open = !open"
      class="w-7 h-7 flex items-center justify-center rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
        <circle cx="10" cy="4" r="1.5" />
        <circle cx="10" cy="10" r="1.5" />
        <circle cx="10" cy="16" r="1.5" />
      </svg>
    </button>
    <div
      v-if="open"
      class="absolute right-0 top-full mt-1 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-40 min-w-[120px]"
      @click.stop
    >
      <slot :close="close" />
    </div>
    <div
      v-if="open"
      class="fixed inset-0 z-30"
      @click="open = false"
    />
  </div>
</template>

<script setup>
import { ref } from "vue";

const open = ref(false);

function close() {
  open.value = false;
}
</script>
