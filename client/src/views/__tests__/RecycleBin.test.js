import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import RecycleBin from "../RecycleBin.vue";

vi.mock("vue-router", () => ({
  useRoute: () => ({ params: { id: "1" } }),
}));

vi.mock("../../api/recycleBin.js", () => ({
  listByTrip: vi.fn(),
  restore: vi.fn(),
  permanentDelete: vi.fn(),
}));

vi.mock("../../composables/useToast.js", () => ({
  useToast: () => ({ show: vi.fn() }),
}));

import * as recycleBinApi from "../../api/recycleBin.js";

describe("RecycleBin", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("loads and displays items", async () => {
    recycleBinApi.listByTrip.mockResolvedValue([
      { type: "trip", id: 1, name: "东京行", deleted_at: "2026-06-10" },
    ]);

    const wrapper = mount(RecycleBin, {
      global: { stubs: { PageLayout: { template: "<slot />" }, RecycleBinContent: true } },
    });
    await flushPromises();

    expect(recycleBinApi.listByTrip).toHaveBeenCalledWith("1");
  });
});
