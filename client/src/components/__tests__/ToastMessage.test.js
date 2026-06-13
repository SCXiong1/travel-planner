import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import ToastMessage from "../ToastMessage.vue";

vi.mock("../../composables/useToast.js", () => ({
  useToast: () => ({
    message: { value: "操作成功" },
    visible: { value: true },
    type: { value: "info" },
  }),
}));

describe("ToastMessage", () => {
  it("displays the message", () => {
    const wrapper = mount(ToastMessage);
    expect(wrapper.text()).toContain("操作成功");
  });

  it("applies info style by default", () => {
    const wrapper = mount(ToastMessage);
    expect(wrapper.find("div").classes()).toContain("bg-blue-600");
  });
});
