"""测试天管理 API"""

import sqlite3
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI, Request

from db.schema import init_db
from middleware.user import UserMiddleware
from routes.trips import router as trip_router
from routes.days import router as day_router


def create_test_app(db_conn: sqlite3.Connection) -> FastAPI:
    app = FastAPI()
    app.add_middleware(UserMiddleware)

    @app.middleware("http")
    async def db_middleware(request: Request, call_next):
        request.state.db = db_conn
        return await call_next(request)

    app.include_router(trip_router)
    app.include_router(day_router)
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


# helper: create trip, return trip_id
async def create_trip(client, title="日本行"):
    r = await client.post(
        "/api/trips",
        json={"title": title, "destination": "东京", "start_date": "2026-06-01", "end_date": "2026-06-07"},
        headers=auth(),
    )
    return r.json()["id"]


# ---------- create ----------

@pytest.mark.anyio
async def test_create_day(client):
    trip_id = await create_trip(client)

    response = await client.post(
        f"/api/trips/{trip_id}/days",
        json={"date": "2026-06-01"},
        headers=auth(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["trip_id"] == trip_id
    assert data["day_number"] == 1
    assert data["date"] == "2026-06-01"
    assert data["deleted_at"] is None


@pytest.mark.anyio
async def test_create_day_increments_day_number(client):
    trip_id = await create_trip(client)

    await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-01"}, headers=auth())
    r = await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-02"}, headers=auth())

    assert r.json()["day_number"] == 2


# ---------- list ----------

@pytest.mark.anyio
async def test_list_days(client):
    trip_id = await create_trip(client)
    await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-02"}, headers=auth())
    await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-01"}, headers=auth())

    response = await client.get(f"/api/trips/{trip_id}/days", headers=auth())

    data = response.json()
    assert len(data) == 2
    assert data[0]["day_number"] == 1  # 按 day_number 排序


# ---------- update ----------

@pytest.mark.anyio
async def test_update_day(client):
    trip_id = await create_trip(client)
    day_id = (await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-01"}, headers=auth())).json()["id"]

    response = await client.put(f"/api/trips/{trip_id}/days/{day_id}", json={"date": "2026-06-03", "title": "第三天"}, headers=auth())

    data = response.json()
    assert data["date"] == "2026-06-03"
    assert data["title"] == "第三天"


# ---------- delete ----------

@pytest.mark.anyio
async def test_delete_day_soft(client):
    trip_id = await create_trip(client)
    day_id = (await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-01"}, headers=auth())).json()["id"]

    await client.delete(f"/api/trips/{trip_id}/days/{day_id}", headers=auth())

    # 列表不再包含已删天
    r = await client.get(f"/api/trips/{trip_id}/days", headers=auth())
    assert len(r.json()) == 0


# ---------- reorder ----------

@pytest.mark.anyio
async def test_reorder_days(client):
    trip_id = await create_trip(client)
    d1 = (await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-01"}, headers=auth())).json()["id"]
    d2 = (await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-02"}, headers=auth())).json()["id"]

    # 交换顺序
    response = await client.put(
        f"/api/trips/{trip_id}/days/reorder",
        json=[{"id": d1, "day_number": 2}, {"id": d2, "day_number": 1}],
        headers=auth(),
    )

    assert response.status_code == 200
    # 验证排序结果
    days = (await client.get(f"/api/trips/{trip_id}/days", headers=auth())).json()
    assert days[0]["id"] == d2
    assert days[1]["id"] == d1


# ---------- date range validation ----------

@pytest.mark.anyio
async def test_create_day_out_of_range(client):
    """创建 day 时 date 超出 trip 的 start_date~end_date 范围应返回 400"""
    trip_id = await create_trip(client)  # 06-01 ~ 06-07

    # 早于 start_date
    r1 = await client.post(
        f"/api/trips/{trip_id}/days",
        json={"date": "2026-05-30"},
        headers=auth(),
    )
    assert r1.status_code == 400

    # 晚于 end_date
    r2 = await client.post(
        f"/api/trips/{trip_id}/days",
        json={"date": "2026-06-10"},
        headers=auth(),
    )
    assert r2.status_code == 400


@pytest.mark.anyio
async def test_create_day_number_skips_deleted(client):
    """软删除天后，新 day 的 day_number 不应回退复用已删的号码"""
    trip_id = await create_trip(client)

    # 创建 3 天
    d1 = await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-01"}, headers=auth())
    d2 = await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-02"}, headers=auth())
    d3 = await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-03"}, headers=auth())

    assert d1.json()["day_number"] == 1
    assert d2.json()["day_number"] == 2
    assert d3.json()["day_number"] == 3

    # 软删除最后一天（第 3 天），暴露 MAX 回退 bug
    await client.delete(f"/api/trips/{trip_id}/days/{d3.json()['id']}", headers=auth())

    # 再创建新天，day_number 应为 4（严格递增），而非回退到 3
    r = await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-04"}, headers=auth())
    assert r.status_code == 200
    assert r.json()["day_number"] == 4
