"""测试 WebSocket 连接管理"""

import sqlite3
import pytest
import asyncio
from ws.manager import ConnectionManager


@pytest.fixture
def manager():
    return ConnectionManager()


def test_join_room(manager):
    ws = object()  # 用 object 代替真正的 WebSocket
    manager.join(1, ws)

    assert len(manager.connections(1)) == 1


def test_join_multiple(manager):
    ws1 = object()
    ws2 = object()

    manager.join(1, ws1)
    manager.join(1, ws2)

    assert len(manager.connections(1)) == 2


def test_leave_room(manager):
    ws1 = object()
    ws2 = object()

    manager.join(1, ws1)
    manager.join(1, ws2)
    manager.leave(1, ws1)

    assert len(manager.connections(1)) == 1


def test_leave_cleans_empty_room(manager):
    ws = object()
    manager.join(1, ws)
    manager.leave(1, ws)

    assert 1 not in manager.rooms()


def test_broadcast_sends_to_all_in_room(manager):
    received = []

    class MockWS:
        async def send_json(self, data):
            received.append(data)

    ws1 = MockWS()
    ws2 = MockWS()
    ws_other = MockWS()

    manager.join(1, ws1)
    manager.join(1, ws2)
    manager.join(2, ws_other)

    async def run():
        await manager.broadcast(1, "activity_created", {"name": "test"})

    asyncio.run(run())

    assert len(received) == 2  # ws1 和 ws2 收到，ws_other 没收到
    assert received[0] == {"type": "activity_created", "payload": {"name": "test"}}


def test_broadcast_excludes_sender(manager):
    received = []

    class MockWS:
        async def send_json(self, data):
            received.append(data)

    ws1 = MockWS()
    ws2 = MockWS()

    manager.join(1, ws1)
    manager.join(1, ws2)

    async def run():
        await manager.broadcast(1, "activity_created", {"name": "test"}, exclude=ws1)

    asyncio.run(run())

    assert len(received) == 1  # ws1 被排除
