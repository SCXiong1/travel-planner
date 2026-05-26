import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import ActivityForm from "../ActivityForm.vue";

describe("ActivityForm", () => {
  function mountForm(initial = null) {
    return mount(ActivityForm, {
      props: { initial },
    });
  }

  // Tracer bullet: create mode renders empty form
  it("renders in create mode when initial is null", () => {
    const wrapper = mountForm(null);
    expect(wrapper.text()).toContain("添加活动");
    // 名称输入框存在且必填
    const nameInput = wrapper.find('input[placeholder="名称"]');
    expect(nameInput.exists()).toBe(true);
  });

  // Edit mode: pre-fills form fields from initial prop
  it("pre-fills form fields from initial prop", () => {
    const wrapper = mountForm({
      id: 1,
      type: "stay",
      name: "东京塔酒店",
      location: "港区",
      start_time: "14:00",
      end_time: "16:00",
      need_reservation: true,
      reservation_detail: "TEL 03-1234",
      expense_items: [
        { _key: 1, amount: 500, payer: "sg", split: "equal" },
      ],
      sd_review: "不错",
      sg_review: "",
    });

    expect(wrapper.text()).toContain("编辑活动");

    // 名称已预填
    const nameInput = wrapper.find('input[placeholder="名称"]');
    expect(nameInput.element.value).toBe("东京塔酒店");

    // 预约复选框已勾选
    const reservationCheckbox = wrapper.find('input[type="checkbox"]');
    expect(reservationCheckbox.element.checked).toBe(true);
  });

  // Submit emits form data
  it("emits submit with form data on save", async () => {
    const wrapper = mountForm(null);

    // 填名称和选类型
    await wrapper.find('input[placeholder="名称"]').setValue("拉面");
    await wrapper.find("select").setValue("eat");
    await wrapper.find("form").trigger("submit.prevent");

    expect(wrapper.emitted("submit")).toBeTruthy();
    const [data] = wrapper.emitted("submit")[0];
    expect(data.name).toBe("拉面");
    expect(data.type).toBe("eat");
  });

  // Cancel emits on overlay click
  it("emits cancel when clicking overlay", async () => {
    const wrapper = mountForm(null);
    // 点击遮罩层
    await wrapper.find(".fixed.inset-0").trigger("click");
    expect(wrapper.emitted("cancel")).toBeTruthy();
  });
});
