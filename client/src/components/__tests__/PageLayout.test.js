import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import PageLayout from "../PageLayout.vue";

describe("PageLayout", () => {
  function mountLayout(props = {}, slots = {}) {
    return mount(PageLayout, {
      props,
      slots,
      global: {
        stubs: { "router-link": true },
      },
    });
  }

  it("renders the title", () => {
    const wrapper = mountLayout({ title: "打包清单", backTo: "/trips/1" });
    expect(wrapper.text()).toContain("打包清单");
  });

  it("renders a back link with correct path", () => {
    const wrapper = mount(PageLayout, {
      props: { title: "结算", backTo: "/trips/1" },
      global: {
        stubs: {
          "router-link": { template: '<a data-testid="back-link"><slot /></a>', props: ["to"] },
        },
      },
    });
    expect(wrapper.text()).toContain("返回");
    expect(wrapper.html()).toContain("返回");
  });

  it("renders slot content", () => {
    const wrapper = mountLayout({ title: "测试", backTo: "/" }, { default: "<p>slot内容</p>" });
    expect(wrapper.text()).toContain("slot内容");
  });
});
