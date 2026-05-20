"""打包清单业务逻辑"""


def create_item(db, trip_id: int, data: dict) -> dict:
    max_order = db.execute(
        "SELECT COALESCE(MAX(sort_order), -1) FROM packing_items WHERE trip_id = ? AND deleted_at IS NULL",
        (trip_id,),
    ).fetchone()[0]

    cursor = db.execute(
        "INSERT INTO packing_items (trip_id, name, category, assignee, sort_order) VALUES (?, ?, ?, ?, ?)",
        (trip_id, data["name"], data["category"], data["assignee"], max_order + 1),
    )
    db.commit()
    item = db.execute("SELECT * FROM packing_items WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(item)


def list_items(db, trip_id: int) -> list[dict]:
    items = db.execute(
        "SELECT * FROM packing_items WHERE trip_id = ? AND deleted_at IS NULL ORDER BY sort_order",
        (trip_id,),
    ).fetchall()
    return [dict(i) for i in items]


def get_item(db, item_id: int) -> dict | None:
    item = db.execute(
        "SELECT * FROM packing_items WHERE id = ? AND deleted_at IS NULL", (item_id,)
    ).fetchone()
    return dict(item) if item else None


def update_item(db, item_id: int, data: dict) -> dict | None:
    item = get_item(db, item_id)
    if not item:
        return None
    fields = []
    values = []
    for key in ("name", "category", "assignee"):
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if fields:
        values.append(item_id)
        db.execute(f"UPDATE packing_items SET {', '.join(fields)} WHERE id = ?", values)
        db.commit()
    return get_item(db, item_id)


def toggle_check(db, item_id: int) -> dict | None:
    item = get_item(db, item_id)
    if not item:
        return None
    new_val = 0 if item["checked"] else 1
    db.execute("UPDATE packing_items SET checked = ? WHERE id = ?", (new_val, item_id))
    db.commit()
    return get_item(db, item_id)


def delete_item(db, item_id: int) -> bool:
    item = get_item(db, item_id)
    if not item:
        return False
    db.execute(
        "UPDATE packing_items SET deleted_at = datetime('now', 'localtime') WHERE id = ?",
        (item_id,),
    )
    db.commit()
    return True
