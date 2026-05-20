"""活动业务逻辑"""


def create_activity(db, day_id: int, data: dict) -> dict:
    max_order = db.execute(
        "SELECT COALESCE(MAX(sort_order), -1) FROM activities WHERE day_id = ? AND deleted_at IS NULL",
        (day_id,),
    ).fetchone()[0]

    need_res = 1 if data.get("need_reservation") else 0
    cursor = db.execute(
        """INSERT INTO activities (day_id, type, name, location, start_time, end_time, sort_order,
           need_reservation, reservation_detail, expense_amount, expense_payer, expense_split, review)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (day_id, data["type"], data["name"],
         data.get("location", ""), data.get("start_time", ""), data.get("end_time", ""),
         max_order + 1,
         need_res, data.get("reservation_detail", ""),
         data.get("expense_amount"),
         data.get("expense_payer") or None, data.get("expense_split") or None,
         data.get("review", "")),
    )
    db.commit()
    act = db.execute("SELECT * FROM activities WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(act)


def list_activities(db, day_id: int) -> list[dict]:
    acts = db.execute(
        "SELECT * FROM activities WHERE day_id = ? AND deleted_at IS NULL ORDER BY sort_order",
        (day_id,),
    ).fetchall()
    return [dict(a) for a in acts]


def get_activity(db, act_id: int) -> dict | None:
    act = db.execute(
        "SELECT * FROM activities WHERE id = ? AND deleted_at IS NULL", (act_id,)
    ).fetchone()
    return dict(act) if act else None


def update_activity(db, act_id: int, data: dict) -> dict | None:
    act = get_activity(db, act_id)
    if not act:
        return None
    fields = []
    values = []
    for key in ("type", "name", "location", "start_time", "end_time",
                 "need_reservation", "reservation_detail",
                 "expense_amount", "expense_payer", "expense_split", "review"):
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if fields:
        values.append(act_id)
        db.execute(f"UPDATE activities SET {', '.join(fields)} WHERE id = ?", values)
        db.commit()
    return get_activity(db, act_id)


def delete_activity(db, act_id: int) -> bool:
    act = get_activity(db, act_id)
    if not act:
        return False
    db.execute(
        "UPDATE activities SET deleted_at = datetime('now', 'localtime') WHERE id = ?",
        (act_id,),
    )
    db.commit()
    return True


def reorder_activities(db, day_id: int, orders: list[dict]) -> bool:
    for item in orders:
        db.execute(
            "UPDATE activities SET sort_order = ? WHERE id = ? AND day_id = ? AND deleted_at IS NULL",
            (item["sort_order"], item["id"], day_id),
        )
    db.commit()
    return True
