<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <h1 class="text-3xl font-bold mb-2 text-gray-800">旅行规划</h1>
      <p class="text-gray-500 mb-8">选择你的身份</p>
      <div class="flex gap-4">
        <button
          data-testid="login-sd"
          @click="login('sd')"
          class="px-10 py-4 bg-blue-500 text-white text-lg rounded-xl hover:bg-blue-600 active:scale-95 transition"
        >
          sd
        </button>
        <button
          data-testid="login-sg"
          @click="login('sg')"
          class="px-10 py-4 bg-pink-400 text-white text-lg rounded-xl hover:bg-pink-500 active:scale-95 transition"
        >
          sg
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useUser } from "../composables/useUser.js";
import { useRouter } from "vue-router";

const { login: setUser } = useUser();
const router = useRouter();

function login(user) {
  setUser(user);
  router.push("/trips");
}
</script>
