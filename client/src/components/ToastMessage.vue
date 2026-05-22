<template>
  <Transition name="toast">
    <div
      v-if="visible"
      :class="[
        'fixed top-4 left-1/2 -translate-x-1/2 z-[100] px-4 py-3 rounded-xl text-sm font-medium shadow-lg max-w-[90vw]',
        type === 'error' ? 'bg-red-500 text-white' : 'bg-blue-600 text-white',
      ]"
    >
      {{ message }}
    </div>
  </Transition>
</template>

<script setup>
import { useToast } from "../composables/useToast.js";

const { message, visible, type } = useToast();
</script>

<style scoped>
.toast-enter-active { transition: all 0.25s ease-out; }
.toast-leave-active { transition: all 0.2s ease-in; }
.toast-enter-from { opacity: 0; transform: translateY(-12px) translateX(-50%); }
.toast-leave-to { opacity: 0; transform: translateY(-8px) translateX(-50%); }
</style>
