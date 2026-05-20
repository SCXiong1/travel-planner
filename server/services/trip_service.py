"""旅行计划业务逻辑"""

from datetime import datetime


def create_trip(db, data: dict) -> dict:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    cursor = db.execute(
        "INSERT INTO trips (title, destination, start_date, end_date, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (data["title"], data["destination"], data["start_date"], data["end_date"], now),
    )
    db.commit()
    trip = db.execute("SELECT * FROM trips WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(trip)


def list_trips(db) -> list[dict]:
    trips = db.execute(
        "SELECT * FROM trips WHERE deleted_at IS NULL ORDER BY created_at DESC, id DESC"
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
