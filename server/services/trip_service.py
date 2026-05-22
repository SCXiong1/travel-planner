"""旅行计划业务逻辑"""

from datetime import datetime
from fastapi import HTTPException


def create_trip(db, data: dict) -> dict:
    if data["start_date"] > data["end_date"]:
        raise HTTPException(400, "开始日期不能晚于结束日期")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    db.execute(
        "UPDATE trips SET sort_order = sort_order + 1 WHERE deleted_at IS NULL"
    )
    cursor = db.execute(
        "INSERT INTO trips (title, destination, start_date, end_date, created_at, sort_order) "
        "VALUES (?, ?, ?, ?, ?, 0)",
        (data["title"], data["destination"], data["start_date"], data["end_date"], now),
    )
    db.commit()
    trip = db.execute("SELECT * FROM trips WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(trip)


def list_trips(db) -> list[dict]:
    trips = db.execute(
        "SELECT * FROM trips WHERE deleted_at IS NULL ORDER BY sort_order, id"
    ).fetchall()
    return [dict(t) for t in trips]


def get_trip(db, trip_id: int) -> dict | None:
    trip = db.execute(
        "SELECT * FROM trips WHERE id = ? AND deleted_at IS NULL", (trip_id,)
    ).fetchone()
    return dict(trip) if trip else None


def update_trip(db, trip_id: int, data: dict) -> dict | None:
    trip = get_trip(db, trip_id)
    if not trip:
        return None

    sd = data.get("start_date", trip["start_date"])
    ed = data.get("end_date", trip["end_date"])
    if sd > ed:
        raise HTTPException(400, "开始日期不能晚于结束日期")

    fields = []
    values = []
    for key in ("title", "destination", "start_date", "end_date"):
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if fields:
        values.append(trip_id)
        db.execute(f"UPDATE trips SET {', '.join(fields)} WHERE id = ?", values)
        db.commit()
    return get_trip(db, trip_id)


def delete_trip(db, trip_id: int) -> bool:
    trip = get_trip(db, trip_id)
    if not trip:
        return False
    db.execute("UPDATE trips SET deleted_at = datetime('now', 'localtime') WHERE id = ?", (trip_id,))
    db.commit()
    return True


def reorder_trips(db, orders: list[dict]) -> bool:
    for item in orders:
        db.execute(
            "UPDATE trips SET sort_order = ? WHERE id = ? AND deleted_at IS NULL",
            (item["sort_order"], item["id"]),
        )
    db.commit()
    return True
