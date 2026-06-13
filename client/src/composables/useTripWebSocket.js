import { watch, onUnmounted } from "vue";
import { useWebSocket } from "./useWebSocket.js";
import { useUser } from "./useUser.js";

export function useTripWebSocket(tripId, onMessage) {
  const { current: currentUser } = useUser();
  const ws = useWebSocket();

  ws.connect(tripId, currentUser.value, onMessage);

  watch(currentUser, () => {
    ws.disconnect();
    ws.connect(tripId, currentUser.value, onMessage);
  });

  function cleanup() {
    ws.disconnect();
  }

  onUnmounted(cleanup);

  return { cleanup };
}
