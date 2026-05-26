import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { ref, nextTick } from "vue";

const { mockToast } = vi.hoisted(() => ({
  mockToast: vi.fn(),
}));

vi.mock("../../composables/useToast.js", () => ({
  useToast: () => ({ show: mockToast }),
}));

vi.mock("../../composables/useUser.js", () => ({
  useUser: () => ({ current: ref("sd"), switchUser: vi.fn() }),
}));

vi.mock("../../composables/useWebSocket.js", () => ({
  useWebSocket: () => ({ connect: vi.fn(), disconnect: vi.fn() }),
}));

vi.mock("../../composables/useDragReorder.js", () => ({
  useDragReorder: () => ({
    setCardRef: vi.fn(),
    onDragStart: vi.fn(),
    onDragMove: vi.fn(),
    onDragEnd: vi.fn(),
    onCardClick: vi.fn(),
    dragging: ref(false),
    dragJustEnded: ref(false),
    dropBefore: ref(-1),
    dragIndex: ref(-1),
  }),
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ params: { id: "1" } }),
}));

vi.mock("../../api/trips.js", () => ({
  get: vi.fn().mockResolvedValue({
    id: 1, title: "测试旅行", destination: "东京",
    start_date: "2026-06-01", end_date: "2026-06-07",
  }),
}));

vi.mock("../../api/days.js", () => ({
  list: vi.fn().mockResolvedValue([
    { id: 10, day_number: 1, date: "2026-06-01", trip_id: 1 },
  ]),
  create: vi.fn(),
  remove: vi.fn(),
}));

vi.mock("../../api/activities.js", () => ({
  list: vi.fn().mockResolvedValue([]),
  create: vi.fn().mockResolvedValue({ id: 100 }),
  update: vi.fn().mockResolvedValue({ id: 100 }),
  remove: vi.fn().mockResolvedValue(true),
  reorder: vi.fn(),
}));

const { default: TripDetail } = await import("../TripDetail.vue");
import * as activitiesApi from "../../api/activities.js";

// 一个 mini ActivityForm stub：点击后渲染占位，emit submit/cancel
const ActivityFormStub = {
  name: "ActivityForm",
  props: ["initial"],
  emits: ["submit", "cancel"],
  template: '<div class="activity-form-stub"><button class="stub-submit" @click="$emit(\'submit\', {type:\'eat\',name:\'test\'})">submit</button><button class="stub-cancel" @click="$emit(\'cancel\')">cancel</button></div>',
};

describe("TripDetail", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockToast.mockClear();
  });

  function mountTripDetail() {
    return mount(TripDetail, {
      global: {
        stubs: { ContextMenu: true, ConfirmDialog: true, ActivityCard: true, DaySidebar: true, ActivityForm: ActivityFormStub },
      },
    });
  }

  it("opens ActivityForm when + add activity button is clicked", async () => {
    const wrapper = mountTripDetail();
    await flushPromises();
    await nextTick();

    expect(wrapper.text()).toContain("添加活动");
    expect(wrapper.find(".activity-form-stub").exists()).toBe(false);

    await wrapper.find("button.bg-blue-500").trigger("click");
    await nextTick();

    expect(wrapper.find(".activity-form-stub").exists()).toBe(true);
  });

  it("ActivityForm cancel closes dialog", async () => {
    const wrapper = mountTripDetail();
    await flushPromises();
    await nextTick();

    await wrapper.find("button.bg-blue-500").trigger("click");
    await nextTick();
    expect(wrapper.find(".activity-form-stub").exists()).toBe(true);

    await wrapper.find(".stub-cancel").trigger("click");
    await nextTick();
    expect(wrapper.find(".activity-form-stub").exists()).toBe(false);
  });

  it("ActivityForm submit calls activitiesApi.create", async () => {
    const wrapper = mountTripDetail();
    await flushPromises();
    await nextTick();

    await wrapper.find("button.bg-blue-500").trigger("click");
    await nextTick();

    await wrapper.find(".stub-submit").trigger("click");
    await flushPromises();
    await nextTick();

    expect(activitiesApi.create).toHaveBeenCalledWith("1", 10, expect.objectContaining({ type: "eat", name: "test" }));
  });

  it("shows toast on create error", async () => {
    activitiesApi.create.mockRejectedValue(new Error("创建失败"));

    const wrapper = mountTripDetail();
    await flushPromises();
    await nextTick();

    await wrapper.find("button.bg-blue-500").trigger("click");
    await nextTick();

    await wrapper.find(".stub-submit").trigger("click");
    await flushPromises();
    await nextTick();

    expect(mockToast).toHaveBeenCalledWith("创建失败", { type: "error" });
  });
});
