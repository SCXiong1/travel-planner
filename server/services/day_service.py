"""天业务逻辑"""


def create_day(db, trip_id: int, data: dict) -> dict:
    # 自动分配 day_number
    max_num = db.execute(
        "SELECT COALESCE(MAX(day_number), 0) FROM days WHERE trip_id = ? AND deleted_at IS NULL",
        (trip_id,),
    ).fetchone()[0]

    cursor = db.execute(
        "INSERT INTO days (trip_id, day_number, date, title) VALUES (?, ?, ?, ?)",
        (trip_id, max_num + 1, data["date"], data.get("title", "")),
    )
    db.commit()
    day = db.execute("SELECT * FROM days WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(day)


def list_days(db, trip_id: int) -> list[dict]:
    days = db.execute(
        "SELECT * FROM days WHERE trip_id = ? AND deleted_at IS NULL ORDER BY day_number",
        (trip_id,),
    ).fetchall()
    return [dict(d) for d in days]


def get_day(db, day_id: int) -> dict | None:
    day = db.execute(
        "SELECT * FROM days WHERE id = ? AND deleted_at IS NULL", (day_id,)
    ).fetchone()
    return dict(day) if day else None


def update_day(db, day_id: int, data: dict) -> dict | None:
    day = get_day(db, day_id)
    if not day:
        return None
    fields = []
    values = []
    for key in ("date", "title"):
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if fields:
        values.append(day_id)
        db.execute(f"UPDATE days SET {', '.join(fields)} WHERE id = ?", values)
        db.commit()
    return get_day(db, day_id)


def delete_day(db, day_id: int) -> bool:
    day = get_day(db, day_id)
    if not day:
        return False
    db.execute(
        "UPDATE days SET deleted_at = datetime('now', 'localtime') WHERE id = ?",
        (day_id,),
    )
    db.commit()
    return True


def reorder_days(db, trip_id: int, orders: list[dict]) -> bool:
    for item in orders:
        db.execute(
            "UPDATE days SET day_number = ? WHERE id = ? AND trip_id = ? AND deleted_at IS NULL",
            (item["day_number"], item["id"], trip_id),
        )
    db.commit()
    return True
