import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import Login from "../Login.vue";

const mockPush = vi.fn();
const mockLogin = vi.fn();

vi.mock("vue-router", () => ({
  useRouter: () => ({ push: mockPush }),
}));

vi.mock("../../composables/useUser.js", () => ({
  useUser: () => ({ login: mockLogin }),
}));

describe("Login", () => {
  it("renders sd and sg buttons", () => {
    const wrapper = mount(Login);
    expect(wrapper.find("[data-testid='login-sd']").exists()).toBe(true);
    expect(wrapper.find("[data-testid='login-sg']").exists()).toBe(true);
  });

  it("calls login('sd') and navigates to /trips when sd clicked", async () => {
    const wrapper = mount(Login);
    await wrapper.find("[data-testid='login-sd']").trigger("click");
    expect(mockLogin).toHaveBeenCalledWith("sd");
    expect(mockPush).toHaveBeenCalledWith("/trips");
  });

  it("calls login('sg') and navigates to /trips when sg clicked", async () => {
    mockLogin.mockClear();
    mockPush.mockClear();
    const wrapper = mount(Login);
    await wrapper.find("[data-testid='login-sg']").trigger("click");
    expect(mockLogin).toHaveBeenCalledWith("sg");
    expect(mockPush).toHaveBeenCalledWith("/trips");
  });
});
