"""测试结算"""

import sqlite3
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI, Request

from db.schema import init_db, migrate
from middleware.user import UserMiddleware
from ws.manager import ConnectionManager
from routes.trips import router as trip_router
from routes.days import router as day_router
from routes.activities import router as activity_router
from routes.settlement import router as settlement_router


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
    app.include_router(settlement_router)
    return app


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    init_db(conn)
    migrate(conn)
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


async def create_act(client, trip_id, day_id, expense_items=None, **extra):
    json = {"type": "eat", "name": "test", "start_time": "08:00", "end_time": "09:00", **extra}
    if expense_items:
        json["expense_items"] = expense_items
    r = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json=json,
        headers=auth(),
    )
    return r.json()


# ---------- tests ----------

@pytest.mark.anyio
async def test_settlement_empty(client):
    trip_id = await create_trip(client)

    resp = await client.get(f"/api/trips/{trip_id}/settlement", headers=auth())

    data = resp.json()
    assert data["sd_paid"] == 0
    assert data["sg_paid"] == 0
    assert data["total"] == 0
    assert data["balance"] == 0  # 持平


@pytest.mark.anyio
async def test_settlement_equal_split(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    # sd 付了 ¥200，平分
    await create_act(client, trip_id, day_id,
                     expense_items=[{"amount": 200, "payer": "sd", "split": "equal"}])

    resp = await client.get(f"/api/trips/{trip_id}/settlement", headers=auth())
    data = resp.json()

    assert data["sd_paid"] == 200
    assert data["sg_paid"] == 0
    assert data["total"] == 200
    assert data["sd_owes"] == 100   # 各承担一半
    assert data["sg_owes"] == 100
    assert data["sd_balance"] == 100   # sd付200只该出100, sg欠sd 100
    assert data["sg_balance"] == -100


@pytest.mark.anyio
async def test_settlement_assign_split(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    # sd 付 ¥300，归集到 sd 自己
    await create_act(client, trip_id, day_id,
                     expense_items=[{"amount": 300, "payer": "sd", "split": "assign"}])

    resp = await client.get(f"/api/trips/{trip_id}/settlement", headers=auth())
    data = resp.json()

    assert data["sd_paid"] == 300
    assert data["sd_owes"] == 300  # 归集全部由 sd 承担
    assert data["sg_owes"] == 0
    assert data["sd_balance"] == 0   # 持平


@pytest.mark.anyio
async def test_settlement_mixed(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    # sd 付200 平分 (各100)
    await create_act(client, trip_id, day_id,
                     expense_items=[{"amount": 200, "payer": "sd", "split": "equal"}])
    # sg 付300 归集 (sg全承担300)
    await create_act(client, trip_id, day_id,
                     expense_items=[{"amount": 300, "payer": "sg", "split": "assign"}])

    resp = await client.get(f"/api/trips/{trip_id}/settlement", headers=auth())
    data = resp.json()

    assert data["total"] == 500
    assert data["sd_paid"] == 200
    assert data["sg_paid"] == 300
    assert data["sd_owes"] == 100    # 只承担平分那条的一半
    assert data["sg_owes"] == 400    # 平分100 + 归集300
    assert data["sd_balance"] == 100   # sd付200该出100，sg欠sd100
    assert data["sg_balance"] == -100


@pytest.mark.anyio
async def test_settlement_multi_expense_per_activity(client):
    """一个活动含多笔开销，各自按不同 payer+split 参与结算"""
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    # 一个活动两笔开销：sd 付 100 平分 + sg 付 200 归集
    await create_act(client, trip_id, day_id, expense_items=[
        {"amount": 100, "payer": "sd", "split": "equal"},
        {"amount": 200, "payer": "sg", "split": "assign"},
    ])

    resp = await client.get(f"/api/trips/{trip_id}/settlement", headers=auth())
    data = resp.json()

    assert data["sd_paid"] == 100
    assert data["sg_paid"] == 200
    assert data["total"] == 300
    assert data["sd_owes"] == 50     # 平分那笔的一半
    assert data["sg_owes"] == 250    # 平分50 + 归集200
    assert data["sd_balance"] == 50
    assert data["sg_balance"] == -50
