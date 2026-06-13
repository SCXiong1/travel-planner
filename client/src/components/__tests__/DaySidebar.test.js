import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import DaySidebar from "../DaySidebar.vue";

describe("DaySidebar", () => {
  const days = [
    { id: 10, day_number: 1, date: "2026-06-01" },
    { id: 11, day_number: 2, date: "2026-06-02" },
  ];

  it("renders day items", () => {
    const wrapper = mount(DaySidebar, {
      props: { days, selectedId: 10 },
      global: { stubs: { ContextMenu: true } },
    });
    const items = wrapper.findAll("[data-testid='day-item']");
    expect(items).toHaveLength(2);
    expect(items[0].text()).toContain("Day 1");
    expect(items[1].text()).toContain("Day 2");
  });

  it("emits select when day clicked", async () => {
    const wrapper = mount(DaySidebar, {
      props: { days, selectedId: 10 },
      global: { stubs: { ContextMenu: true } },
    });
    await wrapper.findAll("[data-testid='day-item']")[1].trigger("click");
    expect(wrapper.emitted("select")[0]).toEqual([11]);
  });

  it("emits add when add button clicked", async () => {
    const wrapper = mount(DaySidebar, {
      props: { days, selectedId: 10 },
      global: { stubs: { ContextMenu: true } },
    });
    await wrapper.find("[data-testid='add-day-button']").trigger("click");
    expect(wrapper.emitted("add")).toBeTruthy();
  });

  it("highlights selected day", () => {
    const wrapper = mount(DaySidebar, {
      props: { days, selectedId: 11 },
      global: { stubs: { ContextMenu: true } },
    });
    const items = wrapper.findAll("[data-testid='day-item']");
    expect(items[0].classes()).not.toContain("bg-blue-500");
    expect(items[1].classes()).toContain("bg-blue-500");
  });
});
