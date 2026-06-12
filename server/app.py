"""FastAPI 应用工厂"""

import os
import sqlite3
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from middleware.user import UserMiddleware
from db.schema import init_db, migrate
from db.database import DB_PATH
from ws.manager import ConnectionManager


def create_app() -> FastAPI:
    app = FastAPI()

    # 数据库初始化
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    init_db(conn)
    migrate(conn)
    app.state.db = conn

    # WebSocket 连接管理
    app.state.ws_manager = ConnectionManager()

    app.add_middleware(UserMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def db_middleware(request: Request, call_next):
        request.state.db = app.state.db
        return await call_next(request)

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    @app.post("/api/test/reset")
    async def test_reset():
        """测试用：清空所有业务数据"""
        tables = ["expense_items", "packing_items", "activities", "days", "trips"]
        for table in tables:
            conn.execute(f"DELETE FROM {table}")
            conn.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        conn.commit()
        return {"ok": True}

    # WebSocket 端点
    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket, trip_id: int = Query(...), user: str = Query(...)):
        if user not in ("sd", "sg"):
            await ws.close(code=4001)
            return
        await ws.accept()
        app.state.ws_manager.join(trip_id, ws)
        try:
            while True:
                await ws.receive_text()  # 保活 + 接收客户端消息
        except WebSocketDisconnect:
            app.state.ws_manager.leave(trip_id, ws)

    from routes.trips import router as trip_router
    from routes.days import router as day_router
    from routes.activities import router as activity_router
    from routes.packing import router as packing_router
    from routes.settlement import router as settlement_router
    from routes.recycle_bin import router as recycle_router
    app.include_router(trip_router)
    app.include_router(day_router)
    app.include_router(activity_router)
    app.include_router(packing_router)
    app.include_router(settlement_router)
    app.include_router(recycle_router)

    # dev: client/dist, docker: /app/static
    for candidate in [
        os.path.join(os.path.dirname(__file__), "..", "client", "dist"),
        os.path.join(os.path.dirname(__file__), "static"),
    ]:
        if os.path.isdir(candidate):
            app.mount("/", StaticFiles(directory=candidate, html=True), name="static")
            break

    return app

