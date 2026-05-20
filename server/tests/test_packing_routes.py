"""测试打包清单 API"""

import sqlite3
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI, Request

from db.schema import init_db
from middleware.user import UserMiddleware
from ws.manager import ConnectionManager
from routes.trips import router as trip_router
from routes.packing import router as packing_router


def create_test_app(db_conn: sqlite3.Connection) -> FastAPI:
    app = FastAPI()
    app.add_middleware(UserMiddleware)
    app.state.ws_manager = ConnectionManager()

    @app.middleware("http")
    async def db_middleware(request: Request, call_next):
        request.state.db = db_conn
        return await call_next(request)

    app.include_router(trip_router)
    app.include_router(packing_router)
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


# ---------- create ----------

@pytest.mark.anyio
async def test_create_packing_item(client):
    trip_id = await create_trip(client)

    response = await client.post(
        f"/api/trips/{trip_id}/packing",
        json={"name": "护照", "category": "证件", "assignee": "sd"},
        headers=auth(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "护照"
    assert data["category"] == "证件"
    assert data["assignee"] == "sd"
    assert data["checked"] == 0
    assert data["deleted_at"] is None


# ---------- list ----------

@pytest.mark.anyio
async def test_list_packing_items(client):
    trip_id = await create_trip(client)
    await client.post(f"/api/trips/{trip_id}/packing", json={"name": "护照", "category": "证件", "assignee": "sd"}, headers=auth())
    await client.post(f"/api/trips/{trip_id}/packing", json={"name": "相机", "category": "电子", "assignee": "sg"}, headers=auth())

    response = await client.get(f"/api/trips/{trip_id}/packing", headers=auth())

    data = response.json()
    assert len(data) == 2


# ---------- update ----------

@pytest.mark.anyio
async def test_update_packing_item(client):
    trip_id = await create_trip(client)
    item_id = (await client.post(f"/api/trips/{trip_id}/packing",
                                 json={"name": "护照", "category": "证件", "assignee": "sd"}, headers=auth())).json()["id"]

    response = await client.put(f"/api/trips/{trip_id}/packing/{item_id}",
                                json={"name": "护照复印件", "category": "证件副本", "assignee": "sg"}, headers=auth())

    data = response.json()
    assert data["name"] == "护照复印件"
    assert data["assignee"] == "sg"


# ---------- check toggle ----------

@pytest.mark.anyio
async def test_check_packing_item(client):
    trip_id = await create_trip(client)
    item_id = (await client.post(f"/api/trips/{trip_id}/packing",
                                 json={"name": "护照", "category": "证件", "assignee": "sd"}, headers=auth())).json()["id"]

    r1 = await client.put(f"/api/trips/{trip_id}/packing/{item_id}/check", headers=auth())
    assert r1.json()["checked"] == 1

    r2 = await client.put(f"/api/trips/{trip_id}/packing/{item_id}/check", headers=auth())
    assert r2.json()["checked"] == 0


# ---------- delete ----------

@pytest.mark.anyio
async def test_delete_packing_item_soft(client):
    trip_id = await create_trip(client)
    item_id = (await client.post(f"/api/trips/{trip_id}/packing",
                                 json={"name": "护照", "category": "证件", "assignee": "sd"}, headers=auth())).json()["id"]

    await client.delete(f"/api/trips/{trip_id}/packing/{item_id}", headers=auth())
    r = await client.get(f"/api/trips/{trip_id}/packing", headers=auth())
    assert len(r.json()) == 0
