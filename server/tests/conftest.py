"""共享测试 fixture"""

import sqlite3
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI, Request

from db.schema import init_db
from middleware.user import UserMiddleware
from ws.manager import ConnectionManager


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    init_db(conn)
    yield conn
    conn.close()


def create_test_app(db_conn: sqlite3.Connection, *routers) -> FastAPI:
    app = FastAPI()
    app.add_middleware(UserMiddleware)
    app.state.ws_manager = ConnectionManager()

    @app.middleware("http")
    async def db_middleware(request: Request, call_next):
        request.state.db = db_conn
        return await call_next(request)

    for router in routers:
        app.include_router(router)
    return app


@pytest.fixture
def create_app(db):
    """返回工厂函数，供需要自定义路由的测试覆盖 app fixture"""
    def _create(*routers):
        return create_test_app(db, *routers)
    return _create


@pytest.fixture
def app(db):
    from routes.trips import router as trip_router
    return create_test_app(db, trip_router)


@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
