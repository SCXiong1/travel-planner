<template>
  <PageLayout title="回收站" :backTo="`/trips/${tripId}`">
      <RecycleBinContent
        :items="items"
        @restore="handleRestore"
        @permanent-delete="handlePermanentDelete"
      />
  </PageLayout>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import * as recycleBin from "../api/recycleBin.js";
import { useToast } from "../composables/useToast.js";
import RecycleBinContent from "../components/RecycleBinContent.vue";
import PageLayout from "../components/PageLayout.vue";

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
