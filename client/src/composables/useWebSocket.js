import { ref } from "vue";

export function useWebSocket() {
  let ws = null;
  const connected = ref(false);

  function connect(tripId, user, onEvent) {
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    const url = `${protocol}//${location.host}/ws?trip_id=${tripId}&user=${user}`;

    ws = new WebSocket(url);

    ws.onopen = () => {
      connected.value = true;
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (onEvent) onEvent(msg);
    };

    ws.onclose = () => {
      connected.value = false;
    };
  }

  function disconnect() {
    if (ws) {
      ws.close();
      ws = null;
    }
  }

  return { connect, disconnect, connected };
}
