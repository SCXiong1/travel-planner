"""回收站业务逻辑"""


def list_deleted(db, trip_id: int) -> list[dict]:
    items = []

    # 已删除的活动
    acts = db.execute(
        """SELECT a.id, a.name, a.deleted_at, 'activity' as type
           FROM activities a
           JOIN days d ON a.day_id = d.id
           WHERE d.trip_id = ? AND a.deleted_at IS NOT NULL
           ORDER BY a.deleted_at DESC""",
        (trip_id,),
    ).fetchall()
    items.extend(dict(a) for a in acts)

    # 已删除的打包物品
    packings = db.execute(
        """SELECT id, name, deleted_at, 'packing' as type
           FROM packing_items
           WHERE trip_id = ? AND deleted_at IS NOT NULL
           ORDER BY deleted_at DESC""",
        (trip_id,),
    ).fetchall()
    items.extend(dict(p) for p in packings)

    # 按删除时间倒序
    items.sort(key=lambda x: x["deleted_at"] or "", reverse=True)
    return items


def restore(db, item_type: str, item_id: int) -> bool:
    table = "activities" if item_type == "activity" else "packing_items"
    item = db.execute(
        f"SELECT id FROM {table} WHERE id = ? AND deleted_at IS NOT NULL", (item_id,)
    ).fetchone()
    if not item:
        return False
    db.execute(f"UPDATE {table} SET deleted_at = NULL WHERE id = ?", (item_id,))
    db.commit()
    return True
