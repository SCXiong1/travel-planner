import { ref } from "vue";
import * as tripsApi from "../api/trips.js";
import * as daysApi from "../api/days.js";
import * as activitiesApi from "../api/activities.js";
import { useToast } from "./useToast.js";

export function useTripData(tripId) {
  const trip = ref({});
  const days = ref([]);
  const selectedDay = ref(null);
  const activities = ref([]);
  const loading = ref(false);
  const { show: toast } = useToast();

  async function loadAll() {
    loading.value = true;
    try {
      trip.value = await tripsApi.get(tripId);
      days.value = await daysApi.list(tripId);
      if (days.value.length > 0 && !selectedDay.value) {
        await selectDay(days.value[0].id);
      }
    } catch (e) {
      toast(e.message || "加载失败", { type: "error" });
    } finally {
      loading.value = false;
    }
  }

  async function selectDay(dayId) {
    try {
      selectedDay.value = dayId;
      activities.value = await activitiesApi.list(tripId, dayId);
    } catch (e) {
      toast(e.message || "加载活动失败", { type: "error" });
    }
  }

  async function addDay() {
    let nextDate;
    if (days.value.length > 0) {
      const lastDate = days.value[days.value.length - 1].date;
      nextDate = new Date(lastDate + "T00:00:00");
      nextDate.setDate(nextDate.getDate() + 1);
    } else {
      nextDate = new Date(trip.value.start_date + "T00:00:00");
    }

    const endDate = trip.value.end_date;
    const MAX_ITERATIONS = 366;
    let iterations = 0;
    while (iterations++ < MAX_ITERATIONS) {
      const dateStr = `${nextDate.getFullYear()}-${String(nextDate.getMonth() + 1).padStart(2, "0")}-${String(nextDate.getDate()).padStart(2, "0")}`;

      if (dateStr > endDate) {
        const start = new Date(trip.value.start_date + "T00:00:00");
        const end = new Date(trip.value.end_date + "T00:00:00");
        const totalDays = Math.round((end - start) / (1000 * 60 * 60 * 24)) + 1;
        if (days.value.length < totalDays) {
          toast("之前删过中间的天，有日期缺口，请从回收站恢复", { type: "info" });
        } else {
          toast("已超过旅行结束日期，无法再添加天", { type: "info" });
        }
        return;
      }

      try {
        const r = await daysApi.create(tripId, { date: dateStr });
        await loadAll();
        await selectDay(r.id);
        return;
      } catch (e) {
        if (e.status === 409) {
          nextDate.setDate(nextDate.getDate() + 1);
          continue;
        }
        throw e;
      }
    }
  }

  async function deleteDay(dayId) {
    try {
      await daysApi.remove(tripId, dayId);
      await loadAll();
      if (selectedDay.value === dayId) {
        selectedDay.value = null;
        activities.value = [];
      }
    } catch (e) {
      toast(e.message || "删除失败", { type: "error" });
    }
  }

  async function addActivity(data) {
    try {
      await activitiesApi.create(tripId, selectedDay.value, data);
      await selectDay(selectedDay.value);
      return true;
    } catch (e) {
      toast(e.message || "操作失败", { type: "error" });
      return false;
    }
  }

  async function updateActivity(actId, data) {
    try {
      await activitiesApi.update(tripId, selectedDay.value, actId, data);
      await selectDay(selectedDay.value);
      return true;
    } catch (e) {
      toast(e.message || "操作失败", { type: "error" });
      return false;
    }
  }

  async function deleteActivity(actId) {
    if (!selectedDay.value) return;
    try {
      await activitiesApi.remove(tripId, selectedDay.value, actId);
      await selectDay(selectedDay.value);
    } catch (e) {
      toast(e.message || "删除失败", { type: "error" });
    }
  }

  return {
    trip, days, activities, selectedDay, loading,
    loadAll, selectDay, addDay, deleteDay,
    addActivity, updateActivity, deleteActivity,
  };
}
