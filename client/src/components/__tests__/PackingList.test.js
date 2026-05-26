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

vi.mock("../../composables/useWebSocket.js", () => ({
  useWebSocket: () => ({ connect: vi.fn(), disconnect: vi.fn() }),
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ params: { id: "1" } }),
}));

vi.mock("../../api/packing.js", () => ({
  list: vi.fn().mockResolvedValue([]),
  create: vi.fn().mockResolvedValue({ id: 1 }),
  toggleCheck: vi.fn(),
  remove: vi.fn(),
}));

const { default: PackingList } = await import("../PackingList.vue");
import * as packingApi from "../../api/packing.js";

describe("PackingList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    packingApi.list.mockResolvedValue([]);
    packingApi.create.mockResolvedValue({ id: 1 });
  });

  function mountPackingList() {
    return mount(PackingList, {
      global: { stubs: { teleport: true } },
    });
  }

  it("shows toast error when addItem fails", async () => {
    packingApi.create.mockRejectedValue(new Error("添加失败"));

    const wrapper = mountPackingList();
    await nextTick();
    await nextTick();

    // 填表
    const inputs = wrapper.findAll("input");
    await inputs[0].setValue("护照"); // name
    await inputs[1].setValue("证件"); // category

    await wrapper.find("form").trigger("submit.prevent");
    await nextTick();

    expect(mockToast).toHaveBeenCalledWith("添加失败", { type: "error" });
  });
});
