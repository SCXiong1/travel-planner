<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-2xl mx-auto">
      <router-link :to="backTo" class="text-blue-500 text-sm mb-4 inline-block">&larr; 返回</router-link>
      <h1 class="text-2xl font-bold text-gray-800 mb-4">{{ title }}</h1>
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  backTo: { type: String, required: true },
});
</script>
