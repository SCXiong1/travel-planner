<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部 -->
    <div class="bg-white border-b px-4 py-3 flex items-center justify-between">
      <div>
        <button @click="$router.push('/trips')" class="text-blue-500 text-sm">&larr; 返回</button>
        <h1 class="text-xl font-bold text-gray-800">{{ trip.title }}</h1>
        <p class="text-sm text-gray-500">{{ trip.destination }} · {{ trip.start_date }} ~ {{ trip.end_date }}</p>
      </div>
      <div class="flex gap-2">
        <button @click="$router.push(`/trips/${trip.id}/packing`)"
          class="px-3 py-1.5 text-xs border rounded-lg text-gray-500 hover:bg-gray-100">打包</button>
        <button @click="$router.push(`/trips/${trip.id}/settlement`)"
          class="px-3 py-1.5 text-xs border rounded-lg text-gray-500 hover:bg-gray-100">结算</button>
        <button @click="$router.push(`/trips/${trip.id}/recycle-bin`)"
          class="px-3 py-1.5 text-xs border rounded-lg text-gray-400 hover:bg-gray-100">回收站</button>
      </div>
    </div>

    <!-- 主体 -->
    <div class="flex flex-col md:flex-row">
      <!-- 天列表：手机横滑，桌面竖排 -->
      <div class="md:w-48 bg-white md:border-r md:min-h-[calc(100vh-80px)] p-3 flex-shrink-0">
        <div class="flex md:flex-col gap-1 overflow-x-auto pb-2 md:pb-0">
          <div
            v-for="day in days"
            :key="day.id"
            @click="selectDay(day.id)"
            :class="[
              'px-3 py-2 rounded-lg cursor-pointer text-sm transition flex-shrink-0 flex items-center justify-between gap-1',
              selectedDay === day.id ? 'bg-blue-500 text-white' : 'text-gray-700 hover:bg-gray-100',
            ]"
          >
            <div>
              <div class="font-medium whitespace-nowrap">Day {{ day.day_number }}</div>
              <div class="text-xs opacity-70 whitespace-nowrap">{{ day.date }}</div>
            </div>
            <ContextMenu @click.stop>
              <template #default="{ close: closeMenu }">
                <button
                  @click="promptDeleteDay(day); closeMenu()"
                  class="block w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50"
                >删除</button>
              </template>
            </ContextMenu>
          </div>
        </div>
        <button @click="addDay"
          class="mt-2 w-full py-2 text-sm text-blue-500 border border-dashed border-blue-300 rounded-lg hover:bg-blue-50 transition flex-shrink-0">
          + 添加天
        </button>
      </div>

      <!-- 右侧活动区 -->
      <div class="flex-1 p-4">
        <p v-if="!selectedDay" class="text-gray-300 text-center py-20">选择左侧的一天</p>
        <div v-else>
          <div v-if="activities.length === 0" class="text-gray-300 text-center py-20">还没有活动，点击下方添加</div>
          <div v-else class="space-y-2">
            <div v-for="act in activities" :key="act.id"
              class="bg-white rounded-lg p-3 border border-gray-100 shadow-sm cursor-pointer hover:shadow-md transition relative"
              @click="openEditDialog(act)">
              <button
                @click.stop="deleteActivity(act.id)"
                class="absolute top-2 right-2 w-6 h-6 flex items-center justify-center rounded-full text-gray-300 hover:text-red-500 hover:bg-red-50 transition"
                title="删除活动"
              >&times;</button>
              <div class="flex items-center gap-2 pr-6">
                <span :class="typeBadge(act.type)" class="text-xs px-2 py-0.5 rounded-full font-medium">
                  {{ typeLabel(act.type) }}
                </span>
                <span class="text-sm text-gray-500">{{ act.start_time }} - {{ act.end_time }}</span>
                <span v-if="act.need_reservation" class="text-xs text-orange-500">📋</span>
              </div>
              <div class="font-medium text-gray-800 mt-1">{{ act.name }}</div>
              <div v-if="act.location" class="text-xs text-gray-400 mt-0.5">{{ act.location }}</div>
              <div v-if="act.expense_amount" class="text-xs text-gray-500 mt-1">
                ¥{{ act.expense_amount }} {{ act.expense_payer }}付 · {{ act.expense_split === 'equal' ? '平分' : '归集' }}
              </div>
              <div v-if="act.review" class="text-xs text-gray-400 mt-1 italic">
                "{{ act.review.length > 50 ? act.review.slice(0, 50) + '...' : act.review }}"
              </div>
            </div>
          </div>

          <button @click="openCreateDialog"
            class="mt-4 w-full py-2.5 bg-blue-500 text-white rounded-xl text-sm font-medium hover:bg-blue-600 active:scale-[0.98] transition">
            + 添加活动
          </button>

          <!-- Day 删除确认 -->
          <ConfirmDialog
            v-if="deleteTargetDay"
            title="删除天"
            :message="`确定删除 Day ${deleteTargetDay.day_number}（${deleteTargetDay.date}）？该天下的活动也将不可见。`"
            @confirm="confirmDeleteDay"
            @cancel="deleteTargetDay = null"
          />

          <!-- 活动编辑弹窗 -->
          <div v-if="showDialog" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="showDialog = false">
            <div class="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl max-h-[90vh] overflow-y-auto">
              <h2 class="text-xl font-bold mb-4 text-gray-800">{{ editingAct ? '编辑活动' : '添加活动' }}</h2>
              <form @submit.prevent="submitActivity">
                <!-- 基本信息 -->
                <div class="mb-3">
                  <label class="block text-sm font-medium text-gray-600 mb-1">类型</label>
                  <select v-model="form.type" required class="w-full border rounded-lg px-3 py-2 text-gray-800 bg-white">
                    <option value="eat">吃</option>
                    <option value="stay">住</option>
                    <option value="transport">行</option>
                    <option value="sight">景点</option>
                  </select>
                </div>
                <div class="mb-3">
                  <label class="block text-sm font-medium text-gray-600 mb-1">名称</label>
                  <input v-model="form.name" required class="w-full border rounded-lg px-3 py-2 text-gray-800" />
                </div>
                <div class="mb-3">
                  <label class="block text-sm font-medium text-gray-600 mb-1">地点（可选）</label>
                  <input v-model="form.location" class="w-full border rounded-lg px-3 py-2 text-gray-800" />
                </div>
                <div class="flex flex-col sm:flex-row gap-3 mb-3">
                  <div class="flex-1 min-w-0">
                    <label class="block text-sm font-medium text-gray-600 mb-1">开始</label>
                    <input v-model="form.start_time" type="time" class="w-full border rounded-lg px-3 py-2 text-gray-800" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <label class="block text-sm font-medium text-gray-600 mb-1">结束</label>
                    <input v-model="form.end_time" type="time" class="w-full border rounded-lg px-3 py-2 text-gray-800" />
                  </div>
                </div>

                <!-- 预约 -->
                <div class="border-t pt-3 mb-3">
                  <label class="flex items-center gap-2 cursor-pointer mb-2">
                    <input v-model="form.need_reservation" type="checkbox" class="rounded" />
                    <span class="text-sm font-medium text-gray-600">需要预约</span>
                  </label>
                  <input v-if="form.need_reservation" v-model="form.reservation_detail"
                    placeholder="预约详情（电话、确认号...）" class="w-full border rounded-lg px-3 py-2 text-gray-800 text-sm" />
                </div>

                <!-- 开销 -->
                <div class="border-t pt-3 mb-3">
                  <p class="text-sm font-medium text-gray-600 mb-2">开销（可选）</p>
                  <div class="flex gap-3 mb-2">
                    <div class="flex-1">
                      <label class="block text-xs text-gray-500 mb-0.5">金额</label>
                      <input v-model.number="form.expense_amount" type="number" step="0.01"
                        class="w-full border rounded-lg px-3 py-2 text-gray-800 text-sm" />
                    </div>
                    <div class="flex-1">
                      <label class="block text-xs text-gray-500 mb-0.5">支付人</label>
                      <select v-model="form.expense_payer" class="w-full border rounded-lg px-3 py-2 text-gray-800 text-sm bg-white">
                        <option value="">-</option>
                        <option value="sd">sd</option>
                        <option value="sg">sg</option>
                      </select>
                    </div>
                  </div>
                  <div v-if="form.expense_payer">
                    <label class="block text-xs text-gray-500 mb-0.5">分摊方式</label>
                    <select v-model="form.expense_split" class="w-full border rounded-lg px-3 py-2 text-gray-800 text-sm bg-white">
                      <option value="equal">平分</option>
                      <option value="assign">归集到此支付人</option>
                    </select>
                  </div>
                </div>

                <!-- 评价 -->
                <div class="border-t pt-3 mb-4">
                  <label class="block text-sm font-medium text-gray-600 mb-1">评价（可选）</label>
                  <textarea v-model="form.review" rows="2" placeholder="旅行评价..."
                    class="w-full border rounded-lg px-3 py-2 text-gray-800 text-sm resize-none"></textarea>
                </div>

                <div class="flex gap-3">
                  <button type="button" @click="showDialog = false"
                    class="flex-1 py-2 border rounded-xl text-gray-600 hover:bg-gray-50 transition">取消</button>
                  <button type="submit"
                    class="flex-1 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition">保存</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api/client.js";
import { useUser } from "../composables/useUser.js";
import { useWebSocket } from "../composables/useWebSocket.js";
import ContextMenu from "./ContextMenu.vue";
import ConfirmDialog from "./ConfirmDialog.vue";

const route = useRoute();
const trip = ref({});
const days = ref([]);
const selectedDay = ref(null);
const activities = ref([]);
const showDialog = ref(false);
const editingAct = ref(null);
const { current: currentUser } = useUser();
const ws = useWebSocket();

const form = ref({
  type: "eat", name: "", location: "", start_time: "", end_time: "",
  need_reservation: false, reservation_detail: "",
  expense_amount: null, expense_payer: "", expense_split: "equal",
  review: "",
});

function typeLabel(t) {
  return { eat: "吃", stay: "住", transport: "行", sight: "景点" }[t] || t;
}

function typeBadge(t) {
  const map = {
    eat: "bg-orange-100 text-orange-700",
    stay: "bg-blue-100 text-blue-700",
    transport: "bg-green-100 text-green-700",
    sight: "bg-purple-100 text-purple-700",
  };
  return map[t] || "";
}

function resetForm() {
  editingAct.value = null;
  form.value = {
    type: "eat", name: "", location: "", start_time: "", end_time: "",
    need_reservation: false, reservation_detail: "",
    expense_amount: null, expense_payer: "", expense_split: "equal",
    review: "",
  };
}

function openCreateDialog() {
  resetForm();
  showDialog.value = true;
}

function openEditDialog(act) {
  editingAct.value = act;
  form.value = {
    type: act.type, name: act.name, location: act.location || "",
    start_time: act.start_time, end_time: act.end_time,
    need_reservation: !!act.need_reservation,
    reservation_detail: act.reservation_detail || "",
    expense_amount: act.expense_amount,
    expense_payer: act.expense_payer || "",
    expense_split: act.expense_split || "equal",
    review: act.review || "",
  };
  showDialog.value = true;
}

async function submitActivity() {
  if (editingAct.value) {
    await api.put(
      `/trips/${route.params.id}/days/${selectedDay.value}/activities/${editingAct.value.id}`,
      form.value,
    );
  } else {
    await api.post(`/trips/${route.params.id}/days/${selectedDay.value}/activities`, form.value);
  }
  showDialog.value = false;
  await selectDay(selectedDay.value);
}

async function loadTrip() {
  trip.value = await api.get(`/trips/${route.params.id}`);
  days.value = await api.get(`/trips/${route.params.id}/days`);
  if (days.value.length > 0 && !selectedDay.value) {
    await selectDay(days.value[0].id);
  }
}

async function selectDay(dayId) {
  selectedDay.value = dayId;
  activities.value = await api.get(`/trips/${route.params.id}/days/${dayId}/activities`);
}

async function addDay() {
  const start = new Date(trip.value.start_date + 'T00:00:00');
  const nextDate = new Date(start);
  nextDate.setDate(start.getDate() + days.value.length);
  const dateStr = nextDate.toISOString().slice(0, 10);

  if (dateStr > trip.value.end_date) {
    alert('已超过旅行结束日期，无法再添加天');
    return;
  }

  const r = await api.post(`/trips/${route.params.id}/days`, { date: dateStr });
  await loadTrip();
  await selectDay(r.id);
}

const deleteTargetDay = ref(null);

function promptDeleteDay(day) {
  deleteTargetDay.value = day;
}

async function confirmDeleteDay() {
  const day = deleteTargetDay.value;
  deleteTargetDay.value = null;
  await api.delete(`/trips/${route.params.id}/days/${day.id}`);
  await loadTrip();
  if (selectedDay.value === day.id) {
    selectedDay.value = null;
    activities.value = [];
  }
}

async function deleteActivity(actId) {
  if (!selectedDay.value) return;
  await api.delete(`/trips/${route.params.id}/days/${selectedDay.value}/activities/${actId}`);
  await selectDay(selectedDay.value);
}

onMounted(() => {
  loadTrip();
  ws.connect(route.params.id, currentUser.value, (msg) => {
    if (msg.type.startsWith("activity_") || msg.type === "activities_reordered") {
      if (selectedDay.value) selectDay(selectedDay.value);
    }
    if (msg.type.startsWith("packing_")) {
      // 打包页的同步由 PackingList 组件自行处理
    }
  });
});

onUnmounted(() => {
  ws.disconnect();
});
</script>
