<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-md mx-auto">
      <button @click="$router.push(`/trips/${tripId}`)" class="text-blue-500 text-sm mb-4 inline-block">&larr; 返回行程</button>
      <h1 class="text-2xl font-bold text-gray-800 mb-6">结算</h1>

      <div class="bg-white rounded-2xl p-6 shadow-sm space-y-4">
        <div class="flex justify-between text-sm">
          <span class="text-gray-500">sd 支付</span>
          <span class="text-blue-600 font-medium">¥{{ data.sd_paid }}</span>
        </div>
        <div class="flex justify-between text-sm">
          <span class="text-gray-500">sg 支付</span>
          <span class="text-pink-500 font-medium">¥{{ data.sg_paid }}</span>
        </div>
        <hr />
        <div class="flex justify-between text-base font-bold">
          <span class="text-gray-800">总开销</span>
          <span>¥{{ data.total }}</span>
        </div>
        <hr />
        <div class="flex justify-between text-sm">
          <span class="text-gray-500">sd 应承担</span>
          <span>¥{{ data.sd_owes }}</span>
        </div>
        <div class="flex justify-between text-sm">
          <span class="text-gray-500">sg 应承担</span>
          <span>¥{{ data.sg_owes }}</span>
        </div>
      </div>

      <!-- 结果 -->
      <div class="mt-6 bg-white rounded-2xl p-6 shadow-sm text-center">
        <p v-if="data.sd_balance === 0 && data.sg_balance === 0" class="text-gray-400 text-lg">
          双方持平，无需补差价
        </p>
        <div v-else-if="data.sd_balance > 0">
          <p class="text-gray-500 text-sm">sg 需支付 sd</p>
          <p class="text-3xl font-bold text-blue-600 mt-1">¥{{ data.sd_balance }}</p>
        </div>
        <div v-else>
          <p class="text-gray-500 text-sm">sd 需支付 sg</p>
          <p class="text-3xl font-bold text-pink-500 mt-1">¥{{ Math.abs(data.sd_balance) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { get as getSettlement } from "../api/settlement.js";

const route = useRoute();
const tripId = route.params.id;
const data = ref({ sd_paid: 0, sg_paid: 0, total: 0, sd_owes: 0, sg_owes: 0, sd_balance: 0, sg_balance: 0 });

onMounted(async () => {
  data.value = await getSettlement(tripId);
});
</script>
