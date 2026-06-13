import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import Settlement from "../Settlement.vue";

vi.mock("vue-router", () => ({
  useRoute: () => ({ params: { id: "1" } }),
}));

vi.mock("../../api/settlement.js", () => ({
  get: vi.fn(),
}));

vi.mock("../../composables/useToast.js", () => ({
  useToast: () => ({ show: vi.fn() }),
}));

import * as settlementApi from "../../api/settlement.js";

describe("Settlement", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("displays settlement data", async () => {
    settlementApi.get.mockResolvedValue({
      sd_paid: 500, sg_paid: 300, total: 800,
      sd_owes: 400, sg_owes: 400, sd_balance: 100, sg_balance: -100,
    });

    const wrapper = mount(Settlement, {
      global: { stubs: { PageLayout: { template: "<slot />" } } },
    });
    await flushPromises();

    expect(wrapper.find("[data-testid='sd-paid']").text()).toBe("¥500");
    expect(wrapper.find("[data-testid='sg-paid']").text()).toBe("¥300");
    expect(wrapper.find("[data-testid='settlement-result']").text()).toContain("sg 需支付 sd");
    expect(wrapper.find("[data-testid='settlement-result']").text()).toContain("¥100");
  });

  it("shows balanced message when sd_balance is 0", async () => {
    settlementApi.get.mockResolvedValue({
      sd_paid: 400, sg_paid: 400, total: 800,
      sd_owes: 400, sg_owes: 400, sd_balance: 0, sg_balance: 0,
    });

    const wrapper = mount(Settlement, {
      global: { stubs: { PageLayout: { template: "<slot />" } } },
    });
    await flushPromises();

    expect(wrapper.find("[data-testid='settlement-result']").text()).toContain("双方持平");
  });
});
