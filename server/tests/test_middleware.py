"""测试 X-User 中间件"""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI, Request
from middleware.user import UserMiddleware


def create_test_app():
    app = FastAPI()
    app.add_middleware(UserMiddleware)

    @app.get("/api/whoami")
    async def whoami(request: Request):
        return {"user": request.state.user}

    return app


@pytest.fixture
def app():
    return create_test_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_valid_user_sd_passes(client):
    """带 X-User: sd 的请求正常通过"""
    response = await client.get("/api/whoami", headers={"X-User": "sd"})

    assert response.status_code == 200
    assert response.json() == {"user": "sd"}


@pytest.mark.anyio
async def test_valid_user_sg_passes(client):
    """带 X-User: sg 的请求正常通过"""
    response = await client.get("/api/whoami", headers={"X-User": "sg"})

    assert response.status_code == 200
    assert response.json() == {"user": "sg"}


@pytest.mark.anyio
async def test_missing_user_header_returns_401(client):
    """缺少 X-User header 返回 401"""
    response = await client.get("/api/whoami")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_invalid_user_returns_401(client):
    """X-User 值不是 sd 或 sg 返回 401"""
    response = await client.get("/api/whoami", headers={"X-User": "admin"})

    assert response.status_code == 401
