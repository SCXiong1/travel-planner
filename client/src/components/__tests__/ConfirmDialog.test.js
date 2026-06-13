import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import ConfirmDialog from "../ConfirmDialog.vue";

describe("ConfirmDialog", () => {
  it("renders title and message", () => {
    const wrapper = mount(ConfirmDialog, {
      props: { title: "删除旅行", message: "确定删除？" },
    });
    expect(wrapper.text()).toContain("删除旅行");
    expect(wrapper.text()).toContain("确定删除？");
  });

  it("emits confirm when confirm button clicked", async () => {
    const wrapper = mount(ConfirmDialog, {
      props: { title: "删除", message: "" },
    });
    await wrapper.find("[data-testid='confirm-dialog-confirm']").trigger("click");
    expect(wrapper.emitted("confirm")).toBeTruthy();
  });

  it("emits cancel when cancel button clicked", async () => {
    const wrapper = mount(ConfirmDialog, {
      props: { title: "删除", message: "" },
    });
    await wrapper.findAll("button")[0].trigger("click");
    expect(wrapper.emitted("cancel")).toBeTruthy();
  });

  it("uses custom confirmText", () => {
    const wrapper = mount(ConfirmDialog, {
      props: { title: "删除", message: "", confirmText: "永久删除" },
    });
    expect(wrapper.find("[data-testid='confirm-dialog-confirm']").text()).toBe("永久删除");
  });
});
