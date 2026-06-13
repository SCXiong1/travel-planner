import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import TripForm from "../TripForm.vue";

describe("TripForm", () => {
  function mountForm(props = {}) {
    return mount(TripForm, { props });
  }

  it("renders empty fields in create mode", () => {
    const wrapper = mountForm();
    expect(wrapper.find("[data-testid='trip-form-title']").element.value).toBe("");
    expect(wrapper.find("[data-testid='trip-form-destination']").element.value).toBe("");
    expect(wrapper.find("[data-testid='trip-form-start-date']").element.value).toBe("");
    expect(wrapper.find("[data-testid='trip-form-end-date']").element.value).toBe("");
  });

  it("renders pre-filled fields when initial is provided", () => {
    const wrapper = mountForm({
      initial: { title: "东京行", destination: "东京", start_date: "2026-06-01", end_date: "2026-06-07" },
    });
    expect(wrapper.find("[data-testid='trip-form-title']").element.value).toBe("东京行");
    expect(wrapper.find("[data-testid='trip-form-destination']").element.value).toBe("东京");
    expect(wrapper.find("[data-testid='trip-form-start-date']").element.value).toBe("2026-06-01");
    expect(wrapper.find("[data-testid='trip-form-end-date']").element.value).toBe("2026-06-07");
  });

  it("emits submit with form data on form submit", async () => {
    const wrapper = mountForm();
    await wrapper.find("[data-testid='trip-form-title']").setValue("日本行");
    await wrapper.find("[data-testid='trip-form-destination']").setValue("大阪");
    await wrapper.find("[data-testid='trip-form-start-date']").setValue("2026-07-01");
    await wrapper.find("[data-testid='trip-form-end-date']").setValue("2026-07-10");

    await wrapper.find("form").trigger("submit.prevent");
    await nextTick();

    expect(wrapper.emitted("submit")[0][0]).toEqual({
      title: "日本行",
      destination: "大阪",
      start_date: "2026-07-01",
      end_date: "2026-07-10",
    });
  });

  it("emits cancel when cancel button is clicked", async () => {
    const wrapper = mountForm();
    await wrapper.find("button[type='button']").trigger("click");
    expect(wrapper.emitted("cancel")).toBeTruthy();
  });
});
