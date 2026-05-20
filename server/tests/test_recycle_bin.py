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
