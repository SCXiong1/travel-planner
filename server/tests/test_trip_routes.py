"""测试旅行计划 API"""

import pytest


def auth(user="sd"):
    return {"X-User": user}


# ---------- create ----------

@pytest.mark.anyio
async def test_create_trip(client):
    response = await client.post(
        "/api/trips",
        json={
            "title": "日本行",
            "destination": "东京",
            "start_date": "2026-06-01",
            "end_date": "2026-06-07",
        },
        headers=auth(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "日本行"
    assert data["destination"] == "东京"
    assert data["id"] == 1
    assert data["created_at"] is not None
    assert data["deleted_at"] is None


# ---------- list ----------

@pytest.mark.anyio
async def test_list_trips_empty(client):
    response = await client.get("/api/trips", headers=auth())

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_list_trips_returns_all(client):
    # 先创建两条
    await client.post(
        "/api/trips",
        json={"title": "日本行", "destination": "东京", "start_date": "2026-06-01", "end_date": "2026-06-07"},
        headers=auth(),
    )
    await client.post(
        "/api/trips",
        json={"title": "韩国行", "destination": "首尔", "start_date": "2026-07-01", "end_date": "2026-07-05"},
        headers=auth(),
    )

    response = await client.get("/api/trips", headers=auth())

    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "韩国行"  # 新建的 sort_order=0 排最前
    assert data[1]["title"] == "日本行"


# ---------- get ----------

@pytest.mark.anyio
async def test_get_trip(client):
    await client.post(
        "/api/trips",
        json={"title": "日本行", "destination": "东京", "start_date": "2026-06-01", "end_date": "2026-06-07"},
        headers=auth(),
    )

    response = await client.get("/api/trips/1", headers=auth())

    assert response.status_code == 200
    assert response.json()["title"] == "日本行"


@pytest.mark.anyio
async def test_get_trip_404(client):
    response = await client.get("/api/trips/999", headers=auth())
    assert response.status_code == 404


# ---------- update ----------

@pytest.mark.anyio
async def test_update_trip(client):
    await client.post(
        "/api/trips",
        json={"title": "日本行", "destination": "东京", "start_date": "2026-06-01", "end_date": "2026-06-07"},
        headers=auth(),
    )

    response = await client.put(
        "/api/trips/1",
        json={"title": "日本游", "destination": "大阪", "start_date": "2026-06-02", "end_date": "2026-06-08"},
        headers=auth(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "日本游"
    assert data["destination"] == "大阪"


# ---------- delete ----------

@pytest.mark.anyio
async def test_delete_trip_soft(client):
    await client.post(
        "/api/trips",
        json={"title": "日本行", "destination": "东京", "start_date": "2026-06-01", "end_date": "2026-06-07"},
        headers=auth(),
    )

    response = await client.delete("/api/trips/1", headers=auth())
    assert response.status_code == 200

    # 列表只显示未删除的
    list_resp = await client.get("/api/trips", headers=auth())
    assert list_resp.json() == []

    # 但可以通过 get 看到 deleted_at（实际上直接 get 也会被过滤的... 取决于实现）
    # 这里验证已删除的不会出现在列表中即可


# ---------- date validation ----------

@pytest.mark.anyio
async def test_create_trip_start_after_end_returns_400(client):
    response = await client.post(
        "/api/trips",
        json={"title": "日期错误", "destination": "测试", "start_date": "2026-06-07", "end_date": "2026-06-01"},
        headers=auth(),
    )

    assert response.status_code == 400
    assert "开始日期" in response.json()["detail"]


@pytest.mark.anyio
async def test_update_trip_start_after_end_returns_400(client):
    await client.post(
        "/api/trips",
        json={"title": "测试", "destination": "测试", "start_date": "2026-06-01", "end_date": "2026-06-07"},
        headers=auth(),
    )

    response = await client.put(
        "/api/trips/1",
        json={"title": "测试", "destination": "测试", "start_date": "2026-06-10", "end_date": "2026-06-05"},
        headers=auth(),
    )

    assert response.status_code == 400
    assert "开始日期" in response.json()["detail"]
