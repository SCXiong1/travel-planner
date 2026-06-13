import { describe, it, expect, vi, beforeEach } from "vitest";
import { ref, nextTick } from "vue";

const { mockToast } = vi.hoisted(() => ({ mockToast: vi.fn() }));

vi.mock("../useToast.js", () => ({
  useToast: () => ({ show: mockToast }),
}));

vi.mock("../../api/trips.js", () => ({
  get: vi.fn(),
}));

vi.mock("../../api/days.js", () => ({
  list: vi.fn(),
  create: vi.fn(),
  remove: vi.fn(),
}));

vi.mock("../../api/activities.js", () => ({
  list: vi.fn(),
  create: vi.fn(),
  update: vi.fn(),
  remove: vi.fn(),
}));

import * as tripsApi from "../../api/trips.js";
import * as daysApi from "../../api/days.js";
import * as activitiesApi from "../../api/activities.js";

// useTripData 尚未创建，动态导入
let useTripData;

describe("useTripData", () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    mockToast.mockClear();
    // 每次重新导入以获得干净状态
    const mod = await import("../useTripData.js");
    useTripData = mod.useTripData;
  });

  it("loadAll fetches trip, days, and auto-selects first day", async () => {
    tripsApi.get.mockResolvedValue({ id: 1, title: "东京行" });
    daysApi.list.mockResolvedValue([{ id: 10, day_number: 1 }]);
    activitiesApi.list.mockResolvedValue([{ id: 100, name: "吃拉面" }]);

    const { trip, days, selectedDay, activities, loadAll } = useTripData("1");
    await loadAll();

    expect(trip.value).toEqual({ id: 1, title: "东京行" });
    expect(days.value).toEqual([{ id: 10, day_number: 1 }]);
    expect(selectedDay.value).toBe(10);
    expect(activities.value).toEqual([{ id: 100, name: "吃拉面" }]);
  });

  it("loadAll does not auto-select when no days exist", async () => {
    tripsApi.get.mockResolvedValue({ id: 1 });
    daysApi.list.mockResolvedValue([]);

    const { selectedDay, loadAll } = useTripData("1");
    await loadAll();

    expect(selectedDay.value).toBeNull();
  });

  it("selectDay loads activities for that day", async () => {
    tripsApi.get.mockResolvedValue({ id: 1 });
    daysApi.list.mockResolvedValue([{ id: 10 }, { id: 11 }]);
    activitiesApi.list.mockResolvedValueOnce([]);
    activitiesApi.list.mockResolvedValueOnce([{ id: 200 }]);

    const { selectedDay, activities, loadAll, selectDay } = useTripData("1");
    await loadAll();
    await selectDay(11);

    expect(selectedDay.value).toBe(11);
    expect(activities.value).toEqual([{ id: 200 }]);
  });

  it("addDay creates a day and reloads", async () => {
    tripsApi.get.mockResolvedValue({ id: 1, start_date: "2026-06-01", end_date: "2026-06-03" });
    daysApi.list.mockResolvedValueOnce([]);
    daysApi.list.mockResolvedValueOnce([{ id: 20, day_number: 1, date: "2026-06-01" }]);
    daysApi.create.mockResolvedValue({ id: 20 });
    activitiesApi.list.mockResolvedValue([]);

    const { days, selectedDay, loadAll, addDay } = useTripData("1");
    await loadAll();
    await addDay();

    expect(daysApi.create).toHaveBeenCalled();
    expect(days.value).toEqual([{ id: 20, day_number: 1, date: "2026-06-01" }]);
    expect(selectedDay.value).toBe(20);
  });

  it("deleteDay removes day and clears selectedDay if it was selected", async () => {
    tripsApi.get.mockResolvedValue({ id: 1 });
    daysApi.list.mockResolvedValueOnce([{ id: 10 }, { id: 11 }]);
    daysApi.list.mockResolvedValueOnce([{ id: 11 }]);
    activitiesApi.list.mockResolvedValue([]);
    daysApi.remove.mockResolvedValue();

    const { selectedDay, loadAll, deleteDay } = useTripData("1");
    await loadAll(); // auto-selects 10
    expect(selectedDay.value).toBe(10);

    await deleteDay(10);
    expect(selectedDay.value).toBeNull();
  });

  it("addActivity creates and reloads activities", async () => {
    tripsApi.get.mockResolvedValue({ id: 1 });
    daysApi.list.mockResolvedValue([{ id: 10 }]);
    activitiesApi.list.mockResolvedValueOnce([]);
    activitiesApi.list.mockResolvedValueOnce([{ id: 100 }]);
    activitiesApi.create.mockResolvedValue({ id: 100 });

    const { activities, loadAll, addActivity } = useTripData("1");
    await loadAll();

    await addActivity({ type: "eat", name: "拉面" });
    expect(activitiesApi.create).toHaveBeenCalledWith("1", 10, { type: "eat", name: "拉面" });
    expect(activities.value).toEqual([{ id: 100 }]);
  });

  it("shows toast when loadAll fails", async () => {
    tripsApi.get.mockRejectedValue(new Error("网络错误"));

    const { loadAll } = useTripData("1");
    await loadAll();

    expect(mockToast).toHaveBeenCalledWith("网络错误", { type: "error" });
  });
});
