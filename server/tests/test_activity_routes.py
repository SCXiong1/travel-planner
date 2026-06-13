"""测试活动管理 API"""

import pytest

from routes.trips import router as trip_router
from routes.days import router as day_router
from routes.activities import router as activity_router


@pytest.fixture
def app(create_app):
    return create_app(trip_router, day_router, activity_router)


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
async def test_create_activity_with_expense_items(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    response = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={
            "type": "eat", "name": "寿司大", "start_time": "08:00", "end_time": "09:00",
            "expense_items": [
                {"amount": 200, "payer": "sd", "split": "equal"},
                {"amount": 50, "payer": "sg", "split": "assign"},
            ],
        },
        headers=auth(),
    )

    data = response.json()
    assert len(data["expense_items"]) == 2
    assert data["expense_items"][0]["amount"] == 200
    assert data["expense_items"][0]["payer"] == "sd"
    assert data["expense_items"][1]["amount"] == 50
    assert data["expense_items"][1]["payer"] == "sg"
    assert data["expense_total"] == 250


@pytest.mark.anyio
async def test_create_activity_with_reservation(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    response = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={
            "type": "stay", "name": "温泉旅馆", "start_time": "15:00", "end_time": "18:00",
            "need_reservation": True, "reservation_detail": "已电话确认, 确认号 1234",
        },
        headers=auth(),
    )

    data = response.json()
    assert data["need_reservation"] == 1
    assert data["reservation_detail"] == "已电话确认, 确认号 1234"


@pytest.mark.anyio
async def test_create_activity_with_sd_review(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    response = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={
            "type": "sight", "name": "浅草寺", "start_time": "10:00", "end_time": "12:00",
            "sd_review": "sd觉得很好",
        },
        headers=auth("sd"),
    )

    data = response.json()
    assert data["sd_review"] == "sd觉得很好"
    assert data["sg_review"] == "" or data["sg_review"] is None


@pytest.mark.anyio
async def test_sd_cannot_write_sg_review(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    response = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={
            "type": "sight", "name": "浅草寺", "start_time": "10:00", "end_time": "12:00",
            "sd_review": "sd的", "sg_review": "sd帮sg写的",
        },
        headers=auth("sd"),
    )

    data = response.json()
    assert data["sd_review"] == "sd的"
    assert not data["sg_review"]


@pytest.mark.anyio
async def test_sg_updates_own_review(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)
    act_id = (await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={
            "type": "sight", "name": "浅草寺", "start_time": "10:00", "end_time": "12:00",
            "sd_review": "sd觉得好",
        },
        headers=auth("sd"),
    )).json()["id"]

    response = await client.put(
        f"/api/trips/{trip_id}/days/{day_id}/activities/{act_id}",
        json={"sg_review": "sg也觉得好"},
        headers=auth("sg"),
    )

    data = response.json()
    assert data["sd_review"] == "sd觉得好"  # 未被覆盖
    assert data["sg_review"] == "sg也觉得好"


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
            "expense_items": [{"amount": 100, "payer": "sg", "split": "assign"}],
            "need_reservation": False,
        },
        headers=auth(),
    )

    data = response.json()
    assert len(data["expense_items"]) == 1
    assert data["expense_items"][0]["amount"] == 100
    assert data["expense_total"] == 100


@pytest.mark.anyio
async def test_update_activity_replaces_expense_items(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)
    act = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={
            "type": "eat", "name": "晚餐", "start_time": "18:00", "end_time": "20:00",
            "expense_items": [
                {"amount": 100, "payer": "sd", "split": "equal"},
                {"amount": 200, "payer": "sg", "split": "assign"},
            ],
        },
        headers=auth(),
    )
    act_id = act.json()["id"]
    assert act.json()["expense_total"] == 300

    # 替换为 1 条新开销
    resp = await client.put(
        f"/api/trips/{trip_id}/days/{day_id}/activities/{act_id}",
        json={"expense_items": [{"amount": 50, "payer": "sd", "split": "equal"}]},
        headers=auth(),
    )
    data = resp.json()
    assert len(data["expense_items"]) == 1
    assert data["expense_items"][0]["amount"] == 50
    assert data["expense_total"] == 50


# ---------- time validation ----------

@pytest.mark.anyio
async def test_create_activity_start_after_end_returns_400(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)

    response = await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={"type": "eat", "name": "测试", "start_time": "09:00", "end_time": "08:00"},
        headers=auth(),
    )

    assert response.status_code == 400
    assert "开始时间" in response.json()["detail"]


@pytest.mark.anyio
async def test_update_activity_start_after_end_returns_400(client):
    trip_id = await create_trip(client)
    day_id = await create_day(client, trip_id)
    act_id = (await client.post(
        f"/api/trips/{trip_id}/days/{day_id}/activities",
        json={"type": "eat", "name": "早餐", "start_time": "08:00", "end_time": "09:00"},
        headers=auth(),
    )).json()["id"]

    response = await client.put(
        f"/api/trips/{trip_id}/days/{day_id}/activities/{act_id}",
        json={"start_time": "10:00", "end_time": "09:00"},
        headers=auth(),
    )

    assert response.status_code == 400
    assert "开始时间" in response.json()["detail"]
