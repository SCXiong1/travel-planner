"""测试回收站"""

import sqlite3
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI, Request

from db.schema import init_db
from middleware.user import UserMiddleware
from ws.manager import ConnectionManager
from routes.trips import router as trip_router
from routes.days import router as day_router
from routes.activities import router as activity_router
from routes.packing import router as packing_router
from routes.recycle_bin import router as recycle_router


def create_test_app(db_conn: sqlite3.Connection) -> FastAPI:
    app = FastAPI()
    app.add_middleware(UserMiddleware)
    app.state.ws_manager = ConnectionManager()

    @app.middleware("http")
    async def db_middleware(request: Request, call_next):
        request.state.db = db_conn
        return await call_next(request)

    for r in [trip_router, day_router, activity_router, packing_router, recycle_router]:
        app.include_router(r)
    return app


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    init_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def app(db):
    return create_test_app(db)


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def auth(user="sd"):
    return {"X-User": user}


async def create_trip(client):
    r = await client.post(
        "/api/trips",
        json={"title": "日本行", "destination": "东京", "start_date": "2026-06-01", "end_date": "2026-06-07"},
        headers=auth(),
    )
    return r.json()["id"]


async def create_day(client, trip_id):
    r = await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-01"}, headers=auth())
    return r.json()["id"]


# ---------- recycle bin list ----------

@pytest.mark.anyio
async def test_recycle_bin_empty(client):
    trip_id = await create_trip(client)

    resp = await client.get(f"/api/trips/{trip_id}/recycle-bin", headers=auth())

    assert resp.json() == []


@pytest.mark.anyio
async def test_recycle_bin_shows_deleted_activities(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    # 创建并删除活动
    r = await client.post(f"/api/trips/{trip_id}/days/{day_id}/activities",
                          json={"type": "eat", "name": "被删的早餐", "start_time": "08:00", "end_time": "09:00"}, headers=auth())
    act_id = r.json()["id"]
    await client.delete(f"/api/trips/{trip_id}/days/{day_id}/activities/{act_id}", headers=auth())

    resp = await client.get(f"/api/trips/{trip_id}/recycle-bin", headers=auth())
    data = resp.json()

    assert len(data) == 1
    assert data[0]["name"] == "被删的早餐"
    assert data[0]["type"] == "activity"
    assert data[0]["deleted_at"] is not None


@pytest.mark.anyio
async def test_recycle_bin_shows_deleted_packing(client):
    trip_id = await create_trip(client)

    r = await client.post(f"/api/trips/{trip_id}/packing",
                          json={"name": "被删的物品", "category": "证件", "assignee": "sd"}, headers=auth())
    item_id = r.json()["id"]
    await client.delete(f"/api/trips/{trip_id}/packing/{item_id}", headers=auth())

    resp = await client.get(f"/api/trips/{trip_id}/recycle-bin", headers=auth())
    data = resp.json()

    assert len(data) == 1
    assert data[0]["name"] == "被删的物品"
    assert data[0]["type"] == "packing"


# ---------- restore ----------

@pytest.mark.anyio
async def test_restore_activity(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    r = await client.post(f"/api/trips/{trip_id}/days/{day_id}/activities",
                          json={"type": "eat", "name": "恢复测试", "start_time": "08:00", "end_time": "09:00"}, headers=auth())
    act_id = r.json()["id"]
    await client.delete(f"/api/trips/{trip_id}/days/{day_id}/activities/{act_id}", headers=auth())

    # 恢复
    restore_resp = await client.post(f"/api/recycle-bin/activity/{act_id}/restore", headers=auth())
    assert restore_resp.status_code == 200

    # 回收站为空
    rb = await client.get(f"/api/trips/{trip_id}/recycle-bin", headers=auth())
    assert len(rb.json()) == 0

    # 活动列表恢复
    acts = await client.get(f"/api/trips/{trip_id}/days/{day_id}/activities", headers=auth())
    assert len(acts.json()) == 1
    assert acts.json()[0]["name"] == "恢复测试"


@pytest.mark.anyio
async def test_restore_packing(client):
    trip_id = await create_trip(client)

    r = await client.post(f"/api/trips/{trip_id}/packing",
                          json={"name": "恢复物品", "category": "证件", "assignee": "sd"}, headers=auth())
    item_id = r.json()["id"]
    await client.delete(f"/api/trips/{trip_id}/packing/{item_id}", headers=auth())

    await client.post(f"/api/recycle-bin/packing/{item_id}/restore", headers=auth())

    items = await client.get(f"/api/trips/{trip_id}/packing", headers=auth())
    assert len(items.json()) == 1


# ---------- global recycle bin (trip/day types) ----------

@pytest.mark.anyio
async def test_recycle_bin_shows_deleted_trip(client):
    """全局回收站列出已删除的 trip"""
    trip_id = await create_trip(client)

    await client.delete(f"/api/trips/{trip_id}", headers=auth())

    resp = await client.get("/api/recycle-bin", headers=auth())
    data = resp.json()

    trip_items = [d for d in data if d["type"] == "trip"]
    assert len(trip_items) == 1
    assert trip_items[0]["name"] == "日本行"
    assert trip_items[0]["deleted_at"] is not None


@pytest.mark.anyio
async def test_recycle_bin_shows_deleted_day(client):
    """全局回收站列出已删除的 day"""
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    await client.delete(f"/api/trips/{trip_id}/days/{day_id}", headers=auth())

    resp = await client.get("/api/recycle-bin", headers=auth())
    data = resp.json()

    day_items = [d for d in data if d["type"] == "day"]
    assert len(day_items) == 1
    assert day_items[0]["deleted_at"] is not None
    assert day_items[0]["trip_id"] == trip_id


# ---------- restore trip/day ----------

@pytest.mark.anyio
async def test_restore_trip(client):
    """恢复已删除的 trip"""
    trip_id = await create_trip(client)

    await client.delete(f"/api/trips/{trip_id}", headers=auth())

    # 确认在回收站
    rb = await client.get("/api/recycle-bin", headers=auth())
    assert len([d for d in rb.json() if d["type"] == "trip"]) == 1

    # 恢复
    r = await client.post(f"/api/recycle-bin/trip/{trip_id}/restore", headers=auth())
    assert r.status_code == 200

    # 回收站不再出现
    rb2 = await client.get("/api/recycle-bin", headers=auth())
    assert len([d for d in rb2.json() if d["type"] == "trip"]) == 0

    # trip 列表恢复正常
    trips = await client.get("/api/trips", headers=auth())
    assert len(trips.json()) == 1
    assert trips.json()[0]["title"] == "日本行"


@pytest.mark.anyio
async def test_restore_day(client):
    """恢复已删除的 day"""
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    await client.delete(f"/api/trips/{trip_id}/days/{day_id}", headers=auth())

    r = await client.post(f"/api/recycle-bin/day/{day_id}/restore", headers=auth())
    assert r.status_code == 200

    # day 列表恢复正常
    days = await client.get(f"/api/trips/{trip_id}/days", headers=auth())
    assert len(days.json()) == 1


# ---------- restore conflict checks ----------

@pytest.mark.anyio
async def test_restore_day_fails_when_trip_deleted(client):
    """恢复 day 时其 trip 已被删 → 阻断并返回 400"""
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    # 先删 day，再删 trip
    await client.delete(f"/api/trips/{trip_id}/days/{day_id}", headers=auth())
    await client.delete(f"/api/trips/{trip_id}", headers=auth())

    r = await client.post(f"/api/recycle-bin/day/{day_id}/restore", headers=auth())
    assert r.status_code == 400
    assert "旅行" in r.json()["detail"]


@pytest.mark.anyio
async def test_restore_activity_fails_when_day_deleted(client):
    """恢复 activity 时其 day 已被删 → 阻断并返回 400"""
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    r = await client.post(f"/api/trips/{trip_id}/days/{day_id}/activities",
                          json={"type": "eat", "name": "寿司", "start_time": "08:00", "end_time": "09:00"}, headers=auth())
    act_id = r.json()["id"]

    # 先删 activity，再删 day
    await client.delete(f"/api/trips/{trip_id}/days/{day_id}/activities/{act_id}", headers=auth())
    await client.delete(f"/api/trips/{trip_id}/days/{day_id}", headers=auth())

    r = await client.post(f"/api/recycle-bin/activity/{act_id}/restore", headers=auth())
    assert r.status_code == 400
    assert "天" in r.json()["detail"]


# ---------- permanent delete ----------

@pytest.mark.anyio
async def test_permanent_delete(client):
    """永久删除后物理清除，回收站不再出现"""
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    r = await client.post(f"/api/trips/{trip_id}/days/{day_id}/activities",
                          json={"type": "eat", "name": "待永久删除", "start_time": "08:00", "end_time": "09:00"}, headers=auth())
    act_id = r.json()["id"]

    # 软删除
    await client.delete(f"/api/trips/{trip_id}/days/{day_id}/activities/{act_id}", headers=auth())

    # 确认在回收站
    rb = await client.get("/api/recycle-bin", headers=auth())
    assert len([d for d in rb.json() if d["type"] == "activity" and d["id"] == act_id]) == 1

    # 永久删除
    r = await client.delete(f"/api/recycle-bin/activity/{act_id}", headers=auth())
    assert r.status_code == 200

    # 回收站不再出现
    rb2 = await client.get("/api/recycle-bin", headers=auth())
    assert len([d for d in rb2.json() if d["type"] == "activity" and d["id"] == act_id]) == 0
