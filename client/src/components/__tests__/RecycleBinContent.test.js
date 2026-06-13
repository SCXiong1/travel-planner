import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import RecycleBinContent from "../RecycleBinContent.vue";

vi.mock("../../constants.js", () => ({
  ENTITY_TYPE_LABEL: { trip: "旅行", day: "天", activity: "活动", packing_item: "物品" },
  ENTITY_TYPE_BADGE: { trip: "bg-blue-100", day: "bg-green-100" },
}));

describe("RecycleBinContent", () => {
  const items = [
    { type: "trip", id: 1, name: "东京行", deleted_at: "2026-06-10", trip_title: "东京行" },
    { type: "activity", id: 2, name: "吃拉面", deleted_at: "2026-06-11", trip_title: "东京行", day_number: 1, day_date: "2026-06-01" },
  ];

  it("renders empty state when no items", () => {
    const wrapper = mount(RecycleBinContent, { props: { items: [] } });
    expect(wrapper.text()).toContain("回收站为空");
  });

  it("renders items with type badge and name", () => {
    const wrapper = mount(RecycleBinContent, { props: { items } });
    const rendered = wrapper.findAll("[data-testid='recycle-bin-item']");
    expect(rendered).toHaveLength(2);
    expect(wrapper.text()).toContain("东京行");
    expect(wrapper.text()).toContain("吃拉面");
  });

  it("emits restore when restore button clicked", async () => {
    const wrapper = mount(RecycleBinContent, { props: { items } });
    await wrapper.findAll("[data-testid='restore-button']")[0].trigger("click");
    expect(wrapper.emitted("restore")[0]).toEqual(["trip", 1]);
  });

  it("emits permanentDelete after confirm dialog", async () => {
    const wrapper = mount(RecycleBinContent, {
      props: { items },
      global: { stubs: { ConfirmDialog: false } },
    });
    await wrapper.findAll("[data-testid='permanent-delete-button']")[0].trigger("click");
    await nextTick();

    const dialog = wrapper.findComponent({ name: "ConfirmDialog" });
    await dialog.find("[data-testid='confirm-dialog-confirm']").trigger("click");

    expect(wrapper.emitted("permanentDelete")[0]).toEqual(["trip", 1]);
  });
});
