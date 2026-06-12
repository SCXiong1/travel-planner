<template>
  <div ref="triggerRef" class="relative inline-flex">
    <button
      data-testid="context-menu-button"
      @click.stop="toggle"
      class="w-7 h-7 flex items-center justify-center rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
        <circle cx="10" cy="4" r="1.5" />
        <circle cx="10" cy="10" r="1.5" />
        <circle cx="10" cy="16" r="1.5" />
      </svg>
    </button>
    <Teleport to="body">
      <div
        v-if="open"
        class="fixed inset-0 z-30"
        @click="open = false"
      />
      <div
        v-if="open"
        ref="menuRef"
        class="fixed bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-40 min-w-[120px]"
        :style="menuStyle"
        @click.stop
      >
        <slot :close="close" />
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from "vue";

const open = ref(false);
const triggerRef = ref(null);
const menuRef = ref(null);
const menuPos = ref({ top: 0, left: 0 });

function toggle() {
  open.value = !open.value;
  if (open.value) {
    nextTick(() => {
      if (!triggerRef.value) return;
      const rect = triggerRef.value.getBoundingClientRect();
      menuPos.value = {
        top: rect.bottom + 4,
        right: window.innerWidth - rect.right,
      };
    });
  }
}

const menuStyle = computed(() => ({
  top: menuPos.value.top + "px",
  right: menuPos.value.right + "px",
}));

function close() {
  open.value = false;
}
</script>
