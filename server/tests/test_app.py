"""测试 FastAPI 应用创建和基础端点"""

import pytest
from httpx import ASGITransport, AsyncClient
from app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_health_returns_200(client):
    """GET /api/health 返回 200 和 ok"""
    response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
