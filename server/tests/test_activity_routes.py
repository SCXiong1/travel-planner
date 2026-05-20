"""测试活动管理 API"""

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


def create_test_app(db_conn: sqlite3.Connection) -> FastAPI:
    app = FastAPI()
    app.add_middleware(UserMiddleware)
    app.state.ws_manager = ConnectionManager()

    @app.middleware("http")
    async def db_middleware(request: Request, call_next):
        request.state.db = db_conn
        return await call_next(request)

    app.include_router(trip_router)
    app.include_router(day_router)
    app.include_router(activity_router)
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


async def create_trip(client, title="日本行"):
    r = await client.post(
        "/api/trips",
        json={"title": title, "destination": "东京", "start_date": "2026-06-01", "end_date": "2026-06-07"},
        headers=auth(),
    )
    return r.json()["id"]


async def create_day(client, trip_id, date="2026-06-01"):
    r = await client.post(f"/api/trips/{trip_id}/days", json={"date": date}, headers=auth())
    return r.json()["id"]


# ---------- create ----------

@pytest.mark.anyio
async def test_create_activity(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    response = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={"type": "eat", "name": "寿司大", "start_time": "08:00", "end_time": "09:00"},
        headers=auth(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "eat"
    assert data["name"] == "寿司大"
    assert data["start_time"] == "08:00"
    assert data["end_time"] == "09:00"
    assert data["sort_order"] == 0
    assert data["deleted_at"] is None


@pytest.mark.anyio
async def test_create_activity_with_location(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    response = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={"type": "sight", "name": "浅草寺", "location": "台东区", "start_time": "10:00", "end_time": "12:00"},
        headers=auth(),
    )

    data = response.json()
    assert data["location"] == "台东区"


# ---------- list ----------

@pytest.mark.anyio
async def test_list_activities(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    await client.post(f"/api/trips/{trip_id}/days/{day_id}/activities",
                      json={"type": "eat", "name": "早餐", "start_time": "08:00", "end_time": "09:00"}, headers=auth())
    await client.post(f"/api/trips/{trip_id}/days/{day_id}/activities",
                      json={"type": "sight", "name": "景点", "start_time": "10:00", "end_time": "12:00"}, headers=auth())

    response = await client.get(f"/api/trips/{trip_id}/days/{day_id}/activities", headers=auth())

    data = response.json()
    assert len(data) == 2


# ---------- update ----------

@pytest.mark.anyio
async def test_update_activity(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)
    act_id = (await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={"type": "eat", "name": "早餐", "start_time": "08:00", "end_time": "09:00"}, headers=auth()
    )).json()["id"]

    response = await client.put(
        f"/api/trips/{trip_id}/days/{day_id}/activities/{act_id}",
        json={"name": "晚早餐", "start_time": "09:00"},
        headers=auth(),
    )

    data = response.json()
    assert data["name"] == "晚早餐"
    assert data["start_time"] == "09:00"
    assert data["type"] == "eat"  # 未改的字段保持不变


# ---------- delete ----------

@pytest.mark.anyio
async def test_delete_activity_soft(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)
    act_id = (await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={"type": "eat", "name": "早餐", "start_time": "08:00", "end_time": "09:00"}, headers=auth()
    )).json()["id"]

    await client.delete(f"/api/trips/{trip_id}/days/{day_id}/activities/{act_id}", headers=auth())

    r = await client.get(f"/api/trips/{trip_id}/days/{day_id}/activities", headers=auth())
    assert len(r.json()) == 0


# ---------- reorder ----------

@pytest.mark.anyio
async def test_reorder_activities(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)
    a1 = (await client.post(f"/api/trips/{trip_id}/days/{day_id}/activities",
                            json={"type": "eat", "name": "A", "start_time": "08:00", "end_time": "09:00"}, headers=auth())).json()["id"]
    a2 = (await client.post(f"/api/trips/{trip_id}/days/{day_id}/activities",
                            json={"type": "sight", "name": "B", "start_time": "10:00", "end_time": "12:00"}, headers=auth())).json()["id"]

    response = await client.put(
        f"/api/trips/{trip_id}/days/{day_id}/activities/reorder",
        json=[{"id": a1, "sort_order": 1}, {"id": a2, "sort_order": 0}],
        headers=auth(),
    )

    assert response.status_code == 200
    acts = (await client.get(f"/api/trips/{trip_id}/days/{day_id}/activities", headers=auth())).json()
    assert acts[0]["id"] == a2
    assert acts[1]["id"] == a1


# ---------- extensions: expense, review, reservation ----------

@pytest.mark.anyio
async def test_create_activity_with_expense(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    response = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={
            "type": "eat", "name": "寿司大", "start_time": "08:00", "end_time": "09:00",
            "expense_amount": 200, "expense_payer": "sd", "expense_split": "equal",
        },
        headers=auth(),
    )

    data = response.json()
    assert data["expense_amount"] == 200
    assert data["expense_payer"] == "sd"
    assert data["expense_split"] == "equal"


@pytest.mark.anyio
async def test_create_activity_with_reservation(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    response = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={
            "type": "stay", "name": "温泉旅馆", "start_time": "18:00", "end_time": "08:00",
            "need_reservation": True, "reservation_detail": "已电话确认, 确认号 1234",
        },
        headers=auth(),
    )

    data = response.json()
    assert data["need_reservation"] == 1
    assert data["reservation_detail"] == "已电话确认, 确认号 1234"


@pytest.mark.anyio
async def test_create_activity_with_review(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    response = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={
            "type": "sight", "name": "浅草寺", "start_time": "10:00", "end_time": "12:00",
            "review": "非常值得去, 人很多但值得排队",
        },
        headers=auth(),
    )

    data = response.json()
    assert data["review"] == "非常值得去, 人很多但值得排队"


@pytest.mark.anyio
async def test_update_activity_extensions(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)
    act_id = (await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={"type": "eat", "name": "早餐", "start_time": "08:00", "end_time": "09:00"},
        headers=auth(),
    )).json()["id"]

    response = await client.put(
        f"/api/trips/{trip_id}/days/{day_id}/activities/{act_id}",
        json={
            "expense_amount": 100, "expense_payer": "sg", "expense_split": "assign",
            "review": "一般般",
            "need_reservation": False,
        },
        headers=auth(),
    )

    data = response.json()
    assert data["expense_amount"] == 100
    assert data["expense_payer"] == "sg"
    assert data["review"] == "一般般"
