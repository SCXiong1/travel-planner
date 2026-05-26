import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { ref, nextTick } from "vue";

const { mockToast } = vi.hoisted(() => ({ mockToast: vi.fn() }));

vi.mock("../../composables/useToast.js", () => ({
  useToast: () => ({ show: mockToast }),
}));

vi.mock("../../composables/useUser.js", () => ({
  useUser: () => ({ current: ref("sd"), switchUser: vi.fn() }),
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
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("../../api/trips.js", () => ({
  list: vi.fn().mockResolvedValue([]),
  create: vi.fn().mockResolvedValue({ id: 1 }),
  update: vi.fn().mockResolvedValue({ id: 1 }),
  remove: vi.fn().mockResolvedValue(true),
  reorder: vi.fn(),
}));

const { default: TripList } = await import("../TripList.vue");
import * as tripsApi from "../../api/trips.js";

describe("TripList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    tripsApi.list.mockResolvedValue([]);
    tripsApi.create.mockResolvedValue({ id: 1 });
  });

  function mountTripList() {
    return mount(TripList, {
      global: {
        stubs: { ContextMenu: true, ConfirmDialog: true, RecycleBinDrawer: true },
      },
    });
  }

  // 找弹窗里的 form inputs（排除外面按钮等）
  function getFormInputs(wrapper) {
    const form = wrapper.find("form");
    const textInputs = form.findAll("input:not([type=date]):not([type=checkbox])");
    const dateInputs = form.findAll('input[type="date"]');
    return { form, textInputs, dateInputs };
  }

  it("opens dialog when +新建旅行 is clicked", async () => {
    const wrapper = mountTripList();
    await nextTick();

    expect(wrapper.text()).toContain("新建旅行");
    expect(wrapper.find("form").exists()).toBe(false);

    // 找到"+ 新建旅行"按钮（不是用户切换按钮）
    const createBtn = wrapper.find("button.bg-blue-500");
    await createBtn.trigger("click");
    await nextTick();

    expect(wrapper.find("form").exists()).toBe(true);
  });

  it("submit calls tripsApi.create with form data", async () => {
    const wrapper = mountTripList();
    await nextTick();

    await wrapper.find("button.bg-blue-500").trigger("click");
    await nextTick();

    const { form, textInputs, dateInputs } = getFormInputs(wrapper);
    await textInputs[0].setValue("日本行");        // 标题
    await textInputs[1].setValue("东京");           // 目的地
    await dateInputs[0].setValue("2026-06-01");     // 开始
    await dateInputs[1].setValue("2026-06-07");     // 结束

    await form.trigger("submit.prevent");
    await nextTick();

    expect(tripsApi.create).toHaveBeenCalledWith({
      title: "日本行", destination: "东京",
      start_date: "2026-06-01", end_date: "2026-06-07",
    });
  });

  it("shows toast error when create fails", async () => {
    tripsApi.create.mockRejectedValue(new Error("HTTP 502"));

    const wrapper = mountTripList();
    await nextTick();

    await wrapper.find("button.bg-blue-500").trigger("click");
    await nextTick();

    const { form, textInputs, dateInputs } = getFormInputs(wrapper);
    await textInputs[0].setValue("x");
    await textInputs[1].setValue("y");
    await dateInputs[0].setValue("2026-01-01");
    await dateInputs[1].setValue("2026-01-07");

    await form.trigger("submit.prevent");
    await nextTick();

    expect(mockToast).toHaveBeenCalledWith("HTTP 502", { type: "error" });
  });
});
