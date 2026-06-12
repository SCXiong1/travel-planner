<template>
  <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="$emit('cancel')">
    <div class="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl max-h-[90vh] overflow-y-auto">
      <h2 class="text-xl font-bold mb-4 text-gray-800">{{ isEdit ? '编辑活动' : '添加活动' }}</h2>
      <form @submit.prevent="onSubmit">
        <!-- 类型 -->
        <div class="mb-3">
          <label class="block text-sm font-medium text-gray-600 mb-1">类型</label>
          <select v-model="form.type" required data-testid="activity-form-type" class="w-full border rounded-lg px-3 py-2 text-gray-800 bg-white">
            <option value="eat">吃</option>
            <option value="stay">住</option>
            <option value="transport">行</option>
            <option value="sight">景点</option>
          </select>
        </div>
        <!-- 名称 -->
        <div class="mb-3">
          <label class="block text-sm font-medium text-gray-600 mb-1">名称</label>
          <input v-model="form.name" required placeholder="名称" data-testid="activity-form-name" class="w-full border rounded-lg px-3 py-2 text-gray-800" />
        </div>
        <!-- 地点 -->
        <div class="mb-3">
          <label class="block text-sm font-medium text-gray-600 mb-1">地点（可选）</label>
          <input v-model="form.location" placeholder="地点" class="w-full border rounded-lg px-3 py-2 text-gray-800" />
        </div>
        <!-- 时间 -->
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
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-medium text-gray-600">开销（可选）</p>
            <button type="button" @click="addExpenseLine"
              class="text-xs text-blue-500 hover:text-blue-600">+ 添加一笔</button>
          </div>
          <div v-for="(item, idx) in form.expense_items" :key="item._key"
            class="flex gap-2 mb-2 items-start">
            <div class="flex-1 min-w-0">
              <input v-model.number="item.amount" type="number" step="0.01" placeholder="金额" data-testid="expense-amount"
                class="w-full border rounded-lg px-2 py-1.5 text-gray-800 text-sm" />
            </div>
            <select v-model="item.payer" data-testid="expense-payer" class="w-14 border rounded-lg px-1 py-1.5 text-sm text-gray-800 bg-white flex-shrink-0">
              <option value="sd">sd</option>
              <option value="sg">sg</option>
            </select>
            <select v-model="item.split" class="w-20 border rounded-lg px-1 py-1.5 text-sm text-gray-800 bg-white flex-shrink-0">
              <option value="equal">平分</option>
              <option value="assign">归集</option>
            </select>
            <button type="button" @click="removeExpenseLine(idx)"
              class="w-6 h-8 flex items-center justify-center text-gray-300 hover:text-red-500 flex-shrink-0">&times;</button>
          </div>
        </div>

        <!-- 评价 -->
        <div class="border-t pt-3 mb-4">
          <p class="text-sm font-medium text-gray-600 mb-2">评价（可选）</p>
          <div class="mb-2">
            <label class="block text-xs text-blue-500 font-medium mb-0.5">
              sd 评价 <span v-if="currentUser !== 'sd'" class="text-gray-400">（仅sd可编辑）</span>
            </label>
            <textarea v-model="form.sd_review" rows="2" placeholder="sd 的评价..."
              :disabled="currentUser !== 'sd'"
              class="w-full border rounded-lg px-3 py-2 text-gray-800 text-sm resize-none disabled:bg-gray-100 disabled:text-gray-400"></textarea>
          </div>
          <div>
            <label class="block text-xs text-pink-500 font-medium mb-0.5">
              sg 评价 <span v-if="currentUser !== 'sg'" class="text-gray-400">（仅sg可编辑）</span>
            </label>
            <textarea v-model="form.sg_review" rows="2" placeholder="sg 的评价..."
              :disabled="currentUser !== 'sg'"
              class="w-full border rounded-lg px-3 py-2 text-gray-800 text-sm resize-none disabled:bg-gray-100 disabled:text-gray-400"></textarea>
          </div>
        </div>

        <div class="flex gap-3">
          <button type="button" @click="$emit('cancel')"
            class="flex-1 py-2 border rounded-xl text-gray-600 hover:bg-gray-50 transition">取消</button>
          <button type="submit" data-testid="activity-form-submit"
            class="flex-1 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition">保存</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useUser } from "../composables/useUser.js";
import { useToast } from "../composables/useToast.js";

const props = defineProps({
  initial: { type: Object, default: null },
});

const emit = defineEmits(["submit", "cancel"]);

const { current: currentUser } = useUser();
const { show: toast } = useToast();

const isEdit = computed(() => props.initial !== null);

let expenseKeyCounter = 0;

const form = ref(buildInitial());

function buildInitial() {
  if (props.initial) {
    expenseKeyCounter = Date.now();
    return {
      type: props.initial.type,
      name: props.initial.name,
      location: props.initial.location || "",
      start_time: props.initial.start_time,
      end_time: props.initial.end_time,
      need_reservation: !!props.initial.need_reservation,
      reservation_detail: props.initial.reservation_detail || "",
      expense_items: props.initial.expense_items?.length
        ? props.initial.expense_items.map((e, i) => ({ ...e, _key: expenseKeyCounter + i }))
        : [],
      sd_review: props.initial.sd_review || "",
      sg_review: props.initial.sg_review || "",
    };
  }
  return {
    type: "eat", name: "", location: "", start_time: "", end_time: "",
    need_reservation: false, reservation_detail: "",
    expense_items: [],
    sd_review: "", sg_review: "",
  };
}

function addExpenseLine() {
  form.value.expense_items.push({ _key: ++expenseKeyCounter, amount: null, payer: "sd", split: "equal" });
}

function removeExpenseLine(idx) {
  form.value.expense_items.splice(idx, 1);
}

function onSubmit() {
  if (form.value.start_time && form.value.end_time && form.value.start_time > form.value.end_time) {
    toast("开始时间不能晚于结束时间", { type: "error" });
    return;
  }
  emit("submit", { ...form.value });
}
</script>
