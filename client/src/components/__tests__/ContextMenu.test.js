import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import ContextMenu from "../ContextMenu.vue";

describe("ContextMenu", () => {
  it("opens menu when button clicked", async () => {
    const wrapper = mount(ContextMenu, {
      slots: { default: '<button class="menu-item">编辑</button>' },
      global: { stubs: { teleport: true } },
    });
    expect(wrapper.find(".menu-item").exists()).toBe(false);

    await wrapper.find("[data-testid='context-menu-button']").trigger("click");
    await nextTick();

    expect(wrapper.find(".menu-item").exists()).toBe(true);
  });

  it("closes menu when close() is called from slot", async () => {
    const wrapper = mount(ContextMenu, {
      slots: {
        default: `<template #default="{ close }"><button class="menu-item" @click="close()">编辑</button></template>`,
      },
      global: { stubs: { teleport: true } },
    });

    await wrapper.find("[data-testid='context-menu-button']").trigger("click");
    await nextTick();
    expect(wrapper.find(".menu-item").exists()).toBe(true);

    await wrapper.find(".menu-item").trigger("click");
    await nextTick();
    expect(wrapper.find(".menu-item").exists()).toBe(false);
  });
});
