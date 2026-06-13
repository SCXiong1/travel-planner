import { describe, it, expect, vi, beforeEach } from "vitest";
import { ref, nextTick } from "vue";

const mockConnect = vi.fn();
const mockDisconnect = vi.fn();

vi.mock("../useWebSocket.js", () => ({
  useWebSocket: () => ({ connect: mockConnect, disconnect: mockDisconnect }),
}));

vi.mock("../useUser.js", () => ({
  useUser: () => ({ current: ref("sd"), switchUser: vi.fn() }),
}));

let useTripWebSocket;

describe("useTripWebSocket", () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    const mod = await import("../useTripWebSocket.js");
    useTripWebSocket = mod.useTripWebSocket;
  });

  it("connects on mount", () => {
    const onMessage = vi.fn();
    useTripWebSocket("1", onMessage);

    expect(mockConnect).toHaveBeenCalledWith("1", "sd", onMessage);
  });

  it("disconnects on cleanup", () => {
    const onMessage = vi.fn();
    const { cleanup } = useTripWebSocket("1", onMessage);

    cleanup();
    expect(mockDisconnect).toHaveBeenCalled();
  });
});
