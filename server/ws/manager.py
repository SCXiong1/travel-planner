"""WebSocket 连接管理"""

from collections import defaultdict


class ConnectionManager:
    def __init__(self):
        self._rooms: dict[int, set] = defaultdict(set)

    def join(self, trip_id: int, ws):
        self._rooms[trip_id].add(ws)

    def leave(self, trip_id: int, ws):
        self._rooms[trip_id].discard(ws)
        if not self._rooms[trip_id]:
            del self._rooms[trip_id]

    def connections(self, trip_id: int) -> set:
        return self._rooms.get(trip_id, set())

    def rooms(self) -> dict:
        return dict(self._rooms)

    async def broadcast(self, trip_id: int, event_type: str, payload: dict, exclude=None):
        message = {"type": event_type, "payload": payload}
        for ws in self.connections(trip_id):
            if ws is exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                pass  # 断开的连接下次 join 时会清理
