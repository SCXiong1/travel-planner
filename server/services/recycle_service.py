"""回收站业务逻辑"""

from fastapi import HTTPException

TABLE_MAP = {
    "trip": "trips",
    "day": "days",
    "activity": "activities",
    "packing": "packing_items",
}


def list_deleted(db, trip_id: int | None = None) -> list[dict]:
    items = []

    # 已删除的 trips
    trip_where = "WHERE deleted_at IS NOT NULL"
    trip_params: tuple = ()
    if trip_id is not None:
        trip_where += " AND id = ?"
        trip_params = (trip_id,)
    trips = db.execute(
        f"""SELECT id, title as name, deleted_at, 'trip' as type
            FROM trips {trip_where}
            ORDER BY deleted_at DESC""",
        trip_params,
    ).fetchall()
    items.extend(dict(t) for t in trips)

    # 已删除的 days
    day_where = "WHERE d.deleted_at IS NOT NULL"
    day_params: tuple = ()
    if trip_id is not None:
        day_where += " AND d.trip_id = ?"
        day_params = (trip_id,)
    days = db.execute(
        f"""SELECT d.id, (d.date || ' Day' || d.day_number) as name, d.deleted_at, 'day' as type,
                   t.title as trip_title, d.trip_id
            FROM days d
            JOIN trips t ON d.trip_id = t.id
            {day_where}
            ORDER BY d.deleted_at DESC""",
        day_params,
    ).fetchall()
    items.extend(dict(d) for d in days)

    # 已删除的活动
    act_where = "a.deleted_at IS NOT NULL"
    act_params: tuple = ()
    if trip_id is not None:
        act_where += " AND d.trip_id = ?"
        act_params = (trip_id,)
    acts = db.execute(
        f"""SELECT a.id, a.name, a.deleted_at, 'activity' as type,
                   d.date as day_date, d.day_number, d.trip_id, t.title as trip_title
            FROM activities a
            JOIN days d ON a.day_id = d.id
            JOIN trips t ON d.trip_id = t.id
            WHERE {act_where}
            ORDER BY a.deleted_at DESC""",
        act_params,
    ).fetchall()
    items.extend(dict(a) for a in acts)

    # 已删除的打包物品
    pkg_where = "p.deleted_at IS NOT NULL"
    pkg_params: tuple = ()
    if trip_id is not None:
        pkg_where += " AND p.trip_id = ?"
        pkg_params = (trip_id,)
    packings = db.execute(
        f"""SELECT p.id, p.name, p.deleted_at, 'packing' as type,
                   t.title as trip_title, p.trip_id
            FROM packing_items p
            JOIN trips t ON p.trip_id = t.id
            WHERE {pkg_where}
            ORDER BY p.deleted_at DESC""",
        pkg_params,
    ).fetchall()
    items.extend(dict(p) for p in packings)

    items.sort(key=lambda x: x["deleted_at"] or "", reverse=True)
    return items


def restore(db, item_type: str, item_id: int) -> bool:
    table = TABLE_MAP.get(item_type)
    if not table:
        return False

    item = db.execute(
        f"SELECT * FROM {table} WHERE id = ? AND deleted_at IS NOT NULL", (item_id,)
    ).fetchone()
    if not item:
        return False

    # parent 链校验
    if item_type == "day":
        trip = db.execute(
            "SELECT id FROM trips WHERE id = ? AND deleted_at IS NOT NULL",
            (item["trip_id"],),
        ).fetchone()
        if trip:
            raise HTTPException(400, "请先恢复所属旅行")

    elif item_type == "activity":
        day = db.execute(
            "SELECT id FROM days WHERE id = ? AND deleted_at IS NOT NULL",
            (item["day_id"],),
        ).fetchone()
        if day:
            raise HTTPException(400, "请先恢复所属天")
        trip = db.execute(
            "SELECT id FROM trips WHERE id IN (SELECT trip_id FROM days WHERE id = ?) AND deleted_at IS NOT NULL",
            (item["day_id"],),
        ).fetchone()
        if trip:
            raise HTTPException(400, "请先恢复所属旅行")

    elif item_type == "packing":
        trip = db.execute(
            "SELECT id FROM trips WHERE id = ? AND deleted_at IS NOT NULL",
            (item["trip_id"],),
        ).fetchone()
        if trip:
            raise HTTPException(400, "请先恢复所属旅行")

    db.execute(f"UPDATE {table} SET deleted_at = NULL WHERE id = ?", (item_id,))
    db.commit()
    return True


def permanent_delete(db, item_type: str, item_id: int) -> bool:
    table = TABLE_MAP.get(item_type)
    if not table:
        return False

    item = db.execute(
        f"SELECT id FROM {table} WHERE id = ? AND deleted_at IS NOT NULL", (item_id,)
    ).fetchone()
    if not item:
        return False

    db.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
    db.commit()
    return True
